from __future__ import annotations

from importlib.metadata import version
from typing import Final

from . import abc, checks, compat, formatting, re, util
from .bot import AutoShardedBot, Bot, BotBase
from .cli import cli
from .cog import Cog
from .config import Config, ConfigException
from .context import EmbedContext, PaginatedContext
from .exceptions import NotGuildOwner, OnlyDirectMessage
from .logging import setup_logging

__title__: Final = 'botus_receptus'
__author__: Final = 'Bryan Forbes'
__license__: Final = 'BSD 3-clause'
__version__: Final = version('botus_receptus')

__all__ = (
    'abc',
    'checks',
    'compat',
    'formatting',
    're',
    'util',
    'AutoShardedBot',
    'Bot',
    'BotBase',
    'cli',
    'Cog',
    'Config',
    'ConfigException',
    'EmbedContext',
    'PaginatedContext',
    'NotGuildOwner',
    'OnlyDirectMessage',
    'setup_logging',
)
