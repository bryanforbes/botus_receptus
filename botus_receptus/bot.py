from typing import Any, cast, TypeVar, Type, Generic, ClassVar, overload, Optional, Union
from typing import _Union  # type: ignore

import aiohttp
import async_timeout
import json
import discord

from discord.ext import commands
from configparser import ConfigParser

from . import abc


old_do_conversion = commands.Command.do_conversion


async def do_conversion(self: Any, ctx: commands.Context, converter: Any, argument: str) -> Any:
    if isinstance(converter, _Union):
        args = converter.__args__

        # Optional[T]
        if len(args) == 2 and args[1] == type(None):  # noqa: E721
            converter = args[0]

    return await old_do_conversion(self, ctx, converter, argument)


commands.Command.do_conversion = do_conversion  # type: ignore


ContextType = TypeVar('ContextType', bound=commands.Context)
OverrideType = TypeVar('OverrideType', bound=commands.Context)


class Bot(commands.Bot, Generic[ContextType]):
    bot_name: str
    config: ConfigParser
    default_prefix: str  # noqa
    session: aiohttp.ClientSession
    context_cls: ClassVar[Type[ContextType]] = cast(Type[ContextType], commands.Context)

    def __init__(self, config: ConfigParser, *args: Any, verify_ssl: bool = True, **kwargs: Any) -> None:
        self.config = config
        self.bot_name = self.config.get('bot', 'command_prefix')
        self.default_prefix = kwargs['command_prefix'] = self.config.get('bot', 'command_prefix', fallback='$')

        super().__init__(*args, **kwargs)

        conn = aiohttp.TCPConnector(verify_ssl=verify_ssl)
        self.session = aiohttp.ClientSession(loop=self.loop, connector=conn)

    @overload
    async def get_context(self, message: discord.Message) -> ContextType: pass

    @overload  # noqa: F811
    async def get_context(self, message: discord.Message, *, cls: Type[OverrideType]) -> OverrideType: pass

    async def get_context(self, message: discord.Message, *,  # noqa: F811
                          cls: Optional[Type[OverrideType]] = None) -> Union[ContextType, OverrideType]:
        context_cls: Union[Type[ContextType], Type[OverrideType]]
        if cls is None:
            context_cls = self.context_cls
        else:
            context_cls = cls

        return await super().get_context(message, cls=context_cls)

    def run_with_config(self) -> None:
        self.run(self.config.get('bot', 'discord_api_key'))

    async def close(self) -> None:
        await super().close()
        await self.session.close()


class DblBot(Bot[ContextType], abc.OnGuildAvailable, abc.OnGuildJoin, abc.OnGuildRemove, Generic[ContextType]):
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
