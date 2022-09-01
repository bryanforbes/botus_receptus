from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .. import bot
from .base import ClientBase
from .context import Context

if TYPE_CHECKING:
    import discord


class BotBase(ClientBase, bot.BotBase):
    async def process_commands(self, message: discord.Message, /) -> None:
        ctx = await self.get_context(message, cls=Context[Any])

        async with ctx.acquire():
            await self.invoke(ctx)


class Bot(BotBase, bot.Bot):
    ...


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    ...
