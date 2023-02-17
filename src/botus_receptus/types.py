from __future__ import annotations

from collections.abc import Callable, Coroutine as _Coroutine
from typing import Any, ParamSpec, TypeAlias
from typing_extensions import TypeVar

from discord.ext import commands

_T = TypeVar('_T', infer_variance=True)
_P = ParamSpec('_P')
_R = TypeVar('_R', infer_variance=True)

Coroutine: TypeAlias = _Coroutine[Any, Any, _T]
CoroutineFunc: TypeAlias = Callable[_P, Coroutine[_R]]
AnyCoroutineFunc: TypeAlias = CoroutineFunc[..., Any]
AnyExtCommand: TypeAlias = commands.Command[Any, ..., Any]
