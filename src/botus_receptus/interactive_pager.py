from __future__ import annotations

import asyncio
import contextlib
import enum
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypedDict, cast
from typing_extensions import Self, TypeVar, override

import discord
import discord.abc
from aioitertools.builtins import enumerate as aenumerate
from aioitertools.helpers import maybe_await
from aioitertools.itertools import starmap
from attrs import define, field

from .formatting import warning
from .utils import race

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, Awaitable, Callable

    from aioitertools.types import AnyIterable
    from discord.ext import commands


_T = TypeVar('_T', infer_variance=True)
_WaitResult: TypeAlias = tuple[discord.Reaction, discord.User | discord.Member]

# Inspired by paginator from https://github.com/Rapptz/RoboDanny


class CannotPaginateReason(enum.IntEnum):
    embed_links = 0
    send_messages = 1
    add_reactions = 2
    read_message_history = 3


class CannotPaginate(Exception):
    reason: CannotPaginateReason

    def __init__(self, reason: CannotPaginateReason, /) -> None:
        self.reason = reason


class Page(TypedDict):
    entry_text: str
    footer_text: str | None


@define
class PageSource(Generic[_T]):
    total: int
    per_page: int
    show_entry_count: bool
    max_pages: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        max_pages, left_over = divmod(self.total, self.per_page)

        if left_over:
            max_pages += 1

        self.max_pages = max_pages

    @property
    def paginated(self) -> bool:
        return self.total > self.per_page

    @abstractmethod
    def get_page_items(
        self, page: int, /
    ) -> Awaitable[AnyIterable[_T]] | AnyIterable[_T]:
        ...

    def format_line(self, index: int, entry: _T, /) -> str:
        return f'{index}. {entry}'

    def get_footer_text(self, page: int, /) -> str | None:
        if self.max_pages < 2:
            return None

        text = f'Page {page}/{self.max_pages}'

        if self.show_entry_count:
            text = f'{text} ({self.total} entries)'

        return text

    async def get_page(self, page: int, /) -> Page:
        entries: AnyIterable[_T] = await maybe_await(self.get_page_items(page))
        lines = [
            self.format_line(index, entry)
            async for index, entry in aenumerate(
                entries, 1 + (page - 1) * self.per_page
            )
        ]

        footer_text = self.get_footer_text(page)

        return {'entry_text': '\n'.join(lines).strip(), 'footer_text': footer_text}


@define
class ListPageSource(PageSource[_T]):
    entries: list[_T]

    @override
    def get_page_items(self, page: int, /) -> list[_T]:
        base = (page - 1) * self.per_page
        return self.entries[base : base + self.per_page]

    @classmethod
    def create(
        cls,
        entries: list[_T],
        per_page: int,
        /,
        *,
        show_entry_count: bool = True,
    ) -> Self:
        return cls(
            total=len(entries),
            entries=entries,
            per_page=per_page,
            show_entry_count=show_entry_count,
        )


