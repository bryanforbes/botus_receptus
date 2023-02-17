from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, overload
from typing_extensions import TypeVar

import discord
from discord import app_commands

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from . import bot


_T = TypeVar('_T', infer_variance=True)
_ClientT = TypeVar(
    '_ClientT', bound='bot.Bot | bot.AutoShardedBot', infer_variance=True
)

_ADMIN_ONLY: Final = -1
_TEST_ONLY: Final = -2
_admin_only_decorator: Final = app_commands.guilds(-1)
_test_only_decorator: Final = app_commands.guilds(-2)


@overload
def admin_guild_only(item: _T) -> _T:
    ...


@overload
def admin_guild_only() -> Callable[[_T], _T]:
    ...


def admin_guild_only(item: _T | None = None, /) -> Callable[[_T], _T] | _T:
    if item is not None:
        return _admin_only_decorator(item)

    return _admin_only_decorator


@overload
def test_guilds_only(item: _T) -> _T:
    ...


@overload
def test_guilds_only() -> Callable[[_T], _T]:
    ...


def test_guilds_only(item: _T | None = None, /) -> Callable[[_T], _T] | _T:
    if item is not None:
        return _test_only_decorator(item)

    return _test_only_decorator


class CommandTree(app_commands.CommandTree[_ClientT]):
    def add_command(
        self,
        command: app_commands.Command[Any, ..., Any]
        | app_commands.ContextMenu
        | app_commands.Group,
        /,
        *,
        guild: discord.abc.Snowflake | None = discord.utils.MISSING,
        guilds: Sequence[discord.abc.Snowflake] = discord.utils.MISSING,
        override: bool = False,
    ) -> None:
        admin_guild_id: int | None = self.client.config.get('admin_guild', None)
        test_guild_ids: list[int] | None = self.client.config.get('test_guilds', None)

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
