from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from .bot import AutoShardedBot, Bot


class Cog[BotT: Bot | AutoShardedBot](commands.Cog):
    bot: BotT

    def __init__(self, bot: BotT, /) -> None:
        super().__init__()

        self.bot = bot


class GroupCog[BotT: Bot | AutoShardedBot](commands.GroupCog, Cog[BotT]): ...
