from __future__ import annotations

from typing import (
    Any,
    Optional,
    Union,
    List,
    Tuple,
    Callable,
    Coroutine,
    TypeVar,
    Type,
    Generic,
    cast,
)
from abc import abstractmethod
import attr
import discord
import asyncio
from discord.ext import commands

from .util import enumerate as aenumerate, maybe_await, SyncOrAsyncIterable


class CannotPaginate(Exception):
    pass


P = TypeVar('P', bound='Paginator')  # noqa: F821
T = TypeVar('T')


@attr.s(slots=True, auto_attribs=True)
class Page:
    entry_text: str
    footer_text: Optional[str]


@attr.s(slots=True, auto_attribs=True)
class PageFetcher(Generic[T]):
    total: int
    per_page: int
    show_entry_count: bool
    max_pages: int = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        max_pages, left_over = divmod(self.total, self.per_page)

        if left_over:
            max_pages += 1

        self.max_pages = max_pages

    @property
    def paginated(self) -> bool:
        return self.total > self.per_page

    @abstractmethod
    def get_page(
        self, page: int
    ) -> Union[Coroutine[Any, Any, SyncOrAsyncIterable[T]], SyncOrAsyncIterable[T]]:
        ...

    def format_entry(self, index: int, entry: T) -> str:
        return f'{index}. {entry}'

    def get_footer_text(self, page: int) -> Optional[str]:
        if self.max_pages < 2:
            return None

        text = f'Page {page}/{self.max_pages}'

        if self.show_entry_count:
            text = f'{text} ({self.total} entries)'

        return text

    async def get_formatted_page(self, page: int) -> Page:
        entries: SyncOrAsyncIterable[T] = await maybe_await(self.get_page(page))
        lines = [
            self.format_entry(index, entry)
            async for index, entry in aenumerate(
                entries, 1 + (page - 1) * self.per_page
            )
        ]

        footer_text = self.get_footer_text(page)

        return Page(entry_text='\n'.join(lines), footer_text=footer_text)


LPF = TypeVar('LPF', bound='ListPageFetcher')  # noqa: F821


@attr.s(slots=True, auto_attribs=True)
class ListPageFetcher(PageFetcher[T]):
    entries: List[T]

    def get_page(self, page: int) -> List[T]:
        base = (page - 1) * self.per_page
        return self.entries[base : base + self.per_page]

    @classmethod
    def create(
        cls: Type[LPF],
        entries: List[T],
        per_page: int,
        *,
        show_entry_count: bool = True,
    ) -> LPF:
        return cls(
            total=len(entries),
            entries=entries,
            per_page=per_page,
            show_entry_count=show_entry_count,
        )


