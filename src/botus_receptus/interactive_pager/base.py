from __future__ import annotations

import asyncio
import enum
from abc import abstractmethod
from collections import OrderedDict
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import discord
from aioitertools.helpers import maybe_await
from aioitertools.types import AnyIterable
from attr import attrib, dataclass
from discord.ext import commands

from ..formatting import warning
from ..util import race

__all__ = (
    'CannotPaginateReason',
    'CannotPaginate',
    'Source',
    'SequenceSource',
    'InteractivePager',
)

_WaitResult = Tuple[discord.Reaction, Optional[Union[discord.User, discord.Member]]]

_P = TypeVar('_P')
_T = TypeVar('_T')


class CannotPaginateReason(enum.IntEnum):
    embed_links = 0
    send_messages = 1
    add_reactions = 2
    read_message_history = 3


class CannotPaginate(Exception):
    reason: CannotPaginateReason

    def __init__(self, reason: CannotPaginateReason) -> None:
        self.reason = reason


@dataclass(slots=True, cmp=False)
class Source(Generic[_P, _T]):
    total: int
    per_page: int
    show_entry_count: bool = attrib(kw_only=True, default=True)
    _max_pages: int = attrib(init=False)

    @discord.utils.cached_slot_property('_max_pages')
    def max_pages(self) -> int:
        max_pages, left_over = divmod(self.total, self.per_page)

        if left_over:
            max_pages += 1

        return max_pages

    @property
    def paginated(self) -> bool:
        return self.total > self.per_page

    @abstractmethod
    def get_page_items(
        self, page: int
    ) -> Union[Coroutine[Any, Any, AnyIterable[_T]], AnyIterable[_T]]:
        ...

    @abstractmethod
    async def get_page_content(self, page: int, entries: AnyIterable[_T]) -> _P:
        ...

    def get_footer_text(self, page: int) -> Optional[str]:
        if self.max_pages < 2:
            return None

        text = f'Page {page}/{self.max_pages}'

        if self.show_entry_count:
            text = f'{text} ({self.total} entries)'

        return text

    async def get_page(self, page: int) -> _P:
        entries: AnyIterable[_T] = await maybe_await(self.get_page_items(page))
        return await maybe_await(self.get_page_content(page, entries))


@dataclass(slots=True, cmp=False)
class SequenceSource(Source[_P, _T]):
    entries: Sequence[_T]
    show_entry_count: bool = attrib(kw_only=True, default=True)
    total: int = attrib(init=False)

    def __attrs_post_init__(self) -> None:
        self.total = len(self.entries)

    def get_page_items(self, page: int) -> Sequence[_T]:
        base = (page - 1) * self.per_page
        return self.entries[base : base + self.per_page]


