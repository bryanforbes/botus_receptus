from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from discord.ext.commands import bot

if TYPE_CHECKING:
    from typing_extensions import Self


class Cog(commands.Cog):
    def _inject(self, bot: bot.BotBase, /) -> Self:
        self.__pre_inject__(bot)

        cog = super()._inject(bot)

        self.__post_inject__(bot)

        return cog

    def _eject(self, bot: bot.BotBase, /) -> None:
        self.__pre_eject__(bot)

        super()._eject(bot)

        self.__post_eject__(bot)

    def __pre_inject__(self, bot: bot.BotBase, /) -> None:
        ...

    def __post_inject__(self, bot: bot.BotBase, /) -> None:
        ...

    def __pre_eject__(self, bot: bot.BotBase, /) -> None:
        ...

    def __post_eject__(self, bot: bot.BotBase, /) -> None:
        ...