@attr.s(slots=True, auto_attribs=True)
class Paginator(Generic[T]):
    bot: commands.Bot
    message: discord.Message
    channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]
    author: Union[discord.User, discord.Member]
    fetcher: PageFetcher[T]

    embed: discord.Embed = attr.ib(init=False)
    paginating: bool = attr.ib(init=False)
    current_page: int = attr.ib(init=False, default=-1)
    reaction_emojis: List[
        Tuple[str, bool, Callable[[], Coroutine[Any, Any, None]]]
    ] = attr.ib(init=False)
    match: Optional[Callable[[], Coroutine[Any, Any, None]]] = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        self.embed = discord.Embed()
        self.paginating = self.fetcher.paginated
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
                if self.fetcher.max_pages == 2 and not show_for_two:
                    return False

                self.match = func
                return True

        return False

    def __message_check(self, message: discord.Message) -> bool:
        return (
            message.author == self.author
            and message.channel == self.channel
            and message.content.isdigit()
        )

    async def __modify_embed(self, page: int, *, first: bool = False) -> None:
        formatted = await self.fetcher.get_formatted_page(page)
        lines = [formatted.entry_text]

        if formatted.footer_text:
            self.embed.set_footer(text=formatted.footer_text)

        if self.paginating and first:
            lines.append('')
            lines.append('Confused? React with \N{INFORMATION SOURCE} for more info.')

        self.embed.description = '\n'.join(lines)

    async def __show_page(self, page: int, *, first: bool = False) -> None:
        self.current_page = page
        await self.__modify_embed(page, first=first)

        if not self.paginating:
            await self.channel.send(embed=self.embed)
            return

        if not first:
            await self.message.edit(embed=self.embed)
            return

        self.message = await self.channel.send(embed=self.embed)

        for reaction, show_for_two, _ in self.reaction_emojis:
            if self.fetcher.max_pages == 2 and not show_for_two:
                continue

            await self.message.add_reaction(reaction)

    async def __checked_show_page(self, page: int) -> None:
        if page > 0 and page <= self.fetcher.max_pages:
            await self.__show_page(page)

    async def __first_page(self) -> None:
        '''goes to the first page'''
        await self.__show_page(1)

    async def __last_page(self) -> None:
        '''goes to the last page'''
        await self.__show_page(self.fetcher.max_pages)

    async def __previous_page(self) -> None:
        '''goes to the previous page'''
        await self.__checked_show_page(self.current_page - 1)

    async def __next_page(self) -> None:
        '''goes to the next page'''
        await self.__checked_show_page(self.current_page + 1)

    async def __numbered_page(self) -> None:
        to_delete: List[discord.Message] = []
        to_delete.append(await self.channel.send('What page do you want to go to?'))

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
            if page != 0 and page <= self.fetcher.max_pages:
                await self.__show_page(page)
            else:
                to_delete.append(
                    await self.channel.send(
                        f'Invalid page given. ({page}/{self.fetcher.max_pages})'
                    )
                )
                await asyncio.sleep(5)

        try:
            await cast(discord.TextChannel, self.channel).delete_messages(to_delete)
        except Exception:
            pass

    async def __stop_pages(self) -> None:
        '''stops the interactive pagination session'''
        await self.message.delete()
        self.paginating = False

    async def __show_current_page(self) -> None:
        if self.paginating:
            await self.__show_page(self.current_page)

    async def __show_help(self) -> None:
        '''shows this message'''
        messages = [
            'Welcome to the interactive paginator!\n',
            'This interactively allows you to see pages of text by navigating with '
            'reactions. They are as follows:\n',
        ]

        for emoji, show_for_two, func in self.reaction_emojis:
            if self.fetcher.max_pages == 2 and not show_for_two:
                continue

            messages.append(f'{emoji} {func.__doc__}')

        self.embed.description = '\n'.join(messages)
        self.embed.clear_fields()
        self.embed.set_footer(
            text=f'You were on page {self.current_page} before this message.'
        )
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page() -> None:
            await asyncio.sleep(60.0)
            await self.__show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def paginate(self) -> None:
        first_page = self.__show_page(1, first=True)
        if not self.paginating:
            await first_page
            return

        self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add', check=self.__react_check, timeout=120.0
                )
            except asyncio.TimeoutError:
                self.paginating = False

                try:
                    await self.message.clear_reactions()
                except Exception:
                    pass
                finally:
                    break

            try:
                if user is not None:
                    await self.message.remove_reaction(reaction, user)
            except Exception:
                pass

            assert self.match is not None
            await self.match()

    @classmethod
    def create(cls: Type[P], ctx: commands.Context, fetcher: PageFetcher[T]) -> P:
        if ctx.guild is not None:
            permissions = cast(discord.abc.GuildChannel, ctx.channel).permissions_for(
                ctx.guild.me
            )
        else:
            permissions = cast(discord.GroupChannel, ctx.channel).permissions_for(
                ctx.bot.user
            )

        if not permissions.embed_links:
            raise CannotPaginate('Bot does not have Embed Links permission.')

        if not permissions.send_messages:
            raise CannotPaginate('Bot cannot send messages.')

        if fetcher.paginated:
            # verify we can actually use the pagination session
            if not permissions.add_reactions:
                raise CannotPaginate('Bot does not have Add Reactions permission.')

            if not permissions.read_message_history:
                raise CannotPaginate(
                    'Bot does not have Read Message History permission.'
                )

        return cls(
            bot=ctx.bot,
            message=ctx.message,
            channel=ctx.channel,
            author=ctx.author,
            fetcher=fetcher,
        )
