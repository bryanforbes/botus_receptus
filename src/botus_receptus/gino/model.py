from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)
from typing_extensions import Final

from gino.declarative import ModelType
from gino.engine import GinoEngine
from sqlalchemy.dialects.postgresql import insert

_M = TypeVar('_M', bound='ModelMixin')


DEFAULT: Final = cast(int, object())


class ModelMixin:
    @classmethod
    async def create_or_update(
        cls: Type[_M],
        *,
        set_: Union[Sequence[str], Mapping[str, str]],
        bind: Optional[GinoEngine] = None,
        timeout: int = DEFAULT,
        **values: Any,
    ) -> _M:
        assert isinstance(cls, ModelType)

        cls._check_abstract()

        column_name_map = cls._column_name_map
        index_elements: List[str] = [
            column_name_map[k] for k in cls.__table__.primary_key.columns.keys()
        ]
        insert_values: Dict[str, Any] = {
            column_name_map[k]: v for k, v in values.items()
        }

        set_values: Mapping[str, str]
        if hasattr(set_, 'get'):
            set_values = cast(Mapping[str, str], set_)
        else:
            set_values = {v: v for v in cast(Sequence[str], set_)}

        opts: Dict[str, Any] = dict(return_model=False, model=cls)
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
