import pytest  # type: ignore
from configparser import ConfigParser
from botus_receptus import Bot, DblBot

import discord
from discord.ext import commands

OriginalBot = commands.Bot


class MockContext(commands.Context):
    pass


class MockConnection:
    def __init__(self):
        self.user = discord.Object(12)
        self.guilds = [1, 2, 3, 4]


@pytest.mark.usefixtures('mock_aiohttp')
class TestBot(object):
    @pytest.fixture
    def config(self):
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY'
        }

    @pytest.fixture
    def config_parser(self, config):
        parser = ConfigParser()
        parser['bot'] = config
        return parser

    @pytest.mark.parametrize('config,prefix', [
        ({'bot_name': 'botty'}, '$'),
        ({'bot_name': 'mcbotterson', 'command_prefix': '!'}, '!')
    ])
    def test_init(self, mocker, config, prefix, config_parser) -> None:
        mocker.patch('discord.ext.commands.Bot', autospec=True)

        bot = Bot(config_parser)

        assert bot.config == config_parser
        assert bot.bot_name == config['bot_name']
        assert bot.default_prefix == prefix

        assert isinstance(bot, OriginalBot)
        assert bot.session is not None

    @pytest.mark.parametrize('context_cls', [
        None,
        MockContext
    ])
    @pytest.mark.asyncio
    async def test_get_context(self, mocker, config_parser, context_cls) -> None:
        get_context = mocker.patch('discord.ext.commands.bot.BotBase.get_context',
                                   new_callable=mocker.CoroutineMock,
                                   return_value=mocker.sentinel.RESULT)

        bot = Bot(config_parser)

        result = await bot.get_context(mocker.sentinel.MESSAGE, cls=context_cls)

        get_context.assert_awaited_with(mocker.sentinel.MESSAGE,
                                        cls=context_cls is None and bot.context_cls or context_cls)
        assert result is mocker.sentinel.RESULT

    def test_run_with_config(self, mocker, config_parser) -> None:
        mocker.patch('discord.ext.commands.Bot.run')

        bot = Bot(config_parser)

        bot.run_with_config()
        bot.run.assert_called_once_with('API_KEY')

    @pytest.mark.asyncio
    async def test_close(self, mocker, config_parser) -> None:
        close = mocker.patch('discord.ext.commands.bot.BotBase.close', new_callable=mocker.CoroutineMock)

        bot = Bot(config_parser)
        await bot.close()

        close.assert_awaited()
        bot.session.close.assert_awaited()


class MockSession:
    async def post(self, url, *, data=None, **kwargs): pass

    async def close(self): pass


class TestDblBot(object):
    @pytest.fixture(autouse=True)
    def mock_aiohttp(self, mocker):
        mocker.patch('aiohttp.ClientSession', new=mocker.create_autospec(MockSession))

    @pytest.fixture
    def config_parser(self):
        parser = ConfigParser()
        parser['bot'] = {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'dbl_token': 'DBL_TOKEN'
        }
        return parser

    @pytest.mark.parametrize('method,args', [
        ('on_ready', []),
        ('on_guild_available', [None]),
        ('on_guild_join', [None]),
        ('on_guild_remove', [None]),
    ])
    @pytest.mark.asyncio
    async def test_report_guilds(self, method, args, mocker, config_parser) -> None:
        bot = DblBot(config_parser)
        bot._connection = MockConnection()

        await getattr(bot, method)(*args)

        bot.session.post.assert_awaited_with('https://discordbots.org/api/bots/12/stats',
                                             data='{"server_count": 4}',
                                             headers={
                                                 'Content-Type': 'application/json',
                                                 'Authorization': 'DBL_TOKEN'
                                             })
