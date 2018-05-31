from typing import Any, TypeVar, Type, Generic, cast, ClassVar
from configparser import ConfigParser

import discord

try:
    from asyncpg import create_pool
    from asyncpg.pool import Pool

    has_asyncpg = True
except ImportError:
    has_asyncpg = False

from ..bot import Bot as BaseBot
from .context import Context


DbContextType = TypeVar('DbContextType', bound=Context)


class Bot(BaseBot[DbContextType], Generic[DbContextType]):
    pool: Pool
    context_cls: ClassVar[Type[DbContextType]] = cast(Type[DbContextType], Context)

    def __init__(self, config: ConfigParser, *args: Any, **kwargs: Any) -> None:
        if not has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(config, *args, **kwargs)

        self.pool = self.loop.run_until_complete(
            create_pool(
                self.config.get('bot', 'db_url'),
                min_size=1,
                max_size=10
            )
        )

    async def close(self) -> None:
        await self.pool.close()
        await super().close()

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message)

        async with ctx.acquire():
            await self.invoke(ctx)
