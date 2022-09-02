from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
import discord

if TYPE_CHECKING:
    from typing_extensions import Self

    from .app_commands import CommandTree
    from .config import Config


class Base:
    bot_name: str
    config: Config
    session: aiohttp.ClientSession

    if TYPE_CHECKING:

        @property
        def application_id(self) -> int:
            ...

        @property
        def tree(self) -> CommandTree[Self]:  # pyright: ignore
            ...

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        self.bot_name = config['bot_name']
        self.config = config

        super().__init__(
            *args,
            **kwargs,
            application_id=config['application_id'],  # pyright: ignore
            intents=config['intents'],  # pyright: ignore
        )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession(loop=self.loop)  # pyright: ignore

    async def close(self) -> None:
        await super().close()  # pyright: ignore

        await self.session.close()

    def run_with_config(self) -> None:
        self.run(self.config['discord_api_key'], log_handler=None)  # pyright: ignore

    async def sync_app_commands(self) -> None:
        guilds_to_sync: set[discord.Object] = set()

        if (guild_ids := self.config.get('test_guilds')) is not None:
            guilds_to_sync = {discord.Object(id=guild_id) for guild_id in guild_ids}

        if (admin_guild_id := self.config.get('admin_guild')) is not None:
            guilds_to_sync.add(discord.Object(id=admin_guild_id))

        for guild_to_sync in guilds_to_sync:
            self.tree.copy_global_to(guild=guild_to_sync)
            await self.tree.sync(guild=guild_to_sync)

        await self.tree.sync()
