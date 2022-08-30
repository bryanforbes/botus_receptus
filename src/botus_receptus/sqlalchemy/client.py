from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import create_async_engine

from .. import client

if TYPE_CHECKING:
    from ..config import Config
    from .session import AsyncSessionMakerType


class Client(client.Client):
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


class AutoShardedClient(  # pyright: ignore [reportIncompatibleVariableOverride]
    client.AutoShardedClient, Client
):
    def __init__(
        self,
        config: Config,
        /,
        *args: Any,
        sessionmaker: AsyncSessionMakerType,
        **kwargs: Any,
    ) -> None:
        super().__init__(config, *args, sessionmaker=sessionmaker, **kwargs)
