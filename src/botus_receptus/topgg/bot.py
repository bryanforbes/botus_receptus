from __future__ import annotations

from .. import bot
from .base import AutoShardedClientMixin, ClientMixin


class Bot(ClientMixin, bot.Bot):
    ...


class AutoShardedBot(AutoShardedClientMixin, bot.AutoShardedBot):
    ...
