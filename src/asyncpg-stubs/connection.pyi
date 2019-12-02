from . import connect_utils
from .exceptions import PostgresLogMessage
from .types import ServerVersion
from .protocol import Record
from .protocol.protocol import ConnectionSettings
from .cursor import CursorFactory
from .prepared_stmt import PreparedStatement
from .transaction import Transaction
from typing import (
    Any,
    Optional,
    Union,
    Type,
    TypeVar,
    Callable,
    List,
    Iterable,
    Sequence,
    IO,
    Coroutine,
    AsyncIterable,
    Tuple,
    NamedTuple,
    overload,
)
from os import PathLike
from asyncio import AbstractEventLoop
from ssl import SSLContext

class ConnectionMeta(type):
    def __instancecheck__(cls, instance: Any): ...

_C = TypeVar('_C', bound=Connection)

class Connection:
    def __init__(
        self,
        protocol: Any,
        transport: Any,
        loop: Any,
        addr: Any,
        config: connect_utils._ClientConfiguration,
        params: connect_utils._ConnectionParameters,
    ) -> None: ...
    def __del__(self) -> None: ...
    async def add_listener(
        self: _C, channel: str, callback: Callable[[_C, int, str, Any], Any]
    ) -> None: ...
    async def remove_listener(
        self: _C, channel: str, callback: Callable[[_C, int, str, Any], Any]
    ) -> None: ...
    def add_log_listener(
        self: _C, callback: Callable[[_C, PostgresLogMessage], Any]
    ) -> None: ...
    def remove_log_listener(
        self: _C, callback: Callable[[_C, PostgresLogMessage], Any]
    ) -> None: ...
    def get_server_pid(self) -> int: ...
    def get_server_version(self) -> ServerVersion: ...
    def get_settings(self) -> ConnectionSettings: ...
    def transaction(
        self, *, isolation: str = ..., readonly: bool = ..., deferrable: bool = ...
    ) -> Transaction: ...
    def is_in_transaction(self) -> bool: ...
    async def execute(self, query: str, *args, timeout: float = ...) -> str: ...
    async def executemany(
        self, command: str, args: Iterable[Sequence[Any]], *, timeout: float = ...
    ) -> None: ...
    def cursor(
        self: _C, query: str, *args, prefetch: int = ..., timeout: float = ...
    ) -> CursorFactory[_C]: ...
    async def prepare(
        self, query: str, *, timeout: float = ...
    ) -> PreparedStatement[_C]: ...
    async def fetch(
        self, query: str, *args, timeout: float = ...
    ) -> List[Record[Any]]: ...
    async def fetchval(
        self, query: str, *args, column: int = ..., timeout: float = ...
    ) -> Optional[Any]: ...
    async def fetchrow(
        self, query: str, *args, timeout: float = ...
    ) -> Optional[Record[Any]]: ...
    async def copy_from_table(
        self,
        table_name: str,
        *,
        output: Union[PathLike, IO, Callable[[bytes], Coroutine[Any, Any, Any]]],
        columns: List[str] = ...,
        schema_name: str = ...,
        timeout: float = ...,
        format: Optional[str] = ...,
        oids: Optional[Any] = ...,
        delimiter: Optional[Any] = ...,
        null: Optional[Any] = ...,
        header: Optional[Any] = ...,
        quote: Optional[Any] = ...,
        escape: Optional[Any] = ...,
        force_quote: Optional[Any] = ...,
        encoding: Optional[Any] = ...,
    ) -> str: ...
    async def copy_from_query(
        self,
        query: str,
        *args,
        output: Union[PathLike, IO, Callable[[bytes], Coroutine[Any, Any, Any]]],
        timeout: float = ...,
        format: Optional[str] = ...,
        oids: Optional[Any] = ...,
        delimiter: Optional[Any] = ...,
        null: Optional[Any] = ...,
        header: Optional[Any] = ...,
        quote: Optional[Any] = ...,
        escape: Optional[Any] = ...,
        force_quote: Optional[Any] = ...,
        encoding: Optional[Any] = ...,
    ) -> str: ...
    async def copy_to_table(
        self,
        table_name: str,
        *,
        source: Union[PathLike, IO, AsyncIterable[bytes]],
        columns: List[str] = ...,
        schema_name: str = ...,
        timeout: float = ...,
        format: Optional[str] = ...,
        oids: Optional[Any] = ...,
        freeze: Optional[Any] = ...,
        delimiter: Optional[Any] = ...,
        null: Optional[Any] = ...,
        header: Optional[Any] = ...,
        quote: Optional[Any] = ...,
        escape: Optional[Any] = ...,
        force_quote: Optional[Any] = ...,
        force_not_null: Optional[Any] = ...,
        force_null: Optional[Any] = ...,
        encoding: Optional[Any] = ...,
    ) -> str: ...
    async def copy_records_to_table(
        self,
        table_name: str,
        *,
        records: Iterable[Tuple[Any, ...]],
        columns: Optional[List[str]] = ...,
        schema_name: Optional[str] = ...,
        timeout: Optional[float] = ...,
    ) -> str: ...
    async def set_type_codec(
        self,
        typename: str,
        *,
        schema: str = ...,
        encoder: Callable[[Any], Any],
        decoder: Callable[[Any], Any],
        format: str = ...,
    ) -> None: ...
    async def reset_type_codec(self, typename: str, *, schema: str = ...) -> None: ...
    async def set_builtin_type_codec(
        self, typename: str, *, schema: str = ..., codec_name: str
    ) -> None: ...
    def is_closed(self) -> bool: ...
    async def close(self, *, timeout: Optional[float] = ...) -> None: ...
    def terminate(self) -> None: ...
    async def reset(self, *, timeout: Optional[float] = ...) -> None: ...
    async def reload_schema_state(self) -> None: ...

@overload
def connect(
    dsn: Optional[str] = ...,
    *,
    host: Optional[str] = ...,
    port: Optional[int] = ...,
    user: Optional[str] = ...,
    password: Optional[str] = ...,
    passfile: Optional[str] = ...,
    database: Optional[str] = ...,
    loop: Optional[AbstractEventLoop] = ...,
    timeout: int = ...,
    statement_cache_size: int = ...,
    max_cached_statement_lifetime: int = ...,
    max_cacheable_statement_size: int = ...,
    command_timeout: Optional[int] = ...,
    ssl: Optional[Union[bool, SSLContext]] = ...,
    server_settings: Optional[Any] = ...,
) -> Connection: ...
@overload
def connect(
    dsn: Optional[str] = ...,
    *,
    host: Optional[str] = ...,
    port: Optional[int] = ...,
    user: Optional[str] = ...,
    password: Optional[str] = ...,
    passfile: Optional[str] = ...,
    database: Optional[str] = ...,
    loop: Optional[AbstractEventLoop] = ...,
    timeout: int = ...,
    statement_cache_size: int = ...,
    max_cached_statement_lifetime: int = ...,
    max_cacheable_statement_size: int = ...,
    command_timeout: Optional[int] = ...,
    ssl: Optional[Union[bool, SSLContext]] = ...,
    connection_class: Type[_C] = ...,
    server_settings: Optional[Any] = ...,
) -> _C: ...

class _ConnectionProxy: ...

class ServerCapabilities(NamedTuple):
    advisory_locks: bool
    notifications: bool
    plpgsql: bool
    sql_reset: bool
    sql_close_all: bool
