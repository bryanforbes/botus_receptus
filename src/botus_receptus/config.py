from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict, cast

import toml

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class ConfigException(Exception):
    ...


class Logging(TypedDict):
    log_file: str
    log_level: str
    log_to_console: bool
    loggers: NotRequired[dict[str, str]]


class Config(TypedDict):
    bot_name: str
    discord_api_key: str
    application_id: int
    logging: Logging
    admin_guild: NotRequired[int]
    test_guilds: NotRequired[list[int]]
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
    if 'application_id' not in config:
        raise ConfigException('"application_id" not specified in the config file')

    if 'logging' not in config:
        config['logging'] = cast(Any, {})
    if 'log_file' not in config['logging']:
        config['logging']['log_file'] = f'{config["bot_name"]}.log'

    return config
