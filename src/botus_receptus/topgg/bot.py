from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import time
from typing import Any, Final, cast

import async_timeout
import discord
import pendulum
from discord.ext import tasks
from more_itertools import bucket
from pendulum.datetime import DateTime

from .. import bot

_log: Final = logging.getLogger(__name__)


class BotBase(bot.BotBase):
    async def __post_topgg_stats(self, token: str, payload: Any, /) -> None:
        headers = {'Content-Type': 'application/json', 'Authorization': token}

        async with async_timeout.timeout(10):
            user_id = cast(Any, self).user.id

            _log.info('POSTing stats for bot %s: %s', user_id, payload)

            await self.session.post(
                f'https://top.gg/api/bots/{user_id}/stats',
                data=discord.utils._to_json(payload),
                headers=headers,
            )

    def _get_topgg_stats(self) -> int | Iterable[tuple[int, int]]:
        ...

    @tasks.loop(time=list(map(time, range(24))))
    async def __topgg_task(self, token: str, /) -> None:
        stats = self._get_topgg_stats()

        if isinstance(stats, int):
            await self.__post_topgg_stats(token, {'server_count': stats})

        else:
            for shard_id, server_count in stats:
                await self.__post_topgg_stats(
                    token, {'shard_id': shard_id, 'server_count': server_count}
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
    def _get_topgg_stats(self) -> int:
        return len(self.guilds)


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    def _get_topgg_stats(self) -> Iterable[tuple[int, int]]:
        guilds_by_shard_id = bucket(self.guilds, key=lambda g: g.shard_id)

        return map(
            lambda shard_id: (shard_id, len(list(guilds_by_shard_id[shard_id]))),
            guilds_by_shard_id,
        )
