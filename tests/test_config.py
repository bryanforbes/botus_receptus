from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import pytest

from botus_receptus import config

if TYPE_CHECKING:
    from pathlib import Path


def test_load(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
intents = "all"
discord_api_key = "API_KEY"
application_id = 1'''
    )

    bot_config = config.load(str(c))
    assert bot_config['bot_name'] == 'botty'
    assert bot_config['intents'] == discord.Intents.all()
    assert bot_config['discord_api_key'] == 'API_KEY'
    assert bot_config['application_id'] == 1

    logging = bot_config.get('logging')
    assert logging is not None
    assert logging == {
        'log_file': 'botty.log',
        'log_level': 'info',
        'log_to_console': False,
    }


def test_load_with_intents_list(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
intents = ["guilds", "reactions", "messages"]
discord_api_key = "API_KEY"
application_id = 1'''
    )

    bot_config = config.load(str(c))
    assert bot_config['intents'] == discord.Intents(
        guilds=True, reactions=True, messages=True
    )


def test_load_logging_config(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
intents = "all"
discord_api_key = "API_KEY"
application_id = 1

[bot.logging]
log_file = "botty-log.log"
log_to_console = true
log_level = "warning"'''
    )

    bot_config = config.load(str(c))
    logging = bot_config.get('logging')
    assert logging is not None
    assert logging.get('log_file') == 'botty-log.log'
    assert logging.get('log_to_console')
    assert logging.get('log_level') == 'warning'


def test_load_no_bot_section(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[foo]
bot_name = "botty"
discord_api_key = "API_KEY"
application_id = 1
'''
    )

    with pytest.raises(
        config.ConfigException, match='"bot" section not in config file'
    ):
        config.load(str(c))


def test_load_no_bot_name(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
intents = "all"
discord_api_key = "API_KEY"
application_id = 1
'''
    )

    with pytest.raises(
        config.ConfigException, match='"bot_name" not specified in the config file'
    ):
        config.load(str(c))


def test_load_no_api_key(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
intents = "all"
application_id = 1
'''
    )

    with pytest.raises(
        config.ConfigException,
        match='"discord_api_key" not specified in the config file',
    ):
        config.load(str(c))


def test_load_no_application_id(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
intents = "all"
discord_api_key = "API_KEY"
'''
    )

    with pytest.raises(
        config.ConfigException,
        match='"application_id" not specified in the config file',
    ):
        config.load(str(c))


def test_load_no_intents(tmp_path: Path) -> None:
    c = tmp_path / 'config.toml'
    c.write_text(
        '''[bot]
bot_name = "botty"
discord_api_key = "API_KEY"
application_id = 1
'''
    )

    with pytest.raises(
        config.ConfigException,
        match='"intents" not specified in the config file',
    ):
        config.load(str(c))
