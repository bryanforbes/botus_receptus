from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord.ext import commands

from botus_receptus import Bot, DblBot
from botus_receptus.compat import list
from botus_receptus.config import Config

from .types import MockerFixture

OriginalBot = commands.Bot


class MockContext(commands.Context[Any]):
    pass


class MockConnection:
    def __init__(self) -> None:
        self.user = discord.Object(12)
        self.guilds = [1, 2, 3, 4]
        self.application_id = 1


class MockHTTPClient:
    def __init__(self, mocker: MockerFixture) -> None:
        self.bulk_upsert_global_commands = mocker.AsyncMock()
        self.bulk_upsert_guild_commands = mocker.AsyncMock()


@pytest.fixture(autouse=True)
def http(mocker: MockerFixture) -> MagicMock:
    mock_http: MagicMock = mocker.patch('discord.client.HTTPClient')

    mock_http.return_value = mocker.MagicMock()
    mock_http.return_value.bulk_upsert_global_commands = mocker.AsyncMock()
    mock_http.return_value.bulk_upsert_guild_commands = mocker.AsyncMock()

    return mock_http


@pytest.mark.usefixtures('mock_aiohttp')
class TestBot(object):
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
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
            ({'bot_name': 'botty', 'application_id': 1}, '$'),
            (
                {'bot_name': 'mcbotterson', 'command_prefix': '!', 'application_id': 1},
                '!',
            ),
        ],
    )
    def test_init(self, mocker: MockerFixture, config: Config, prefix: str) -> None:
        mocker.patch('discord.ext.commands.Bot', autospec=True)

        bot = Bot(config)

        assert bot.config == config
        assert bot.bot_name == config['bot_name']
        assert bot.default_prefix == prefix

        assert isinstance(bot, OriginalBot)

    def test_run_with_config(self, mocker: MockerFixture, config: Config) -> None:
        run = mocker.patch('discord.ext.commands.Bot.run')

        bot = Bot(config)

        bot.run_with_config()
        run.assert_called_once_with('API_KEY')

    async def test_close(self, mocker: MockerFixture, config: Config) -> None:
        close = mocker.patch(
            'discord.ext.commands.bot.BotBase.close', new_callable=mocker.AsyncMock
        )

        bot = Bot(config)
        await bot.setup_hook()
        await bot.close()

        close.assert_awaited()
        cast(AsyncMock, bot.session.close).assert_awaited()


class MockSession:
    async def post(self, url: str, *, data: Any = None, **kwargs: Any):
        pass

    async def close(self):
        pass


class TestDblBot(object):
    @pytest.fixture(autouse=True)
    def mock_aiohttp(self, mocker: MockerFixture):
        mocker.patch('aiohttp.ClientSession', new=mocker.create_autospec(MockSession))

    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'dbl_token': 'DBL_TOKEN',
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    @pytest.mark.parametrize(
        'method,args',
        [
            ('on_ready', []),
            ('on_guild_available', [None]),
            ('on_guild_join', [None]),
            ('on_guild_remove', [None]),
        ],
    )
    async def test_report_guilds(
        self, method: str, args: list[Any], config: Config
    ) -> None:
        bot = DblBot(config)
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()

        await getattr(bot, method)(*args)

        cast(AsyncMock, bot.session.post).assert_awaited_with(
            'https://discordbots.org/api/bots/12/stats',
            data='{"server_count": 4}',
            headers={'Content-Type': 'application/json', 'Authorization': 'DBL_TOKEN'},
        )
