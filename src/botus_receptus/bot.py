from __future__ import annotations

from typing import Any, cast, TypeVar, Type, ClassVar, overload, Optional, Union

import aiohttp
import async_timeout
import discord
import json

from discord.ext import commands

from . import abc
from .config import Config


CT = TypeVar('CT', bound=commands.Context)
OT = TypeVar('OT', bound=commands.Context)


class Bot(commands.Bot[CT]):
    bot_name: str
    config: Config
    default_prefix: str
    session: aiohttp.ClientSession
    context_cls: ClassVar[Type[CT]] = cast(Type[CT], commands.Context)

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
        pass  # pragma: no cover

    @overload  # noqa: F811
    async def get_context(self, message: discord.Message, *, cls: Type[OT]) -> OT:
        pass  # pragma: no cover

    async def get_context(  # noqa: F811
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


class DblBot(Bot[CT], abc.OnGuildAvailable, abc.OnGuildJoin, abc.OnGuildRemove):
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
