import pytest

from botus_receptus import config


def test_load(tmp_path):
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
discord_api_key = "API_KEY"'''
    )

    bot_config = config.load(str(c))
    assert bot_config['bot_name'] == 'botty'
    assert bot_config['discord_api_key'] == 'API_KEY'
    assert 'logging' in bot_config
    assert bot_config.get('logging', {}).get('log_file') == 'botty.log'


def test_load_logging_config(tmp_path):
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
discord_api_key = "API_KEY"

[bot.logging]
log_file = "botty-log.log"
log_to_console = true
log_level = "warning"'''
    )

    bot_config = config.load(str(c))
    assert 'logging' in bot_config
    assert bot_config.get('logging', {}).get('log_file') == 'botty-log.log'
    assert bot_config.get('logging', {}).get('log_to_console')
    assert bot_config.get('logging', {}).get('log_level') == 'warning'


def test_load_no_bot_section(tmp_path):
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[foo]
bot_name = "botty"
discord_api_key = "API_KEY"
'''
    )

    with pytest.raises(
        config.ConfigException, match='"bot" section not in config file'
    ):
        config.load(str(c))


def test_load_no_bot_name(tmp_path):
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
discord_api_key = "API_KEY"
'''
    )

    with pytest.raises(
        config.ConfigException, match='"bot_name" not specified in the config file'
    ):
        config.load(str(c))


def test_load_no_api_key(tmp_path):
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
'''
    )

    with pytest.raises(
        config.ConfigException,
        match='"discord_api_key" not specified in the config file',
    ):
        config.load(str(c))
