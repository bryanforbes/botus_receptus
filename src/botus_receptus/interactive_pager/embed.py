from __future__ import annotations

from abc import abstractmethod
from typing import AsyncIterator, Tuple, TypeVar

import discord
from aioitertools import enumerate as aenumerate
from aioitertools.types import AnyIterable
from attr import dataclass

from .base import InteractivePager, SequenceSource, Source

__all__ = (
    'EmbedSource',
    'DescriptionSource',
    'DescriptionSequenceSource',
    'FieldSource',
    'FieldSequenceSource',
    'InteractiveEmbedPager',
)


_T = TypeVar('_T')


class EmbedSource(Source[discord.Embed, _T]):
    @abstractmethod
    async def add_entries_to_embed(
        self, embed: discord.Embed, entries: AsyncIterator[Tuple[int, _T]]
    ) -> None:
        ...

    async def get_page_content(
        self, page: int, entries: AnyIterable[_T]
    ) -> discord.Embed:
        embed = discord.Embed()

        await self.add_entries_to_embed(
            embed, aenumerate(entries, 1 + (page - 1) * self.per_page)
        )

        footer_text = self.get_footer_text(page)
        if footer_text is not None:
            embed.set_footer(text=footer_text)

        return embed


class DescriptionSource(EmbedSource[_T]):
    def format_entry(self, index: int, entry: _T) -> str:
        return f'{index}. {entry}'

    async def add_entries_to_embed(
        self, embed: discord.Embed, entries: AsyncIterator[Tuple[int, _T]]
    ) -> None:
        lines = [self.format_entry(index, entry) async for index, entry in entries]

        embed.description = '\n'.join(lines)


class FieldSource(EmbedSource[_T]):
    def format_entry(self, index: int, entry: _T) -> Tuple[str, str]:
        return (str(index), str(entry))

    async def add_entries_to_embed(
        self, embed: discord.Embed, entries: AsyncIterator[Tuple[int, _T]]
    ) -> None:
        async for index, entry in entries:
            name, value = self.format_entry(index, entry)
            embed.add_field(name=name, value=value, inline=False)


class DescriptionSequenceSource(
    SequenceSource[discord.Embed, _T], DescriptionSource[_T]
):
    pass


class FieldSequenceSource(SequenceSource[discord.Embed, _T], FieldSource[_T]):
    pass


@dataclass(slots=True, cmp=False)
class InteractiveEmbedPager(InteractivePager[discord.Embed, _T]):
    async def send_message(
        self, page: discord.Embed, *, first: bool = False
    ) -> discord.Message:
        return await self.channel.send(embed=page)

    async def edit_message(self, page: discord.Embed) -> None:
        await self.message.edit(embed=page)

    async def edit_help(self, help_text: str, footer_text: str) -> None:
        embed = discord.Embed()
        embed.description = help_text
        embed.set_footer(text=footer_text)
        await self.edit_message(embed)