@dataclass(slots=True, cmp=False)
class InteractivePager(Generic[_P, _T]):
    REACTION_MAP: ClassVar[OrderedDict[str, str]] = OrderedDict(
        [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', 'first_page'),
            (
                '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                'previous_page',
            ),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', 'next_page'),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', 'last_page'),
            ('\N{INPUT SYMBOL FOR NUMBERS}', 'numbered_page'),
            ('\N{BLACK SQUARE FOR STOP}', 'stop_pages'),
            ('\N{INFORMATION SOURCE}', 'show_help'),
        ]
    )

    ctx: commands.Context
    source: Source[_P, _T]

    message: discord.Message = attrib(init=False)
    can_manage_messages: bool = attrib(init=False)
    paginating: bool = attrib(init=False)
    current_page: int = attrib(init=False, default=-1)
    reaction_emojis: List[
        Tuple[str, bool, Callable[[], Coroutine[Any, Any, None]]]
    ] = attrib(init=False)
    match: Optional[Callable[[], Coroutine[Any, Any, None]]] = attrib(
        init=False, default=None
    )
    help_task: Optional[asyncio.Task[Any]] = attrib(init=False, default=None)

    @property
    def bot(self) -> commands.Bot[Any]:
        return self.ctx.bot

    @property
    def channel(
        self,
    ) -> Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]:
        return self.ctx.channel

    @property
    def author(self) -> Union[discord.User, discord.Member]:
        return self.ctx.author

    def __attrs_post_init__(self) -> None:
        self.message = self.ctx.message

        if self.ctx.guild is not None:
            permissions = cast(discord.abc.GuildChannel, self.channel).permissions_for(
                self.ctx.guild.me
            )
        else:
            permissions = cast(discord.GroupChannel, self.channel).permissions_for(
                self.bot.user
            )

        if not permissions.embed_links:
            raise CannotPaginate(CannotPaginateReason.embed_links)

        if not permissions.send_messages:
            raise CannotPaginate(CannotPaginateReason.send_messages)

        if self.source.paginated:
            # verify we can actually use the pagination session
            if not permissions.add_reactions:
                raise CannotPaginate(CannotPaginateReason.add_reactions)

            if not permissions.read_message_history:
                raise CannotPaginate(CannotPaginateReason.read_message_history)

        self.can_manage_messages = permissions.manage_messages
        self.paginating = self.source.paginated

        self.reaction_emojis = [
            (
                emoji,
                method_name != 'first_page' and method_name != 'last_page',
                getattr(self, f'_{method_name}'),
            )
            for emoji, method_name in self.REACTION_MAP
        ]

    def _check_reaction(
        self,
        reaction: discord.Reaction,
        user: Optional[Union[discord.User, discord.Member]],
    ) -> bool:
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for (emoji, show_for_two, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                if self.source.max_pages == 2 and not show_for_two:
                    return False

                self.match = func

                if self.help_task is not None:
                    if self.match == self._show_help:
                        self.match = self._show_current_page

                    self.help_task.cancel()
                    self.help_task = None

                return True

        return False

    def _check_message(self, message: discord.Message) -> bool:
        return (
            message.author == self.author
            and message.channel == self.channel
            and message.content.isdigit()
        )

    async def _show_page(self, page_num: int, *, first: bool = False) -> None:
        self.current_page = page_num
        page = await self.source.get_page(page_num)

        if not self.paginating:
            await self.send_message(page)
            return

        if not first:
            await self.edit_message(page)
            return

        self.message = await self.send_message(page)

        for reaction, show_for_two, _ in self.reaction_emojis:
            if self.source.max_pages == 2 and not show_for_two:
                continue

            await self.message.add_reaction(reaction)

    async def _checked_show_page(self, page: int) -> None:
        if page > 0 and page <= self.source.max_pages:
            await self._show_page(page)

    async def _first_page(self) -> None:
        '''goes to the first page'''
        await self._show_page(1)

    async def _last_page(self) -> None:
        '''goes to the last page'''
        await self._show_page(self.source.max_pages)

    async def _previous_page(self) -> None:
        '''goes to the previous page'''
        await self._checked_show_page(self.current_page - 1)

    async def _next_page(self) -> None:
        '''goes to the next page'''
        await self._checked_show_page(self.current_page + 1)

    async def _numbered_page(self) -> None:
        '''lets you type a page number to go to'''
        to_delete: List[discord.Message] = []
        to_delete.append(await self.channel.send('What page do you want to go to?'))

        try:
            message = await self.bot.wait_for(
                'message', check=self._check_message, timeout=30.0
            )
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(message.content)
            to_delete.append(message)
            if page != 0 and page <= self.source.max_pages:
                await self._show_page(page)
            else:
                to_delete.append(
                    await self.channel.send(
                        f'Invalid page given. ({page}/{self.source.max_pages})'
                    )
                )
                await asyncio.sleep(5)

        try:
            await cast(discord.TextChannel, self.channel).delete_messages(to_delete)
        except Exception:
            pass

    async def _stop_pages(self) -> None:
        '''stops the interactive pagination session'''
        await self.message.delete()
        self.paginating = False
        if self.help_task is not None:
            self.help_task.cancel()
            self.help_task = None

    async def _show_current_page(self) -> None:
        if self.paginating:
            await self._show_page(self.current_page)

    def get_help_text(self) -> Tuple[str, str]:
        messages = [
            'Welcome to the interactive pager!\n',
            'This interactively allows you to see pages of text by navigating with '
            'reactions. They are as follows:\n',
        ]

        for emoji, show_for_two, func in self.reaction_emojis:
            if self.source.max_pages == 2 and not show_for_two:
                continue

            messages.append(f'{emoji} - {func.__doc__}')

        if not self.can_manage_messages:
            messages.append(
                '\n'
                + warning(
                    'Giving me "Manage Messages" permissions will provide a better '
                    'user experience for the interactive pager'
                )
            )

        return (
            '\n'.join(messages),
            f'You were on page {self.current_page} before this message.',
        )

    async def _show_help(self) -> None:
        '''shows this message'''
        help_text, footer_text = self.get_help_text()

        await self.edit_help(help_text, footer_text)

        async def go_back_to_current_page() -> None:
            await asyncio.sleep(60.0)
            await self._show_current_page()
            self.help_task = None

        self.help_task = self.bot.loop.create_task(go_back_to_current_page())

    @abstractmethod
    async def send_message(self, page: _P) -> discord.Message:
        ...

    @abstractmethod
    async def edit_message(self, page: _P) -> None:
        ...

    @abstractmethod
    async def edit_help(self, help_text: str, footer_text: str) -> None:
        ...

    async def paginate(self) -> None:
        first_page = self._show_page(1, first=True)

        if not self.paginating:
            await first_page
            return

        self.bot.loop.create_task(first_page)

        if self.can_manage_messages:

            def wait_for_reaction() -> 'asyncio.Future[_WaitResult]':
                return self.bot.wait_for(
                    'reaction_add', check=self._check_reaction, timeout=120.0
                )

        else:

            def wait_for_reaction() -> 'asyncio.Future[_WaitResult]':
                return self.bot.loop.create_task(
                    race(
                        [
                            self.bot.wait_for(
                                'reaction_add', check=self._check_reaction
                            ),
                            self.bot.wait_for(
                                'reaction_remove', check=self._check_reaction
                            ),
                        ],
                        timeout=120.0,
                        loop=self.bot.loop,
                    )
                )

        while self.paginating:
            try:
                reaction, user = await wait_for_reaction()
            except asyncio.TimeoutError:
                self.paginating = False

                try:
                    await self.message.clear_reactions()
                except Exception:
                    pass

                break

            try:
                if user is not None:
                    await self.message.remove_reaction(reaction, user)
            except Exception:
                pass

            assert self.match is not None
            await self.match()
