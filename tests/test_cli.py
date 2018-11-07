import pytest
from click.testing import CliRunner

from botus_receptus.cli import cli


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture
def mock_bot_class_instance(mocker):
    class MockBot:
        run_with_config = mocker.stub()

    return MockBot()


@pytest.fixture
def mock_bot_class(mocker, mock_bot_class_instance):
    return mocker.Mock(return_value=mock_bot_class_instance)


@pytest.fixture(autouse=True)
def mock_setup_logging(mocker):
    return mocker.patch('botus_receptus.logging.setup_logging')


def test_run(cli_runner, mock_bot_class, mock_bot_class_instance, mock_setup_logging):
    with open('config.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty'''
        )

    command = cli(mock_bot_class, './config.ini')
    cli_runner.invoke(command, [])

    mock_setup_logging.assert_called()
    config = mock_setup_logging.call_args[0][0]
    assert config.has_section('logging')
    assert config.get('logging', 'log_file') == 'botty.log'
    assert not config.getboolean('logging', 'log_to_console')
    assert config.get('logging', 'log_level') == 'info'
    mock_bot_class.assert_called()
    mock_bot_class_instance.run_with_config.assert_called()


def test_run_logging_config(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty

[logging]
log_file = botty-log.log
log_level = warning'''
        )

    command = cli(mock_bot_class, './config.ini')
    cli_runner.invoke(command, [])

    mock_setup_logging.assert_called()
    config = mock_setup_logging.call_args[0][0]
    assert config.has_section('logging')
    assert config.get('logging', 'log_file') == 'botty-log.log'
    assert not config.getboolean('logging', 'log_to_console')
    assert config.get('logging', 'log_level') == 'warning'


def test_run_config(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty'''
        )

    with open('config-test.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty-test'''
        )

    command = cli(mock_bot_class, './config.ini')
    cli_runner.invoke(command, ['--config=config-test.ini'])

    mock_setup_logging.assert_called()
    config = mock_setup_logging.call_args[0][0]
    assert config.has_section('logging')
    assert config.get('logging', 'log_file') == 'botty-test.log'
    assert not config.getboolean('logging', 'log_to_console')
    assert config.get('logging', 'log_level') == 'info'


def test_run_log_to_console(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty'''
        )

    command = cli(mock_bot_class, './config.ini')
    cli_runner.invoke(command, ['--log-to-console'])

    mock_setup_logging.assert_called()
    config = mock_setup_logging.call_args[0][0]
    assert config.has_section('logging')
    assert config.get('logging', 'log_file') == 'botty.log'
    assert config.getboolean('logging', 'log_to_console')
    assert config.get('logging', 'log_level') == 'info'


def test_run_log_level(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.ini', 'w') as f:
        f.write(
            '''[bot]
bot_name = botty

[logging]
log_level = error'''
        )

    command = cli(mock_bot_class, './config.ini')
    cli_runner.invoke(command, ['--log-level=critical'])

    mock_setup_logging.assert_called()
    config = mock_setup_logging.call_args[0][0]
    assert config.has_section('logging')
    assert config.get('logging', 'log_file') == 'botty.log'
    assert not config.getboolean('logging', 'log_to_console')
    assert config.get('logging', 'log_level') == 'critical'
