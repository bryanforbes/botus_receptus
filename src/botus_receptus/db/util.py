from __future__ import annotations

from typing import Any, Type, TypeVar, overload

from asyncpg import Connection, Record
from asyncpg.pool import PoolConnectionProxy

from ..compat import Sequence, dict, list
from ..compat import tuple as Tuple

_Record = TypeVar('_Record', bound=Record)

__all__ = ('select_all', 'select_one', 'insert_into', 'delete_from', 'search')


def _get_join_string(joins: Sequence[Tuple[str, str]] | None, /) -> str:
    if joins is None or len(joins) == 0:
        return ''

    return ' ' + ' '.join(map(lambda join: f'JOIN {join[0]} ON {join[1]}', joins))


def _get_where_string(conditions: Sequence[str] | None, /) -> str:
    if conditions is None or len(conditions) == 0:
        return ''

    return ' WHERE ' + ' AND '.join(conditions)


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
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
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
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
    record_class: Type[_Record],
) -> list[_Record]:
    ...


async def select_all(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    where: Sequence[str] | None = None,
    group_by: Sequence[str] | None = None,
    order_by: str | None = None,
    joins: Sequence[Tuple[str, str]] | None = None,
    record_class: Type[_Record] | None = None,
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
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
) -> _Record | None:
    ...


@overload
async def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    record_class: Type[_Record],
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
) -> _Record | None:
    ...


async def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    record_class: Type[_Record] | None = None,
    where: Sequence[str] | None = None,
    group_by: Sequence[str] | None = None,
    joins: Sequence[Tuple[str, str]] | None = None,
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
    search_columns: Sequence[str],
    terms: Sequence[str],
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
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
    search_columns: Sequence[str],
    terms: Sequence[str],
    where: Sequence[str] | None = ...,
    group_by: Sequence[str] | None = ...,
    order_by: str | None = ...,
    joins: Sequence[Tuple[str, str]] | None = ...,
    record_class: Type[_Record],
) -> list[_Record]:
    ...


async def search(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: Any,
    table: str,
    columns: Sequence[str],
    search_columns: Sequence[str],
    terms: Sequence[str],
    where: Sequence[str] | None = None,
    group_by: Sequence[str] | None = None,
    order_by: str | None = None,
    joins: Sequence[Tuple[str, str]] | None = None,
    record_class: Type[_Record] | None = None,
) -> list[_Record]:
    columns_str = ', '.join(columns)
    joins_str = _get_join_string(joins)
    search_columns_str = " || ' ' || ".join(search_columns)
    search_terms_str = ' & '.join(terms)
    where_str = _get_where_string(
        tuple(where if where is not None else [])
        + (
            f"to_tsvector('english', {search_columns_str}) @@ to_tsquery('english', "
            f"'{search_terms_str}')",
        )
    )
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
    where: Sequence[str] | None = None,
) -> None:
    set_str = ', '.join([' = '.join([key, value]) for key, value in values.items()])
    where_str = _get_where_string(where if where is not None else [])

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
    where: Sequence[str],
) -> None:
    where_str = _get_where_string(where)
    await db.execute(f'DELETE FROM {table}{where_str}', *args)
