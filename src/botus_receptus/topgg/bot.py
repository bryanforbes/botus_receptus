from __future__ import annotations

from typing import Any, cast

import async_timeout
import discord

from .. import bot


class BotBase(bot.BotBase):
    async def __report_guilds(self, /) -> None:
        token = self.config.get('dbl_token', None)
        if token is None:
            return

        headers = {'Content-Type': 'application/json', 'Authorization': token}
        payload = {'server_count': len(cast(Any, self).guilds)}

        with async_timeout.timeout(10):
            await self.session.post(
                f'https://top.gg/api/bots/{cast(Any, self).user.id}/stats',
                data=discord.utils._to_json(payload),
                headers=headers,
            )

    async def on_ready(self, /) -> None:
        await self.__report_guilds()

    async def on_guild_available(self, guild: discord.Guild, /) -> None:
        await self.__report_guilds()

    async def on_guild_join(self, guild: discord.Guild, /) -> None:
        await self.__report_guilds()

    async def on_guild_remove(self, guild: discord.Guild, /) -> None:
        await self.__report_guilds()


class Bot(BotBase, bot.Bot):
    ...


class AutoShardedBot(BotBase, bot.AutoShardedBot):
    ...
