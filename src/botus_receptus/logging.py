from __future__ import annotations

import contextlib
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    Formatter,
    StreamHandler,
    getLogger,
)
from typing import Dict, Iterator

from .config import Config

log_levels: Dict[str, int] = {
    'critical': CRITICAL,
    'error': ERROR,
    'warning': WARNING,
    'info': INFO,
    'debug': DEBUG,
}


@contextlib.contextmanager
def setup_logging(config: Config) -> Iterator[None]:
    try:
        bot_name = config['bot_name']
        log_file = config['logging']['log_file']
        log_to_console = config['logging']['log_to_console']
        log_level = config['logging']['log_level']

        getLogger('discord').setLevel(log_levels['info'])
        getLogger('discord.http').setLevel(log_levels['warning'])

        getLogger(bot_name).setLevel(log_levels.get(log_level, log_levels['info']))

        if 'loggers' in config['logging']:
            for name, value in config['logging']['loggers'].items():
                getLogger(name).setLevel(log_levels.get(value, log_levels['info']))

        log = getLogger()
        log.setLevel(log_levels['info'])

        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = Formatter(
            '[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{'
        )

        handler = FileHandler(filename=log_file, encoding='utf-8', mode='a')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        if log_to_console:
            console_handler = StreamHandler()
            console_handler.setFormatter(fmt)
            log.addHandler(console_handler)

        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
