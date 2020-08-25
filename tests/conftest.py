from __future__ import annotations

import asyncio
from typing import Any

import asynctest.mock  # type: ignore
import pytest  # type: ignore
import pytest_mock.plugin  # type: ignore

pytest_mock.plugin._get_mock_module._module = asynctest.mock


class EventLoopClockAdvancer:
    """
    A helper object that when called will advance the event loop's time. If the
    call is awaited, the caller task will wait an iteration for the update to
    wake up any awaiting handlers.
    """

    __slots__ = ("offset", "loop", "sleep_duration", "_base_time")

    def __init__(self, loop, sleep_duration=1e-4):
        self.offset = 0.0
        self._base_time = loop.time
        self.loop = loop
        self.sleep_duration = sleep_duration

        # incorporate offset timing into the event loop
        self.loop.time = self.time

    def time(self):
        """
        Return the time according to the event loop's clock. The time is
        adjusted by an offset.
        """
        return self._base_time() + self.offset

    async def __call__(self, seconds):
        """
        Advance time by a given offset in seconds. Returns an awaitable
        that will complete after all tasks scheduled for after advancement
        of time are proceeding.
        """
        # sleep so that the loop does everything currently waiting
        await asyncio.sleep(self.sleep_duration)

        if seconds > 0:
            # advance the clock by the given offset
            self.offset += seconds

            # Once the clock is adjusted, new tasks may have just been
            # scheduled for running in the next pass through the event loop
            await asyncio.sleep(self.sleep_duration)


@pytest.fixture
def advance_time(event_loop):
    return EventLoopClockAdvancer(event_loop)


@pytest.fixture
def mock_aiohttp(mocker: Any) -> None:
    mocker.patch('aiohttp.ClientSession', autospec=True)


@pytest.fixture
def mock_discord_bot(mocker: Any) -> None:
    mocker.patch('discord.ext.commands.Bot')


@pytest.fixture(autouse=True)
def add_async_mocks(mocker: Any) -> None:
    mocker.CoroutineMock = mocker.mock_module.CoroutineMock
