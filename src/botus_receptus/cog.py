from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from discord.ext import commands

if TYPE_CHECKING:
    from .bot import AutoShardedBot, Bot


_BotT = TypeVar('_BotT', bound='Bot | AutoShardedBot')


class Cog(commands.Cog, Generic[_BotT]):
    bot: _BotT

    def __init__(self, bot: _BotT, /) -> None:
        super().__init__()

        self.bot = bot


class GroupCog(commands.GroupCog, Cog[_BotT]):
    ...
