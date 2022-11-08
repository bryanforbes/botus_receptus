from __future__ import annotations

from enum import Flag as _EnumFlag
from typing import TYPE_CHECKING, TypeVar

from sqlalchemy import BigInteger, ColumnOperators, Operators, String, TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR

_FlagT = TypeVar('_FlagT', bound=_EnumFlag)


class Snowflake(TypeDecorator[int]):
    impl: String = String  # pyright: ignore
    cache_ok = True

    def process_bind_param(self, value: int | None, dialect: object) -> str | None:
        if value is None:
            return value

        return str(value)

    def process_result_value(self, value: str | None, dialect: object) -> int | None:
        if value is None:
            return value

        return int(value)

    def copy(self, /, **kwargs: object) -> Snowflake:
        return Snowflake(self.impl.length)


class _TSVectorComparator(TSVECTOR.Comparator[str]):
    def match(self, other: object, **kwargs: object) -> ColumnOperators:
        if TYPE_CHECKING:
            assert isinstance(self.expr.type, TypeDecorator)

        if (
            'postgresql_regconfig' not in kwargs
            and 'regconfig' in self.expr.type.options
        ):
            kwargs['postgresql_regconfig'] = self.expr.type.options['regconfig']

        return super().match(other, **kwargs)

    def __or__(self, other: object) -> Operators:
        return self.op('||')(other)


class TSVector(TypeDecorator[str]):
    impl = TSVECTOR
    cache_ok = True

    @property
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


class Flag(TypeDecorator[_FlagT]):
    impl = BigInteger
    cache_ok = True

    _flag_cls: type[_FlagT]

    def __init__(
        self, flag_cls: type[_FlagT], /, *args: object, **kwargs: object
    ) -> None:
        self._flag_cls = flag_cls
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: _FlagT | None, dialect: object) -> int | None:
        if value is None:
            return None

        return value.value

    def process_result_value(self, value: int | None, dialect: object) -> _FlagT | None:
        if value is None:
            return None

        return self._flag_cls(value)
