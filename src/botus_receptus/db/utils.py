from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing_extensions import LiteralString, StrictTypeGuard

    from asyncpg import Connection, Record
    from asyncpg.pool import PoolConnectionProxy

    from ..types import Coroutine

_Record = TypeVar('_Record', bound='Record')

__all__ = ('select_all', 'select_one', 'insert_into', 'delete_from', 'search')


ConditionsType: TypeAlias = 'Sequence[LiteralString] | LiteralString'


def _is_literal_string(obj: object) -> StrictTypeGuard[LiteralString]:
    return isinstance(obj, str)


def _get_join_string(
    joins: Sequence[tuple[LiteralString, LiteralString]] | None, /
) -> LiteralString:
    if joins is None or len(joins) == 0:
        return ''

    return ' ' + ' '.join(f'JOIN {join[0]} ON {join[1]}' for join in joins)


def _get_where_string(conditions: ConditionsType | None, /) -> LiteralString:
    _conditions: Sequence[LiteralString] | None = (
        [conditions] if _is_literal_string(conditions) else conditions
    )

    if _conditions is None or len(_conditions) == 0:
        return ''

    return ' WHERE ' + ' AND '.join(_conditions)


def _get_order_by_string(order_by: LiteralString | None, /) -> LiteralString:
    if order_by is None:
        return ''

    return f' ORDER BY {order_by} ASC'


def _get_group_by_string(group_by: Sequence[LiteralString] | None, /) -> LiteralString:
    if group_by is None:
        return ''

    return ' GROUP BY ' + ', '.join(group_by)


@overload
async def select_all(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    order_by: LiteralString | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
    record_class: None = ...,
) -> list[_Record]:
    ...


@overload
async def select_all(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    order_by: LiteralString | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
    record_class: type[_Record],
) -> list[_Record]:
    ...


def select_all(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    where: ConditionsType | None = None,
    group_by: Sequence[LiteralString] | None = None,
    order_by: LiteralString | None = None,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
    record_class: type[_Record] | None = None,
) -> Coroutine[list[Any]]:
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}'
        f'{order_by_str}',
        *args,
        record_class=record_class,
    )


@overload
async def select_one(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: None = ...,
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
) -> _Record | None:
    ...


@overload
async def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: type[_Record],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
) -> _Record | None:
    ...


def select_one(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: type[_Record] | None = None,
    where: ConditionsType | None = None,
    group_by: Sequence[LiteralString] | None = None,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
) -> Coroutine[Any | None]:
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)

    return db.fetchrow(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}',
        *args,
        record_class=record_class,
    )


@overload
async def search(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    search_columns: Sequence[LiteralString],
    terms: Sequence[str],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    order_by: LiteralString | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
    record_class: None = ...,
) -> list[_Record]:
    ...


@overload
async def search(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    search_columns: Sequence[LiteralString],
    terms: Sequence[str],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    order_by: LiteralString | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
    record_class: type[_Record],
) -> list[_Record]:
    ...


def search(
    db: Connection[_Record] | PoolConnectionProxy[_Record],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    search_columns: Sequence[LiteralString],
    terms: Sequence[str],
    where: ConditionsType | None = None,
    group_by: Sequence[LiteralString] | None = None,
    order_by: LiteralString | None = None,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
    record_class: type[_Record] | None = None,
) -> Coroutine[list[_Record]]:
    if where is None:
        where_list: list[LiteralString] = []
    else:
        if _is_literal_string(where):
            where_list = [where]
        else:
            where_list = list(where)

    columns_str = ', '.join(columns)
    joins_str = _get_join_string(joins)
    search_columns_str: LiteralString = " || ' ' || ".join(search_columns)
    args = args + (' & '.join(terms),)

    where_list.append(
        f"to_tsvector('english', {search_columns_str}) @@ "  # type: ignore
        f"to_tsquery('english', ${len(args)})"
    )

    where_str = _get_where_string(where_list)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}{group_by_str}'
        f'{order_by_str}',
        *args,
        record_class=record_class,
    )


async def update(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    values: Mapping[LiteralString, Any],
    where: ConditionsType | None = None,
) -> None:
    set_str = ', '.join([' = '.join([key, value]) for key, value in values.items()])
    where_str = _get_where_string(where)

    await db.execute(f'UPDATE {table} SET {set_str}{where_str}', *args)


async def insert_into(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *,
    table: LiteralString,
    values: Mapping[LiteralString, object],
    extra: str = '',
) -> None:
    columns: list[LiteralString] = []
    data: list[Any] = []

    for column, value in values.items():
        columns.append(column)
        data.append(value)

    if extra:
        extra = ' ' + extra

    columns_str = ', '.join(columns)
    values_str = ', '.join(f'${index}' for index in range(1, len(values) + 1))
    await db.execute(
        f'INSERT INTO {table} ({columns_str}) VALUES ({values_str}){extra}', *data
    )


async def delete_from(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    where: ConditionsType,
) -> None:
    where_str = _get_where_string(where)
    await db.execute(f'DELETE FROM {table}{where_str}', *args)
