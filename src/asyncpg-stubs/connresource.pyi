from typing import Any, TypeArg, Generic, Callable
from .connection import Connection

_F = TypeArg('_F', bound=Callable[..., Any])

def guarded(meth: _F) -> _F: ...

_C = TypeArg('_C', bound=Connection)

class ConnectionResource(Generic[_C]):
    def __init__(self, connection: _C) -> None: ...
