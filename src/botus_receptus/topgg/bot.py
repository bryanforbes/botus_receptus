from __future__ import annotations

from .. import bot
from .base import AutoShardedClientBase, ClientBase


class Bot(ClientBase, bot.Bot):
    ...


class AutoShardedBot(AutoShardedClientBase, bot.AutoShardedBot):
    ...
