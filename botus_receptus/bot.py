from typing import Any

import aiohttp

from discord.ext import commands
from configparser import ConfigParser


class Bot(commands.Bot):
    bot_name: str
    config: ConfigParser
    default_prefix: str  # noqa
    session: aiohttp.ClientSession

    def __init__(self, bot_name: str, config: ConfigParser, *args: Any, **kwargs: Any) -> None:
        self.bot_name = bot_name
        self.config = config
        self.default_prefix = kwargs['command_prefix'] = self.config.get(bot_name, 'command_prefix', fallback='$')

        super().__init__(*args, **kwargs)

        self.session = aiohttp.ClientSession(loop=self.loop)

    def run_with_config(self) -> None:
        self.run(self.config.get(self.bot_name, 'discord_api_key'))

    async def close(self) -> None:
        await super().close()
        await self.session.close()
