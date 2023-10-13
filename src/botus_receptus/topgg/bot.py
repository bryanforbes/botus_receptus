from __future__ import annotations

import asyncio
import logging
from datetime import time
from typing import TYPE_CHECKING, Final, NotRequired, TypedDict
from typing_extensions import override

import discord
import pendulum
from discord.ext import tasks

from .. import bot

_log: Final = logging.getLogger(__name__)


class _BotStats(TypedDict):
    server_count: int | list[int]
    shards: NotRequired[list[int]]
    shard_id: NotRequired[int]
    shard_count: NotRequired[int]


class BotBase(bot.BotBase):
    if TYPE_CHECKING:

        @property
        def user(self) -> discord.ClientUser:
            ...

    def _get_topgg_stats(self) -> _BotStats:
        raise NotImplementedError

    @tasks.loop(time=list(map(time, range(24))))
    async def __topgg_task(self, token: str, /) -> None:
        stats = self._get_topgg_stats()
        headers = {'Content-Type': 'application/json', 'Authorization': token}

        async with asyncio.timeout(10):
            user_id = self.user.id

            _log.info('POSTing stats for bot %s: %s', user_id, stats)

            await self.session.post(
                f'https://top.gg/api/bots/{user_id}/stats',
                data=discord.utils._to_json(stats),
                headers=headers,
            )

    async def on_ready(self) -> None:
        token = self.config.get('dbl_token')

        if token is None:
            return

        self.__topgg_task.start(token)

        next_hour = pendulum.now('UTC').start_of('hour').add(hours=1)

        if next_hour.diff().in_minutes() > 15:
            await self.__topgg_task(token)

    @override
    async def close(self) -> None:
        self.__topgg_task.cancel()

        await super().close()


class Bot(BotBase, bot.Bot):
    @override
    def _get_topgg_stats(self) -> _BotStats:
        return {'server_count': len(self.guilds)}


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    @override
    def _get_topgg_stats(self) -> _BotStats:
        return {
            'server_count': len(self.guilds),
            'shard_count': self.shard_count,
        }
