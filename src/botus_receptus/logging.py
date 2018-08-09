import logging
import contextlib

from typing import Iterator


@contextlib.contextmanager
def setup_logging(bot_name: str, log_file: str, log_to_console: bool, log_level: str) -> Iterator:
    try:
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        logging.getLogger(bot_name).setLevel(getattr(logging, log_level))

        log = logging.getLogger()
        log.setLevel(logging.INFO)

        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')

        handler = logging.FileHandler(filename=log_file, encoding='utf-8', mode='w')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(fmt)
            log.addHandler(console_handler)

        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
