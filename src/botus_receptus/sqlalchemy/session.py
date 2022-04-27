from __future__ import annotations

from typing import TYPE_CHECKING, Any, MutableMapping

from sqlalchemy.ext.asyncio.engine import AsyncConnection, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import sessionmaker as _sessionmaker

if TYPE_CHECKING:

    _sessionmakerbase = _sessionmaker[AsyncSession]  # type: ignore

else:

    _sessionmakerbase = _sessionmaker


class sessionmaker(_sessionmakerbase):
    def __init__(
        self,
        bind: AsyncConnection | AsyncEngine | None = None,
        autoflush: bool = True,
        info: MutableMapping[Any, Any] | None = None,
        **kw: Any,
    ) -> None:
        super().__init__(  # type: ignore
            bind=bind,
            autoflush=autoflush,
            info=info,
            class_=AsyncSession,
            expire_on_commit=False,
            **kw,
        )
