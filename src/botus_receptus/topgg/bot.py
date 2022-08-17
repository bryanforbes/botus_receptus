from __future__ import annotations

import logging
from datetime import time
from typing import TYPE_CHECKING, Any, Final, TypedDict, cast

import async_timeout
import discord
import pendulum
from discord.ext import tasks

from .. import bot

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from pendulum.datetime import DateTime

_log: Final = logging.getLogger(__name__)


class _BotStats(TypedDict):
    server_count: int | list[int]
    shards: NotRequired[list[int]]
    shard_id: NotRequired[int]
    shard_count: NotRequired[int]


class BotBase(bot.BotBase):
    def _get_topgg_stats(self) -> _BotStats:
        ...

    @tasks.loop(time=list(map(time, range(24))))
    async def __topgg_task(self, token: str, /) -> None:
        stats = self._get_topgg_stats()
        headers = {'Content-Type': 'application/json', 'Authorization': token}

        async with async_timeout.timeout(10):
            user_id = cast('Any', self).user.id

            _log.info('POSTing stats for bot %s: %s', user_id, stats)

            await self.session.post(
                f'https://top.gg/api/bots/{user_id}/stats',
                data=discord.utils._to_json(stats),
                headers=headers,
            )

    async def on_ready(self, /) -> None:
        token = self.config.get('dbl_token', None)

        if token is None:
            return

        self.__topgg_task.start(token)

        next_hour: DateTime = (
            pendulum.now('UTC').start_of('hour').add(hours=1)  # type: ignore
        )

        if next_hour.diff().in_minutes() > 15:  # type: ignore
            await self.__topgg_task(token)

    async def close(self) -> None:
        self.__topgg_task.cancel()

        await super().close()


class Bot(BotBase, bot.Bot):
    def _get_topgg_stats(self) -> _BotStats:
        return {'server_count': len(self.guilds)}


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    def _get_topgg_stats(self) -> _BotStats:
        return {
            'server_count': len(self.guilds),
            'shard_count': self.shard_count,
        }
