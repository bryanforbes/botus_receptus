from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, TypeVar

import discord
from discord import app_commands

from .compat import Callable

if TYPE_CHECKING:
    from .bot import AutoShardedBot, Bot


T = TypeVar('T')
ClientT = TypeVar('ClientT', bound='Bot | AutoShardedBot')


_ADMIN_ONLY: Final = discord.Object(id=-1)


def admin_guild_only() -> Callable[[T], T]:
    return app_commands.guilds(_ADMIN_ONLY)


class CommandTree(app_commands.CommandTree[ClientT]):
    def add_command(
        self,
        command: app_commands.Command[Any, ..., Any]
        | app_commands.ContextMenu
        | app_commands.Group,
        /,
        *,
        guild: discord.abc.Snowflake | None = discord.utils.MISSING,
        guilds: list[discord.abc.Snowflake] = discord.utils.MISSING,
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
