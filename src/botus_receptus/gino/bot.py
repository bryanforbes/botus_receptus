from __future__ import annotations

from typing import Any, ClassVar

from gino import Gino

from ..bot import AutoShardedBot as _AutoShardedBot
from ..bot import Bot as _Bot
from ..bot import BotBase as _BotBase
from ..config import Config


class BotBase(_BotBase):
    db: ClassVar[Gino]

    def __init__(self, config: Config, /, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)

    async def setup_hook(self) -> None:
        await self.db.set_bind(self.config.get('db_url', ''))

        await super().setup_hook()

    async def close(self, /) -> None:
        bind = self.db.pop_bind()

        if bind is not None:
            await bind.close()

        await super().close()


class Bot(BotBase, _Bot):
    ...


class AutoShardedBot(BotBase, _AutoShardedBot):
    ...
