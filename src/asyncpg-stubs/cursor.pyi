from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Generator,
    Generic,
    List,
    Optional,
    TypeVar,
)

from . import connresource
from .connection import Connection
from .protocol import Record

_C = TypeVar('_C', bound=Connection)

class CursorFactory(
    connresource.ConnectionResource[_C],
    AsyncIterable[Record],
    Awaitable[Cursor],
    Generic[_C],
):
    def __init__(
        self,
        connection: _C,
        query: Any,
        state: Any,
        args: Any,
        prefetch: Any,
        timeout: Any,
    ) -> None: ...
    def __aiter__(self) -> CursorIterator[_C]: ...
    def __await__(self) -> Generator[Any, None, Cursor[_C]]: ...
    def __del__(self) -> None: ...

class BaseCursor(connresource.ConnectionResource[_C]):
    def __init__(self, connection: _C, query: Any, state: Any, args: Any) -> None: ...
    def __del__(self) -> None: ...

_CI = TypeVar('_CI', bound=CursorIterator)

class CursorIterator(BaseCursor[_C], AsyncIterator[Record]):
    def __init__(
        self,
        connection: _C,
        query: Any,
        state: Any,
        args: Any,
        prefetch: Any,
        timeout: Any,
    ) -> None: ...
    def __aiter__(self: _CI) -> _CI: ...
    async def __anext__(self) -> Record: ...

class Cursor(BaseCursor[_C]):
    async def fetch(
        self, n: int, *, timeout: Optional[float] = ...
    ) -> List[Record]: ...
    async def fetchrow(self, *, timeout: Optional[float] = ...) -> Optional[Record]: ...
    async def forward(self, n: int, *, timeout: Optional[float] = ...) -> int: ...
