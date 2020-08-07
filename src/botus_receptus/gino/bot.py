from __future__ import annotations

from typing import Any, ClassVar, TypeVar

from discord.ext import typed_commands
from gino import Gino

from ..bot import Bot as BaseBot
from ..config import Config

CT = TypeVar('CT', bound=typed_commands.Context)


class Bot(BaseBot[CT]):
    db: ClassVar[Gino]

    def __init__(self, config: Config, *args: Any, **kwargs: Any) -> None:
        super().__init__(config, *args, **kwargs)

        self.loop.run_until_complete(self.db.set_bind(self.config.get('db_url', '')))

    async def close(self) -> None:
        bind = self.db.pop_bind()

        if bind is not None:
            await bind.close()

        await super().close()
