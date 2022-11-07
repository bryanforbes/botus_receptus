from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import close_all_sessions

from .. import bot

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..config import Config
    from .session import AsyncSessionMakerType


class BotBase(bot.BotBase):
    __sessionmaker: AsyncSessionMakerType

    def __init__(
        self,
        config: Config,
        /,
        sessionmaker: AsyncSessionMakerType,
        engine_kwargs: Mapping[str, object] | None = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        self.__sessionmaker = sessionmaker

        super().__init__(config, *args, **kwargs)

        engine_kwargs = engine_kwargs if engine_kwargs is not None else {}

        self.__sessionmaker.configure(
            bind=create_async_engine(self.config.get('db_url', ''), **engine_kwargs),
        )

    async def close(self) -> None:
        close_all_sessions()

        await super().close()


class Bot(BotBase, bot.Bot):
    ...


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    ...
