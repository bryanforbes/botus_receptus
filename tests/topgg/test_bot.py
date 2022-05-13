from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, Mock, call

import discord
import pytest
from pendulum.duration import Duration

from botus_receptus import Config
from botus_receptus.topgg.bot import AutoShardedBot, Bot

from ..types import MockerFixture


class MockGuild:
    __slots__ = ('id', 'shard_id')

    def __init__(self, id: int) -> None:
        self.id = id
        self.shard_id = id % 2


class MockConnection:
    __slots__ = ('user', 'guilds', 'application_id')

    def __init__(self) -> None:
        self.user = discord.Object(12)
        self.guilds = [
            MockGuild(1),
            MockGuild(2),
            MockGuild(3),
            MockGuild(4),
            MockGuild(5),
        ]
        self.application_id = 1


class MockSession:
    async def post(self, url: str, *, data: Any = None, **kwargs: Any):
        pass

    async def close(self):
        pass


@pytest.fixture(autouse=True)
def mock_aiohttp(mocker: MockerFixture):
    mocker.patch('aiohttp.ClientSession', new=mocker.create_autospec(MockSession))


@pytest.fixture
def mock_task_start(mocker: MockerFixture) -> Mock:
    return mocker.patch('discord.ext.tasks.Loop.start')


@pytest.fixture
def mock_task_cancel(mocker: MockerFixture) -> Mock:
    return mocker.patch('discord.ext.tasks.Loop.cancel')


@pytest.fixture
def mock_in_minutes(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(Duration, 'in_minutes')


class TestTopggBot(object):
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

    async def test_no_token(self, config: Config, mock_task_start: Mock) -> None:
        del config['dbl_token']
        bot = Bot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_not_called()
        cast(AsyncMock, bot.session.post).assert_not_awaited()

    async def test_report_guilds_before_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 15.1
        bot = Bot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast(AsyncMock, bot.session.post).assert_awaited_with(
            'https://top.gg/api/bots/12/stats',
            data='{"server_count":5}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'DBL_TOKEN',
            },
        )

    async def test_report_guilds_within_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 14.9
        bot = Bot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast(AsyncMock, bot.session.post).assert_not_awaited()

    async def test_close(self, config: Config, mock_task_cancel: Mock) -> None:
        bot = Bot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        bot._closed = True
        await bot.close()

        mock_task_cancel.assert_called_once_with()


class TestTopggAutoShardedBot(object):
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

    async def test_no_token(self, config: Config, mock_task_start: Mock) -> None:
        del config['dbl_token']
        bot = AutoShardedBot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_not_called()
        cast(AsyncMock, bot.session.post).assert_not_awaited()

    async def test_report_guilds_before_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 15.1
        bot = AutoShardedBot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast(AsyncMock, bot.session.post).assert_has_awaits(
            [
                call(
                    'https://top.gg/api/bots/12/stats',
                    data='{"shard_id":1,"server_count":3}',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'DBL_TOKEN',
                    },
                ),
                call(
                    'https://top.gg/api/bots/12/stats',
                    data='{"shard_id":0,"server_count":2}',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': 'DBL_TOKEN',
                    },
                ),
            ]
        )
        assert cast(AsyncMock, bot.session.post).await_count == 2

    async def test_report_guilds_within_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 14.9
        bot = AutoShardedBot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast(AsyncMock, bot.session.post).assert_not_awaited()

    async def test_close(self, config: Config, mock_task_cancel: Mock) -> None:
        bot = AutoShardedBot(config, intents=discord.Intents.all())
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()
        bot._closed = True
        await bot.close()

        mock_task_cancel.assert_called_once_with()
