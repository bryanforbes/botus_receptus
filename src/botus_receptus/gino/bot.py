from __future__ import annotations

from typing import Any, ClassVar

from discord.ext import commands
from gino import Gino

from ..bot import BotBase as _BotBase
from ..config import Config


class BotBase(_BotBase):
    db: ClassVar[Gino]

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)

    async def setup_hook(self) -> None:
        await self.db.set_bind(self.config.get('db_url', ''))

    async def close(self, /) -> None:
        bind = self.db.pop_bind()

        if bind is not None:
            await bind.close()

        await super().close()


class Bot(BotBase, commands.Bot):
    ...


class AutoShardedBot(BotBase, commands.AutoShardedBot):
    ...
