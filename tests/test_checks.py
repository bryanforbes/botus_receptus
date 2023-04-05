from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from typing_extensions import override

import discord
import pytest
from attrs import define, field
from discord.ext import commands

from botus_receptus import NotGuildOwner, OnlyDirectMessage, checks

if TYPE_CHECKING:
    from .types import MockerFixture


@define
class MockContext:
    channel: MockDMChannel | None = field(default=None)
    guild: MockGuild | None = field(default=None)
    author: MockUser | None = field(default=None)


@define
class MockGuild:
    owner: Any


@define
class MockUser:
    id: int

    @override
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
