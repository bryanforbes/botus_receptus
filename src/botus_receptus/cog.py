from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from discord.ext import commands

C = TypeVar('C', bound='Cog[Any]')
CT = TypeVar('CT', bound=commands.Context)

if TYPE_CHECKING:

    class _CogBase(commands.Cog[CT]):
        ...


else:

    class _CogBase(commands.Cog, Generic[CT]):
        ...


class Cog(_CogBase[CT]):
    def _inject(self: C, bot: commands.Bot[CT]) -> C:
        self.__pre_inject__(bot)

        cog: C = cast(Any, super())._inject(bot)

        self.__post_inject__(bot)

        return cog

    def _eject(self, bot: commands.Bot[CT]) -> None:
        self.__pre_eject__(bot)

        cast(Any, super())._eject(bot)

        self.__post_eject__(bot)

    def __pre_inject__(self, bot: commands.Bot[CT]) -> None:
        ...

    def __post_inject__(self, bot: commands.Bot[CT]) -> None:
        ...

    def __pre_eject__(self, bot: commands.Bot[CT]) -> None:
        ...

    def __post_eject__(self, bot: commands.Bot[CT]) -> None:
        ...
