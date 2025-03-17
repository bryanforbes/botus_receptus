from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine as _Coroutine
    from types import CoroutineType as _CoroutineType

    from discord.ext import commands

type AnyCallable = Callable[..., Any]
type Coroutine[T] = _Coroutine[Any, Any, T]
type CoroutineType[T] = _CoroutineType[Any, Any, T]
type CoroutineFunc[**P, R] = Callable[P, Coroutine[R]]
type AnyCoroutineFunc = CoroutineFunc[..., Any]
type AnyExtCommand = commands.Command[Any, ..., Any]
