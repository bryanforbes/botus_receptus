from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import create_async_engine

from .. import bot

if TYPE_CHECKING:
    from ..config import Config
    from .session import AsyncSessionMakerType


class BotBase(bot.BotBase):
    __Session: AsyncSessionMakerType

    def __init__(
        self,
        config: Config,
        /,
        sessionmaker: AsyncSessionMakerType,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.__Session = sessionmaker

        super().__init__(config, *args, **kwargs)

    async def setup_hook(self) -> None:
        self.__Session.configure(
            bind=create_async_engine(self.config.get('db_url', '')),
        )

        await super().setup_hook()

    async def close(self) -> None:
        self.__Session.close_all()

        await super().close()


class Bot(BotBase, bot.Bot):
    ...


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    ...
