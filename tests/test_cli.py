import pytest
from click.testing import CliRunner

from botus_receptus import ConfigException, cli


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


@pytest.fixture
def mock_config():
    return {
        'bot_name': 'botty',
        'discord_api_key': 'API_KEY',
        'logging': {'log_file': 'botty.log'},
    }


@pytest.fixture(autouse=True)
def mock_config_load(mocker, mock_config):
    return mocker.patch('botus_receptus.config.load', return_value=mock_config)


def test_run(
    cli_runner,
    mock_bot_class,
    mock_bot_class_instance,
    mock_setup_logging,
    mock_config_load,
):
    with open('config.toml', 'w') as f:
        f.write('')

    command = cli(mock_bot_class, './config.toml')
    cli_runner.invoke(command, [])

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': False,
                'log_level': 'info',
            },
        }
    )
    mock_config_load.assert_called_once()
    mock_config_load.call_args[0][0].endswith('/config.toml')
    mock_bot_class.assert_called()
    mock_bot_class_instance.run_with_config.assert_called()


@pytest.mark.parametrize(
    'mock_config',
    [
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'logging': {
                'log_file': 'botty.log',
                'log_level': 'warning',
                'log_to_console': True,
            },
        }
    ],
)
def test_run_logging_config(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.toml', 'w') as f:
        f.write('')

    command = cli(mock_bot_class, './config.toml')
    cli_runner.invoke(command, [])

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': True,
                'log_level': 'warning',
            },
        }
    )


def test_run_config(cli_runner, mock_bot_class, mock_config_load):
    with open('config.toml', 'w') as f:
        f.write('')

    with open('config-test.toml', 'w') as f:
        f.write('')

    command = cli(mock_bot_class, './config.toml')
    cli_runner.invoke(command, ['--config=config-test.toml'])

    mock_config_load.call_args[0][0].endswith('/config-test.toml')


def test_run_log_to_console(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.toml', 'w') as f:
        f.write('')

    command = cli(mock_bot_class, './config.toml')
    cli_runner.invoke(command, ['--log-to-console'])

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': True,
                'log_level': 'info',
            },
        }
    )


def test_run_log_level(cli_runner, mock_bot_class, mock_setup_logging):
    with open('config.toml', 'w') as f:
        f.write('')

    command = cli(mock_bot_class, './config.toml')
    cli_runner.invoke(command, ['--log-level=critical'])

    mock_setup_logging.assert_called_once_with(
        {
            'bot_name': 'botty',
            'discord_api_key': 'API_KEY',
            'logging': {
                'log_file': 'botty.log',
                'log_to_console': False,
                'log_level': 'critical',
            },
        }
    )


def test_run_error_no_config(cli_runner, mock_bot_class, mock_setup_logging):
    command = cli(mock_bot_class, './config.toml')
    result = cli_runner.invoke(command, [])
    assert result.exit_code == 2
    mock_setup_logging.assert_not_called()


def test_run_error_reading(
    cli_runner, mock_bot_class, mock_config_load, mock_setup_logging
):
    with open('config.toml', 'w') as f:
        f.write('')

    mock_config_load.side_effect = OSError()
    command = cli(mock_bot_class, './config.toml')
    result = cli_runner.invoke(command, [])
    assert result.exit_code == 2
    assert 'Error reading configuration file: ' in result.output
    mock_setup_logging.assert_not_called()


def test_run_config_exception(
    cli_runner, mock_bot_class, mock_config_load, mock_setup_logging
):
    with open('config.toml', 'w') as f:
        f.write('')

    mock_config_load.side_effect = ConfigException('No section and stuff')
    command = cli(mock_bot_class, './config.toml')
    result = cli_runner.invoke(command, [])
    assert result.exit_code == 2
    assert 'No section and stuff' in result.output
    mock_setup_logging.assert_not_called()
