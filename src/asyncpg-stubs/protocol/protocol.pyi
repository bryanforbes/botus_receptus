from typing import (
    Any,
    Iterator,
    Tuple,
    Union,
    TypeVar,
    Collection,
    Optional,
    Hashable,
    Sized,
    Dict,
    overload,
)
from typing_extensions import Protocol as _TEProtocol
import asyncio
import asyncio.protocols
import asyncpg.pgproto.pgproto

from ..types import (
    BitString as BitString,
    Point as Point,
    Box as Box,
    Line as Line,
    LineSegment as LineSegment,
    Path as Path,
    Point as Point,
    Polygon as Polygon,
    Circle as Circle,
)

BUILTIN_TYPE_NAME_MAP: Dict[str, int]
BUILTIN_TYPE_OID_MAP: Dict[int, str]
NO_TIMEOUT: object

def __pyx_unpickle_BaseProtocol(*args, **kwargs) -> Any: ...
def __pyx_unpickle_CoreProtocol(*args, **kwargs) -> Any: ...
def __pyx_unpickle_DataCodecConfig(*args, **kwargs) -> Any: ...
def _create_record(*args, **kwargs) -> Any: ...
def hashlib_md5(*args, **kwargs) -> Any: ...

class BaseProtocol(CoreProtocol):
    queries_count: Any = ...
    __pyx_vtable__: Any = ...
    def __init__(self, *args, **kwargs): ...
    @classmethod
    def _create_future_fallback(cls, *args, **kwargs): ...
    def _get_timeout(self, *args, **kwargs): ...
    def _on_timeout(self, *args, **kwargs): ...
    def _on_waiter_completed(self, *args, **kwargs): ...
    def _request_cancel(self, *args, **kwargs): ...
    def abort(self, *args, **kwargs): ...
    async def bind(self, *args, **kwargs): ...
    async def bind_execute(self, *args, **kwargs): ...
    async def bind_execute_many(self, *args, **kwargs): ...
    async def close(self, *args, **kwargs): ...
    async def close_statement(self, *args, **kwargs): ...
    async def copy_in(self, *args, **kwargs): ...
    async def copy_out(self, *args, **kwargs): ...
    async def execute(self, *args, **kwargs): ...
    def get_server_pid(self, *args, **kwargs): ...
    def get_settings(self, *args, **kwargs): ...
    def is_closed(self, *args, **kwargs): ...
    def is_connected(self, *args, **kwargs): ...
    def is_in_transaction(self, *args, **kwargs): ...
    def pause_writing(self, *args, **kwargs): ...
    async def prepare(self, *args, **kwargs): ...
    async def query(self, *args, **kwargs): ...
    def resume_writing(self, *args, **kwargs): ...
    def set_connection(self, *args, **kwargs): ...
    def __reduce__(self): ...
    def __setstate__(self, state): ...

class Codec:
    __pyx_vtable__: Any = ...
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

class ConnectionSettings(asyncpg.pgproto.pgproto.CodecContext):
    __pyx_vtable__: Any = ...
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def add_python_codec(self, *args, **kwargs) -> Any: ...
    def clear_type_cache(self, *args, **kwargs) -> Any: ...
    def get_data_codec(self, *args, **kwargs) -> Any: ...
    def get_text_codec(self, *args, **kwargs) -> Any: ...
    def register_data_types(self, *args, **kwargs) -> Any: ...
    def remove_python_codec(self, *args, **kwargs) -> Any: ...
    def set_builtin_type_codec(self, *args, **kwargs) -> Any: ...
    def __getattr__(self, name) -> Any: ...
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

class CoreProtocol:
    backend_pid: Any = ...
    backend_secret: Any = ...
    __pyx_vtable__: Any = ...
    def __init__(self, *args, **kwargs) -> None: ...
    @classmethod
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

class DataCodecConfig:
    __pyx_vtable__: Any = ...
    def __init__(self, *args, **kwargs) -> None: ...
    @classmethod
    def _set_builtin_type_codec(self, *args, **kwargs) -> Any: ...
    def add_python_codec(self, *args, **kwargs) -> Any: ...
    def add_types(self, *args, **kwargs) -> Any: ...
    def clear_type_cache(self, *args, **kwargs) -> Any: ...
    def declare_fallback_codec(self, *args, **kwargs) -> Any: ...
    def remove_python_codec(self, *args, **kwargs) -> Any: ...
    def set_builtin_type_codec(self, *args, **kwargs) -> Any: ...
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

class PreparedStatementState:
    closed: Any = ...
    name: Any = ...
    query: Any = ...
    refs: Any = ...
    __pyx_vtable__: Any = ...
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def _get_attributes(self, *args, **kwargs) -> Any: ...
    def _get_parameters(self, *args, **kwargs) -> Any: ...
    def _init_codecs(self, *args, **kwargs) -> Any: ...
    def _init_types(self, *args, **kwargs) -> Any: ...
    def attach(self, *args, **kwargs) -> Any: ...
    def detach(self, *args, **kwargs) -> Any: ...
    def mark_closed(self, *args, **kwargs) -> Any: ...
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

class Protocol(BaseProtocol, asyncio.protocols.Protocol): ...

_VT = TypeVar('_VT', covariant=True)

class Record(_TEProtocol[_VT]):
    def items(self) -> Iterator[Tuple[str, _VT]]: ...
    def keys(self) -> Iterator[str]: ...
    def values(self) -> Iterator[_VT]: ...
    @overload
    def __getitem__(self, index: int) -> _VT: ...
    @overload
    def __getitem__(self, index: str) -> _VT: ...
    def __iter__(self) -> Iterator[_VT]: ...
    def __contains__(self, x: object) -> bool: ...
    def __len__(self) -> int: ...

class Timer:
    def __init__(self, *args, **kwargs) -> None: ...
    def get_remaining_budget(self, *args, **kwargs) -> Any: ...
    def __enter__(self, *args, **kwargs) -> Any: ...
    def __exit__(self, *args, **kwargs) -> Any: ...
