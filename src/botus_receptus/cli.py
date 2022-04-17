from __future__ import annotations

from logging import FileHandler
from typing import Any, cast

import click
import discord
import toml

from . import config, logging
from .bot import BotBase


def config_callback(
    ctx: click.Context,
    param: click.Parameter,
    value: str | int | bool | None,
    /,
) -> Any:
    assert (
        not isinstance(value, (int, bool)) and value is not None
    ), "Invalid parameter type passed"

    assert param.name is not None, "Invalid parameter name passed"

    try:
        bot_config = config.load(value)
    except (toml.TomlDecodeError, OSError) as e:
        raise click.BadOptionUsage(
            param.name, f'Error reading configuration file: {e}', ctx=ctx
        ) from e
    except config.ConfigException as e:
        raise click.BadOptionUsage(param.name, e.args[0], ctx=ctx) from e

    if ctx.default_map is None:
        ctx.default_map = {}

    try:
        ctx.default_map.update(
            {
                k.replace("--", "").replace("-", "_"): v
                for k, v in bot_config['logging'].items()
            }
        )
    except KeyError:
        pass

    return bot_config


def cli(
    bot_class: type[BotBase],
    default_config_path: str,
    /,
    handler_cls: type[FileHandler] = discord.utils.MISSING,
) -> click.Command:
    @click.command()
    @click.option(
        '-c',
        '--config',
        'bot_config',
        required=True,
        is_eager=True,
        type=click.Path(exists=True, file_okay=True),
        default=default_config_path,
        callback=config_callback,
    )
    @click.option('--log-to-console', is_flag=True)
    @click.option(
        '--log-level',
        type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
        default='info',
    )
    def main(bot_config: config.Config, log_to_console: bool, log_level: str) -> None:
        cast(dict[str, Any], bot_config['logging']).update(
            {'log_to_console': log_to_console, 'log_level': log_level}
        )

        with logging.setup_logging(bot_config, handler_cls=handler_cls):
            bot = bot_class(bot_config)
            bot.run_with_config()

    return main
