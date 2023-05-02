from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import discord
import pytest
from attrs import define, field
from pendulum.duration import Duration

from botus_receptus.topgg.bot import AutoShardedBot, Bot

if TYPE_CHECKING:
    from unittest.mock import AsyncMock, Mock

    from botus_receptus import Config

    from ..types import MockerFixture


@define
class MockGuild:
    id: int
    shard_id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.shard_id = self.id % 2


@define
class MockConnection:
    user: discord.Object = field(init=False)
    guilds: list[MockGuild] = field(init=False)
    application_id: int = field(init=False)

    def __attrs_post_init__(self) -> None:
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
    async def post(self, url: str, *, data: Any = None, **kwargs: Any) -> None:
        pass

    async def close(self) -> None:
        pass


@pytest.fixture(autouse=True)
def mock_aiohttp(mocker: MockerFixture) -> None:
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


class TestTopggBot:
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'dbl_token': 'DBL_TOKEN',
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    async def test_no_token(self, config: Config, mock_task_start: Mock) -> None:
        del config['dbl_token']
        bot = Bot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_not_called()
        cast('AsyncMock', bot.session.post).assert_not_awaited()

    async def test_report_guilds_before_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 15.1
        bot = Bot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast('AsyncMock', bot.session.post).assert_awaited_with(
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
        bot = Bot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast('AsyncMock', bot.session.post).assert_not_awaited()

    async def test_close(self, config: Config, mock_task_cancel: Mock) -> None:
        bot = Bot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        bot._closed = True
        await bot.close()

        mock_task_cancel.assert_called_once_with()


class TestTopggAutoShardedBot:
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'dbl_token': 'DBL_TOKEN',
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    async def test_no_token(self, config: Config, mock_task_start: Mock) -> None:
        del config['dbl_token']
        bot = AutoShardedBot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_not_called()
        cast('AsyncMock', bot.session.post).assert_not_awaited()

    async def test_report_guilds_before_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 15.1
        bot = AutoShardedBot(config)
        cast('Any', bot)._connection = MockConnection()
        bot.shard_count = 2
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast('AsyncMock', bot.session.post).assert_awaited_once_with(
            'https://top.gg/api/bots/12/stats',
            data='{"server_count":5,"shard_count":2}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'DBL_TOKEN',
            },
        )

    async def test_report_guilds_within_15_minutes(
        self, config: Config, mock_in_minutes: Mock, mock_task_start: Mock
    ) -> None:
        mock_in_minutes.return_value = 14.9
        bot = AutoShardedBot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        await bot.on_ready()

        mock_task_start.assert_called_once_with(config.get('dbl_token'))
        cast('AsyncMock', bot.session.post).assert_not_awaited()

    async def test_close(self, config: Config, mock_task_cancel: Mock) -> None:
        bot = AutoShardedBot(config)
        cast('Any', bot)._connection = MockConnection()
        await bot.setup_hook()
        bot._closed = True
        await bot.close()

        mock_task_cancel.assert_called_once_with()
