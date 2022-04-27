from __future__ import annotations

from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .. import bot


class BotBase(bot.BotBase):
    session_maker: ClassVar[sessionmaker[AsyncSession]]  # type: ignore

    async def setup_hook(self) -> None:
        self.session_maker.configure(
            bind=create_async_engine(self.config.get('db_url', ''))
        )

        await super().setup_hook()

    async def close(self) -> None:
        self.session_maker.close_all()

        await super().close()


class Bot(BotBase, bot.Bot):
    ...


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    ...
