from typing import Callable
from configparser import ConfigParser

import click

from .logging import setup_logging


def launcher(bot_name: str, config_path: str) -> Callable[[Callable[[str, ConfigParser], None]], click.Command]:
    def decorator(func: Callable[[str, ConfigParser], None]) -> click.Command:
        @click.command()
        @click.option('--log-to-console', is_flag=True)
        @click.option('--log-level',
                      type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
                      default='info')
        def main(log_to_console: bool, log_level: str) -> None:
            log_level = log_level.upper()

            config = ConfigParser(default_section=bot_name)
            config.read(config_path)

            with setup_logging(bot_name,
                               config.get('logging', 'log_file', fallback=f'{bot_name}.log'),
                               log_to_console,
                               log_level):
                func(bot_name, config)

        return main

    return decorator
