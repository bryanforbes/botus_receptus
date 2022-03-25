from __future__ import annotations

from collections.abc import Awaitable, Coroutine, Iterable
from typing import TYPE_CHECKING, Any, Callable, TypeVar, overload

import discord

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias

from discord import app_commands
from discord.abc import Snowflake
from discord.ext import commands
from discord.ext.commands import bot  # type: ignore
from discord.ext.commands import cog  # type: ignore
from discord.utils import maybe_coroutine

_T = TypeVar('_T')
_CogT = TypeVar('_CogT', bound='Cog')
_Coro: TypeAlias = Coroutine[Any, Any, _T]
_UnboundError: TypeAlias = Callable[
    [discord.Interaction, app_commands.AppCommandError], _Coro[None]
]
_BoundError: TypeAlias = Callable[
    [_T, discord.Interaction, app_commands.AppCommandError], _Coro[None]
]
_GroupError: TypeAlias = Callable[
    [
        app_commands.Group,
        discord.Interaction,
        'app_commands.Command[Any, ..., Any]',
        app_commands.AppCommandError,
    ],
    _Coro[None],
]


@overload
def _wrap_on_error(
    cog: _CogT,
    member: app_commands.Command[Any, ..., Any],
    /,
) -> _UnboundError | _BoundError[_CogT]:
    ...


@overload
def _wrap_on_error(
    cog: Cog,
    member: app_commands.Group,
    /,
) -> _GroupError:
    ...


def _wrap_on_error(
    cog: _CogT,
    member: app_commands.Command[Any, ..., Any] | app_commands.Group,
    /,
) -> _UnboundError | _BoundError[_CogT] | _GroupError:
    if isinstance(member, app_commands.Command):
        old_on_error = member.on_error

        async def on_command_error(
            *args: Any,
        ) -> None:
            if old_on_error is not None:
                await old_on_error(*args)

            if len(args) == 2:
                interaction, error = args
            else:
                interaction, error = args[1:]

            await cog.cog_app_command_error(interaction, member, error)

        return on_command_error

    else:
        old_on_error = member.on_error

        async def on_group_error(
            self: app_commands.Group,
            interaction: discord.Interaction,
            command: app_commands.Command[Any, ..., Any],
            error: app_commands.AppCommandError,
            /,
        ) -> None:
            if old_on_error.__func__ is not app_commands.Group.on_error:  # type: ignore
                await old_on_error(interaction, command, error)

            await cog.cog_app_command_error(interaction, command, error)

        return on_group_error


class Cog(commands.Cog):
    def __init__(self) -> None:
        super().__init__()

        if Cog._get_overridden_method(self.cog_app_command_error):
            for member in self.__dict__.values():
                if isinstance(member, (app_commands.Command, app_commands.Group)):
                    member.on_error = _wrap_on_error(self, member)  # type: ignore

    async def _inject(
        self,
        bot: bot.BotBase,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
    ) -> Self:
        await maybe_coroutine(self.__pre_inject__, bot, override, guild, guilds)

        _cog = await super()._inject(bot, override, guild, guilds)

        await maybe_coroutine(self.__post_inject__, bot, override, guild, guilds)

        return _cog

    async def _eject(
        self,
        bot: bot.BotBase,
        guild_ids: Iterable[int] | None,
    ) -> None:
        await maybe_coroutine(self.__pre_eject__, bot, guild_ids)

        await super()._eject(bot, guild_ids)

        await maybe_coroutine(self.__post_eject__, bot, guild_ids)

    def __pre_inject__(
        self,
        bot: bot.BotBase,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_inject__(
        self,
        bot: bot.BotBase,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __pre_eject__(
        self,
        bot: bot.BotBase,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_eject__(
        self,
        bot: bot.BotBase,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...

    @cog._cog_special_method
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command[Self, ..., Any],
        error: app_commands.AppCommandError,
        /,
    ) -> None:
        ...
