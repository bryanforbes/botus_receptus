from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord.ext import commands
from discord.ext.commands import bot  # type: ignore

from . import base
from .app_commands import CommandTree

if TYPE_CHECKING:
    from .config import Config


class BotBase(base.Base, bot.BotBase):
    default_prefix: str

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        self.default_prefix = config.get('command_prefix', '$')

        super().__init__(
            config,
            *args,
            **kwargs,
            command_prefix=self.default_prefix,
            tree_cls=CommandTree,
        )


class Bot(BotBase, commands.Bot):
    ...


class AutoShardedBot(BotBase, commands.AutoShardedBot):
    ...
