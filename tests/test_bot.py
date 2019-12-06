import discord
import pytest  # type: ignore
from discord.ext import commands

from botus_receptus import Bot, DblBot

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
        return {'bot_name': 'botty', 'discord_api_key': 'API_KEY'}

    @pytest.mark.parametrize(
        'config,prefix',
        [
            ({'bot_name': 'botty'}, '$'),
            ({'bot_name': 'mcbotterson', 'command_prefix': '!'}, '!'),
        ],
    )
    def test_init(self, mocker, config, prefix) -> None:
        mocker.patch('discord.ext.commands.Bot', autospec=True)

        bot = Bot(config)

        assert bot.config == config
        assert bot.bot_name == config['bot_name']
        assert bot.default_prefix == prefix

        assert isinstance(bot, OriginalBot)
        assert bot.session is not None

    @pytest.mark.parametrize('context_cls', [None, MockContext])
    @pytest.mark.asyncio
    async def test_get_context(self, mocker, config, context_cls) -> None:
        get_context = mocker.patch(
            'discord.ext.commands.bot.BotBase.get_context',
            new_callable=mocker.CoroutineMock,
            return_value=mocker.sentinel.RESULT,
        )

        bot = Bot(config)

        result = await bot.get_context(mocker.sentinel.MESSAGE, cls=context_cls)

        get_context.assert_awaited_with(
            mocker.sentinel.MESSAGE,
            cls=context_cls is None and bot.context_cls or context_cls,
        )
        assert result is mocker.sentinel.RESULT

    def test_run_with_config(self, mocker, config) -> None:
        mocker.patch('discord.ext.commands.Bot.run')

        bot = Bot(config)

        bot.run_with_config()
        bot.run.assert_called_once_with('API_KEY')

    @pytest.mark.asyncio
    async def test_close(self, mocker, config) -> None:
        close = mocker.patch(
            'discord.ext.commands.bot.BotBase.close', new_callable=mocker.CoroutineMock
        )

        bot = Bot(config)
        await bot.close()

        close.assert_awaited()
        bot.session.close.assert_awaited()


class MockSession:
    async def post(self, url, *, data=None, **kwargs):
        pass

    async def close(self):
        pass


class TestDblBot(object):
    @pytest.fixture(autouse=True)
    def mock_aiohttp(self, mocker):
        mocker.patch('aiohttp.ClientSession', new=mocker.create_autospec(MockSession))

    @pytest.fixture
    def config(self):
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'dbl_token': 'DBL_TOKEN',
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
    @pytest.mark.asyncio
    async def test_report_guilds(self, method, args, mocker, config) -> None:
        bot = DblBot(config)
        bot._connection = MockConnection()

        await getattr(bot, method)(*args)

        bot.session.post.assert_awaited_with(
            'https://discordbots.org/api/bots/12/stats',
            data='{"server_count": 4}',
            headers={'Content-Type': 'application/json', 'Authorization': 'DBL_TOKEN'},
        )
