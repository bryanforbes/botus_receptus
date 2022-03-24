from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock

import discord
import pytest

from botus_receptus import Config
from botus_receptus.topgg.bot import Bot

from ..types import MockerFixture


class MockConnection:
    def __init__(self) -> None:
        self.user = discord.Object(12)
        self.guilds = [1, 2, 3, 4]
        self.application_id = 1


class MockSession:
    async def post(self, url: str, *, data: Any = None, **kwargs: Any):
        pass

    async def close(self):
        pass


class TestTopggBot(object):
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
        bot = Bot(config)
        cast(Any, bot)._connection = MockConnection()
        await bot.setup_hook()

        await getattr(bot, method)(*args)

        cast(AsyncMock, bot.session.post).assert_awaited_with(
            'https://top.gg/api/bots/12/stats',
            data='{"server_count":4}',
            headers={'Content-Type': 'application/json', 'Authorization': 'DBL_TOKEN'},
        )
