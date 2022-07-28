from __future__ import annotations

from collections.abc import Awaitable, Iterable
from typing import TYPE_CHECKING, Generic, TypeVar

from discord.abc import Snowflake
from discord.ext import commands
from discord.utils import maybe_coroutine

from .bot import AutoShardedBot, Bot

if TYPE_CHECKING:
    from typing_extensions import Self


_BotT = TypeVar('_BotT', bound=Bot | AutoShardedBot)


class Cog(commands.Cog, Generic[_BotT]):
    bot: _BotT

    def __init__(self, bot: _BotT, /) -> None:
        super().__init__()

        self.bot = bot

    async def _inject(  # type: ignore
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
    ) -> Self:
        await maybe_coroutine(self.__pre_inject__, bot, override, guild, guilds)

        _cog = await super()._inject(bot, override, guild, guilds)

        await maybe_coroutine(self.__post_inject__, bot, override, guild, guilds)

        return _cog

    async def _eject(  # type: ignore
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
    ) -> None:
        await maybe_coroutine(self.__pre_eject__, bot, guild_ids)

        await super()._eject(bot, guild_ids)

        await maybe_coroutine(self.__post_eject__, bot, guild_ids)

    def __pre_inject__(
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_inject__(
        self,
        bot: _BotT,
        override: bool,
        guild: Snowflake | None,
        guilds: list[Snowflake],
        /,
    ) -> None | Awaitable[None]:
        ...

    def __pre_eject__(
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...

    def __post_eject__(
        self,
        bot: _BotT,
        guild_ids: Iterable[int] | None,
        /,
    ) -> None | Awaitable[None]:
        ...


class GroupCog(commands.GroupCog, Cog[_BotT]):
    ...
