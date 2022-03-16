from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock

import discord
import pytest
from pytest_mock import MockerFixture

from botus_receptus import Bot, Cog


class MockBot(object):
    ...


class TestCog(object):
    @pytest.fixture
    def mock_bot(self) -> MockBot:
        return MockBot()

    @pytest.fixture
    def mock_cog(self, mocker: Any) -> Cog:
        return Cog()

    async def test_inject(self, mock_bot: Bot) -> None:
        cog = Cog()
        result = await cog._inject(
            mock_bot, override=False, guild=discord.utils.MISSING, guilds=[]
        )

        assert result is cog

    @pytest.mark.parametrize('async_methods', [True, False])
    async def test_inject_methods(
        self,
        mock_bot: Bot,
        mock_cog: Cog,
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
        cog: Cog = Cog()
        await cog._eject(mock_bot, guild_ids=[])

    @pytest.mark.parametrize('async_methods', [True, False])
    async def test_eject_methods(
        self,
        mock_bot: Bot,
        mock_cog: Cog,
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
