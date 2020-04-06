from __future__ import annotations

import asyncio
from typing import Any, ClassVar, Dict, Type, TypeVar, cast

import discord

from ..bot import Bot as BaseBot
from ..config import Config
from .context import Context

try:
    from asyncpg import create_pool
    from asyncpg.pool import Pool

    has_asyncpg = True
except ImportError:
    has_asyncpg = False


CT = TypeVar('CT', bound=Context)


class Bot(BaseBot[CT]):
    pool: Pool[Any]
    context_cls: ClassVar[Type[CT]] = cast(Type[CT], Context)

    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        if not has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(config, *args, **kwargs)

        pool_kwargs: Dict[str, Any] = {}

        if hasattr(self, '__init_connection__') and asyncio.iscoroutinefunction(
            cast(Any, self).__init_connection__
        ):
            pool_kwargs['init'] = cast(Any, self).__init_connection__
        if hasattr(self, '__setup_connection__') and asyncio.iscoroutinefunction(
            cast(Any, self).__setup_connection__
        ):
            pool_kwargs['setup'] = cast(Any, self).__setup_connection__

        self.pool = self.loop.run_until_complete(
            create_pool(
                self.config.get('db_url', ''), min_size=1, max_size=10, **pool_kwargs
            )
        )

    async def close(self) -> None:
        await self.pool.close()
        await super().close()

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message)

        async with ctx.acquire():
            await self.invoke(ctx)
