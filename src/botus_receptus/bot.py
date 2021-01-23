from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar, cast, overload

import aiohttp
import async_timeout
import discord
from discord.ext import typed_commands
from discord.ext.commands import bot

from . import abc
from .compat import type
from .config import Config

CT = TypeVar('CT', bound=typed_commands.Context)
OT = TypeVar('OT', bound=typed_commands.Context)


if TYPE_CHECKING:

    class _BotBase(bot.BotBase[CT]):
        ...


else:

    class _BotBase(bot.BotBase, Generic[CT]):
        ...


class BotBase(_BotBase[CT]):
    bot_name: str
    config: Config
    default_prefix: str
    session: aiohttp.ClientSession
    context_cls: ClassVar[type[CT]] = cast(type[CT], typed_commands.Context)
    loop: asyncio.AbstractEventLoop

    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        self.config = config
        self.bot_name = self.config['bot_name']
        self.default_prefix = kwargs['command_prefix'] = self.config.get(
            'command_prefix', '$'
        )

        super().__init__(*args, **kwargs)

        self.session = aiohttp.ClientSession(loop=self.loop)

    @overload
    async def get_context(self, message: discord.Message) -> CT:
        ...

    @overload
    async def get_context(self, message: discord.Message, *, cls: type[OT]) -> OT:
        ...

    async def get_context(
        self, message: discord.Message, *, cls: type[OT] | None = None
    ) -> CT | OT:
        context_cls: type[CT] | type[OT]
        if cls is None:
            context_cls = self.context_cls
        else:
            context_cls = cls

        return await super().get_context(message, cls=context_cls)

    def run_with_config(self) -> None:
        cast(Any, self).run(self.config['discord_api_key'])

    async def close(self) -> None:
        await super().close()
        await self.session.close()


class Bot(BotBase[CT], typed_commands.Bot[CT]):
    ...


class AutoShardedBot(BotBase[CT], typed_commands.AutoShardedBot[CT]):
    ...


class DblBotBase(
    BotBase[CT], abc.OnReady, abc.OnGuildAvailable, abc.OnGuildJoin, abc.OnGuildRemove
):
    async def __report_guilds(self) -> None:
        token = self.config.get('dbl_token', '')
        if not token:
            return

        headers = {'Content-Type': 'application/json', 'Authorization': token}
        payload = {'server_count': len(cast(Any, self).guilds)}

        with async_timeout.timeout(10):
            await self.session.post(
                f'https://discordbots.org/api/bots/{cast(Any, self).user.id}/stats',
                data=json.dumps(payload, ensure_ascii=True),
                headers=headers,
            )

    async def on_ready(self) -> None:
        await self.__report_guilds()

    async def on_guild_available(self, guild: discord.Guild) -> None:
        await self.__report_guilds()

    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.__report_guilds()

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self.__report_guilds()


class DblBot(DblBotBase[CT], typed_commands.Bot[CT]):
    ...


class AutoShardedDblBot(DblBotBase[CT], typed_commands.AutoShardedBot[CT]):
    ...
