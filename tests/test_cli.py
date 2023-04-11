from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import discord
import pytest
from attrs import define
from click.testing import CliRunner

from botus_receptus import ConfigException, cli

if TYPE_CHECKING:
    from unittest.mock import MagicMock, Mock

    from botus_receptus.bot import BotBase
    from botus_receptus.config import Config

    from .types import MockerFixture


@define
class MockBot:
    run_with_config: MagicMock


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():  # type: ignore
        yield runner


@pytest.fixture
def mock_bot_class_instance(mocker: MockerFixture):
    return MockBot(mocker.stub())


@pytest.fixture
def mock_bot_class(mocker: MockerFixture, mock_bot_class_instance: MockBot):
    return mocker.Mock(return_value=mock_bot_class_instance)


@pytest.fixture(autouse=True)
def mock_setup_logging(mocker: MockerFixture):
    return mocker.patch('botus_receptus.logging.setup_logging')


@pytest.fixture
def mock_config() -> Config:
    return {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'intents': discord.Intents.all(),
        'logging': {
            'log_file': 'botty.log',
            'log_level': 'info',
            'log_to_console': False,
        },
    }


@pytest.fixture(autouse=True)
def mock_config_load(mocker: MockerFixture, mock_config: Config):
    return mocker.patch('botus_receptus.config.load', return_value=mock_config)


def test_run(
    cli_runner: CliRunner,
    mock_bot_class: Mock,
    mock_bot_class_instance: MockBot,
    mock_setup_logging: MagicMock,
    mock_config_load: MagicMock,
):
    with Path('config.toml').open('w') as f:
        f.write('')

    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    cli_runner.invoke(command, [])  # type: ignore

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': False,
                'log_level': 'info',
            },
        },
        handler_cls=discord.utils.MISSING,
    )
    mock_config_load.assert_called_once()
    assert mock_config_load.call_args[0][0].endswith('/config.toml')
    mock_bot_class.assert_called()
    mock_bot_class_instance.run_with_config.assert_called()


@pytest.mark.parametrize(
    'mock_config',
    [
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'logging': {
                'log_file': 'botty.log',
                'log_level': 'warning',
                'log_to_console': True,
            },
        }
    ],
)
def test_run_logging_config(
    cli_runner: CliRunner,
    mocker: MockerFixture,
    mock_bot_class: Mock,
    mock_setup_logging: MagicMock,
    mock_config_load: MagicMock,
):
    with Path('config.toml').open('w') as f:
        f.write('')

    mock_cls = mocker.MagicMock()

    command = cli(
        cast('type[BotBase]', mock_bot_class),
        './config.toml',
        handler_cls=cast('Any', mock_cls),
    )
    cli_runner.invoke(command, [])  # type: ignore

    assert mock_config_load.call_args[0][0].endswith('/config.toml')
    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': True,
                'log_level': 'warning',
            },
        },
        handler_cls=mock_cls,
    )


def test_run_config(
    cli_runner: CliRunner, mock_bot_class: Mock, mock_config_load: MagicMock
):
    with Path('config.toml').open('w') as f:
        f.write('')

    with Path('config-test.toml').open('w') as f:
        f.write('')

    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    cli_runner.invoke(command, ['--config=config-test.toml'])  # type: ignore

    assert mock_config_load.call_args[0][0].endswith('config-test.toml')


def test_run_log_to_console(
    cli_runner: CliRunner, mock_bot_class: Mock, mock_setup_logging: MagicMock
):
    with Path('config.toml').open('w') as f:
        f.write('')

    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    cli_runner.invoke(command, ['--log-to-console'])  # type: ignore

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': True,
                'log_level': 'info',
            },
        },
        handler_cls=discord.utils.MISSING,
    )


def test_run_log_level(
    cli_runner: CliRunner, mock_bot_class: Mock, mock_setup_logging: MagicMock
):
    with Path('config.toml').open('w') as f:
        f.write('')

    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    cli_runner.invoke(command, ['--log-level=critical'])  # type: ignore

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'application_id': 1,
            'intents': discord.Intents.all(),
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': False,
                'log_level': 'critical',
            },
        },
        handler_cls=discord.utils.MISSING,
    )


def test_run_error_no_config(
    cli_runner: CliRunner, mock_bot_class: Mock, mock_setup_logging: MagicMock
):
    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    result = cli_runner.invoke(command, [])  # type: ignore
    assert result.exit_code == 2
    mock_setup_logging.assert_not_called()


def test_run_error_reading(
    cli_runner: CliRunner,
    mock_bot_class: Mock,
    mock_config_load: MagicMock,
    mock_setup_logging: MagicMock,
):
    with Path('config.toml').open('w') as f:
        f.write('')

    mock_config_load.side_effect = OSError()
    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    result = cli_runner.invoke(command, [])  # type: ignore
    assert result.exit_code == 2
    assert 'Error reading configuration file: ' in result.output
    mock_setup_logging.assert_not_called()


def test_run_config_exception(
    cli_runner: CliRunner,
    mock_bot_class: Mock,
    mock_config_load: MagicMock,
    mock_setup_logging: MagicMock,
):
    with Path('config.toml').open('w') as f:
        f.write('')

    mock_config_load.side_effect = ConfigException('No section and stuff')
    command = cli(cast('type[BotBase]', mock_bot_class), './config.toml')
    result = cli_runner.invoke(command, [])  # type: ignore
    assert result.exit_code == 2
    assert 'No section and stuff' in result.output
    mock_setup_logging.assert_not_called()
