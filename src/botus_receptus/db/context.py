from __future__ import annotations

from collections.abc import Awaitable, Generator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, LiteralString, overload, override

from attrs import define
from discord.ext import commands

from .utils import (
    ConditionsType,
    delete_from,
    insert_into,
    search,
    select_all,
    select_one,
    update,
)

if TYPE_CHECKING:
    from asyncpg import Record
    from asyncpg.pool import PoolConnectionProxy

    from ..types import Coroutine, CoroutineFunc
    from .bot import AutoShardedBot, Bot

type _DbMethod[C: 'Context[Any]', **P, R] = CoroutineFunc[Concatenate[C, P], R]


@define
class AcquireContextManager(
    AbstractAsyncContextManager['PoolConnectionProxy[Record]'],
    Awaitable['PoolConnectionProxy[Record]'],
):
    ctx: Context[Any]
    timeout: float | None = None

    async def __acquire(self) -> PoolConnectionProxy[Record]:
        ctx = self.ctx
        if not hasattr(ctx, 'db'):
            ctx.db = await ctx.bot.pool.acquire(timeout=self.timeout)

        return ctx.db

    @override
    def __await__(self) -> Generator[Any, None, PoolConnectionProxy[Record]]:
        return self.__acquire().__await__()

    @override
    def __aenter__(self) -> Coroutine[PoolConnectionProxy[Record]]:
        return self.__acquire()

    @override
    async def __aexit__(self, /, *args: object) -> None:
        await self.ctx.release()


def ensure_db[C: 'Context[Any]', **P, R](
    func: _DbMethod[C, P, R], /
) -> _DbMethod[C, P, R]:
    @wraps(func)
    def wrapper(self: C, /, *args: P.args, **kwargs: P.kwargs) -> Coroutine[R]:
        if not hasattr(self, 'db'):
            raise RuntimeError(
                'No database object available; ensure acquire() was called'
            )

        return func(self, *args, **kwargs)

    return wrapper


class Context[BotT: Bot | AutoShardedBot](commands.Context[BotT]):
    db: PoolConnectionProxy[Record]

    def acquire(self, /, *, timeout: float | None = None) -> AcquireContextManager:
        return AcquireContextManager(self, timeout)

    async def release(self) -> None:
        if hasattr(self, 'db'):
            await self.bot.pool.release(self.db)
            del self.db

    @overload
    async def select_all(
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        order_by: LiteralString | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: None = ...,
    ) -> list[Record]: ...

    @overload
    async def select_all[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        order_by: LiteralString | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: type[RecordT],
    ) -> list[RecordT]: ...

    @ensure_db
    def select_all[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: type[RecordT] | None = None,
    ) -> Coroutine[list[Any]]:
        return select_all(
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
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: None = ...,
    ) -> Record | None: ...

    @overload
    async def select_one[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: type[RecordT],
    ) -> RecordT | None: ...

    @ensure_db
    def select_one[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: type[RecordT] | None = None,
    ) -> Coroutine[Any | None]:
        return select_one(
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
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: None = ...,
    ) -> list[Record]: ...

    @overload
    async def search[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: type[RecordT],
    ) -> list[RecordT]: ...

    @ensure_db
    def search[RecordT: Record](
        self,
        /,
        *args: object,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: type[RecordT] | None = None,
    ) -> Coroutine[list[Any]]:
        return search(
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
    def update(
        self,
        /,
        *args: object,
        table: LiteralString,
        values: Mapping[LiteralString, object],
        where: ConditionsType | None = None,
    ) -> Coroutine[None]:
        return update(self.db, *args, table=table, values=values, where=where)

    @ensure_db
    def insert_into(
        self,
        /,
        *,
        table: LiteralString,
        values: Mapping[LiteralString, object],
        extra: str = '',
    ) -> Coroutine[None]:
        return insert_into(self.db, table=table, values=values, extra=extra)

    @ensure_db
    def delete_from(
        self, /, *args: object, table: LiteralString, where: ConditionsType
    ) -> Coroutine[None]:
        return delete_from(self.db, *args, table=table, where=where)
