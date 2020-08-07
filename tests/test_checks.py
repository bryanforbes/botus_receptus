import discord
import pytest
from discord.ext import commands

from botus_receptus import NotGuildOwner, OnlyDirectMessage, checks


class MockContext:
    pass


class MockGuild(object):
    __slots__ = ('owner',)

    def __init__(self, owner):
        self.owner = owner


class MockUser:
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id


class MockDMChannel(discord.DMChannel):
    def __init__(self):
        pass


@pytest.fixture
def mock_commands_check(mocker):
    return mocker.patch('discord.ext.typed_commands.check', wraps=commands.check)


def test_dm_only(mock_commands_check):
    @checks.dm_only()
    def test() -> None:
        pass

    mock_commands_check.assert_called_once()

    predicate = test.__commands_checks__[0]

    ctx = MockContext()
    ctx.channel = MockDMChannel()

    assert predicate(ctx)

    ctx.channel = None

    with pytest.raises(OnlyDirectMessage):
        predicate(ctx)


def test_is_guild_owner(mock_commands_check):
    @checks.is_guild_owner()
    def test() -> None:
        pass

    mock_commands_check.assert_called_once()

    predicate = test.__commands_checks__[0]

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
