import pytest
import aiohttp
from botus_receptus.testing import AsyncMock, AsyncMagicMock, AsyncWithMock


@pytest.mark.asyncio
async def test_mocker_additions(mocker):
    assert mocker.AsyncMock is AsyncMock
    assert mocker.AsyncMagicMock is AsyncMagicMock
    assert mocker.AsyncWithMock is AsyncWithMock

    asyncMock = mocker.AsyncMock(return_value=True)
    assert await asyncMock()

    asyncMagicMock = mocker.AsyncMagicMock(return_value=1)
    assert await asyncMagicMock() == 1

    asyncWithMock = mocker.AsyncWithMock()
    asyncWithMock.__aenter__.return_value = 'foo bar baz'

    async with asyncWithMock as result:
        assert result == 'foo bar baz'


@pytest.mark.asyncio
async def test_mock_response(mock_response):
    assert mock_response is not None
    assert hasattr(mock_response, '__aenter__')

    async with mock_response as response:
        assert mock_response is response


@pytest.mark.asyncio
async def test_mock_client_session(mock_response, mock_client_session):
    assert hasattr(mock_client_session, '__aenter__')
    assert hasattr(mock_client_session, 'get')
    assert hasattr(mock_client_session, 'post')

    async with mock_client_session as session:
        assert session is mock_client_session
    async with mock_client_session.get() as resp:
        assert resp is mock_response
    async with mock_client_session.post() as resp:
        assert resp is mock_response


def test_MockClientSession(MockClientSession, mock_client_session):
    assert MockClientSession() is mock_client_session


@pytest.mark.usefixtures('mock_aiohttp')
def test_mock_aiohttp(MockClientSession):
    assert aiohttp.ClientSession is MockClientSession
