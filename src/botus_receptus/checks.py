from __future__ import annotations

from typing import Any, Callable, TypeVar, Union

import discord
from discord.ext import commands

from .exceptions import NotGuildOwner, OnlyDirectMessage

FuncType = Callable[..., Any]
F = TypeVar('F', bound=Union[FuncType, commands.Command])


def dm_only() -> Callable[[F], F]:
    def predicate(ctx: commands.Context) -> bool:
        if not isinstance(ctx.channel, discord.DMChannel):
            raise OnlyDirectMessage('This command can only be used in private messags.')
        return True

    return commands.check(predicate)


def is_guild_owner() -> Callable[[F], F]:
    def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage(
                'This command cannot be used in private messages.'
            )
        if ctx.guild.owner != ctx.author:
            raise NotGuildOwner('You do not own this guild')
        return True

    return commands.check(predicate)
