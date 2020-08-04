from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence
from typing_extensions import Protocol
from unittest.mock import (
    ANY,
    DEFAULT,
    MagicMock,
    Mock,
    PropertyMock,
    call,
    mock_open,
    sentinel,
)

if TYPE_CHECKING:
    from unittest.mock import _Call, _patcher


class ClockAdvancer(Protocol):
    async def __call__(self, seconds: float) -> None:
        ...

    def time(self) -> float:
        ...


class CoroutineMock(Mock):
    def assert_awaited(self) -> None:
        ...

    def assert_awaited_once(self, *args: Any, **kwargs: Any) -> None:
        ...

    def assert_awaited_with(self, *args: Any, **kwargs: Any) -> None:
        ...

    def assert_awaited_once_with(self, *args: Any, **kwargs: Any) -> None:
        ...

    def assert_any_await(self, *args: Any, **kwargs: Any) -> None:
        ...

    def assert_has_awaits(self, calls: Sequence[_Call], any_order: bool = ...) -> None:
        ...

    def assert_not_awaited(self) -> None:
        ...


class Mocker:
    patch: _patcher
    Mock = Mock
    MagicMock = MagicMock
    PropertyMock = PropertyMock
    ANY = ANY
    DEFAULT = DEFAULT
    call = call
    sentinel = sentinel
    mock_open = mock_open
    CoroutineMock = CoroutineMock

    def stopall(self) -> None:
        ...

    def resetall(self) -> None:
        ...