@define
class InteractivePager(Generic[_T]):
    bot: commands.Bot
    message: discord.Message
    channel: discord.abc.MessageableChannel
    author: discord.User | discord.Member
    can_manage_messages: bool
    source: PageSource[_T]

    embed: discord.Embed = field(init=False)
    paginating: bool = field(init=False)
    current_page: int = field(init=False, default=-1)
    reaction_emojis: list[tuple[str, bool, Callable[[], Awaitable[None]]]] = field(
        init=False
    )
    match: Callable[[], Awaitable[None]] | None = field(init=False, default=None)
    help_task: asyncio.Task[None] | None = field(init=False, default=None)

    def __attrs_post_init__(self) -> None:
        self.embed = discord.Embed()
        self.paginating = self.source.paginated
        self.reaction_emojis = [
            (
                '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                False,
                self.__first_page,
            ),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', True, self.__previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', True, self.__next_page),
            (
                '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                False,
                self.__last_page,
            ),
            ('\N{INPUT SYMBOL FOR NUMBERS}', True, self.__numbered_page),
            ('\N{BLACK SQUARE FOR STOP}', True, self.__stop_pages),
            ('\N{INFORMATION SOURCE}', True, self.__show_help),
        ]

    def __react_check(
        self, reaction: discord.Reaction, user: discord.User | discord.Member | None, /
    ) -> bool:
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for emoji, show_for_two, func in self.reaction_emojis:
            if reaction.emoji == emoji:
                if self.source.max_pages == 2 and not show_for_two:
                    return False

                self.match = func

                if self.help_task is not None:
                    if self.match == self.__show_help:
                        self.match = self.__show_current_page

                    self.help_task.cancel()
                    self.help_task = None

                return True

        return False

    def __message_check(self, message: discord.Message, /) -> bool:
        return (
            message.author == self.author
            and message.channel == self.channel
            and message.content.isdigit()
        )

    async def modify_embed(
        self, page: Page, page_num: int, /, *, first: bool = False
    ) -> None:
        lines = [page['entry_text']]

        if page['footer_text'] is not None:
            self.embed.set_footer(text=page['footer_text'])

        if self.paginating and first:
            lines.append('')
            lines.append('Confused? React with \N{INFORMATION SOURCE} for more info.')

        self.embed.description = '\n'.join(lines)

    async def __show_page(self, page_num: int, /, *, first: bool = False) -> None:
        self.current_page = page_num
        page = await self.source.get_page(page_num)
        await self.modify_embed(page, page_num, first=first)

        if not self.paginating:
            await self.channel.send(embed=self.embed)
            return

        if not first:
            await self.message.edit(embed=self.embed)
            return

        self.message = await self.channel.send(embed=self.embed)

        for reaction, show_for_two, _ in self.reaction_emojis:
            if self.source.max_pages == 2 and not show_for_two:
                continue

            await self.message.add_reaction(reaction)

    async def __checked_show_page(self, page: int, /) -> None:
        if page > 0 and page <= self.source.max_pages:
            await self.__show_page(page)

    async def __first_page(self) -> None:
        """goes to the first page"""
        await self.__show_page(1)

    async def __last_page(self) -> None:
        """goes to the last page"""
        await self.__show_page(self.source.max_pages)

    async def __previous_page(self) -> None:
        """goes to the previous page"""
        await self.__checked_show_page(self.current_page - 1)

    async def __next_page(self) -> None:
        """goes to the next page"""
        await self.__checked_show_page(self.current_page + 1)

    async def __numbered_page(self) -> None:
        """lets you type a page number to go to"""
        to_delete: list[discord.Message] = [
            await self.channel.send('What page do you want to go to?')
        ]

        try:
            message = await self.bot.wait_for(
                'message', check=self.__message_check, timeout=30.0
            )
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(message.content)
            to_delete.append(message)
            if page != 0 and page <= self.source.max_pages:
                await self.__show_page(page)
            else:
                to_delete.append(
                    await self.channel.send(
                        f'Invalid page given. ({page}/{self.source.max_pages})'
                    )
                )
                await asyncio.sleep(5)

        with contextlib.suppress(Exception):
            await cast(discord.TextChannel, self.channel).delete_messages(to_delete)

    async def __stop_pages(self) -> None:
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False
        if self.help_task is not None:
            self.help_task.cancel()
            self.help_task = None

    async def __show_current_page(self) -> None:
        if self.paginating:
            await self.__show_page(self.current_page)

    async def __show_help(self) -> None:
        """shows this message"""
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

        self.embed.description = '\n'.join(messages)
        self.embed.clear_fields()
        self.embed.set_footer(
            text=f'You were on page {self.current_page} before this message.'
        )
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page() -> None:
            await asyncio.sleep(60.0)
            await self.__show_current_page()
            self.help_task = None

        self.help_task = self.bot.loop.create_task(go_back_to_current_page())

    async def paginate(self) -> None:
        first_page = self.__show_page(1, first=True)
        if not self.paginating:
            await first_page
            return

        self.bot.loop.create_task(first_page)

        if self.can_manage_messages:

            def wait_for_reaction() -> Awaitable[_WaitResult]:
                return self.bot.wait_for(
                    'reaction_add', check=self.__react_check, timeout=120.0
                )

        else:

            def wait_for_reaction() -> Awaitable[_WaitResult]:
                return self.bot.loop.create_task(
                    race(
                        [
                            self.bot.wait_for('reaction_add', check=self.__react_check),
                            self.bot.wait_for(
                                'reaction_remove', check=self.__react_check
                            ),
                        ],
                        timeout=120.0,
                    )
                )

        while self.paginating:
            try:
                reaction, user = await wait_for_reaction()
            except asyncio.TimeoutError:
                self.paginating = False

                try:
                    await self.message.clear_reactions()
                    break
                except discord.DiscordException:
                    break

            with contextlib.suppress(Exception):
                await self.message.remove_reaction(reaction, user)

            if TYPE_CHECKING:
                assert self.match is not None

            await self.match()

    @classmethod
    def create(cls, ctx: commands.Context[Any], source: PageSource[_T], /) -> Self:
        if ctx.guild is not None:
            permissions = ctx.channel.permissions_for(ctx.guild.me)
        else:
            permissions = ctx.channel.permissions_for(ctx.bot.user)

        if not permissions.embed_links:
            raise CannotPaginate(CannotPaginateReason.embed_links)

        if not permissions.send_messages:
            raise CannotPaginate(CannotPaginateReason.send_messages)

        if source.paginated:
            # verify we can actually use the pagination session
            if not permissions.add_reactions:
                raise CannotPaginate(CannotPaginateReason.add_reactions)

            if not permissions.read_message_history:
                raise CannotPaginate(CannotPaginateReason.read_message_history)

        return cls(
            bot=ctx.bot,
            message=ctx.message,
            channel=ctx.channel,
            author=ctx.author,
            can_manage_messages=permissions.manage_messages,
            source=source,
        )


class FieldPage(Page):
    fields: AsyncIterable[tuple[int, object]]


@define
class FieldPageSource(PageSource[_T]):
    def format_field(self, index: int, entry: _T, /) -> tuple[int, _T]:
        return (index, entry)

    @override
    async def get_page(self, page: int, /) -> FieldPage:
        entries: AnyIterable[_T] = await maybe_await(self.get_page_items(page))
        fields = starmap(
            self.format_field, aenumerate(entries, 1 + (page - 1) * self.per_page)
        )
        return {
            'entry_text': '',
            'footer_text': self.get_footer_text(page),
            'fields': fields,
        }


@define
class InteractiveFieldPager(InteractivePager[_T]):
    source: FieldPageSource[_T]

    @override
    async def modify_embed(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, page: FieldPage, page_num: int, /, *, first: bool = False
    ) -> None:
        self.embed.clear_fields()
        self.embed.description = None

        async for key, value in page['fields']:
            self.embed.add_field(name=key, value=value, inline=False)

        if page['footer_text'] is not None:
            self.embed.set_footer(text=page['footer_text'])

    @classmethod
    @override
    def create(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, ctx: commands.Context[Any], source: FieldPageSource[_T], /
    ) -> Self:
        return super().create(ctx, source)
