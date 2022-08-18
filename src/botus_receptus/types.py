from __future__ import annotations

from collections.abc import Callable, Coroutine as _Coroutine
from typing import Any, ParamSpec, TypeAlias, TypeVar

from discord.ext import commands

_T_co = TypeVar('_T_co', covariant=True)
_P = ParamSpec('_P')
_R = TypeVar('_R')

Coroutine: TypeAlias = _Coroutine[Any, Any, _T_co]
CoroutineFunc: TypeAlias = Callable[_P, Coroutine[_R]]
AnyCoroutineFunc: TypeAlias = CoroutineFunc[..., Any]
AnyExtCommand: TypeAlias = commands.Command[Any, ..., Any]
