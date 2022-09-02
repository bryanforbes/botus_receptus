from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker as _sessionmaker

if TYPE_CHECKING:
    from collections.abc import MutableMapping

    AsyncSessionMakerType = _sessionmaker[AsyncSession]  # type: ignore

else:

    AsyncSessionMakerType = _sessionmaker


class async_sessionmaker(AsyncSessionMakerType):
    def __init__(
        self,
        bind: AsyncConnection | AsyncEngine | None = None,
        autoflush: bool = True,
        info: MutableMapping[Any, Any] | None = None,
        expire_on_commit: bool = True,
        **kw: Any,
    ) -> None:
        super().__init__(
            bind=bind,
            autoflush=autoflush,
            info=info,
            class_=AsyncSession,
            expire_on_commit=expire_on_commit,
            **kw,
        )
