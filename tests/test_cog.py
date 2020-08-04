from typing import Any
from unittest.mock import Mock

import pytest
from discord.ext import commands

from botus_receptus import Bot, Cog


class MockBot(object):
    ...


class TestCog(object):
    @pytest.fixture
    def mock_bot(self) -> MockBot:
        return MockBot()

    @pytest.fixture
    def mock_cog(self, mocker: Any) -> Cog[commands.Context]:
        return Cog()

    @pytest.fixture
    def pre_inject_spy(self, mocker: Any, mock_cog: Cog[commands.Context]) -> Any:
        return mocker.spy(mock_cog, '__pre_inject__')

    @pytest.fixture
    def post_inject_spy(self, mocker: Any, mock_cog: Cog[commands.Context]) -> Any:
        return mocker.spy(mock_cog, '__post_inject__')

    @pytest.fixture
    def pre_eject_spy(self, mocker: Any, mock_cog: Cog[commands.Context]) -> Any:
        return mocker.spy(mock_cog, '__pre_eject__')

    @pytest.fixture
    def post_eject_spy(self, mocker: Any, mock_cog: Cog[commands.Context]) -> Any:
        return mocker.spy(mock_cog, '__post_eject__')

    def test_inject(self, mock_bot: Bot[commands.Context]) -> None:
        cog: Cog[commands.Context] = Cog()
        result = cog._inject(mock_bot)

        assert result is cog

    def test_inject_methods(
        self,
        mock_bot: Bot[commands.Context],
        mock_cog: Cog[commands.Context],
        pre_inject_spy: Mock,
        post_inject_spy: Mock,
    ) -> None:
        mock_cog._inject(mock_bot)

        pre_inject_spy.assert_called_once()
        post_inject_spy.assert_called_once()

    def test_eject(self, mock_bot: Bot[commands.Context]) -> None:
        cog: Cog[commands.Context] = Cog()
        cog._eject(mock_bot)

    def test_eject_methods(
        self,
        mock_bot: Bot[commands.Context],
        mock_cog: Cog[commands.Context],
        pre_eject_spy: Mock,
        post_eject_spy: Mock,
    ) -> None:
        mock_cog._eject(mock_bot)

        pre_eject_spy.assert_called_once()
        post_eject_spy.assert_called_once()
