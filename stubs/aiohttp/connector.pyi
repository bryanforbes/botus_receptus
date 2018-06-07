from typing import Optional
import asyncio


class BaseConnector(object):
    def __init__(self, *, keepalive_timeout: Optional[int] = ...,
                 force_close: bool = ..., limit: int = ...,
                 limit_per_host: int = ..., enable_cleanup_closed: bool = ...,
                 loop: Optional[asyncio.AbstractEventLoop] = ...) -> None: ...

    def __del__(self) -> None: ...

    @property
    def loop(self) -> asyncio.AbstractEventLoop: ...


class TCPConnector(BaseConnector):
    def __init__(self, *, verify_ssl: Optional[bool] = ..., fingerprint: Optional[str] = ...,
                 use_dns_cache: bool = ..., ttl_dns_cache: Optional[int] = ...,
                 keepalive_timeout: Optional[int] = ...,
                 force_close: bool = ..., limit: int = ...,
                 limit_per_host: int = ..., enable_cleanup_closed: bool = ...,
                 loop: Optional[asyncio.AbstractEventLoop] = ...) -> None: ...
