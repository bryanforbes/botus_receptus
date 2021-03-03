from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import typed_commands

from .exceptions import NotGuildOwner, OnlyDirectMessage

if TYPE_CHECKING:
    from discord.ext.commands import core


def dm_only() -> core._CheckDecorator:
    def predicate(ctx: core._CT, /) -> bool:
        if not isinstance(ctx.channel, discord.DMChannel):
            raise OnlyDirectMessage('This command can only be used in private messags.')
        return True

    return typed_commands.check(predicate)


def is_guild_owner() -> core._CheckDecorator:
    def predicate(ctx: core._CT, /) -> bool:
        if ctx.guild is None:
            raise typed_commands.NoPrivateMessage(
                'This command cannot be used in private messages.'
            )
        if ctx.guild.owner != ctx.author:
            raise NotGuildOwner('You do not own this guild')
        return True

    return typed_commands.check(predicate)
