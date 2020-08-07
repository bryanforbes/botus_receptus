from __future__ import annotations

from discord.ext import typed_commands


class OnlyDirectMessage(typed_commands.CheckFailure):
    ...


class NotGuildOwner(typed_commands.CheckFailure):
    ...
