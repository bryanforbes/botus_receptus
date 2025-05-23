from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    LiteralString,
    cast,
    overload,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing_extensions import TypeIs

    from asyncpg import Connection, Record
    from asyncpg.pool import PoolConnectionProxy

    from ..types import Coroutine

__all__ = ('delete_from', 'insert_into', 'search', 'select_all', 'select_one')


type ConditionsType = Sequence[LiteralString] | LiteralString


def _is_literal_string(obj: ConditionsType | None) -> TypeIs[LiteralString]:
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
async def select_all[RecordT: Record](
    db: Connection[RecordT] | PoolConnectionProxy[RecordT],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    order_by: LiteralString | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
    record_class: None = ...,
) -> list[RecordT]: ...


@overload
async def select_all[RecordT: Record](
    db: Connection[Any] | PoolConnectionProxy[Any],
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


def select_all[RecordT: Record](
    db: Connection[Any] | PoolConnectionProxy[Any],
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
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}'  # noqa: S608
        f'{group_by_str}{order_by_str}',
        *args,
        record_class=record_class,
    )


@overload
async def select_one[RecordT: Record](
    db: Connection[RecordT] | PoolConnectionProxy[RecordT],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: None = ...,
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
) -> RecordT | None: ...


@overload
async def select_one[RecordT: Record](
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: type[RecordT],
    where: ConditionsType | None = ...,
    group_by: Sequence[LiteralString] | None = ...,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = ...,
) -> RecordT | None: ...


def select_one[RecordT: Record](
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    columns: Sequence[LiteralString],
    record_class: type[RecordT] | None = None,
    where: ConditionsType | None = None,
    group_by: Sequence[LiteralString] | None = None,
    joins: Sequence[tuple[LiteralString, LiteralString]] | None = None,
) -> Coroutine[Any | None]:
    columns_str = ', '.join(columns)
    where_str = _get_where_string(where)
    joins_str = _get_join_string(joins)
    group_by_str = _get_group_by_string(group_by)

    return db.fetchrow(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}'  # noqa: S608
        + group_by_str,
        *args,
        record_class=record_class,
    )


@overload
async def search[RecordT: Record](
    db: Connection[RecordT] | PoolConnectionProxy[RecordT],
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
) -> list[RecordT]: ...


@overload
async def search[RecordT: Record](
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
    record_class: type[RecordT],
) -> list[RecordT]: ...


def search[RecordT: Record](
    db: Connection[RecordT] | PoolConnectionProxy[RecordT],
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
    record_class: type[RecordT] | None = None,
) -> Coroutine[list[RecordT]]:
    if where is None:
        where_list: list[LiteralString] = []
    elif _is_literal_string(where):
        where_list = [where]
    else:
        where_list = list[LiteralString](where)

    columns_str = ', '.join(columns)
    joins_str = _get_join_string(joins)
    search_columns_str = " || ' ' || ".join(search_columns)
    args = (*args, ' & '.join(terms))
    len_str: LiteralString = cast('LiteralString', str(len(args)))

    where_list.append(
        f"to_tsvector('english', {search_columns_str}) @@ "
        f"to_tsquery('english', ${len_str})"
    )

    where_str = _get_where_string(where_list)
    group_by_str = _get_group_by_string(group_by)
    order_by_str = _get_order_by_string(order_by)

    return db.fetch(
        f'SELECT {columns_str} FROM {table}{joins_str}{where_str}'  # noqa: S608
        f'{group_by_str}{order_by_str}',
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

    await db.execute(f'UPDATE {table} SET {set_str}{where_str}', *args)  # noqa: S608


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
        f'INSERT INTO {table} ({columns_str}) VALUES '  # noqa: S608
        f'({values_str}){extra}',
        *data,
    )


async def delete_from(
    db: Connection[Any] | PoolConnectionProxy[Any],
    /,
    *args: object,
    table: LiteralString,
    where: ConditionsType,
) -> None:
    where_str = _get_where_string(where)
    await db.execute(f'DELETE FROM {table}{where_str}', *args)  # noqa: S608
