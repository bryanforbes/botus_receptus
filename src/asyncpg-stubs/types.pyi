from asyncpg.pgproto.types import (
    BitString as BitString,
    Box as Box,
    Circle as Circle,
    Line as Line,
    LineSegment as LineSegment,
    Path as Path,
    Point as Point,
    Polygon as Polygon,
)
from typing import (
    Any,
    Optional,
    NamedTuple,
    Hashable,
    Sized,
    Sequence,
    Iterable,
    Tuple,
    Iterator,
    TypeVar,
    Generic,
)

_T = TypeVar('_T')

class Type(NamedTuple):
    oid: int
    name: str
    kind: str
    schema: str

class Attribute(NamedTuple):
    name: str
    type: Type

class ServerVersion(NamedTuple):
    major: int
    minor: int
    micro: int
    level: str
    serial: int

class Range(Hashable, Generic[_T]):
    def __init__(
        self,
        lower: Optional[_T] = ...,
        upper: Optional[_T] = ...,
        *,
        lower_inc: bool = ...,
        upper_inc: bool = ...,
        empty: bool = ...,
    ) -> None: ...
    @property
    def lower(self) -> Optional[_T]: ...
    @property
    def lower_inc(self) -> bool: ...
    @property
    def lower_inf(self) -> bool: ...
    @property
    def upper(self) -> Optional[_T]: ...
    @property
    def upper_inc(self) -> bool: ...
    @property
    def upper_inf(self) -> bool: ...
    @property
    def isempty(self) -> bool: ...
    def __bool__(self) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...
