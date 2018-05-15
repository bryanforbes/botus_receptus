from typing import Any, cast
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


class Bot(BaseBot):
    pool: Pool

    def __init__(self, bot_name: str, config: ConfigParser, *args: Any, **kwargs: Any) -> None:
        if not has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(bot_name, config, *args, **kwargs)

        self.pool = self.loop.run_until_complete(
            create_pool(
                self.config.get(self.bot_name, 'db_url'),
                min_size=1,
                max_size=10
            )
        )

    async def close(self) -> None:
        await self.pool.close()
        await super().close()

    async def get_context(self, message: discord.Message, *, cls: Any=Context) -> Context:
        return cast(Context, await super().get_context(message, cls=cls))

    async def process_commands(self, message: discord.Message) -> None:
        ctx = await self.get_context(message)

        async with ctx.acquire():
            await self.invoke(ctx)
