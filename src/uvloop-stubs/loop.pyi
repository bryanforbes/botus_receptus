from typing import (
    Any,
    Optional,
    Union,
    Callable,
    Awaitable,
    Generator,
    TypeVar,
    List,
    Tuple,
    Sequence,
    Dict,
    overload,
)
import asyncio
import ssl
from socket import socket
import selectors

_T = TypeVar('_T')
_Context = Dict[str, Any]
_ExceptionHandler = Callable[[asyncio.AbstractEventLoop, _Context], Any]
_ProtocolFactory = Callable[[], asyncio.BaseProtocol]
_SSLContext = Union[bool, None, ssl.SSLContext]
_TransProtPair = Tuple[asyncio.BaseTransport, asyncio.BaseProtocol]

class Loop:
    def call_soon(self, callback: Callable[..., Any], *args: Any) -> asyncio.Handle: ...
    def call_soon_threadsafe(
        self, callback: Callable[..., Any], *args: Any
    ) -> asyncio.Handle: ...
    def call_later(
        self, delay: float, callback: Callable[..., Any], *args: Any
    ) -> asyncio.TimerHandle: ...
    def call_at(
        self, when: float, callback: Callable[..., Any], *args: Any
    ) -> asyncio.TimerHandle: ...
    def time(self) -> float: ...
    def stop(self) -> None: ...
    def run_forever(self) -> None: ...
    def close(self) -> None: ...
    def get_debug(self) -> bool: ...
    def set_debug(self, enabled: bool) -> None: ...
    def is_running(self) -> bool: ...
    def is_closed(self) -> bool: ...
    def create_future(self) -> asyncio.Future[Any]: ...
    def create_task(
        self, coro: Union[Awaitable[_T], Generator[Any, None, _T]]
    ) -> asyncio.Task[_T]: ...
    def set_task_factory(
        self,
        factory: Optional[
            Callable[
                [asyncio.AbstractEventLoop, Generator[Any, None, _T]],
                asyncio.Future[_T],
            ]
        ],
    ) -> None: ...
    def get_task_factory(
        self
    ) -> Optional[
        Callable[
            [asyncio.AbstractEventLoop, Generator[Any, None, _T]], asyncio.Future[_T]
        ]
    ]: ...
    @overload
    def run_until_complete(self, future: Generator[Any, None, _T]) -> _T: ...
    @overload
    def run_until_complete(self, future: Awaitable[_T]) -> _T: ...
    @asyncio.coroutine
    def getaddrinfo(
        self,
        host: Optional[str],
        port: Union[str, int, None],
        *,
        family: int = ...,
        type: int = ...,
        proto: int = ...,
        flags: int = ...,
    ) -> Generator[Any, None, List[Tuple[int, int, int, str, Tuple[Any, ...]]]]: ...
    @asyncio.coroutine
    def getnameinfo(
        self, sockaddr: tuple, flags: int = ...
    ) -> Generator[Any, None, Tuple[str, int]]: ...
    @asyncio.coroutine
    def create_server(
        self,
        protocol_factory: _ProtocolFactory,
        host: Union[str, Sequence[str]] = ...,
        port: int = ...,
        *,
        family: int = ...,
        flags: int = ...,
        sock: Optional[socket] = ...,
        backlog: int = ...,
        ssl: _SSLContext = ...,
        reuse_address: Optional[bool] = ...,
        reuse_port: Optional[bool] = ...,
    ) -> Generator[Any, None, asyncio.AbstractServer]: ...
    @asyncio.coroutine
    def create_connection(
        self,
        protocol_factory: _ProtocolFactory,
        host: str = ...,
        port: int = ...,
        *,
        ssl: _SSLContext = ...,
        family: int = ...,
        proto: int = ...,
        flags: int = ...,
        sock: Optional[socket] = ...,
        local_addr: str = ...,
        server_hostname: str = ...,
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def create_unix_server(
        self,
        protocol_factory: _ProtocolFactory,
        path: str,
        *,
        sock: Optional[socket] = ...,
        backlog: int = ...,
        ssl: _SSLContext = ...,
    ) -> Generator[Any, None, asyncio.AbstractServer]: ...
    @asyncio.coroutine
    def create_unix_connection(
        self,
        protocol_factory: _ProtocolFactory,
        path: str,
        *,
        ssl: _SSLContext = ...,
        sock: Optional[socket] = ...,
        server_hostname: str = ...,
    ) -> Generator[Any, None, _TransProtPair]: ...
    def default_exception_handler(self, context: _Context) -> None: ...
    def get_exception_handler(self) -> Optional[_ExceptionHandler]: ...
    def set_exception_handler(self, handler: Optional[_ExceptionHandler]) -> None: ...
    def call_exception_handler(self, context: _Context) -> None: ...
    def add_reader(
        self, fd: selectors._FileObject, callback: Callable[..., Any], *args: Any
    ) -> None: ...
    def remove_reader(self, fd: selectors._FileObject) -> None: ...
    def add_writer(
        self, fd: selectors._FileObject, callback: Callable[..., Any], *args: Any
    ) -> None: ...
    def remove_writer(self, fd: selectors._FileObject) -> None: ...
    @asyncio.coroutine
    def sock_recv(self, sock: socket, nbytes: int) -> Generator[Any, None, bytes]: ...
    @asyncio.coroutine
    def sock_sendall(self, sock: socket, data: bytes) -> Generator[Any, None, None]: ...
    @asyncio.coroutine
    def sock_accept(self, sock: socket) -> Generator[Any, None, Tuple[socket, Any]]: ...
    @asyncio.coroutine
    def sock_connect(
        self, sock: socket, address: str
    ) -> Generator[Any, None, None]: ...
    @asyncio.coroutine
    def connect_accepted_socket(
        self,
        protocol_factory: _ProtocolFactory,
        sock: socket,
        *,
        ssl: _SSLContext = ...,
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def run_in_executor(
        self, executor: Any, func: Callable[..., _T], *args: Any
    ) -> Generator[Any, None, _T]: ...
    def set_default_executor(self, executor: Any) -> None: ...
    @asyncio.coroutine
    def subprocess_shell(
        self,
        protocol_factory: _ProtocolFactory,
        cmd: Union[bytes, str],
        *,
        stdin: Any = ...,
        stdout: Any = ...,
        stderr: Any = ...,
        **kwargs: Any,
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def subprocess_exec(
        self,
        protocol_factory: _ProtocolFactory,
        *args: Any,
        stdin: Any = ...,
        stdout: Any = ...,
        stderr: Any = ...,
        **kwargs: Any,
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def connect_read_pipe(
        self, protocol_factory: _ProtocolFactory, pipe: Any
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def connect_write_pipe(
        self, protocol_factory: _ProtocolFactory, pipe: Any
    ) -> Generator[Any, None, _TransProtPair]: ...
    def add_signal_handler(
        self, sig: int, callback: Callable[..., Any], *args: Any
    ) -> None: ...
    def remove_signal_handler(self, sig: int) -> None: ...
    @asyncio.coroutine
    def create_datagram_endpoint(
        self,
        protocol_factory: _ProtocolFactory,
        local_addr: Optional[Tuple[str, int]] = ...,
        remote_addr: Optional[Tuple[str, int]] = ...,
        *,
        family: int = ...,
        proto: int = ...,
        flags: int = ...,
        reuse_address: Optional[bool] = ...,
        reuse_port: Optional[bool] = ...,
        allow_broadcast: Optional[bool] = ...,
        sock: Optional[socket] = ...,
    ) -> Generator[Any, None, _TransProtPair]: ...
    @asyncio.coroutine
    def shutdown_asyncgens(self) -> Generator[Any, None, None]: ...
