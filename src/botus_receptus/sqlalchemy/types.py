from __future__ import annotations

from enum import Flag as _EnumFlag
from typing import TYPE_CHECKING, Self
from typing_extensions import TypeVar, override

from sqlalchemy import BigInteger, ColumnOperators, Operators, String, TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR

_FlagT = TypeVar('_FlagT', bound=_EnumFlag, infer_variance=True)


class Snowflake(TypeDecorator[int]):
    impl = String
    cache_ok = True

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
    def copy(self, /, **kwargs: object) -> Self:
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
    impl = TSVECTOR
    cache_ok = True

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


class Flag(TypeDecorator[_FlagT]):
    impl = BigInteger
    cache_ok = True

    _flag_cls: type[_FlagT]

    def __init__(
        self, flag_cls: type[_FlagT], /, *args: object, **kwargs: object
    ) -> None:
        self._flag_cls = flag_cls
        super().__init__(*args, **kwargs)

    @override
    def process_bind_param(self, value: _FlagT | None, dialect: object) -> int | None:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: int | None, dialect: object) -> _FlagT | None:
        if value is None:
            return None

        return self._flag_cls(value)
