from __future__ import annotations

from collections.abc import Awaitable, Iterable
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import discord
from discord import app_commands
from discord.abc import Snowflake
from discord.ext import commands
from discord.ext.commands import cog  # type: ignore
from discord.utils import maybe_coroutine

from .bot import AutoShardedBot, Bot

if TYPE_CHECKING:
    from typing_extensions import Self


_BotT = TypeVar('_BotT', bound=Bot | AutoShardedBot)


class Cog(commands.Cog, Generic[_BotT]):
    bot: _BotT

    def __init__(self, bot: _BotT, /) -> None:
        super().__init__()

        self.bot = bot

        if commands.Cog._get_overridden_method(self.cog_app_command_error) is not None:
            for command in self.__cog_app_commands__:
                self._set_command_error_handler(command)

    def _set_command_error_handler(
        self,
        command: app_commands.Command[Self, ..., Any] | app_commands.Group,
        /,
    ) -> None:
        if isinstance(command, app_commands.Group):
            if (
                hasattr(command.on_error, '__func__')
                and command.on_error.__func__  # type: ignore
                is app_commands.Group.on_error
            ):
                command.on_error = self.cog_app_command_error  # type: ignore
            else:
                old_on_group_error = command.on_error

                async def on_group_error(
                    interaction: discord.Interaction,
                    error: app_commands.AppCommandError,
                ) -> None:
                    await old_on_group_error(interaction, error)
                    await self.cog_app_command_error(interaction, error)

                command.on_error = on_group_error
            return

        if command.binding is not self:
            return

        old_on_error = command.on_error

        async def on_command_error_with_binding(
            binding: Self,
            interaction: discord.Interaction,
            error: app_commands.AppCommandError,
            /,
        ) -> None:
            if old_on_error is not None:
                await old_on_error(binding, interaction, error)  # type: ignore
            await self.cog_app_command_error(interaction, error)

        command.on_error = on_command_error_with_binding

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
        error: app_commands.AppCommandError,
        /,
    ) -> None:
        ...
