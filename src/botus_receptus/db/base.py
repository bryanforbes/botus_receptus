from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..config import Config

try:
    from asyncpg import Connection, Record, create_pool

    if TYPE_CHECKING:
        from asyncpg.pool import Pool, PoolConnectionProxy

    _has_asyncpg = True
except ImportError:
    _has_asyncpg = False

_FuncT = TypeVar('_FuncT', bound='Callable[..., Any]')


def _special_method(func: _FuncT) -> _FuncT:
    func.__asyncpg_special_method__ = None  # pyright: ignore
    return func


def _get_overridden_method(method: _FuncT) -> _FuncT | None:
    return getattr(
        method.__func__, '__asyncpg_special_method__', method  # pyright: ignore
    )


class ClientBase:
    config: Config
    pool: Pool[Record]

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        if not _has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(config, *args, **kwargs)  # pyright: ignore

    async def setup_hook(self) -> None:
        pool_kwargs: dict[str, Any] = {}

        if (
            init_connection := _get_overridden_method(self.__init_asyncpg_connection__)
        ) is not None and asyncio.iscoroutinefunction(init_connection):
            pool_kwargs['init'] = init_connection

        if (
            setup_connection := _get_overridden_method(
                self.__setup_asyncpg_connection__
            )
        ) is not None and asyncio.iscoroutinefunction(setup_connection):
            pool_kwargs['setup'] = setup_connection

        pool = await create_pool(
            self.config.get('db_url', ''),
            min_size=1,
            max_size=10,
            **pool_kwargs,
        )

        assert pool is not None

        self.pool = pool

        await super().setup_hook()  # pyright: ignore

    @_special_method
    async def __init_asyncpg_connection__(
        self, connection: Connection[Record], /
    ) -> None:
        raise NotImplementedError

    @_special_method
    async def __setup_asyncpg_connection__(
        self, proxy: PoolConnectionProxy[Record], /
    ) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        await self.pool.close()
        await super().close()  # pyright: ignore
