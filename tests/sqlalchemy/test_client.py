from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import pytest

import botus_receptus.client
from botus_receptus.sqlalchemy.client import AutoShardedClient, Client

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, Mock

    from botus_receptus.config import Config

    from ..types import MockerFixture


@pytest.fixture
def config() -> Config:
    return {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'db_url': 'some://db/url',
        'logging': {
            'log_file': '',
            'log_level': '',
            'log_to_console': False,
        },
    }


@pytest.fixture
def mock_sessionmaker(mocker: MockerFixture) -> Mock:
    mock = mocker.Mock()
    mock.configure = mocker.Mock()
    mock.close_all = mocker.Mock()
    return mock


class TestClient:
    @pytest.fixture
    def mock_create_async_engine(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            'botus_receptus.sqlalchemy.client.create_async_engine',
            return_value=mocker.sentinel.create_async_engine_result,
        )

    @pytest.fixture
    def mock_client_close(self, mocker: MockerFixture) -> AsyncMock:
        return mocker.patch('botus_receptus.client.Client.close')

    def test_init(self, config: Config, mock_sessionmaker: Mock) -> None:
        client = Client(
            config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all()
        )

        assert client.config == config
        assert client.intents.value == discord.Intents.all().value

        assert isinstance(client, Client)
        assert isinstance(client, botus_receptus.client.Client)
        assert isinstance(client, discord.Client)

    async def test_setup_hook(
        self,
        mocker: MockerFixture,
        config: Config,
        mock_sessionmaker: Mock,
        mock_create_async_engine: Mock,
    ) -> None:
        setup_hook = mocker.patch(
            'botus_receptus.client.Client.setup_hook', new_callable=mocker.AsyncMock
        )
        client = Client(
            config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all()
        )
        await client.setup_hook()

        mock_sessionmaker.configure.assert_called_once_with(  # type: ignore
            bind=mocker.sentinel.create_async_engine_result
        )
        mock_create_async_engine.assert_called_once_with('some://db/url')
        setup_hook.assert_awaited_once_with()

    async def test_close(
        self,
        mocker: MockerFixture,
        config: Config,
        mock_sessionmaker: Mock,
    ) -> None:
        close = mocker.patch(
            'botus_receptus.client.Client.close', new_callable=mocker.AsyncMock
        )
        client = Client(
            config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all()
        )
        await client.close()

        mock_sessionmaker.close_all.assert_called_once_with()  # type: ignore
        close.assert_awaited_once_with()


class TestAutoShardedClient:
    def test_init(self, config: Config, mock_sessionmaker: Mock) -> None:
        client = AutoShardedClient(
            config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all()
        )

        assert client.config == config
        assert client.intents.value == discord.Intents.all().value

        assert isinstance(client, AutoShardedClient)
        assert isinstance(client, discord.AutoShardedClient)
        assert isinstance(client, Client)
        assert isinstance(client, botus_receptus.client.Client)
        assert isinstance(client, discord.Client)
