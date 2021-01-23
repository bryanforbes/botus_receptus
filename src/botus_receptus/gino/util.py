from __future__ import annotations

from typing import Any, TypeVar, cast

from gino.crud import CRUDModel
from sqlalchemy.dialects.postgresql import insert

from ..compat import Mapping, Sequence, dict, list, type

_CM = TypeVar('_CM', bound=CRUDModel)


async def create_or_update(
    cls: type[_CM], *, set_: Sequence[str] | Mapping[str, str], **values: Any
) -> _CM:
    column_name_map = cls._column_name_map

    index_elements: list[str] = [
        column_name_map[k] for k in cls.__table__.primary_key.columns.keys()
    ]
    insert_values: dict[str, Any] = {column_name_map[k]: v for k, v in values.items()}

    set_values: Mapping[str, str]
    if hasattr(set_, 'get'):
        set_values = cast(Mapping[str, str], set_)
    else:
        set_values = {v: v for v in cast(Sequence[str], set_)}

    stmt = insert(cls).values(**insert_values).returning(*cls)
    stmt = stmt.on_conflict_do_update(
        index_elements=index_elements,
        set_={k: getattr(stmt.excluded, v) for k, v in set_values.items()},
    ).execution_options(return_model=False, model=cls)

    assert cls.__metadata__.bind is not None

    row = await cls.__metadata__.bind.first(stmt)
    return cls(**{column_name_map.invert_get(k, ''): v for k, v in row.items()})
