from __future__ import annotations

import json
from typing import Any, ClassVar, Optional, Type, TypeVar, Union, cast, overload

import aiohttp
import async_timeout
import discord
from discord.ext import typed_commands

from . import abc
from .config import Config

CT = TypeVar('CT', bound=typed_commands.Context)
OT = TypeVar('OT', bound=typed_commands.Context)


class Bot(typed_commands.Bot[CT]):
    bot_name: str
    config: Config
    default_prefix: str
    session: aiohttp.ClientSession
    context_cls: ClassVar[Type[CT]] = cast(Type[CT], typed_commands.Context)

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
    async def get_context(self, message: discord.Message, *, cls: Type[OT]) -> OT:
        ...

    async def get_context(
        self, message: discord.Message, *, cls: Optional[Type[OT]] = None
    ) -> Union[CT, OT]:
        context_cls: Union[Type[CT], Type[OT]]
        if cls is None:
            context_cls = self.context_cls
        else:
            context_cls = cls

        return await super().get_context(message, cls=context_cls)

    def run_with_config(self) -> None:
        self.run(self.config['discord_api_key'])

    async def close(self) -> None:
        await super().close()
        await self.session.close()


class DblBot(
    Bot[CT], abc.OnReady, abc.OnGuildAvailable, abc.OnGuildJoin, abc.OnGuildRemove
):
    async def __report_guilds(self) -> None:
        token = self.config.get('dbl_token', '')
        if not token:
            return

        headers = {'Content-Type': 'application/json', 'Authorization': token}
        payload = {'server_count': len(self.guilds)}

        with async_timeout.timeout(10):
            await self.session.post(
                f'https://discordbots.org/api/bots/{self.user.id}/stats',
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
