from __future__ import annotations

from discord.ext import commands


class OnlyDirectMessage(commands.CheckFailure): ...


class NotGuildOwner(commands.CheckFailure): ...
