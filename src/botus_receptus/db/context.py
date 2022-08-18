from __future__ import annotations

from collections.abc import Awaitable, Generator, Sequence
from contextlib import AbstractAsyncContextManager
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from attrs import define
from discord.ext import commands

from ..types import Coroutine, CoroutineFunc
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
    from typing_extensions import LiteralString

    from asyncpg import Record
    from asyncpg.pool import PoolConnectionProxy

    from .bot import AutoShardedBot, Bot

_Record = TypeVar('_Record', bound='Record')
_BotT = TypeVar('_BotT', bound='Bot | AutoShardedBot')
_P = ParamSpec('_P')
_R = TypeVar('_R')

_DbMethod: TypeAlias = CoroutineFunc[Concatenate['Context[Any]', _P], _R]


@define
class AquireContextManager(
    AbstractAsyncContextManager['PoolConnectionProxy[Record]'],
    Awaitable['PoolConnectionProxy[Record]'],
):
    ctx: Context[Any]
    timeout: float | None = None

    def __await__(self, /) -> Generator[Any, None, PoolConnectionProxy[Record]]:
        return self.ctx._acquire(self.timeout).__await__()

    def __aenter__(self, /) -> Coroutine[PoolConnectionProxy[Record]]:
        return self.ctx._acquire(self.timeout)

    async def __aexit__(self, /, *args: Any) -> None:
        await self.ctx.release()


def ensure_db(func: _DbMethod[_P, _R], /) -> _DbMethod[_P, _R]:
    def wrapper(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> Coroutine[_R]:
        if not hasattr(self, 'db'):
            raise RuntimeError(
                'No database object available; ensure acquire() was called'
            )

        return func(self, *args, **kwargs)

    return wrapper


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
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        order_by: LiteralString | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: None = ...,
    ) -> list[Record]:
        ...

    @overload
    async def select_all(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        order_by: LiteralString | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: type[_Record],
    ) -> list[_Record]:
        ...

    @ensure_db
    def select_all(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: Any | None = None,
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
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: None = ...,
    ) -> Record | None:
        ...

    @overload
    async def select_one(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = ...,
        group_by: Sequence[LiteralString] | None = ...,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
        record_class: type[_Record],
    ) -> _Record | None:
        ...

    @ensure_db
    def select_one(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: Any | None = None,
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
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: None = ...,
    ) -> list[Record]:
        ...

    @overload
    async def search(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: type[_Record],
    ) -> list[_Record]:
        ...

    @ensure_db
    def search(
        self,
        /,
        *args: Any,
        table: LiteralString,
        columns: Sequence[LiteralString],
        search_columns: Sequence[LiteralString],
        terms: Sequence[LiteralString],
        where: ConditionsType | None = None,
        group_by: Sequence[LiteralString] | None = None,
        order_by: LiteralString | None = None,
        joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
        record_class: Any | None = None,
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
        *args: Any,
        table: LiteralString,
        values: dict[LiteralString, Any],
        where: ConditionsType | None = None,
    ) -> Coroutine[None]:
        return update(self.db, *args, table=table, values=values, where=where)

    @ensure_db
    def insert_into(
        self,
        /,
        *,
        table: LiteralString,
        values: dict[LiteralString, Any],
        extra: str = '',
    ) -> Coroutine[None]:
        return insert_into(self.db, table=table, values=values, extra=extra)

    @ensure_db
    def delete_from(
        self, /, *args: Any, table: LiteralString, where: ConditionsType
    ) -> Coroutine[None]:
        return delete_from(self.db, *args, table=table, where=where)
