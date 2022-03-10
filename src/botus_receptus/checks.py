from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import discord
from discord.ext import commands

from .compat import Callable, Coroutine
from .exceptions import NotGuildOwner, OnlyDirectMessage

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


_CoroType: TypeAlias = Callable[..., Coroutine[Any, Any, Any]]
_F = TypeVar('_F', bound='_CoroType | commands.Command[Any, Any, Any]')


def dm_only() -> Callable[[_F], _F]:
    def predicate(ctx: commands.Context[Any], /) -> bool:
        if not isinstance(ctx.channel, discord.DMChannel):
            raise OnlyDirectMessage('This command can only be used in private messags.')
        return True

    return commands.check(predicate)  # type: ignore


def is_guild_owner() -> Callable[[_F], _F]:
    def predicate(ctx: commands.Context[Any], /) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage(
                'This command cannot be used in private messages.'
            )
        if ctx.guild.owner != ctx.author:
            raise NotGuildOwner('You do not own this guild')
        return True

    return commands.check(predicate)  # type: ignore
