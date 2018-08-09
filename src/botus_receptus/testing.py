from typing import Any, AsyncContextManager

import pytest  # type: ignore
from unittest.mock import Mock, MagicMock


class AsyncMixin(object):
    async def __call__(_mock_self: Any, *args: Any, **kwargs: Any) -> Any:
        _mock_self._mock_check_sig(*args, **kwargs)
        return _mock_self._mock_call(*args, **kwargs)


class AsyncMock(AsyncMixin, Mock):  # type: ignore
    pass


class AsyncMagicMock(AsyncMixin, MagicMock):  # type: ignore
    pass


class AsyncWithMockType(Mock, AsyncContextManager[AsyncMock]):  # type: ignore
    pass


def AsyncWithMock(*args: Any, **kwargs: Any) -> AsyncWithMockType:
    mock = Mock(*args, **kwargs)

    setattr(type(mock), '__aenter__', AsyncMock())
    setattr(type(mock), '__aexit__', AsyncMock(return_value=False))

    return mock


@pytest.fixture
def mock_response(mocker: Any) -> None:
    response = mocker.AsyncWithMock()
    response.__aenter__.return_value = response

    return response


@pytest.fixture
def mock_client_session(mocker: Any, mock_response: Any) -> None:
    session = mocker.AsyncWithMock()
    session.__aenter__.return_value = session
    session.get = Mock(return_value=mock_response)
    session.post = Mock(return_value=mock_response)

    return session


@pytest.fixture
def MockClientSession(mocker: Any, mock_client_session: Any) -> None:
    ClientSession = mocker.Mock()
    ClientSession.return_value = mock_client_session

    return ClientSession


@pytest.fixture
def mock_aiohttp(mocker: Any, MockClientSession: Any) -> None:
    mocker.patch('aiohttp.ClientSession', MockClientSession)


@pytest.fixture(autouse=True)
def add_async_mocks(mocker: Any) -> None:
    mocker.AsyncMock = AsyncMock
    mocker.AsyncMagicMock = AsyncMagicMock
    mocker.AsyncWithMock = AsyncWithMock
