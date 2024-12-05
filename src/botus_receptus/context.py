from __future__ import annotations

from typing import TYPE_CHECKING, Final

import discord
from discord.ext import commands

from . import utils

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from datetime import datetime

    from . import embed
    from .bot import AutoShardedBot, Bot
    from .types import Coroutine


_MISSING: Final = discord.utils.MISSING


class GuildContext[BotT: Bot | AutoShardedBot](commands.Context[BotT]):
    @discord.utils.cached_property
    def guild(
        self,
    ) -> discord.Guild:
        return self.message.guild  # pyright: ignore[reportReturnType]

    @discord.utils.cached_property
    def channel(
        self,
    ) -> discord.TextChannel:
        return self.message.channel  # pyright: ignore[reportReturnType]

    @discord.utils.cached_property
    def author(
        self,
    ) -> discord.Member:
        return self.message.author  # pyright: ignore[reportReturnType]


class EmbedContext[BotT: Bot | AutoShardedBot](commands.Context[BotT]):
    def send_embed(
        self,
        description: str,
        *,
        title: str | None = None,
        color: discord.Color | int | None = None,
        footer: str | embed.FooterData | None = None,
        thumbnail: str | None = None,
        author: str | embed.AuthorData | None = None,
        image: str | None = None,
        timestamp: datetime | None = None,
        fields: Sequence[embed.FieldData] | None = None,
        reference: (
            discord.Message | discord.MessageReference | discord.PartialMessage
        ) = _MISSING,
        view: discord.ui.View = _MISSING,
    ) -> Coroutine[discord.Message]:
        return utils.send_embed(
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
            reference=reference,
            view=view,
        )


class PaginatedContext[BotT: Bot | AutoShardedBot](commands.Context[BotT]):
    async def send_pages(
        self,
        pages: Iterable[str],
        *,
        tts: bool = False,
        delete_after: float | None = None,
        nonce: int | None = None,
        reference: (
            discord.Message | discord.MessageReference | discord.PartialMessage | None
        ) = None,
        view: discord.ui.View | None = None,
    ) -> list[discord.Message]:
        return [  # pyright: ignore[reportUnknownVariableType]
            await self.send(  # pyright: ignore[reportCallIssue]
                page,
                tts=tts,
                delete_after=delete_after,  # pyright: ignore[reportArgumentType]
                nonce=nonce,  # pyright: ignore[reportArgumentType]
                reference=reference,  # pyright: ignore[reportArgumentType]
                view=view,  # pyright: ignore[reportArgumentType]
            )
            for page in pages
        ]
