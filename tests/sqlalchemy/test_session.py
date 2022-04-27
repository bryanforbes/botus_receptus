from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from botus_receptus.sqlalchemy.session import sessionmaker


class TestSessionmaker:
    def test_init(self) -> None:
        Session = sessionmaker()
        assert issubclass(Session.class_, AsyncSession)
