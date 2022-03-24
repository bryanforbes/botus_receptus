from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TypedDict, TypeVar, cast

import discord
from discord.ext import commands

from .bot import AutoShardedBot, Bot

BotT = TypeVar('BotT', bound='Bot | AutoShardedBot')


class GuildContext(commands.Context[BotT]):
    @discord.utils.cached_property
    def guild(self, /) -> discord.Guild:
        return self.message.guild  # type: ignore

    @discord.utils.cached_property
    def channel(self, /) -> discord.TextChannel:
        return self.message.channel  # type: ignore

    @discord.utils.cached_property
    def author(self, /) -> discord.Member:
        return self.message.author  # type: ignore


class FooterData(TypedDict, total=False):
    text: str
    icon_url: str


class UrlData(TypedDict, total=False):
    url: str


class AuthorDataBase(TypedDict):
    name: str


class AuthorData(AuthorDataBase, UrlData, total=False):
    icon_url: str


class FieldDataBase(TypedDict):
    name: str
    value: str


class FieldData(FieldDataBase, total=False):
    inline: bool


class EmbedContext(commands.Context[BotT]):
    async def send_embed(
        self,
        description: str,
        *,
        title: str | None = None,
        color: discord.Color | int | None = None,
        footer: str | FooterData | None = None,
        thumbnail: str | None = None,
        author: str | AuthorData | None = None,
        image: str | None = None,
        timestamp: datetime | None = None,
        fields: list[FieldData] | None = None,
        tts: bool = False,
        file: discord.File | None = None,
        files: list[discord.File] | None = None,
        delete_after: float | None = None,
        nonce: int | None = None,
        reference: discord.Message
        | discord.MessageReference
        | discord.PartialMessage
        | None = None,
        view: discord.ui.View | None = None,
    ) -> discord.Message:
        embed = discord.Embed(description=description)

        if title is not None:
            embed.title = title
        if color is not None:
            embed.color = color
        if footer is not None:
            if isinstance(footer, str):
                embed.set_footer(text=footer)
            else:
                embed.set_footer(**footer)
        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)
        if author is not None:
            if isinstance(author, str):
                embed.set_author(name=author)
            else:
                embed.set_author(**author)
        if image is not None:
            embed.set_image(url=image)
        if timestamp is not None:
            embed.timestamp = timestamp
        if fields is not None:
            setattr(embed, '_fields', fields)  # noqa: B010

        return await self.send(  # type: ignore
            tts=tts,
            embed=embed,
            file=file,
            files=files,
            delete_after=delete_after,
            nonce=nonce,
            reference=reference,
            view=view,
        )


class PaginatedContext(commands.Context[BotT]):
    async def send_pages(
        self,
        pages: Iterable[str],
        *,
        tts: bool = False,
        delete_after: float | None = None,
        nonce: int | None = None,
        reference: discord.Message
        | discord.MessageReference
        | discord.PartialMessage
        | None = None,
        view: discord.ui.View | None = None,
    ) -> list[discord.Message]:
        return [
            await self.send(
                page,
                tts=tts,
                delete_after=cast(float, delete_after),
                nonce=cast(int, nonce),
                reference=reference,  # type: ignore
                view=view,  # type: ignore
            )
            for page in pages
        ]
