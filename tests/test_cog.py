from __future__ import annotations

import pytest
from discord.ext import commands

from botus_receptus import Bot, Cog
from botus_receptus.cog import GroupCog


class MockBot: ...


@pytest.fixture
def mock_bot() -> MockBot:
    return MockBot()


class TestCog:
    def test_instantiate(self, mock_bot: Bot) -> None:
        cog = Cog(mock_bot)
        assert cog.bot is mock_bot
        assert isinstance(cog, Cog)
        assert not isinstance(cog, commands.GroupCog)


class TestGroupCog:
    def test_init(self, mock_bot: Bot) -> None:
        cog = GroupCog(mock_bot)
        assert cog.bot is mock_bot
        assert isinstance(cog, commands.GroupCog)
        assert isinstance(cog, Cog)
