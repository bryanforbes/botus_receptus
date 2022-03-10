from __future__ import annotations

import builtins
from typing import Any, ClassVar, Final, Protocol, TypeVar, cast

from gino.api import Gino
from gino.declarative import InvertDict
from gino.engine import GinoEngine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.schema import Table

from ..compat import Mapping, Sequence, dict, list

DEFAULT: Final = cast(int, object())


class ModelTypeProtocol(Protocol):
    __metadata__: ClassVar[Gino]
    __table__: ClassVar[Table]
    _column_name_map: ClassVar[InvertDict[str, str]]

    def __init__(self, **kwargs: Any) -> None:
        ...

    @classmethod
    def _check_abstract(cls) -> None:
        ...


_MTP = TypeVar('_MTP', bound='ModelTypeProtocol')


class ModelMixin:
    @classmethod
    async def create_or_update(
        cls: type[_MTP],
        /,
        *,
        set_: Sequence[str] | Mapping[str, str],
        bind: GinoEngine | None = None,
        timeout: int = DEFAULT,
        **values: Any,
    ) -> _MTP:
        cls._check_abstract()

        column_name_map = cls._column_name_map
        index_elements: list[str] = [
            column_name_map[k] for k in cls.__table__.primary_key.columns.keys()
        ]
        insert_values: dict[str, Any] = {
            column_name_map[k]: v for k, v in values.items()
        }

        set_values: Mapping[str, str]
        if hasattr(set_, 'get'):
            set_values = cast(Mapping[str, str], set_)
        else:
            set_values = {v: v for v in cast(Sequence[str], set_)}

        opts: dict[str, Any] = builtins.dict(return_model=False, model=cls)
        if timeout is not DEFAULT:
            opts['timeout'] = timeout

        stmt = insert(cls).values(**insert_values).returning(*cls)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={k: getattr(stmt.excluded, v) for k, v in set_values.items()},
        ).execution_options(**opts)

        if bind is None:
            assert cls.__metadata__.bind is not None
            bind = cls.__metadata__.bind

        row = await bind.first(stmt)

        return cls(**{column_name_map.invert_get(k, ''): v for k, v in row.items()})
