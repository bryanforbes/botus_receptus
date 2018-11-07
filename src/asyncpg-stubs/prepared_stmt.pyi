# Stubs for asyncpg.prepared_stmt (Python 3.6)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from . import connresource
from .cursor import CursorFactory
from .protocol import Record
from .types import Attribute, Type
from typing import Any, Optional, List, Tuple

class PreparedStatement(connresource.ConnectionResource):
    def __init__(self, connection, query, state) -> None: ...
    def get_query(self) -> str: ...
    def get_statusmsg(self) -> str: ...
    def get_parameters(self) -> Tuple[Type, ...]: ...
    def get_attributes(self) -> Tuple[Attribute, ...]: ...
    def cursor(
        self, *args, prefetch: int = ..., timeout: float = ...
    ) -> CursorFactory: ...
    async def explain(self, *args, analyze: bool = ...) -> Any: ...
    async def fetch(self, *args, timeout: float = ...) -> List[Record]: ...
    async def fetchval(
        self, *args, column: int = ..., timeout: float = ...
    ) -> Optional[Any]: ...
    async def fetchrow(self, *args, timeout: float = ...) -> Optional[Record]: ...
    def __del__(self): ...
