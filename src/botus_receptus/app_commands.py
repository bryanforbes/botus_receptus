from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, overload, override

import discord
from discord import app_commands

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from . import bot


_ADMIN_ONLY: Final = -1
_TEST_ONLY: Final = -2
_admin_only_decorator: Final = app_commands.guilds(-1)
_test_only_decorator: Final = app_commands.guilds(-2)


@overload
def admin_guild_only[T](item: T, /) -> T: ...


@overload
def admin_guild_only[T]() -> Callable[[T], T]: ...


def admin_guild_only[T](item: T | None = None, /) -> Callable[[T], T] | T:
    if item is not None:
        return _admin_only_decorator(item)

    return _admin_only_decorator


@overload
def test_guilds_only[T](item: T, /) -> T: ...


@overload
def test_guilds_only[T]() -> Callable[[T], T]: ...


def test_guilds_only[T](item: T | None = None, /) -> Callable[[T], T] | T:
    if item is not None:
        return _test_only_decorator(item)

    return _test_only_decorator


class CommandTree[ClientT: bot.Bot | bot.AutoShardedBot](
    app_commands.CommandTree[ClientT]
):
    @override
    def add_command(
        self,
        command: (
            app_commands.Command[Any, ..., Any]
            | app_commands.ContextMenu
            | app_commands.Group
        ),
        /,
        *,
        guild: discord.abc.Snowflake | None = discord.utils.MISSING,
        guilds: Sequence[discord.abc.Snowflake] = discord.utils.MISSING,
        override: bool = False,
    ) -> None:
        admin_guild_id: int | None = self.client.config.get('admin_guild')
        test_guild_ids: list[int] | None = self.client.config.get('test_guilds')

        guild_ids = [] if command._guild_ids is None else command._guild_ids

        if _ADMIN_ONLY in guild_ids and _TEST_ONLY in guild_ids:
            raise TypeError('Cannot mix @admin_guild_only and @test_guilds_only')

        if admin_guild_id is not None and _ADMIN_ONLY in guild_ids:
            guild = discord.Object(id=admin_guild_id)
            guilds = discord.utils.MISSING
        elif test_guild_ids is not None and _TEST_ONLY in guild_ids:
            guild = discord.utils.MISSING
            guilds = [
                discord.Object(id=test_guild_id) for test_guild_id in test_guild_ids
            ]

        super().add_command(command, guild=guild, guilds=guilds, override=override)
