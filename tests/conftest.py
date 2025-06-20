from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, final

import pytest
import pytest_asyncio

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop

    from .types import MockerFixture


@final
class EventLoopClockAdvancer:
    """
    A helper object that when called will advance the event loop's time. If the
    call is awaited, the caller task will wait an iteration for the update to
    wake up any awaiting handlers.
    """

    __slots__ = ('_base_time', 'loop', 'offset', 'sleep_duration')

    def __init__(self, loop: AbstractEventLoop, sleep_duration: float = 1e-4) -> None:
        self.offset = 0.0
        self._base_time = loop.time
        self.loop = loop
        self.sleep_duration = sleep_duration

        # incorporate offset timing into the event loop
        self.loop.time = self.time

    def time(self) -> float:
        """
        Return the time according to the event loop's clock. The time is
        adjusted by an offset.
        """
        return self._base_time() + self.offset

    async def __call__(self, seconds: float) -> None:
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


@pytest_asyncio.fixture
async def advance_time() -> EventLoopClockAdvancer:
    return EventLoopClockAdvancer(asyncio.get_running_loop())


@pytest.fixture
def mock_aiohttp(mocker: MockerFixture) -> None:
    mocker.patch('aiohttp.ClientSession', autospec=True)


@pytest.fixture
def mock_discord_bot(mocker: MockerFixture) -> None:
    mocker.patch('discord.ext.commands.Bot')
