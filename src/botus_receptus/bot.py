from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, cast

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import bot  # type: ignore

from .app_commands import CommandTree
from .config import Config


class BotBase(bot.BotBase):
    bot_name: str
    config: Config
    default_prefix: str
    session: aiohttp.ClientSession
    loop: asyncio.AbstractEventLoop

    if TYPE_CHECKING:

        @property
        def application_id(self) -> int:
            ...

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        self.config = config
        self.bot_name = self.config['bot_name']
        self.default_prefix = kwargs['command_prefix'] = self.config.get(
            'command_prefix', '$'
        )

        kwargs['application_id'] = config['application_id']

        super().__init__(*args, **kwargs)

        self._connection._command_tree = None  # type: ignore
        self._BotBase__tree = CommandTree(self)  # type: ignore

    def run_with_config(self, /) -> None:
        cast(Any, self).run(self.config['discord_api_key'])

    async def setup_hook(self, /) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def sync_app_commands(self, /) -> None:
        test_guild: discord.Object | None = None

        if (guild_id := self.config.get('test_guild')) is not None:
            test_guild = discord.Object(id=guild_id)

        if test_guild is not None:
            self.tree.copy_global_to(guild=test_guild)

        await self.tree.sync(guild=test_guild)

    async def close(self, /) -> None:
        await super().close()
        await self.session.close()


class Bot(BotBase, commands.Bot):
    ...


class AutoShardedBot(BotBase, commands.AutoShardedBot):
    ...
