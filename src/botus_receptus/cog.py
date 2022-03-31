from __future__ import annotations

from collections.abc import Awaitable, Coroutine, Iterable
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypeVar

import discord
from discord import app_commands
from discord.abc import Snowflake
from discord.ext import commands
from discord.ext.commands import cog  # type: ignore
from discord.utils import maybe_coroutine

from .bot import AutoShardedBot, Bot

if TYPE_CHECKING:
    from typing_extensions import Self


_T = TypeVar('_T')
_BotT = TypeVar('_BotT', bound=Bot | AutoShardedBot)
_Coro: TypeAlias = Coroutine[Any, Any, _T]


class Cog(commands.Cog, Generic[_BotT]):
    bot: _BotT

    def __init__(self, bot: _BotT, /) -> None:
        super().__init__()

        self.bot = bot

        on_error = commands.Cog._get_overridden_method(self.cog_app_command_error)

        if on_error is not None:
            for command in self.__cog_app_commands__:
                if command.parent is None:
                    self._set_command_error_handler(command)

    def _set_command_error_handler(
        self,
        command: app_commands.Command[Self, ..., Any] | app_commands.Group,
        /,
    ) -> None:
        if isinstance(command, app_commands.Group):
            command.on_error = self.cog_app_command_error  # type: ignore
            return

        def on_error(interaction: discord.Interaction, error: Exception) -> _Coro[Any]:
            return self.cog_app_command_error(interaction, command, error)

        command.on_error = on_error

    async def _inject(  # type: ignore
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
    ) -> Self:
        await maybe_coroutine(self.__pre_inject__, bot, override, guild, guilds)

        _cog = await super()._inject(bot, override, guild, guilds)

        await maybe_coroutine(self.__post_inject__, bot, override, guild, guilds)

        return _cog

    async def _eject(  # type: ignore
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
    ) -> None:
        await maybe_coroutine(self.__pre_eject__, bot, guild_ids)

        await super()._eject(bot, guild_ids)

        await maybe_coroutine(self.__post_eject__, bot, guild_ids)

    def __pre_inject__(
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_inject__(
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __pre_eject__(
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_eject__(
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...

    @cog._cog_special_method
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command[Self, ..., Any],
        error: Exception,
        /,
    ) -> None:
        ...
