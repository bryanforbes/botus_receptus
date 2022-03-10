from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict, cast

import toml

from .compat import dict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class ConfigException(Exception):
    ...


class LoggingBase(TypedDict):
    log_file: str
    log_level: str
    log_to_console: bool


class Logging(LoggingBase):
    loggers: NotRequired[dict[str, str]]


class ConfigBase(TypedDict):
    bot_name: str
    discord_api_key: str
    logging: Logging


class Config(ConfigBase):
    command_prefix: NotRequired[str]
    db_url: NotRequired[str]
    dbl_token: NotRequired[str]


def load(path: str, /) -> Config:
    config_toml = toml.load(path)
    config: Config | None = config_toml.get('bot')

    if config is None:
        raise ConfigException('"bot" section not in config file')
    if 'bot_name' not in config:
        raise ConfigException('"bot_name" not specified in the config file')
    if 'discord_api_key' not in config:
        raise ConfigException('"discord_api_key" not specified in the config file')

    if 'logging' not in config:
        config['logging'] = cast(Any, {})
    if 'log_file' not in config['logging']:
        config['logging']['log_file'] = f'{config["bot_name"]}.log'

    return config
