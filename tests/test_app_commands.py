from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
import pytest
from attrs import define, field
from discord import app_commands

from botus_receptus.app_commands import (
    CommandTree,
    admin_guild_only,
    test_guilds_only as _test_guilds_only,
)

if TYPE_CHECKING:
    from botus_receptus.bot import Bot


@define
class MockConnection:
    _command_tree: app_commands.CommandTree[Any] | None = field(default=None)


@define
class MockClient:
    http: object = field(factory=object)
    _connection: MockConnection = field(factory=MockConnection)
    config: dict[str, Any] = field(factory=dict)


def test_admin_guild_only() -> None:
    @app_commands.command()
    @admin_guild_only
    async def my_command(interaction: discord.Interaction) -> None:
        ...

    assert my_command._guild_ids == [-1]


def test_admin_guild_only_invoke() -> None:
    @app_commands.command()
    @admin_guild_only()
    async def my_command(interaction: discord.Interaction) -> None:
        ...

    assert my_command._guild_ids == [-1]


def test_test_guilds_only() -> None:
    @app_commands.command()
    @_test_guilds_only
    async def my_command(interaction: discord.Interaction) -> None:
        ...

    assert my_command._guild_ids == [-2]


def test_test_guilds_only_invoke() -> None:
    @app_commands.command()
    @_test_guilds_only()
    async def my_command(interaction: discord.Interaction) -> None:
        ...

    assert my_command._guild_ids == [-2]


class TestCommandTree:
    @pytest.fixture
    def mock_client(self) -> MockClient:
        return MockClient()

    def test_add_command(self, mock_client: Bot) -> None:
        mock_client.config['admin_guild'] = 12345
        mock_client.config['test_guilds'] = [23456, 34567]

        @app_commands.command()
        async def my_command(interaction: discord.Interaction) -> None:
            ...

        @app_commands.command()
        @admin_guild_only()
        async def my_admin_command(interaction: discord.Interaction) -> None:
            ...

        @app_commands.command()
        @_test_guilds_only()
        async def my_test_command(interaction: discord.Interaction) -> None:
            ...

        tree = CommandTree(mock_client)

        tree.add_command(my_command)
        tree.add_command(my_admin_command)
        tree.add_command(my_test_command)

        assert tree.get_commands() == [my_command]
        assert tree.get_commands(guild=discord.Object(id=12345)) == [my_admin_command]
        assert tree.get_commands(guild=discord.Object(id=23456)) == [my_test_command]
        assert tree.get_commands(guild=discord.Object(id=34567)) == [my_test_command]

    def test_add_command_raises(self, mock_client: Bot) -> None:
        @app_commands.command()
        @app_commands.guilds(-1, -2)
        async def my_command(interaction: discord.Interaction) -> None:
            ...

        tree = CommandTree(mock_client)

        with pytest.raises(TypeError):
            tree.add_command(my_command)
