from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Final, TypeVar

import discord
from discord.ext import commands

from . import utils
from .bot import AutoShardedBot, Bot

_BotT = TypeVar('_BotT', bound=Bot | AutoShardedBot)

_MISSING: Final = discord.utils.MISSING


class GuildContext(commands.Context[_BotT]):
    @discord.utils.cached_property
    def guild(self, /) -> discord.Guild:
        return self.message.guild  # type: ignore

    @discord.utils.cached_property
    def channel(self, /) -> discord.TextChannel:
        return self.message.channel  # type: ignore

    @discord.utils.cached_property
    def author(self, /) -> discord.Member:
        return self.message.author  # type: ignore


class EmbedContext(commands.Context[_BotT]):
    async def send_embed(
        self,
        description: str,
        *,
        title: str | None = None,
        color: discord.Color | int | None = None,
        footer: str | utils.FooterData | None = None,
        thumbnail: str | None = None,
        author: str | utils.AuthorData | None = None,
        image: str | None = None,
        timestamp: datetime | None = None,
        fields: Sequence[utils.FieldData] | None = None,
        tts: bool = False,
        file: discord.File = _MISSING,
        files: Sequence[discord.File] = _MISSING,
        delete_after: float = _MISSING,
        nonce: int = _MISSING,
        reference: discord.Message
        | discord.MessageReference
        | discord.PartialMessage = _MISSING,
        view: discord.ui.View = _MISSING,
    ) -> discord.Message:
        return await utils.send(  # type: ignore
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


class PaginatedContext(commands.Context[_BotT]):
    async def send_pages(
        self,
        pages: Iterable[str],
        *,
        tts: bool = False,
        delete_after: float = _MISSING,
        nonce: int = _MISSING,
        reference: discord.Message
        | discord.MessageReference
        | discord.PartialMessage = _MISSING,
        view: discord.ui.View = _MISSING,
    ) -> list[discord.Message]:
        return [
            await self.send(
                page,
                tts=tts,
                delete_after=delete_after,
                nonce=nonce,
                reference=reference,
                view=view,
            )
            for page in pages
        ]
