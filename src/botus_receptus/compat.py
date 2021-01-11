from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import Final as Final
    from typing import Literal as Literal
    from typing import Protocol as Protocol
    from typing import TypedDict as TypedDict
else:
    from typing_extensions import Final as Final  # noqa: F401
    from typing_extensions import Literal as Literal  # noqa: F401
    from typing_extensions import Protocol as Protocol  # noqa: F401
    from typing_extensions import TypedDict as TypedDict  # noqa: F401

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterable as AsyncIterable
    from collections.abc import Awaitable as Awaitable
    from collections.abc import Callable as Callable
    from collections.abc import Container as Container
    from collections.abc import Coroutine as Coroutine
    from collections.abc import Generator as Generator
    from collections.abc import Iterable as Iterable
    from collections.abc import Iterator as Iterator
    from collections.abc import Mapping as Mapping
    from collections.abc import Sequence as Sequence
    from contextlib import AbstractAsyncContextManager as AbstractAsyncContextManager
    from re import Pattern as Pattern
else:
    from typing import AsyncContextManager as AbstractAsyncContextManager  # noqa: F401
    from typing import AsyncIterable as AsyncIterable  # noqa: F401
    from typing import Awaitable as Awaitable  # noqa: F401
    from typing import Callable as Callable  # noqa: F401
    from typing import Container as Container  # noqa: F401
    from typing import Coroutine as Coroutine  # noqa: F401
    from typing import Generator as Generator  # noqa: F401
    from typing import Iterable as Iterable  # noqa: F401
    from typing import Iterator as Iterator  # noqa: F401
    from typing import Mapping as Mapping  # noqa: F401
    from typing import Pattern as Pattern  # noqa: F401
    from typing import Sequence as Sequence  # noqa: F401
