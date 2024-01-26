from __future__ import annotations

from typing import TYPE_CHECKING, Any
from typing_extensions import override

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    close_all_sessions,
    create_async_engine,
)

from .. import bot

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..config import Config


class BotBase(bot.BotBase):
    __sessionmaker: async_sessionmaker[Any]

    def __init__(
        self,
        config: Config,
        /,
        sessionmaker: async_sessionmaker[Any],
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

    @override
    async def close(self) -> None:
        await close_all_sessions()

        await super().close()


class Bot(BotBase, bot.Bot): ...


class AutoShardedBot(BotBase, bot.AutoShardedBot): ...
