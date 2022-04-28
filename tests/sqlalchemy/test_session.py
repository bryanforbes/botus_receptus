from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from botus_receptus.sqlalchemy.session import async_sessionmaker


class TestAsyncSessionmaker:
    def test_init(self) -> None:
        Session = async_sessionmaker()
        assert issubclass(Session.class_, AsyncSession)
