from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

import pytest

from botus_receptus.logging import setup_logging

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from botus_receptus.config import Config

    from .types import MockerFixture


class MockHandler:
    def setFormatter(self, formatter: Any):
        pass


@pytest.fixture(autouse=True)
def mock_get_logger(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('botus_receptus.logging.getLogger')


@pytest.fixture(autouse=True)
def mock_formatter(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('botus_receptus.logging.Formatter')


@pytest.fixture(autouse=True)
def mock_file_handler(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('botus_receptus.logging.FileHandler')


@pytest.fixture(autouse=True)
def mock_stream_handler(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('botus_receptus.logging.StreamHandler')


def test_setup_logging(
    mocker: MockerFixture,
    mock_get_logger: MagicMock,
    mock_formatter: MagicMock,
    mock_file_handler: MagicMock,
    mock_stream_handler: MagicMock,
) -> None:
    config: Config = {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'logging': {
            'log_file': 'botty.log',
            'log_to_console': False,
            'log_level': 'info',
        },
    }

    with setup_logging(config):
        mock_get_logger.assert_has_calls(
            [
                mocker.call(),
                mocker.call('discord'),
                mocker.call('discord').setLevel(logging.INFO),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.WARNING),
                mocker.call('botus_receptus'),
                mocker.call('botus_receptus').setLevel(logging.INFO),
                mocker.call('botty'),
                mocker.call('botty').setLevel(logging.INFO),
                mocker.call().setLevel(logging.INFO),
            ]
        )
        mock_formatter.assert_called()
        mock_file_handler.assert_called_with(
            filename='botty.log', encoding='utf-8', mode='a'
        )
        mock_file_handler.return_value.setFormatter.assert_called_with(
            mock_formatter.return_value
        )
        mock_get_logger.return_value.addHandler.assert_called_with(
            mock_file_handler.return_value
        )
        mock_stream_handler.assert_not_called()


def test_setup_logging_console(
    mock_get_logger: MagicMock,
    mock_formatter: MagicMock,
    mock_stream_handler: MagicMock,
) -> None:
    config: Config = {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'logging': {
            'log_file': 'botty.log',
            'log_to_console': True,
            'log_level': 'info',
        },
    }

    with setup_logging(config):
        mock_stream_handler.assert_called()
        mock_stream_handler.return_value.setFormatter.assert_called_with(
            mock_formatter.return_value
        )
        mock_get_logger.return_value.addHandler.assert_called_with(
            mock_stream_handler.return_value
        )


def test_setup_logging_loggers(
    mocker: MockerFixture, mock_get_logger: MagicMock
) -> None:
    config: Config = {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'logging': {
            'log_file': 'botty.log',
            'log_to_console': True,
            'log_level': 'info',
            'loggers': {'gino': 'error', 'discord.http': 'error'},
        },
    }

    with setup_logging(config):
        mock_get_logger.assert_has_calls(
            [
                mocker.call(),
                mocker.call('discord'),
                mocker.call('discord').setLevel(logging.INFO),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.WARNING),
                mocker.call('botus_receptus'),
                mocker.call('botus_receptus').setLevel(logging.INFO),
                mocker.call('botty'),
                mocker.call('botty').setLevel(logging.INFO),
                mocker.call('gino'),
                mocker.call('gino').setLevel(logging.ERROR),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.ERROR),
                mocker.call().setLevel(logging.INFO),
            ]
        )


def test_setup_logging_handler_cls(
    mocker: MockerFixture,
    mock_get_logger: MagicMock,
) -> None:
    config: Config = {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'application_id': 1,
        'logging': {
            'log_file': 'botty.log',
            'log_to_console': False,
            'log_level': 'info',
        },
    }

    mock_handler = mocker.MagicMock()
    mock_cls = mocker.MagicMock(return_value=mock_handler)

    with setup_logging(config, handler_cls=cast('Any', mock_cls)):
        mock_cls.assert_called_with(filename='botty.log', encoding='utf-8', mode='a')
        mock_get_logger.return_value.addHandler.assert_called_with(mock_handler)
