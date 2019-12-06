import asyncio
import selectors
import ssl
import sys
from socket import _Address, _RetAddress, socket
from typing import (
    IO,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)

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
        self,
    ) -> Optional[
        Callable[
            [asyncio.AbstractEventLoop, Generator[Any, None, _T]], asyncio.Future[_T]
        ]
    ]: ...
    @overload
    def run_until_complete(self, future: Generator[Any, None, _T]) -> _T: ...
    @overload
    def run_until_complete(self, future: Awaitable[_T]) -> _T: ...
    async def getaddrinfo(
        self,
        host: Optional[str],
        port: Union[str, int, None],
        *,
        family: int = ...,
        type: int = ...,
        proto: int = ...,
        flags: int = ...,
    ) -> List[Tuple[int, int, int, str, Tuple[Any, ...]]]: ...
    async def getnameinfo(
        self, sockaddr: Tuple[Any, ...], flags: int = ...
    ) -> Tuple[str, int]: ...
    if sys.version_info >= (3, 7):
        @overload
        async def create_server(
            self,
            protocol_factory: _ProtocolFactory,
            host: Optional[Union[str, Sequence[str]]] = ...,
            port: int = ...,
            *,
            family: int = ...,
            flags: int = ...,
            sock: None = ...,
            backlog: int = ...,
            ssl: _SSLContext = ...,
            reuse_address: Optional[bool] = ...,
            reuse_port: Optional[bool] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
            start_serving: bool = ...,
        ) -> asyncio.AbstractServer: ...
        @overload
        async def create_server(
            self,
            protocol_factory: _ProtocolFactory,
            host: None = ...,
            port: None = ...,
            *,
            family: int = ...,
            flags: int = ...,
            sock: socket = ...,
            backlog: int = ...,
            ssl: _SSLContext = ...,
            reuse_address: Optional[bool] = ...,
            reuse_port: Optional[bool] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
            start_serving: bool = ...,
        ) -> asyncio.AbstractServer: ...
        async def create_unix_connection(
            self,
            protocol_factory: _ProtocolFactory,
            path: str,
            *,
            ssl: _SSLContext = ...,
            sock: Optional[socket] = ...,
            server_hostname: str = ...,
            ssl_handshake_timeout: Optional[float] = ...,
        ) -> _TransProtPair: ...
        async def create_unix_server(
            self,
            protocol_factory: _ProtocolFactory,
            path: str,
            *,
            sock: Optional[socket] = ...,
            backlog: int = ...,
            ssl: _SSLContext = ...,
            ssl_handshake_timeout: Optional[float] = ...,
            start_serving: bool = ...,
        ) -> asyncio.AbstractServer: ...
        async def connect_accepted_socket(
            self,
            protocol_factory: _ProtocolFactory,
            sock: socket,
            *,
            ssl: _SSLContext = ...,
            ssl_handshake_timeout: Optional[float] = ...,
        ) -> _TransProtPair: ...
        async def start_tls(
            self,
            transport: asyncio.BaseTransport,
            protocol: asyncio.BaseProtocol,
            sslcontext: ssl.SSLContext,
            *,
            server_side: bool = ...,
            server_hostname: Optional[str] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
        ) -> asyncio.BaseTransport: ...
    else:
        @overload
        async def create_server(
            self,
            protocol_factory: _ProtocolFactory,
            host: Optional[Union[str, Sequence[str]]] = ...,
            port: int = ...,
            *,
            family: int = ...,
            flags: int = ...,
            sock: None = ...,
            backlog: int = ...,
            ssl: _SSLContext = ...,
            reuse_address: Optional[bool] = ...,
            reuse_port: Optional[bool] = ...,
        ) -> asyncio.AbstractServer: ...
        @overload
        async def create_server(
            self,
            protocol_factory: _ProtocolFactory,
            host: None = ...,
            port: None = ...,
            *,
            family: int = ...,
            flags: int = ...,
            sock: socket,
            backlog: int = ...,
            ssl: _SSLContext = ...,
            reuse_address: Optional[bool] = ...,
            reuse_port: Optional[bool] = ...,
        ) -> asyncio.AbstractServer: ...
        async def create_unix_connection(
            self,
            protocol_factory: _ProtocolFactory,
            path: str,
            *,
            ssl: _SSLContext = ...,
            sock: Optional[socket] = ...,
            server_hostname: str = ...,
        ) -> _TransProtPair: ...
        async def create_unix_server(
            self,
            protocol_factory: _ProtocolFactory,
            path: str,
            *,
            sock: Optional[socket] = ...,
            backlog: int = ...,
            ssl: _SSLContext = ...,
        ) -> asyncio.AbstractServer: ...
        async def connect_accepted_socket(
            self,
            protocol_factory: _ProtocolFactory,
            sock: socket,
            *,
            ssl: _SSLContext = ...,
        ) -> _TransProtPair: ...
    if sys.version_info >= (3, 8):
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: str = ...,
            port: int = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: None = ...,
            local_addr: Optional[str] = ...,
            server_hostname: Optional[str] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
            happy_eyeballs_delay: Optional[float] = ...,
            interleave: Optional[int] = ...,
        ) -> _TransProtPair: ...
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: None = ...,
            port: None = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: socket,
            local_addr: None = ...,
            server_hostname: Optional[str] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
            happy_eyeballs_delay: Optional[float] = ...,
            interleave: Optional[int] = ...,
        ) -> _TransProtPair: ...
    elif sys.version_info >= (3, 7):
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: str = ...,
            port: int = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: None = ...,
            local_addr: Optional[str] = ...,
            server_hostname: Optional[str] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
        ) -> _TransProtPair: ...
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: None = ...,
            port: None = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: socket,
            local_addr: None = ...,
            server_hostname: Optional[str] = ...,
            ssl_handshake_timeout: Optional[float] = ...,
        ) -> _TransProtPair: ...
    else:
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: str = ...,
            port: int = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: None = ...,
            local_addr: Optional[str] = ...,
            server_hostname: Optional[str] = ...,
        ) -> _TransProtPair: ...
        @overload
        async def create_connection(
            self,
            protocol_factory: _ProtocolFactory,
            host: None = ...,
            port: None = ...,
            *,
            ssl: _SSLContext = ...,
            family: int = ...,
            proto: int = ...,
            flags: int = ...,
            sock: socket,
            local_addr: None = ...,
            server_hostname: Optional[str] = ...,
        ) -> _TransProtPair: ...
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
    if sys.version_info >= (3, 7):
        async def sock_recv(self, sock: socket, nbytes: int) -> bytes: ...
        async def sock_recv_into(self, sock: socket, buf: bytearray) -> int: ...
        async def sock_sendall(self, sock: socket, data: bytes) -> None: ...
        async def sock_connect(self, sock: socket, address: _Address) -> None: ...
        async def sock_accept(self, sock: socket) -> Tuple[socket, _RetAddress]: ...
    else:
        def sock_recv(self, sock: socket, nbytes: int) -> asyncio.Future[bytes]: ...
        def sock_sendall(self, sock: socket, data: bytes) -> asyncio.Future[None]: ...
        def sock_connect(
            self, sock: socket, address: _Address
        ) -> asyncio.Future[None]: ...
        def sock_accept(
            self, sock: socket
        ) -> asyncio.Future[Tuple[socket, _RetAddress]]: ...
    async def run_in_executor(
        self, executor: Any, func: Callable[..., _T], *args: Any
    ) -> _T: ...
    def set_default_executor(self, executor: Any) -> None: ...
    async def subprocess_shell(
        self,
        protocol_factory: _ProtocolFactory,
        cmd: Union[bytes, str],
        *,
        stdin: Any = ...,
        stdout: Any = ...,
        stderr: Any = ...,
        **kwargs: Any,
    ) -> _TransProtPair: ...
    async def subprocess_exec(
        self,
        protocol_factory: _ProtocolFactory,
        *args: Any,
        stdin: Any = ...,
        stdout: Any = ...,
        stderr: Any = ...,
        **kwargs: Any,
    ) -> _TransProtPair: ...
    async def connect_read_pipe(
        self, protocol_factory: _ProtocolFactory, pipe: Any
    ) -> _TransProtPair: ...
    async def connect_write_pipe(
        self, protocol_factory: _ProtocolFactory, pipe: Any
    ) -> _TransProtPair: ...
    def add_signal_handler(
        self, sig: int, callback: Callable[..., Any], *args: Any
    ) -> None: ...
    def remove_signal_handler(self, sig: int) -> None: ...
    async def create_datagram_endpoint(
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
    ) -> _TransProtPair: ...
    if sys.version_info >= (3, 6):
        async def shutdown_asyncgens(self) -> None: ...
    if sys.version_info >= (3, 7):
        async def sock_sendfile(
            self,
            sock: socket,
            file: IO[bytes],
            offset: int = ...,
            count: Optional[int] = ...,
            *,
            fallback: bool = ...,
        ) -> int: ...
        async def sendfile(
            self,
            transport: asyncio.BaseTransport,
            file: IO[bytes],
            offset: int = ...,
            count: Optional[int] = ...,
            *,
            fallback: bool = ...,
        ) -> int: ...
