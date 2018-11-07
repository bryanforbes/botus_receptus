from __future__ import annotations

import contextlib

from typing import Iterator
from configparser import ConfigParser
from logging import (
    getLogger,
    Formatter,
    FileHandler,
    StreamHandler,
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    DEBUG,
)


log_levels = {
    'critical': CRITICAL,
    'error': ERROR,
    'warning': WARNING,
    'info': INFO,
    'debug': DEBUG,
}


@contextlib.contextmanager
def setup_logging(config: ConfigParser) -> Iterator[None]:
    try:
        bot_name = config.get('bot', 'bot_name')
        log_file = config.get('logging', 'log_file')
        log_to_console = config.getboolean('logging', 'log_to_console')
        log_level = config.get('logging', 'log_level')

        getLogger('discord').setLevel(log_levels['info'])
        getLogger('discord.http').setLevel(log_levels['warning'])

        getLogger(bot_name).setLevel(log_levels.get(log_level, log_levels['info']))

        if config.has_section('loggers'):
            for name, value in config.items('loggers'):
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
