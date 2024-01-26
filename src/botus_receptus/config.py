from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict

import discord
import tomli

if TYPE_CHECKING:
    from os import PathLike


class ConfigException(Exception): ...


class _BaseConfig(TypedDict):
    bot_name: str
    discord_api_key: str
    application_id: int
    admin_guild: NotRequired[int]
    test_guilds: NotRequired[list[int]]
    command_prefix: NotRequired[str]
    db_url: NotRequired[str]
    dbl_token: NotRequired[str]


class _RawLogging(TypedDict):
    log_file: NotRequired[str]
    log_level: NotRequired[str]
    log_to_console: NotRequired[bool]
    loggers: NotRequired[dict[str, str]]


class _RawConfig(_BaseConfig):
    intents: list[str] | str
    logging: NotRequired[_RawLogging]


class Logging(TypedDict):
    log_file: str
    log_level: str
    log_to_console: bool
    loggers: NotRequired[dict[str, str]]


class Config(_BaseConfig):
    intents: discord.Intents
    logging: Logging


def load(path: str | PathLike[str], /) -> Config:
    with Path(path).open('rb') as f:
        config_toml = tomli.load(f)

    raw_config: _RawConfig | None = config_toml.get('bot')

    if raw_config is None:
        raise ConfigException('"bot" section not in config file')
    if 'bot_name' not in raw_config:
        raise ConfigException('"bot_name" not specified in the config file')
    if 'discord_api_key' not in raw_config:
        raise ConfigException('"discord_api_key" not specified in the config file')
    if 'application_id' not in raw_config:
        raise ConfigException('"application_id" not specified in the config file')
    if 'intents' not in raw_config:
        raise ConfigException('"intents" not specified in the config file')

    if isinstance(raw_config['intents'], str):
        intents: discord.Intents = getattr(discord.Intents, raw_config['intents'])()
    else:
        intents = discord.Intents(**{key: True for key in raw_config['intents']})

    raw_logging = raw_config.get('logging', {})

    logging: Logging = {
        'log_file': raw_logging.get('log_file', f'{raw_config["bot_name"]}.log'),
        'log_level': raw_logging.get('log_level', 'info'),
        'log_to_console': raw_logging.get('log_to_console', False),
    }

    if 'loggers' in raw_logging:
        logging['loggers'] = raw_logging['loggers']

    config: Config = {
        'bot_name': raw_config['bot_name'],
        'discord_api_key': raw_config['discord_api_key'],
        'application_id': raw_config['application_id'],
        'intents': intents,
        'logging': logging,
    }

    for key, value in raw_config.items():
        if key not in config:
            config[key] = value

    return config
