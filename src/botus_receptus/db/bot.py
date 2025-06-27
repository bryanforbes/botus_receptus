from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from .. import bot
from .context import Context

if TYPE_CHECKING:
    import discord

    from ..config import Config
    from ..types import AnyCallable

try:
    from asyncpg import Connection, create_pool

    if TYPE_CHECKING:
        from asyncpg.pool import Pool, PoolConnectionProxy

    _has_asyncpg = True
except ImportError:
    _has_asyncpg = False


def _db_special_method[F: AnyCallable](func: F, /) -> F:
    func.__db_special_method__ = None  # pyright: ignore[reportFunctionMemberAccess]
    return func


def _get_special_method[F: AnyCallable](method: F, /) -> F | None:
    return getattr(
        method.__func__,  # pyright: ignore[reportFunctionMemberAccess]
        '__db_special_method__',
        method,
    )


class BotBase(bot.BotBase):
    pool: Pool

    def __init__(self, config: Config, /, *args: object, **kwargs: object) -> None:
        if not _has_asyncpg:
            raise RuntimeError('asyncpg library needed in order to use a database')

        super().__init__(config, *args, **kwargs)

    @override
    async def setup_hook(self) -> None:
        pool_kwargs: dict[str, Any] = {}

        if (init := _get_special_method(self.__db_init_connection__)) is not None:
            pool_kwargs['init'] = init

        if (setup := _get_special_method(self.__db_setup_connection__)) is not None:
            pool_kwargs['setup'] = setup

        self.pool = await create_pool(  # pyright: ignore[reportPossiblyUnboundVariable]
            self.config.get('db_url', ''),
            min_size=1,
            max_size=10,
            **pool_kwargs,
        )

        await super().setup_hook()

    @_db_special_method
    async def __db_init_connection__(self, connection: Connection, /) -> None: ...

    @_db_special_method
    async def __db_setup_connection__(
        self, connection: PoolConnectionProxy, /
    ) -> None: ...

    @override
    async def close(self) -> None:
        await self.pool.close()
        await super().close()

    @override
    async def process_commands(self, message: discord.Message, /) -> None:
        ctx = await self.get_context(message, cls=Context[Any])

        async with ctx.acquire():
            await self.invoke(ctx)


class Bot(BotBase, bot.Bot): ...


class AutoShardedBot(BotBase, bot.AutoShardedBot): ...
