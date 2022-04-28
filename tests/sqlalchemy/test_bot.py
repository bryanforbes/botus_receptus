from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import discord
import pytest

from botus_receptus.config import Config
from botus_receptus.sqlalchemy.bot import Bot

from ..types import MockerFixture


class TestBotBase:
    @pytest.fixture
    def config(self) -> Config:
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
    def mock_sessionmaker(self, mocker: MockerFixture) -> Mock:
        mock = mocker.Mock()
        mock.configure = mocker.Mock()
        mock.close_all = mocker.Mock()
        return mock

    @pytest.fixture
    def mock_create_async_engine(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            'botus_receptus.sqlalchemy.bot.create_async_engine',
            return_value=mocker.sentinel.create_async_engine_result,
        )

    @pytest.fixture
    def mock_bot_base_setup_hook(self, mocker: MockerFixture) -> AsyncMock:
        return mocker.patch('botus_receptus.bot.BotBase.setup_hook')

    @pytest.fixture
    def mock_bot_base_close(self, mocker: MockerFixture) -> AsyncMock:
        return mocker.patch('botus_receptus.bot.BotBase.close')

    async def test_setup_hook(
        self,
        mocker: MockerFixture,
        config: Config,
        mock_sessionmaker: Mock,
        mock_create_async_engine: Mock,
        mock_bot_base_setup_hook: AsyncMock,
    ) -> None:
        bot = Bot(config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all())
        await bot.setup_hook()

        mock_sessionmaker.configure.assert_called_once_with(  # type: ignore
            bind=mocker.sentinel.create_async_engine_result
        )
        mock_create_async_engine.assert_called_once_with('some://db/url')
        mock_bot_base_setup_hook.assert_awaited_once_with()

    async def test_close(
        self, config: Config, mock_sessionmaker: Mock, mock_bot_base_close: AsyncMock
    ) -> None:
        bot = Bot(config, sessionmaker=mock_sessionmaker, intents=discord.Intents.all())
        await bot.close()

        mock_sessionmaker.close_all.assert_called_once_with()  # type: ignore
        mock_bot_base_close.assert_awaited_once_with()
