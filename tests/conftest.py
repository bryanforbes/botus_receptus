from __future__ import annotations

from typing import Any

import pytest  # type: ignore
import pytest_mock  # type: ignore
import asynctest.mock  # type: ignore

pytest_mock._get_mock_module._module = asynctest.mock


def pytest_configure():
    workaround_sugar_issue_159()


def workaround_sugar_issue_159():
    "https://github.com/Frozenball/pytest-sugar/issues/159"
    import pytest_sugar

    pytest_sugar.SugarTerminalReporter.pytest_runtest_logfinish = lambda self: None


@pytest.fixture
def mock_aiohttp(mocker: Any) -> None:
    mocker.patch('aiohttp.ClientSession', autospec=True)


@pytest.fixture
def mock_discord_bot(mocker: Any) -> None:
    mocker.patch('discord.ext.commands.Bot')


@pytest.fixture(autouse=True)
def add_async_mocks(mocker: Any) -> None:
    mocker.CoroutineMock = mocker.mock_module.CoroutineMock
