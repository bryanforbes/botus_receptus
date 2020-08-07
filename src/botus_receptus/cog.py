from __future__ import annotations

from typing import Any, TypeVar, cast

from discord.ext import typed_commands

C = TypeVar('C', bound='Cog[Any]')
CT = TypeVar('CT', bound=typed_commands.Context)


class Cog(typed_commands.Cog[CT]):
    def _inject(self: C, bot: typed_commands.Bot[CT]) -> C:
        self.__pre_inject__(bot)

        cog: C = cast(Any, super())._inject(bot)

        self.__post_inject__(bot)

        return cog

    def _eject(self, bot: typed_commands.Bot[CT]) -> None:
        self.__pre_eject__(bot)

        cast(Any, super())._eject(bot)

        self.__post_eject__(bot)

    def __pre_inject__(self, bot: typed_commands.Bot[CT]) -> None:
        ...

    def __post_inject__(self, bot: typed_commands.Bot[CT]) -> None:
        ...

    def __pre_eject__(self, bot: typed_commands.Bot[CT]) -> None:
        ...

    def __post_eject__(self, bot: typed_commands.Bot[CT]) -> None:
        ...
