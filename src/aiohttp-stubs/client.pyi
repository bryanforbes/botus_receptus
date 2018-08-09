import asyncio
from typing import (
    Dict, Mapping, Iterable, Callable, Union, AsyncContextManager, Any, Optional, TypeVar, IO, Generator, Coroutine,
    Tuple, overload, Type
)
from types import TracebackType
from .connector import BaseConnector
from .abc import AbstractCookieJar
from .helpers import BasicAuth
from .client_reqrep import ClientResponse, Fingerprint
from yarl import URL
from ssl import SSLContext


_RT = TypeVar('_RT')


class _BaseRequestContextManager(Coroutine[Any, None, _RT], AsyncContextManager[_RT]):
    def send(self, arg: None) -> Any: ...

    def throw(self, typ: Type[BaseException], val: Optional[BaseException] = ...,
              tb: Optional[TracebackType] = ...) -> Any: ...

    def close(self) -> None: ...

    def __await__(self) -> Generator[Any, None, _RT]:
        ...

    def __iter__(self) -> Generator[Any, None, _RT]:
        ...

    async def __aenter__(self) -> Any:
        ...


class _RequestContextManager(_BaseRequestContextManager[_RT]):
    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        ...


class ClientSession:
    def __init__(self, *, connector: BaseConnector = ...,
                 loop: asyncio.AbstractEventLoop = ...,
                 cookies: Dict[str, str] = ...,
                 headers: Mapping[str, str] = ...,
                 skip_auto_headers: Iterable[str] = ...,
                 auth: BasicAuth = ...,
                 version: str = ...,
                 cookie_jar: AbstractCookieJar = ...,
                 json_serialize: Callable[..., str] = ...,
                 raise_for_status: bool = ...,
                 read_timeout: float = ...,
                 conn_timeout: Optional[float] = ...) -> None: ...

    @overload
    def request(self, method: str, url: Union[str, URL], *,
                params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
                data: Optional[Union[Dict[str, Any], bytes, str, IO]] = ...,
                headers: Optional[Mapping[str, str]] = ...,
                skip_auto_headers: Optional[Iterable[str]] = ...,
                auth: Optional[BasicAuth] = ...,
                allow_redirects: bool = ...,
                max_redirects: int = ...,
                compress: Optional[bool] = ...,
                chunked: Optional[int] = ...,
                expect100: bool = ...,
                read_until_eof: bool = ...,
                proxy: Optional[Union[str, URL]] = ...,
                proxy_auth: Optional[BasicAuth] = ...,
                timeout: int = ...,
                ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
                proxy_headers: Optional[Mapping[str, str]] = ...,
                trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    @overload  # noqa: F811
    def request(self, method: str, url: Union[str, URL], *,
                params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
                json: Optional[Any] = ...,
                headers: Optional[Mapping[str, str]] = ...,
                skip_auto_headers: Optional[Iterable[str]] = ...,
                auth: Optional[BasicAuth] = ...,
                allow_redirects: bool = ...,
                max_redirects: int = ...,
                compress: Optional[bool] = ...,
                chunked: Optional[int] = ...,
                expect100: bool = ...,
                read_until_eof: bool = ...,
                proxy: Optional[Union[str, URL]] = ...,
                proxy_auth: Optional[BasicAuth] = ...,
                timeout: int = ...,
                ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
                proxy_headers: Optional[Mapping[str, str]] = ...,
                trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    @overload
    def get(self, url: Union[str, URL], *,
            params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
            data: Optional[Union[Dict[str, Any], bytes, str, IO]] = ...,
            headers: Optional[Mapping[str, str]] = ...,
            skip_auto_headers: Optional[Iterable[str]] = ...,
            auth: Optional[BasicAuth] = ...,
            allow_redirects: bool = ...,
            max_redirects: int = ...,
            compress: Optional[bool] = ...,
            chunked: Optional[int] = ...,
            expect100: bool = ...,
            read_until_eof: bool = ...,
            proxy: Optional[Union[str, URL]] = ...,
            proxy_auth: Optional[BasicAuth] = ...,
            timeout: int = ...,
            ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
            proxy_headers: Optional[Mapping[str, str]] = ...,
            trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    @overload  # noqa: F811
    def get(self, url: Union[str, URL], *,
            params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
            json: Optional[Any] = ...,
            headers: Optional[Mapping[str, str]] = ...,
            skip_auto_headers: Optional[Iterable[str]] = ...,
            auth: Optional[BasicAuth] = ...,
            allow_redirects: bool = ...,
            max_redirects: int = ...,
            compress: Optional[bool] = ...,
            chunked: Optional[int] = ...,
            expect100: bool = ...,
            read_until_eof: bool = ...,
            proxy: Optional[Union[str, URL]] = ...,
            proxy_auth: Optional[BasicAuth] = ...,
            timeout: int = ...,
            ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
            proxy_headers: Optional[Mapping[str, str]] = ...,
            trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    @overload
    def post(self, url: Union[str, URL], *,
             params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
             data: Optional[Union[Dict[str, Any], bytes, str, IO]] = ...,
             headers: Optional[Mapping[str, str]] = ...,
             skip_auto_headers: Optional[Iterable[str]] = ...,
             auth: Optional[BasicAuth] = ...,
             allow_redirects: bool = ...,
             max_redirects: int = ...,
             compress: Optional[bool] = ...,
             chunked: Optional[int] = ...,
             expect100: bool = ...,
             read_until_eof: bool = ...,
             proxy: Optional[Union[str, URL]] = ...,
             proxy_auth: Optional[BasicAuth] = ...,
             timeout: int = ...,
             ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
             proxy_headers: Optional[Mapping[str, str]] = ...,
             trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    @overload  # noqa: F811
    def post(self, url: Union[str, URL], *,
             params: Optional[Union[Mapping[str, str], Iterable[Tuple[str, str]], str]] = ...,
             json: Optional[Any] = ...,
             headers: Optional[Mapping[str, str]] = ...,
             skip_auto_headers: Optional[Iterable[str]] = ...,
             auth: Optional[BasicAuth] = ...,
             allow_redirects: bool = ...,
             max_redirects: int = ...,
             compress: Optional[bool] = ...,
             chunked: Optional[int] = ...,
             expect100: bool = ...,
             read_until_eof: bool = ...,
             proxy: Optional[Union[str, URL]] = ...,
             proxy_auth: Optional[BasicAuth] = ...,
             timeout: int = ...,
             ssl: Optional[Union[bool, Fingerprint, SSLContext]] = ...,
             proxy_headers: Optional[Mapping[str, str]] = ...,
             trace_request_ctx: Optional[Any] = ...) -> _RequestContextManager[ClientResponse]: ...

    async def close(self): ...

    async def __aenter__(self) -> 'ClientSession':
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...
