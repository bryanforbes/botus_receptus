from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import pytest

from botus_receptus.sqlalchemy.bot import Bot

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, Mock

    from botus_receptus.config import Config

    from ..types import MockerFixture


class TestBotBase:
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'db_url': 'some://db/url',
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    @pytest.fixture
    def mock_close_all_sessions(self, mocker: MockerFixture) -> Mock:
        return mocker.patch('botus_receptus.sqlalchemy.bot.close_all_sessions')

    @pytest.fixture
    def mock_sessionmaker(self, mocker: MockerFixture) -> Mock:
        mock = mocker.Mock()
        mock.configure = mocker.Mock()
        mock.close_all = mocker.Mock()
        return mock

    @pytest.fixture(autouse=True)
    def mock_create_async_engine(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            'botus_receptus.sqlalchemy.bot.create_async_engine',
            return_value=mocker.sentinel.create_async_engine_result,
        )

    @pytest.fixture
    def mock_bot_base_close(self, mocker: MockerFixture) -> AsyncMock:
        return mocker.patch('botus_receptus.bot.BotBase.close')

    def test_init(
        self,
        mocker: MockerFixture,
        config: Config,
        mock_sessionmaker: Mock,
        mock_create_async_engine: Mock,
    ) -> None:
        Bot(config, sessionmaker=mock_sessionmaker)

        mock_sessionmaker.configure.assert_called_once_with(  # type: ignore
            bind=mocker.sentinel.create_async_engine_result
        )
        mock_create_async_engine.assert_called_once_with('some://db/url')

    def test_init_engine_kwargs(
        self,
        mocker: MockerFixture,
        config: Config,
        mock_sessionmaker: Mock,
        mock_create_async_engine: Mock,
    ) -> None:
        Bot(config, sessionmaker=mock_sessionmaker, engine_kwargs={'one': 1, 'two': 2})

        mock_sessionmaker.configure.assert_called_once_with(  # type: ignore
            bind=mocker.sentinel.create_async_engine_result
        )
        mock_create_async_engine.assert_called_once_with('some://db/url', one=1, two=2)

    async def test_close(
        self,
        config: Config,
        mock_sessionmaker: Mock,
        mock_bot_base_close: AsyncMock,
        mock_close_all_sessions: Mock,
    ) -> None:
        bot = Bot(config, sessionmaker=mock_sessionmaker)
        await bot.close()

        mock_close_all_sessions.assert_called_once_with()
        mock_sessionmaker.close_all.assert_not_called()  # type: ignore
        mock_bot_base_close.assert_awaited_once_with()
