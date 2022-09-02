from __future__ import annotations

from .. import bot
from .base import ClientBase


class Bot(ClientBase, bot.Bot):
    ...


class AutoShardedBot(ClientBase, bot.AutoShardedBot):
    ...
