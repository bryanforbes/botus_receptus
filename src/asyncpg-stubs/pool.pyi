from . import connection
from .protocol import Record
from typing import (
    Any,
    Optional,
    Union,
    Type,
    TypeArg,
    Generic,
    Callable,
    Iterable,
    Sequence,
    List,
    AsyncContextManager,
    Awaitable,
    Generator,
    overload,
)
from asyncio import AbstractEventLoop, Future

_C = TypeArg('_C', bound=connection.Connection)
_P = TypeArg('_P', bound=Pool)

class PoolConnectionProxyMeta(type):
    def __new__(metacls: Any, name: Any, bases: Any, dct: Any, *, wrap: bool = ...): ...
    def __init__(cls, name: Any, bases: Any, dct: Any, *, wrap: bool = ...) -> None: ...

class PoolConnectionProxy(connection._ConnectionProxy, Generic[_C]):
    def __init__(self, holder: PoolConnectionHolder[_C], con: _C) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...

class PoolConnectionHolder(Generic[_C]):
    def __init__(
        self,
        pool: Pool[_C],
        *,
        max_queries: int = ...,
        setup: Callable[[PoolConnectionProxy[_C]], None] = ...,
        max_inactive_time: Union[int, float] = ...,
    ) -> None: ...
    async def connect(self) -> None: ...
    async def acquire(self) -> PoolConnectionProxy[_C]: ...
    async def release(self, timeout: float) -> None: ...
    async def wait_until_released(self) -> Optional[Future]: ...
    async def close(self) -> None: ...
    def terminate(self) -> None: ...

class Pool(AsyncContextManager[Pool[_C]], Awaitable[Pool[_C]], Generic[_C]):
    def __init__(
        self,
        *connect_args: Any,
        min_size: int,
        max_size: int,
        max_queries: int,
        max_inactive_connection_lifetime: float,
        setup: Callable[[PoolConnectionProxy[_C]], None],
        init: Callable[[_C], None],
        loop: Optional[AbstractEventLoop],
        connection_class: Type[_C],
        **connect_kwargs: Any,
    ) -> None: ...
    async def _async__init__(self: _P) -> _P: ...
    def set_connect_args(
        self, dsn: Optional[str] = ..., **connect_kwargs: Any
    ) -> None: ...
    async def execute(self, query: str, *args: Any, timeout: float = ...) -> str: ...
    async def executemany(
        self, command: str, args: Iterable[Sequence[Any]], *, timeout: float = ...
    ) -> None: ...
    async def fetch(
        self, query: str, *args: Any, timeout: float = ...
    ) -> List[Record[Any]]: ...
    async def fetchval(
        self, query: str, *args: Any, column: int = ..., timeout: float = ...
    ) -> Optional[Any]: ...
    async def fetchrow(
        self, query: str, *args: Any, timeout: float = ...
    ) -> Optional[Record[Any]]: ...
    def acquire(self, *, timeout: Optional[float] = ...) -> PoolAcquireContext[_C]: ...
    async def release(self, connection: _C, *, timeout: float = ...) -> None: ...
    async def close(self) -> None: ...
    def terminate(self) -> None: ...
    async def expire_connections(self) -> None: ...
    def __await__(self: _P) -> Generator[Any, None, _P]: ...
    async def __aenter__(self: _P) -> _P: ...
    async def __aexit__(self, *exc: Any) -> None: ...

class PoolAcquireContext(AsyncContextManager[_C], Awaitable[_C], Generic[_C]):
    pool: Pool[_C] = ...
    timeout: Optional[float] = ...
    connection: Optional[_C] = ...
    done: bool = ...
    def __init__(self, pool: Pool[_C], timeout: Optional[float]) -> None: ...
    async def __aenter__(self) -> _C: ...
    async def __aexit__(self, *exc: Any) -> None: ...
    def __await__(self) -> Generator[Any, None, _C]: ...

@overload
def create_pool(
    dsn: Optional[str] = ...,
    *,
    min_size: int = ...,
    max_size: int = ...,
    max_queries: int = ...,
    max_inactive_connection_lifetime: float = ...,
    setup: Optional[Callable[[PoolConnectionProxy[_C]], None]] = ...,
    init: Optional[Callable[[_C], Any]] = ...,
    loop: Optional[AbstractEventLoop] = ...,
    connection_class: Type[_C],
    **connect_kwargs: Any,
) -> Pool[_C]: ...
@overload
def create_pool(
    dsn: Optional[str] = ...,
    *,
    min_size: int = ...,
    max_size: int = ...,
    max_queries: int = ...,
    max_inactive_connection_lifetime: float = ...,
    setup: Optional[Callable[[PoolConnectionProxy[connection.Connection]], None]] = ...,
    init: Optional[Callable[[connection.Connection], Any]] = ...,
    loop: Optional[AbstractEventLoop] = ...,
    **connect_kwargs: Any,
) -> Pool[connection.Connection]: ...
