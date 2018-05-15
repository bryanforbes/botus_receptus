from typing import Any, cast

import aiohttp
import async_timeout
import json
import discord

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


class DblBot(Bot):
    async def _report_guilds(self) -> None:
        token = self.config.get(self.bot_name, 'dbl_token', fallback='')
        if not token:
            return

        headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }
        payload = {'server_count': len(self.guilds)}
        user = cast(discord.ClientUser, self.user)

        with async_timeout.timeout(10):
            await self.session.post(f'https://discordbots.org/api/bots/{user.id}/stats',
                                    data=json.dumps(payload, ensure_ascii=True),
                                    headers=headers)

    async def on_ready(self) -> None:
        await self._report_guilds()

    async def on_guild_available(self, guild: discord.Guild) -> None:
        await self._report_guilds()

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self._report_guilds()

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self._report_guilds()
