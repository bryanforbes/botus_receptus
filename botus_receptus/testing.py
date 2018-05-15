from typing import Any, AsyncContextManager

import pytest  # type: ignore
from unittest.mock import Mock, MagicMock


class AsyncMixin(object):
    async def __call__(_mock_self: Any, *args: Any, **kwargs: Any) -> Any:
        _mock_self._mock_check_sig(*args, **kwargs)
        return _mock_self._mock_call(*args, **kwargs)


class AsyncMock(AsyncMixin, Mock):
    pass


class AsyncMagicMock(AsyncMixin, MagicMock):
    pass


class AsyncWithMockType(Mock, AsyncContextManager):
    pass


def AsyncWithMock(*args: Any, **kwargs: Any) -> AsyncWithMockType:
    mock = Mock(*args, **kwargs)

    setattr(type(mock), '__aenter__', AsyncMock())
    setattr(type(mock), '__aexit__', AsyncMock(return_value=False))

    return mock


@pytest.fixture(autouse=True)
def add_async_mocks(mocker: Any) -> None:
    mocker.AsyncMock = AsyncMock
    mocker.AsyncMagicMock = AsyncMagicMock
    mocker.AsyncWithMock = AsyncWithMock
