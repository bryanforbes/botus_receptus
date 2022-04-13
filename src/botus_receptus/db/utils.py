from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, overload

from asyncpg import Connection, Record
from asyncpg.pool import PoolConnectionProxy

if TYPE_CHECKING:
    from typing_extensions import LiteralString

_Record = TypeVar('_Record', bound=Record)

__all__ = ('select_all', 'select_one', 'insert_into', 'delete_from', 'search')


ConditionsType: TypeAlias = "Sequence['LiteralString'] | 'LiteralString'"


def _get_join_string(joins: Sequence[tuple[str, str]] | None, /) -> str:
    if joins is None or len(joins) == 0:
        return ''

    return ' ' + ' '.join(map(lambda join: f'JOIN {join[0]} ON {join[1]}', joins))


def _get_where_string(conditions: ConditionsType | None, /) -> LiteralString:
    if conditions and not isinstance(conditions, Sequence):
        conditions = [conditions]

    if conditions is None or len(conditions) == 0:
        return ''

    return ' WHERE ' + ' AND '.join(conditions)  # type: ignore


def _get_order_by_string(order_by: str | None, /) -> str:
    if order_by is None:
        return ''

    return f' ORDER BY {order_by} ASC'


def _get_group_by_string(group_by: Sequence[str] | None, /) -> str:
    if group_by is None:
        return ''

    return ' GROUP BY ' + ', '.join(group_by)


@overload
async def select_all(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    where: ConditionsType | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[tuple[str, str]] | None = ...,
    record_class: None = ...,
) -> list[_Record]:
    ...


@overload
async def select_all(
    db: Connection[Any] | PoolConnectionProxy[Any],
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


async def select_all(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    where: ConditionsType | None = None,
    group_by: Sequence[str] | None = None,
    order_by: str | None = None,
    joins: Sequence[tuple[str, str]] | None = None,
    record_class: type[_Record] | None = None,
) -> list[Any]:
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return await db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}'
        f'{order_by_str}',
        *args,
        record_class=record_class,
    )


@overload
async def select_one(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    record_class: None = ...,
    where: ConditionsType | None = ...,
    group_by: Sequence[str] | None = ...,
    joins: Sequence[tuple[str, str]] | None = ...,
) -> _Record | None:
    ...


@overload
async def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    record_class: type[_Record],
    where: ConditionsType | None = ...,
    group_by: Sequence[str] | None = ...,
    joins: Sequence[tuple[str, str]] | None = ...,
) -> _Record | None:
    ...


async def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    record_class: type[_Record] | None = None,
    where: ConditionsType | None = None,
    group_by: Sequence[str] | None = None,
    joins: Sequence[tuple[str, str]] | None = None,
) -> Any | None:
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)

    return await db.fetchrow(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}',
        *args,
        record_class=record_class,
    )


@overload
async def search(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    search_columns: Sequence[LiteralString],
    terms: Sequence[str],
    where: ConditionsType | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[tuple[str, str]] | None = ...,
    record_class: None = ...,
) -> list[_Record]:
    ...


@overload
async def search(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    search_columns: Sequence[LiteralString],
    terms: Sequence[str],
    where: ConditionsType | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[tuple[str, str]] | None = ...,
    record_class: type[_Record],
) -> list[_Record]:
    ...


async def search(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
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
    record_class: type[_Record] | None = None,
) -> list[_Record]:
    if where is None:
        where = []
    if not isinstance(where, Sequence):
        where = [where]
    else:
        where = list(where)

    columns_str = ', '.join(columns)
    joins_str = _get_join_string(joins)
    search_columns_str = " || ' ' || ".join(search_columns)
    args = args + (' & '.join(terms),)

    where.append(
        f"to_tsvector('english', {search_columns_str}) @@ "  # type: ignore
        f"to_tsquery('english', ${len(args)})"
    )

    where_str = _get_where_string(where)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return await db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}'
        f'{order_by_str}',
        *args,
        record_class=record_class,
    )


async def update(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    values: dict[str, Any],
    where: ConditionsType | None = None,
) -> None:
    set_str = ', '.join([' = '.join([key, value]) for key, value in values.items()])
    where_str = _get_where_string(where)

    await db.execute(f'UPDATE {table} SET {set_str}{where_str}', *args)


async def insert_into(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *,
    table: str,
    values: dict[str, Any],
    extra: str = '',
) -> None:
    columns: list[str] = []
    data: list[Any] = []

    for column, value in values.items():
        columns.append(column)
        data.append(value)

    if extra:
        extra = ' ' + extra

    columns_str = ', '.join(columns)
    values_str = ', '.join(map(lambda index: f'${index}', range(1, len(values) + 1)))
    await db.execute(
        f'INSERT INTO {table} ({columns_str}) VALUES ({values_str}){extra}', *data
    )


async def delete_from(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    where: ConditionsType,
) -> None:
    where_str = _get_where_string(where)
    await db.execute(f'DELETE FROM {table}{where_str}', *args)
