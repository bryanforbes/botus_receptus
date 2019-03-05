from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AsyncContextManager,
    Awaitable,
    Coroutine,
    Any,
    Generator,
    Optional,
    Callable,
    List,
    Sequence,
    Tuple,
    Dict,
    TypeVar,
    cast,
)
from asyncpg import Connection
from dataclasses import dataclass
from dataslots import with_slots
from discord.ext import commands

from .util import select_all, select_one, search, insert_into, delete_from, update

if TYPE_CHECKING:
    from .bot import Bot


@with_slots
@dataclass
class AquireContextManager(AsyncContextManager[Connection], Awaitable[Connection]):
    ctx: Context
    timeout: Optional[float] = None

    def __await__(self) -> Generator[Any, None, Connection]:
        return self.ctx._acquire(self.timeout).__await__()

    async def __aenter__(self) -> Connection:
        return await self.ctx._acquire(self.timeout)

    async def __aexit__(self, *args: Any) -> None:
        await self.ctx.release()


FunctionType = Callable[..., Coroutine[Any, Any, Any]]
F = TypeVar('F', bound=FunctionType)


def ensure_db(func: F) -> F:
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, 'db'):
            raise RuntimeError(
                'No database object available; ensure acquire() was called'
            )

        return func(self, *args, **kwargs)

    return cast(F, wrapper)


class Context(commands.Context):
    bot: Bot
    db: Connection

    async def _acquire(self, timeout: Optional[float]) -> Connection:
        if not hasattr(self, 'db'):
            self.db = await self.bot.pool.acquire(timeout=timeout)

        return self.db

    def acquire(self, *, timeout: Optional[float] = None) -> AquireContextManager:
        return AquireContextManager(self, timeout)

    async def release(self) -> None:
        if hasattr(self, 'db'):
            await self.bot.pool.release(self.db)
            del self.db

    @ensure_db
    async def select_all(
        self,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: Optional[Sequence[str]] = None,
        group_by: Optional[Sequence[str]] = None,
        order_by: Optional[str] = None,
        joins: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> List[Any]:
        return await select_all(
            self.db,
            *args,
            columns=columns,
            table=table,
            order_by=order_by,
            where=where,
            group_by=group_by,
            joins=joins,
        )

    @ensure_db
    async def select_one(
        self,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: Optional[Sequence[str]] = None,
        group_by: Optional[Sequence[str]] = None,
        joins: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> Optional[Any]:
        return await select_one(
            self.db,
            *args,
            columns=columns,
            table=table,
            where=where,
            group_by=group_by,
            joins=joins,
        )

    @ensure_db
    async def search(
        self,
        *args: Any,
        table: str,
        columns: Sequence[str],
        search_columns: Sequence[str],
        terms: Sequence[str],
        where: Optional[Sequence[str]] = None,
        group_by: Optional[Sequence[str]] = None,
        order_by: Optional[str] = None,
        joins: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> List[Any]:
        return await search(
            self.db,
            *args,
            columns=columns,
            table=table,
            search_columns=search_columns,
            terms=terms,
            where=where,
            group_by=group_by,
            order_by=order_by,
            joins=joins,
        )

    @ensure_db
    async def update(
        self,
        *args: Any,
        table: str,
        values: Dict[str, Any],
        where: Optional[Sequence[str]] = None,
    ) -> None:
        return await update(self.db, *args, table=table, values=values, where=where)

    @ensure_db
    async def insert_into(
        self, *, table: str, values: Dict[str, Any], extra: str = ''
    ) -> None:
        return await insert_into(self.db, table=table, values=values, extra=extra)

    @ensure_db
    async def delete_from(self, *args: Any, table: str, where: Sequence[str]) -> None:
        return await delete_from(self.db, *args, table=table, where=where)
