from __future__ import annotations

import discord
from discord.ext import commands

from .exceptions import NotGuildOwner, OnlyDirectMessage


def dm_only() -> 'commands._CheckDecorator':
    def predicate(ctx: commands.Context) -> bool:
        if not isinstance(ctx.channel, discord.DMChannel):
            raise OnlyDirectMessage('This command can only be used in private messags.')
        return True

    return commands.check(predicate)


def is_guild_owner() -> 'commands._CheckDecorator':
    def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage(
                'This command cannot be used in private messages.'
            )
        if ctx.guild.owner != ctx.author:
            raise NotGuildOwner('You do not own this guild')
        return True

    return commands.check(predicate)
