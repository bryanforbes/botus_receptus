from typing import Type, cast, Any, Union, Dict
from configparser import ConfigParser

import click

from .bot import Bot
from .logging import setup_logging


def config_callback(ctx: click.Context, param: Union[click.Option, click.Parameter],
                    value: str) -> Any:
    if not ctx.default_map:
        ctx.default_map = {}

    parser = ConfigParser(default_section='bot')
    parser.read(value)

    try:
        cast(Dict[str, Any], ctx.default_map).update(parser['logging'])
    except KeyError:
        pass

    return parser


def run(bot_class: Type[Bot], default_config_path: str) -> None:
    @click.command()
    @click.option('--config', required=True, is_eager=True,
                  type=click.Path(exists=True, file_okay=True, resolve_path=True),
                  default=default_config_path, callback=cast(Any, config_callback))
    @click.option('--log-to-console', is_flag=True)
    @click.option('--log-level',
                  type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
                  default='info')
    def main(config: ConfigParser, log_to_console: bool, log_level: str) -> None:
        bot_name = config.get('bot', 'bot_name')
        log_level = log_level.upper()

        with setup_logging(bot_name,
                           config.get('logging', 'log_file', fallback=f'{bot_name}.log'),
                           log_to_console,
                           log_level):
            bot = bot_class(config)
            bot.run_with_config()

    main()
