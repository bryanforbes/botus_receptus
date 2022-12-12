from __future__ import annotations

from enum import Flag as _EnumFlag
from typing import TYPE_CHECKING, Generic, TypeVar

from sqlalchemy import BigInteger, Boolean, String, TypeDecorator as _TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import TypeEngine

if TYPE_CHECKING:
    from sqlalchemy.sql import ColumnElement


_T = TypeVar('_T')
_FlagT = TypeVar('_FlagT', bound=_EnumFlag)

if TYPE_CHECKING:
    _TSVectorComparatorBase = TypeEngine.Comparator['TSVector']

    class TypeDecorator(_TypeDecorator[_T]):
        ...

else:
    _TSVectorComparatorBase = TSVECTOR.Comparator

    class TypeDecorator(_TypeDecorator, Generic[_T]):
        ...


class Snowflake(TypeDecorator[int]):
    impl = String
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


class TSVector(TypeDecorator[str]):
    impl = TSVECTOR
    cache_ok = True

    class Comparator(_TSVectorComparatorBase):
        def match(self, other: object, **kwargs: object) -> ColumnElement[Boolean]:
            if (
                'postgresql_regconfig' not in kwargs
                and 'regconfig' in self.type.options
            ):
                kwargs['postgresql_regconfig'] = self.type.options['regconfig']
            return TSVECTOR.Comparator.match(self, other, **kwargs)

        def __or__(self, other: object) -> ColumnElement[TSVector]:
            return self.op('||')(other)  # type: ignore

    comparator_factory = Comparator  # type: ignore

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
