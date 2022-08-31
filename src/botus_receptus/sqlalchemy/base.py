from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import create_async_engine

if TYPE_CHECKING:
    from ..config import Config
    from .session import AsyncSessionMakerType


class ClientBase:
    config: Config
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

        super().__init__(config, *args, **kwargs)  # pyright: ignore

    async def setup_hook(self) -> None:
        self.__Session.configure(
            bind=create_async_engine(self.config.get('db_url', '')),
        )

        await super().setup_hook()  # pyright: ignore

    async def close(self) -> None:
        self.__Session.close_all()

        await super().close()  # pyright: ignore
