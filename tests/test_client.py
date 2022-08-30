from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import call

import discord
import pytest

from botus_receptus.app_commands import CommandTree
from botus_receptus.client import AutoShardedClient, Client
from botus_receptus.exceptions import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError,
)

from . import client as _client_module

if TYPE_CHECKING:
    from collections.abc import Iterable
    from unittest.mock import AsyncMock

    from botus_receptus.config import Config

    from .types import MockerFixture

OriginalClient = discord.Client
OriginalAutoShardedClient = discord.AutoShardedClient


class MyCommandTree(CommandTree[Any]):
    ...


@pytest.fixture(autouse=True)
def cleanup_modules() -> Iterable[None]:
    yield

    for module in list(sys.modules.keys()):
        if module.startswith('tests.client.'):
            del sys.modules[module]


@pytest.mark.usefixtures('mock_aiohttp')
class TestClient:
    @pytest.fixture
    def config(self) -> Config:
        return {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'intents': discord.Intents(guilds=True),
            'application_id': 1,
            'logging': {
                'log_file': '',
                'log_level': '',
                'log_to_console': False,
            },
        }

    @pytest.fixture
    def botus_tests(self, tmp_path: Path) -> Iterable[Path]:
        botus_tests = tmp_path / 'botus_tests'
        botus_tests.mkdir()

        sys.path.append(str(tmp_path))

        yield botus_tests

        sys.path.remove(str(tmp_path))
        shutil.rmtree(botus_tests)

    @pytest.mark.parametrize(
        'config,tree_cls',
        [
            (
                {
                    'bot_name': 'botty',
                    'intents': discord.Intents.all(),
                    'application_id': 1,
                },
                None,
            ),
            (
                {
                    'bot_name': 'mcbotterson',
                    'intents': discord.Intents.none(),
                    'application_id': 2,
                },
                MyCommandTree,
            ),
        ],
    )
    def test_init(self, config: Config, tree_cls: type[Any] | None) -> None:
        kwargs: dict[str, Any] = {}

        if tree_cls is not None:
            kwargs['tree_cls'] = tree_cls

        client = Client(config, **kwargs)

        assert client.config == config
        assert client.bot_name == config['bot_name']
        assert client.application_id == config['application_id']
        assert client.intents.value == config['intents'].value

        assert isinstance(client, Client)
        assert isinstance(client, OriginalClient)
        assert isinstance(client.tree, CommandTree)
        if tree_cls is not None:
            assert isinstance(client.tree, tree_cls)
        assert not hasattr(client, 'session')
        assert client.extensions == {}

    def test_run_with_config(self, mocker: MockerFixture, config: Config) -> None:
        run = mocker.patch('discord.Client.run')

        client = Client(config)

        client.run_with_config()
        run.assert_called_once_with('API_KEY', log_handler=None)

    @pytest.mark.parametrize(
        'config,calls',
        [
            (
                {
                    'bot_name': 'botty',
                    'intents': discord.Intents.all(),
                    'application_id': 1,
                },
                [call()],
            ),
            (
                {
                    'bot_name': 'mcbotterson',
                    'intents': discord.Intents.all(),
                    'application_id': 2,
                    'test_guilds': [1234, 5678],
                },
                [
                    call(guild=discord.Object(id=1234)),
                    call(guild=discord.Object(id=5678)),
                    call(),
                ],
            ),
            (
                {
                    'bot_name': 'mcbotterson',
                    'intents': discord.Intents.all(),
                    'application_id': 2,
                    'admin_guild': 91011,
                },
                [
                    call(guild=discord.Object(id=91011)),
                    call(),
                ],
            ),
            (
                {
                    'bot_name': 'mcbotterson',
                    'intents': discord.Intents.all(),
                    'application_id': 2,
                    'test_guilds': [1234, 5678],
                    'admin_guild': 91011,
                },
                [
                    call(guild=discord.Object(id=1234)),
                    call(guild=discord.Object(id=5678)),
                    call(guild=discord.Object(id=91011)),
                    call(),
                ],
            ),
        ],
    )
    async def test_sync_app_commands(
        self, mocker: MockerFixture, config: Config, calls: Any
    ) -> None:
        sync = mocker.patch(
            'botus_receptus.client.CommandTree.sync', new_callable=mocker.AsyncMock
        )

        client = Client(config)
        await client.sync_app_commands()

        sync.assert_has_awaits(calls)

    async def test_close(self, mocker: MockerFixture, config: Config) -> None:
        close = mocker.patch('discord.Client.close', new_callable=mocker.AsyncMock)

        client = Client(config)
        await client.setup_hook()
        await client.close()

        close.assert_awaited()
        cast('AsyncMock', client.session.close).assert_awaited()

    async def test_load_extension(self, mocker: MockerFixture, config: Config) -> None:
        client = Client(config)

        client.module_1_setup = False  # pyright: ignore
        client.module_2_setup = False  # pyright: ignore

        await client.load_extension('tests.client.module_1')

        assert 'tests.client.module_1' in sys.modules
        assert client.module_1_setup  # pyright: ignore

        await client.load_extension('.module_2', package=_client_module.__spec__.parent)

        assert 'tests.client.module_2' in sys.modules
        assert client.module_2_setup  # pyright: ignore

        with pytest.raises(ExtensionAlreadyLoaded):
            await client.load_extension('tests.client.module_1')
        assert 'tests.client.module_1' in sys.modules

        with pytest.raises(ExtensionNotFound):
            await client.load_extension('tests.client.not_found')

        assert 'tests.client.not_found' not in sys.modules

        with pytest.raises(ExtensionNotFound):
            await client.load_extension(
                '.also_not_found', package=_client_module.__spec__.parent
            )

        assert 'tests.client.also_not_found' not in sys.modules

        with pytest.raises(ExtensionNotFound):
            await client.load_extension(
                '...also_not_found', package=_client_module.__spec__.parent
            )

        remove = mocker.patch(
            'botus_receptus.app_commands.CommandTree._remove_with_module'
        )

        with pytest.raises(ExtensionFailed):
            await client.load_extension('tests.client.module_with_error')

        assert 'tests.client.module_with_error' not in sys.modules
        remove.assert_not_called()

        with pytest.raises(NoEntryPointError):
            await client.load_extension('tests.client.module_without_setup')

        assert 'tests.client.module_without_setup' not in sys.modules

        client.setup_raises_torn_down = False  # pyright: ignore
        with pytest.raises(ExtensionFailed):
            await client.load_extension('tests.client.setup_raises')

        assert 'tests.client.setup_raises' not in sys.modules
        assert not client.setup_raises_torn_down  # pyright: ignore
        remove.assert_called_once_with('tests.client.setup_raises')

        remove.reset_mock()
        with pytest.raises(ExtensionFailed):
            await client.load_extension('tests.client.setup_raises_with_teardown')

        assert 'tests.client.setup_raises_with_teardown' not in sys.modules
        assert client.setup_raises_torn_down  # pyright: ignore
        remove.assert_called_once_with('tests.client.setup_raises_with_teardown')

    async def test_unload_extension(
        self, mocker: MockerFixture, config: Config
    ) -> None:
        client = Client(config)

        client.module_2_torn_down = False  # pyright: ignore
        remove = mocker.patch(
            'botus_receptus.app_commands.CommandTree._remove_with_module'
        )

        await client.load_extension('tests.client.module_2')

        assert not client.module_2_torn_down  # pyright: ignore
        remove.assert_not_called()

        await client.unload_extension('tests.client.module_2')

        assert client.module_2_torn_down  # pyright: ignore
        remove.assert_called_once_with('tests.client.module_2')

        with pytest.raises(ExtensionNotLoaded):
            await client.unload_extension('tests.client.module_1')

        await client.load_extension('tests.client.things')
        await client.unload_extension('tests.client.things')

        assert 'tests.client.things.one' not in sys.modules
        assert 'tests.client.things' not in sys.modules

    async def test_reload_extension(
        self, mocker: MockerFixture, config: Config, botus_tests: Path
    ) -> None:
        client = Client(config)

        remove = mocker.patch(
            'botus_receptus.app_commands.CommandTree._remove_with_module'
        )

        await client.load_extension('tests.client.module_2')

        assert client.module_2_setup  # pyright: ignore
        remove.assert_not_called()

        client.module_2_setup = False  # pyright: ignore
        client.module_2_torn_down = False  # pyright: ignore

        await client.reload_extension('tests.client.module_2')

        assert client.module_2_setup  # pyright: ignore
        assert client.module_2_torn_down  # pyright: ignore
        remove.assert_called_once_with('tests.client.module_2')

        with pytest.raises(ExtensionNotLoaded):
            await client.reload_extension('tests.client.module_1')

        remove.reset_mock()

        client.module_3_setup_1 = False  # pyright: ignore
        client.module_3_torn_down_1 = False  # pyright: ignore
        client.module_3_setup_2 = False  # pyright: ignore
        client.module_3_torn_down_2 = False  # pyright: ignore
        client.module_3_setup_3 = False  # pyright: ignore

        (botus_tests / '__init__.py').touch()
        (botus_tests / 'module_3.py').symlink_to(
            Path(__file__).parent.absolute() / 'client' / 'module_3.py'
        )
        await client.load_extension('botus_tests.module_3')

        assert client.module_3_setup_1  # pyright: ignore
        assert not client.module_3_torn_down_1  # pyright: ignore
        assert not client.module_3_setup_2  # pyright: ignore
        assert not client.module_3_torn_down_2  # pyright: ignore
        assert not client.module_3_setup_3  # pyright: ignore

        old_module_3 = client.extensions['botus_tests.module_3']

        (botus_tests / 'module_3.py').unlink()
        (botus_tests / 'module_3.py').symlink_to(
            Path(__file__).parent.absolute() / 'client' / 'module_3_new.py'
        )

        with pytest.raises(ExtensionFailed):
            await client.reload_extension('botus_tests.module_3')

        assert client.module_3_setup_1  # pyright: ignore
        assert client.module_3_torn_down_1  # pyright: ignore
        assert client.module_3_setup_2  # pyright: ignore
        assert client.module_3_torn_down_2  # pyright: ignore
        assert client.module_3_setup_3  # pyright: ignore
        assert client.extensions['botus_tests.module_3'] is old_module_3

    async def test_close_with_extension(
        self, mocker: MockerFixture, config: Config
    ) -> None:
        mocker.patch('discord.Client.close', new_callable=mocker.AsyncMock)

        client = Client(config)
        await client.load_extension('tests.client.module_2')
        await client.setup_hook()
        await client.close()

        assert client.module_2_torn_down  # pyright: ignore


class TestAutoShardedClient:
    @pytest.mark.parametrize(
        'config',
        [
            {
                'bot_name': 'botty',
                'intents': discord.Intents.all(),
                'application_id': 1,
            },
            {
                'bot_name': 'mcbotterson',
                'intents': discord.Intents.none(),
                'application_id': 2,
            },
        ],
    )
    def test_init(self, config: Config) -> None:
        client = AutoShardedClient(config)

        assert client.config == config
        assert client.bot_name == config['bot_name']
        assert client.application_id == config['application_id']
        assert client.intents.value == config['intents'].value

        assert isinstance(client, AutoShardedClient)
        assert isinstance(client, OriginalAutoShardedClient)
        assert isinstance(client, OriginalClient)
        assert isinstance(client.tree, CommandTree)
        assert not hasattr(client, 'session')
        assert client.extensions == {}
