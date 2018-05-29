from typing import Any, cast, _Union  # type: ignore

import aiohttp
import async_timeout
import json
import discord

from discord.ext import commands
from configparser import ConfigParser


old_do_conversion = commands.Command.do_conversion


async def do_conversion(self: Any, ctx: commands.Context, converter: Any, argument: str) -> Any:
    if isinstance(converter, _Union):
        tree = converter._subs_tree()

        if len(tree) == 3 and tree[2] == type(None):  # noqa: E721
            converter = converter._subs_tree()[1]

    return await old_do_conversion(self, ctx, converter, argument)


commands.Command.do_conversion = do_conversion  # type: ignore


class Bot(commands.Bot):
    bot_name: str
    config: ConfigParser
    default_prefix: str  # noqa
    session: aiohttp.ClientSession

    def __init__(self, config: ConfigParser, *args: Any, **kwargs: Any) -> None:
        self.config = config
        self.bot_name = self.config.get('bot', 'command_prefix')
        self.default_prefix = kwargs['command_prefix'] = self.config.get('bot', 'command_prefix', fallback='$')

        super().__init__(*args, **kwargs)

        self.session = aiohttp.ClientSession(loop=self.loop)

    def run_with_config(self) -> None:
        self.run(self.config.get('bot', 'discord_api_key'))

    async def close(self) -> None:
        await super().close()
        await self.session.close()


class DblBot(Bot):
    async def _report_guilds(self) -> None:
        token = self.config.get('bot', 'dbl_token', fallback='')
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
