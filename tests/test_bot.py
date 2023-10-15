from __future__ import annotations

from typing import TYPE_CHECKING, cast

import discord
import pytest
from discord.ext import commands

from botus_receptus.bot import Bot

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, MagicMock

    from botus_receptus.config import Config

    from .types import MockerFixture


OriginalBot = commands.Bot


@pytest.fixture(autouse=True)
def http(mocker: MockerFixture) -> MagicMock:
    mock_http: MagicMock = mocker.patch('discord.client.HTTPClient')

    mock_http.return_value = mocker.MagicMock()
    mock_http.return_value.bulk_upsert_global_commands = mocker.AsyncMock()
    mock_http.return_value.bulk_upsert_guild_commands = mocker.AsyncMock()

    return mock_http


@pytest.mark.usefixtures('mock_aiohttp')
class TestBot:
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'intents': discord.Intents.all(),
            'application_id': 1,
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    @pytest.mark.parametrize(
        'config,prefix',
        [
            (
                {
                    'bot_name': 'botty',
                    'intents': discord.Intents.all(),
                    'application_id': 1,
                },
                '$',
            ),
            (
                {
                    'bot_name': 'mcbotterson',
                    'intents': discord.Intents.none(),
                    'command_prefix': '!',
                    'application_id': 1,
                },
                '!',
            ),
        ],
    )
    def test_init(self, mocker: MockerFixture, config: Config, prefix: str) -> None:
        mocker.patch('discord.ext.commands.Bot', autospec=True)

        bot = Bot(config)

        assert bot.config == config
        assert bot.bot_name == config['bot_name']
        assert bot.intents.value == config['intents'].value
        assert bot.default_prefix == prefix

        assert isinstance(bot, OriginalBot)

    async def test_start_with_config(
        self, mocker: MockerFixture, config: Config
    ) -> None:
        start = mocker.patch(
            'discord.ext.commands.Bot.start', new_callable=mocker.AsyncMock
        )

        bot = Bot(config)

        await bot.start_with_config()
        start.assert_awaited_once_with('API_KEY', reconnect=True)

    @pytest.mark.parametrize('reconnect', [True, False])
    async def test_start_with_config_reconnect(
        self, mocker: MockerFixture, config: Config, reconnect: bool
    ) -> None:
        start = mocker.patch(
            'discord.ext.commands.Bot.start', new_callable=mocker.AsyncMock
        )

        bot = Bot(config)

        await bot.start_with_config(reconnect=reconnect)
        start.assert_awaited_once_with('API_KEY', reconnect=reconnect)

    def test_run_with_config(self, mocker: MockerFixture, config: Config) -> None:
        run = mocker.patch('discord.ext.commands.Bot.run')

        bot = Bot(config)

        bot.run_with_config()
        run.assert_called_once_with('API_KEY', log_handler=None)

    async def test_close(self, mocker: MockerFixture, config: Config) -> None:
        close = mocker.patch(
            'discord.ext.commands.bot.BotBase.close', new_callable=mocker.AsyncMock
        )

        bot = Bot(config)
        await bot.setup_hook()
        await bot.close()

        close.assert_awaited()
        cast('AsyncMock', bot.session.close).assert_awaited()
