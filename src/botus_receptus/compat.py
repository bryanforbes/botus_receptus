from __future__ import annotations

import sys
from typing import Final

if sys.version_info >= (3, 9):
    from builtins import dict, list, tuple, type
    from collections.abc import (
        AsyncIterable,
        Awaitable,
        Callable,
        Container,
        Coroutine,
        Generator,
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )
    from contextlib import AbstractAsyncContextManager
    from re import Pattern
else:
    from typing import (
        AsyncContextManager as AbstractAsyncContextManager,
        AsyncIterable,
        Awaitable,
        Callable,
        Container,
        Coroutine,
        Dict as dict,
        Generator,
        Iterable,
        Iterator,
        List as list,
        Mapping,
        Pattern,
        Sequence,
        Tuple as tuple,
        Type as type,
    )

__all__: Final = (
    'AbstractAsyncContextManager',
    'AsyncIterable',
    'Awaitable',
    'Callable',
    'Container',
    'Coroutine',
    'Generator',
    'Iterable',
    'Iterator',
    'Mapping',
    'Pattern',
    'Sequence',
    'dict',
    'list',
    'tuple',
    'type',
)
