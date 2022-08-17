from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import discord
import pytest
from discord.ext import commands

from botus_receptus import NotGuildOwner, OnlyDirectMessage, checks

if TYPE_CHECKING:
    from .types import MockerFixture


class MockContext:
    channel: MockDMChannel | None
    guild: MockGuild | None
    author: MockUser | None


class MockGuild(object):
    __slots__ = ('owner',)

    def __init__(self, owner: Any):
        self.owner = owner


class MockUser:
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other: Any):
        return self.id == other.id


class MockDMChannel(discord.DMChannel):
    def __init__(self):
        pass


@pytest.fixture
def mock_commands_check(mocker: MockerFixture):
    return mocker.patch('discord.ext.commands.check')


def test_dm_only() -> None:
    @checks.dm_only()
    async def test() -> None:
        pass

    predicate = cast('Any', test).__commands_checks__[0]

    ctx = MockContext()
    ctx.channel = MockDMChannel()

    assert predicate(ctx)

    ctx.channel = None

    with pytest.raises(OnlyDirectMessage):
        predicate(ctx)


def test_is_guild_owner() -> None:
    @checks.is_guild_owner()
    async def test() -> None:
        pass

    predicate = cast('Any', test).__commands_checks__[0]

    ctx = MockContext()
    ctx.guild = None

    with pytest.raises(commands.NoPrivateMessage):
        predicate(ctx)

    ctx.guild = MockGuild(MockUser(0))
    ctx.author = MockUser(1)

    with pytest.raises(NotGuildOwner):
        predicate(ctx)

    ctx.author = MockUser(0)

    assert predicate(ctx)
