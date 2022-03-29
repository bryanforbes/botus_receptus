from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import TypeVar, cast

import discord
from discord.ext import commands

from .bot import AutoShardedBot, Bot
from .util import AuthorData, FieldData, FooterData, send_context

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
        fields: Sequence[FieldData] | None = None,
        tts: bool = False,
        file: discord.File | None = None,
        files: Sequence[discord.File] | None = None,
        delete_after: float | None = None,
        nonce: int | None = None,
        reference: discord.Message
        | discord.MessageReference
        | discord.PartialMessage
        | None = None,
        view: discord.ui.View | None = None,
    ) -> discord.Message:
        return await send_context(
            self,
            description=description,
            title=title,
            color=color,
            footer=footer,
            thumbnail=thumbnail,
            author=author,
            image=image,
            timestamp=timestamp,
            fields=fields,
            tts=tts,
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
