from __future__ import annotations

from . import abc, checks, formatting, re, util
from .bot import Bot, DblBot
from .cli import cli
from .config import Config
from .context import EmbedContext, PaginatedContext
from .exceptions import NotGuildOwner, OnlyDirectMessage
from .logging import setup_logging

__title__ = 'botus_receptus'
__author__ = 'Bryan Forbes'
__license__ = 'BSD 3-clause'
__version__ = '0.0.1a'

__all__ = (
    'formatting',
    're',
    'db',
    'checks',
    'abc',
    'util',
    'setup_logging',
    'cli',
    'Config',
    'Bot',
    'DblBot',
    'EmbedContext',
    'PaginatedContext',
    'OnlyDirectMessage',
    'NotGuildOwner',
)
