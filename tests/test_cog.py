from __future__ import annotations

from typing import Any, Coroutine, cast
from typing_extensions import Self
from unittest.mock import AsyncMock

import discord
import pytest
from discord import app_commands
from pytest_mock import MockerFixture

from botus_receptus import Bot, Cog


class MockBot(object):
    ...


class TestCog(object):
    @pytest.fixture
    def mock_bot(self) -> MockBot:
        return MockBot()

    @pytest.fixture
    def mock_cog(self, mock_bot: Bot) -> Cog[Bot]:
        return Cog(mock_bot)

    def test_instantiate(self, mock_bot: Bot) -> None:
        cog = Cog(mock_bot)
        assert cog.bot is mock_bot

    async def test_inject(self, mock_bot: Bot) -> None:
        cog = Cog(mock_bot)
        result = await cog._inject(
            mock_bot, override=False, guild=discord.utils.MISSING, guilds=[]
        )

        assert result is cog

    @pytest.mark.parametrize('async_methods', [True, False])
    async def test_inject_methods(
        self,
        mock_bot: Bot,
        mock_cog: Cog[Bot],
        mocker: MockerFixture,
        async_methods: bool,
    ) -> None:
        pre_inject_spy = cast(
            AsyncMock,
            mocker.patch.object(
                mock_cog,
                '__pre_inject__',
                new_callable=mocker.AsyncMock if async_methods else mocker.Mock,
            ),
        )
        post_inject_spy = cast(
            AsyncMock,
            mocker.patch.object(
                mock_cog,
                '__post_inject__',
                new_callable=mocker.AsyncMock if async_methods else mocker.Mock,
            ),
        )

        await mock_cog._inject(
            mock_bot, override=False, guild=discord.utils.MISSING, guilds=[]
        )

        pre_inject_spy.assert_called_once()
        post_inject_spy.assert_called_once()

        if async_methods:
            pre_inject_spy.assert_awaited_once()
            post_inject_spy.assert_awaited_once()

    async def test_eject(self, mock_bot: Bot) -> None:
        cog = Cog(mock_bot)
        await cog._eject(mock_bot, guild_ids=[])

    @pytest.mark.parametrize('async_methods', [True, False])
    async def test_eject_methods(
        self,
        mock_bot: Bot,
        mock_cog: Cog[Bot],
        mocker: MockerFixture,
        async_methods: bool,
    ) -> None:
        pre_eject_spy = cast(
            AsyncMock,
            mocker.patch.object(
                mock_cog,
                '__pre_eject__',
                new_callable=mocker.AsyncMock if async_methods else mocker.Mock,
            ),
        )
        post_eject_spy = cast(
            AsyncMock,
            mocker.patch.object(
                mock_cog,
                '__post_eject__',
                new_callable=mocker.AsyncMock if async_methods else mocker.Mock,
            ),
        )
        await mock_cog._eject(mock_bot, guild_ids=[])

        pre_eject_spy.assert_called_once()
        post_eject_spy.assert_called_once()

        if async_methods:
            pre_eject_spy.assert_awaited_once()
            post_eject_spy.assert_awaited_once()

    async def test_cog_app_command_error(
        self, mocker: MockerFixture, mock_bot: Bot
    ) -> None:
        on_error = mocker.AsyncMock()
        on_group_handler_error = mocker.AsyncMock()
        on_command_error = mocker.AsyncMock()

        class MyGroup(app_commands.Group):
            @app_commands.command()
            async def my_group_command(self, interaction: discord.Interaction) -> None:
                ...

        class MyGroupWithHandler(app_commands.Group):
            @app_commands.command()
            async def my_group_command(self, interaction: discord.Interaction) -> None:
                ...

            def on_error(
                self,
                interaction: discord.Interaction,
                command: app_commands.Command[Any, ..., Any],
                error: app_commands.AppCommandError,
            ) -> Coroutine[Any, Any, None]:
                return on_group_handler_error(self, interaction, command, error)

        class MyCog(Cog[Any]):
            my_group = MyGroup()
            my_group_with_handler = MyGroupWithHandler()

            @app_commands.command()
            async def my_command(self, interaction: discord.Interaction) -> None:
                ...

            @app_commands.command()
            async def my_command_with_handler(
                self, interaction: discord.Interaction
            ) -> None:
                ...

            @my_command_with_handler.error
            async def on_my_command_with_handler_error(
                self,
                interaction: discord.Interaction,
                error: app_commands.AppCommandError,
            ) -> None:
                await on_command_error(self, interaction, error)

            def cog_app_command_error(
                self,
                interaction: discord.Interaction,
                command: app_commands.Command[Self, ..., Any],
                error: app_commands.AppCommandError,
                /,
            ) -> Coroutine[Any, Any, None]:
                return on_error(self, interaction, command, error)

        interaction = cast(discord.Interaction, object())
        error = app_commands.CheckFailure()

        cog = MyCog(mock_bot)

        assert cog.my_group.on_error is not app_commands.Group.on_error
        assert cog.my_group_with_handler.on_error is not MyGroupWithHandler.on_error
        assert cog.my_command.on_error is not None

        await cog.my_group.my_group_command._invoke_error_handler(interaction, error)
        on_error.assert_awaited_once_with(
            cog, interaction, cog.my_group.my_group_command, error
        )

        on_error.reset_mock()

        await cog.my_group_with_handler.my_group_command._invoke_error_handler(
            interaction, error
        )
        on_group_handler_error.assert_awaited_once_with(
            cog.my_group_with_handler,
            interaction,
            cog.my_group_with_handler.my_group_command,
            error,
        )
        on_error.assert_awaited_once_with(
            cog, interaction, cog.my_group_with_handler.my_group_command, error
        )

        on_error.reset_mock()

        await cog.my_command._invoke_error_handler(interaction, error)
        on_error.assert_awaited_once_with(cog, interaction, cog.my_command, error)

        on_error.reset_mock()

        await cog.my_command_with_handler._invoke_error_handler(interaction, error)
        on_command_error.assert_awaited_once_with(cog, interaction, error)
        on_error.assert_awaited_once_with(
            cog, interaction, cog.my_command_with_handler, error
        )
