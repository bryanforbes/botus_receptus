from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.types import String, TypeDecorator

if TYPE_CHECKING:
    IntBase = TypeDecorator[int]
else:
    IntBase = TypeDecorator


class Snowflake(IntBase):
    impl = String

    def process_bind_param(self, value: Any, dialect: Any, /) -> str | None:
        return str(value) if value is not None else value

    def process_result_value(self, value: Any, dialect: Any, /) -> int | None:
        return int(value) if value is not None else value

    def copy(self, /, **kwargs: Any) -> Snowflake:
        return Snowflake(self.impl.length)
