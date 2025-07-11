from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from sqlalchemy import BigInteger, ColumnOperators, Operators, String, TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR

if TYPE_CHECKING:
    from enum import Flag as _EnumFlag

    from sqlalchemy.types import TypeEngine


class Snowflake(TypeDecorator[int]):
    impl: TypeEngine[Any] | type[TypeEngine[Any]] = String
    cache_ok: bool | None = True

    @override
    def process_bind_param(self, value: int | None, dialect: object) -> str | None:
        if value is None:
            return value

        return str(value)

    @override
    def process_result_value(self, value: str | None, dialect: object) -> int | None:
        if value is None:
            return value

        return int(value)

    @override
    def copy(self, /, **kwargs: object) -> Snowflake:
        if TYPE_CHECKING:
            assert isinstance(self.impl_instance, String)

        return Snowflake(self.impl_instance.length)


class _TSVectorComparator(TSVECTOR.Comparator[str]):
    @override
    def match(self, other: object, **kwargs: object) -> ColumnOperators:
        if TYPE_CHECKING:
            assert isinstance(self.expr.type, TypeDecorator)

        if (
            'postgresql_regconfig' not in kwargs
            and 'regconfig' in self.expr.type.options
        ):
            kwargs['postgresql_regconfig'] = self.expr.type.options['regconfig']

        return super().match(other, **kwargs)

    @override
    def __or__(self, other: object) -> Operators:
        return self.op('||')(other)


class TSVector(TypeDecorator[str]):
    impl: TypeEngine[Any] | type[TypeEngine[Any]] = TSVECTOR
    cache_ok: bool | None = True

    columns: tuple[object, ...]
    options: dict[str, object]

    @property
    @override
    def comparator_factory(self) -> type[_TSVectorComparator]:
        return _TSVectorComparator

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initializes new TSVectorType

        :param *args: list of column names
        :param **kwargs: various other options for this TSVectorType
        """
        self.columns = args
        self.options = kwargs

        super().__init__()


class Flag[FlagT: _EnumFlag](TypeDecorator[FlagT]):
    impl: TypeEngine[Any] | type[TypeEngine[Any]] = BigInteger
    cache_ok: bool | None = True

    _flag_cls: type[FlagT]

    def __init__(
        self, flag_cls: type[FlagT], /, *args: object, **kwargs: object
    ) -> None:
        self._flag_cls = flag_cls
        super().__init__(*args, **kwargs)

    @override
    def process_bind_param(self, value: FlagT | None, dialect: object) -> int | None:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: int | None, dialect: object) -> FlagT | None:
        if value is None:
            return None

        return self._flag_cls(value)
