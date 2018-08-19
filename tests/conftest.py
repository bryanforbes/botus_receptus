from __future__ import annotations

from typing import Any

import pytest  # type: ignore
import pytest_mock  # type: ignore
import asynctest.mock  # type: ignore

pytest_mock._get_mock_module._module = asynctest.mock


@pytest.fixture
def mock_aiohttp(mocker: Any) -> None:
    mocker.patch('aiohttp.ClientSession')


@pytest.fixture(autouse=True)
def add_async_mocks(mocker: Any) -> None:
    mocker.CoroutineMock = mocker.mock_module.CoroutineMock
