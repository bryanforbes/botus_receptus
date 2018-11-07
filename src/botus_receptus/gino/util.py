from typing import Any, Union, TypeVar, Type, Sequence, Mapping, List, Dict, cast
from gino.crud import CRUDModel
from sqlalchemy.dialects.postgresql import insert

from .base import db

_CM = TypeVar('_CM', bound=CRUDModel)


async def create_or_update(
    cls: Type[_CM], *, set_: Union[Sequence[str], Mapping[str, str]], **values: Any
) -> _CM:
    column_name_map = cls._column_name_map

    index_elements: List[str] = [
        column_name_map[k] for k in cls.__table__.primary_key.columns.keys()
    ]
    insert_values: Dict[str, Any] = {column_name_map[k]: v for k, v in values.items()}

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

    row = await db.bind.first(stmt)
    return cls(**{column_name_map.invert_get(k, ''): v for k, v in row.items()})
