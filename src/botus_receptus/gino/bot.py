from __future__ import annotations

from typing import Any, TypeVar
from configparser import ConfigParser
from discord.ext import commands

from ..bot import Bot as BaseBot
from .base import db


CT = TypeVar('CT', bound=commands.Context)


class Bot(BaseBot[CT]):
    def __init__(self, config: ConfigParser, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)

        self.loop.run_until_complete(db.set_bind(self.config.get('bot', 'db_url')))
