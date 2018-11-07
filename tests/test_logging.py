import pytest

import logging
from configparser import ConfigParser
from botus_receptus.logging import setup_logging


class MockHandler:
    def setFormatter(self, formatter):
        pass


@pytest.fixture(autouse=True)
def mock_get_logger(mocker):
    return mocker.patch('botus_receptus.logging.getLogger')


@pytest.fixture(autouse=True)
def mock_formatter(mocker):
    return mocker.patch('botus_receptus.logging.Formatter')


@pytest.fixture(autouse=True)
def mock_file_handler(mocker):
    return mocker.patch('botus_receptus.logging.FileHandler')


@pytest.fixture(autouse=True)
def mock_stream_handler(mocker):
    return mocker.patch('botus_receptus.logging.StreamHandler')


def test_setup_logging(
    mocker, mock_get_logger, mock_formatter, mock_file_handler, mock_stream_handler
):
    parser = ConfigParser()
    parser.read_string(
        '''
[bot]
bot_name = botty

[logging]
log_file = botty.log
log_to_console = False
log_level = info'''
    )

    with setup_logging(parser):
        mock_get_logger.assert_has_calls(
            [
                mocker.call('discord'),
                mocker.call('discord').setLevel(logging.INFO),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.WARNING),
                mocker.call('botty'),
                mocker.call('botty').setLevel(logging.INFO),
                mocker.call(),
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
    mocker, mock_get_logger, mock_formatter, mock_stream_handler
):
    parser = ConfigParser()
    parser.read_string(
        '''
[bot]
bot_name = botty

[logging]
log_file = botty.log
log_to_console = True
log_level = info'''
    )

    with setup_logging(parser):
        mock_stream_handler.assert_called()
        mock_stream_handler.return_value.setFormatter.assert_called_with(
            mock_formatter.return_value
        )
        mock_get_logger.return_value.addHandler.assert_called_with(
            mock_stream_handler.return_value
        )


def test_setup_logging_loggers(
    mocker, mock_get_logger, mock_formatter, mock_file_handler, mock_stream_handler
):
    parser = ConfigParser()
    parser.read_string(
        '''
[bot]
bot_name = botty

[logging]
log_file = botty.log
log_to_console = True
log_level = info

[loggers]
gino = error
discord.http = error'''
    )

    with setup_logging(parser):
        mock_get_logger.assert_has_calls(
            [
                mocker.call('discord'),
                mocker.call('discord').setLevel(logging.INFO),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.WARNING),
                mocker.call('botty'),
                mocker.call('botty').setLevel(logging.INFO),
                mocker.call('gino'),
                mocker.call('gino').setLevel(logging.ERROR),
                mocker.call('discord.http'),
                mocker.call('discord.http').setLevel(logging.ERROR),
                mocker.call(),
                mocker.call().setLevel(logging.INFO),
            ]
        )
