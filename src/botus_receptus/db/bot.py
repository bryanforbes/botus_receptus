from __future__ import annotations

import asyncio
from typing import Any, ClassVar, cast

import discord

from ..bot import AutoShardedBot as _AutoShardedBot
from ..bot import Bot as _Bot
from ..bot import BotBase as _BotBase
from ..compat import dict
from ..config import Config
from .context import Context

try:
    from asyncpg import Record, create_pool
    from asyncpg.pool import Pool

    _has_asyncpg = True
except ImportError:
    _has_asyncpg = False


class BotBase(_BotBase):
    pool: Pool[Record]
    context_cls: ClassVar = Context

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        if not _has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(config, *args, **kwargs)

    async def setup_hook(self) -> None:
        pool_kwargs: dict[str, Any] = {}

        if hasattr(self, '__init_connection__') and asyncio.iscoroutinefunction(
            cast(Any, self).__init_connection__
        ):
            pool_kwargs['init'] = cast(Any, self).__init_connection__
        if hasattr(self, '__setup_connection__') and asyncio.iscoroutinefunction(
            cast(Any, self).__setup_connection__
        ):
            pool_kwargs['setup'] = cast(Any, self).__setup_connection__

        pool = await create_pool(
            self.config.get('db_url', ''),
            min_size=1,
            max_size=10,
            **pool_kwargs,
        )

        assert pool is not None

        self.pool = pool

        await super().setup_hook()

    async def close(self, /) -> None:
        await self.pool.close()
        await super().close()

    async def process_commands(self, message: discord.Message, /) -> None:
        ctx = await self.get_context(message, cls=Context[Any])

        async with ctx.acquire():
            await self.invoke(ctx)


class Bot(BotBase, _Bot):
    ...


class AutoShardedBot(BotBase, _AutoShardedBot):
    ...
