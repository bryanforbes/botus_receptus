from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Final, TypeVar, overload

import discord
from discord import app_commands

if TYPE_CHECKING:
    from . import bot


_T = TypeVar('_T')
_ClientT = TypeVar('_ClientT', bound='bot.Bot | bot.AutoShardedBot')


_ADMIN_ONLY: Final = discord.Object(id=-1)
_admin_only_decorator: Final = app_commands.guilds(_ADMIN_ONLY)


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

        if admin_guild_id is not None and (
            (
                isinstance(command, discord.app_commands.Group)
                or (
                    isinstance(command, discord.app_commands.Command)
                    and command.parent is None
                )
            )
            and command._guild_ids is not None
            and _ADMIN_ONLY.id in command._guild_ids
        ):
            guild = discord.Object(id=admin_guild_id)
            guilds = discord.utils.MISSING

        super().add_command(command, guild=guild, guilds=guilds, override=override)
