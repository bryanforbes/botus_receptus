from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine, Generator, Sequence
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload
from typing_extensions import LiteralString

from asyncpg import Record
from asyncpg.pool import PoolConnectionProxy
from attr import dataclass
from discord.ext import commands

from .util import (
    ConditionsType,
    delete_from,
    insert_into,
    search,
    select_all,
    select_one,
    update,
)

if TYPE_CHECKING:
    from .bot import AutoShardedBot, Bot

_Record = TypeVar('_Record', bound=Record)
_BotT = TypeVar('_BotT', bound='Bot | AutoShardedBot')


@dataclass(slots=True)
class AquireContextManager(
    AbstractAsyncContextManager['PoolConnectionProxy[Record]'],
    Awaitable['PoolConnectionProxy[Record]'],
):
    ctx: Context[Any]
    timeout: float | None = None

    def __await__(self, /) -> Generator[Any, None, PoolConnectionProxy[Record]]:
        return self.ctx._acquire(self.timeout).__await__()

    async def __aenter__(self, /) -> PoolConnectionProxy[Record]:
        return await self.ctx._acquire(self.timeout)

    async def __aexit__(self, /, *args: Any) -> None:
        await self.ctx.release()


FunctionType = Callable[..., Coroutine[Any, Any, Any]]
F = TypeVar('F', bound=FunctionType)


def ensure_db(func: F, /) -> F:
    def wrapper(self: Any, /, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, 'db'):
            raise RuntimeError(
                'No database object available; ensure acquire() was called'
            )

        return func(self, *args, **kwargs)

    return cast(F, wrapper)


class Context(commands.Context[_BotT]):
    db: PoolConnectionProxy[Record]

    async def _acquire(self, timeout: float | None, /) -> PoolConnectionProxy[Record]:
        if not hasattr(self, 'db'):
            self.db = await self.bot.pool.acquire(timeout=timeout)

        return self.db

    def acquire(self, /, *, timeout: float | None = None) -> AquireContextManager:
        return AquireContextManager(self, timeout)

    async def release(self, /) -> None:
        if hasattr(self, 'db'):
            await self.bot.pool.release(self.db)
            del self.db

    @overload
    async def select_all(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = ...,
        group_by: Sequence[str] | None = ...,
        order_by: str | None = ...,
        joins: Sequence[tuple[str, str]] | None = ...,
        record_class: None = ...,
    ) -> list[Record]:
        ...

    @overload
    async def select_all(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = ...,
        group_by: Sequence[str] | None = ...,
        order_by: str | None = ...,
        joins: Sequence[tuple[str, str]] | None = ...,
        record_class: type[_Record],
    ) -> list[_Record]:
        ...

    @ensure_db
    async def select_all(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = None,
        group_by: Sequence[str] | None = None,
        order_by: str | None = None,
        joins: Sequence[tuple[str, str]] | None = None,
        record_class: Any | None = None,
    ) -> list[Any]:
        return await select_all(
            self.db,
            *args,
            columns=columns,
            table=table,
            order_by=order_by,
            where=where,
            group_by=group_by,
            joins=joins,
            record_class=record_class,
        )

    @overload
    async def select_one(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = ...,
        group_by: Sequence[str] | None = ...,
        joins: Sequence[tuple[str, str]] | None = ...,
        record_class: None = ...,
    ) -> Record | None:
        ...

    @overload
    async def select_one(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = ...,
        group_by: Sequence[str] | None = ...,
        joins: Sequence[tuple[str, str]] | None = ...,
        record_class: type[_Record],
    ) -> _Record | None:
        ...

    @ensure_db
    async def select_one(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        where: ConditionsType | None = None,
        group_by: Sequence[str] | None = None,
        joins: Sequence[tuple[str, str]] | None = None,
        record_class: Any | None = None,
    ) -> Any | None:
        return await select_one(
            self.db,
            *args,
            columns=columns,
            table=table,
            where=where,
            group_by=group_by,
            joins=joins,
            record_class=record_class,
        )

    @overload
    async def search(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        search_columns: Sequence[LiteralString],
        terms: Sequence[str],
        where: ConditionsType | None = None,
        group_by: Sequence[str] | None = None,
        order_by: str | None = None,
        joins: Sequence[tuple[str, str]] | None = None,
        record_class: None = ...,
    ) -> list[Record]:
        ...

    @overload
    async def search(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        search_columns: Sequence[LiteralString],
        terms: Sequence[str],
        where: ConditionsType | None = None,
        group_by: Sequence[str] | None = None,
        order_by: str | None = None,
        joins: Sequence[tuple[str, str]] | None = None,
        record_class: type[_Record],
    ) -> list[_Record]:
        ...

    @ensure_db
    async def search(
        self,
        /,
        *args: Any,
        table: str,
        columns: Sequence[str],
        search_columns: Sequence[LiteralString],
        terms: Sequence[str],
        where: ConditionsType | None = None,
        group_by: Sequence[str] | None = None,
        order_by: str | None = None,
        joins: Sequence[tuple[str, str]] | None = None,
        record_class: Any | None = None,
    ) -> list[Any]:
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
            record_class=record_class,
        )

    @ensure_db
    async def update(
        self,
        /,
        *args: Any,
        table: str,
        values: dict[str, Any],
        where: ConditionsType | None = None,
    ) -> None:
        return await update(self.db, *args, table=table, values=values, where=where)

    @ensure_db
    async def insert_into(
        self, /, *, table: str, values: dict[str, Any], extra: str = ''
    ) -> None:
        return await insert_into(self.db, table=table, values=values, extra=extra)

    @ensure_db
    async def delete_from(
        self, /, *args: Any, table: str, where: ConditionsType
    ) -> None:
        return await delete_from(self.db, *args, table=table, where=where)
