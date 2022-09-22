from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.types import String, TypeDecorator

if TYPE_CHECKING:
    _SnowflakeBase = TypeDecorator[int]
else:
    _SnowflakeBase = TypeDecorator


class Snowflake(_SnowflakeBase):
    impl = String
    cache_ok = True

    def process_bind_param(self, value: int | None, dialect: object) -> str | None:
        return str(value) if value is not None else value

    def process_result_value(self, value: str | None, dialect: object) -> int | None:
        return int(value) if value is not None else value

    def copy(self, /, **kwargs: object) -> Snowflake:
        return Snowflake(self.impl.length)
