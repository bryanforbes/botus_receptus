import asyncio
from typing import List

import discord
import pendulum
import pytest
from attr import attrib, dataclass

from botus_receptus import util

from .types import ClockAdvancer


@dataclass(slots=True)
class MockRole(object):
    id: int = 0
    name: str = ''


@dataclass(slots=True)
class MockMember(object):
    roles: List[MockRole] = attrib(factory=list)


@pytest.fixture
def mock_member() -> MockMember:
    return MockMember(
        roles=[
            MockRole(id=1, name='foo'),
            MockRole(id=2, name='bar'),
            MockRole(id=3, name='baz'),
        ]
    )


def test_has_any_role(mock_member: discord.Member) -> None:
    assert util.has_any_role(mock_member, ['ham', 'spam', 'bar'])
    assert not util.has_any_role(mock_member, ['ham', 'spam', 'blah'])


def test_has_any_role_id(mock_member: discord.Member) -> None:
    assert util.has_any_role_id(mock_member, [2, 4, 18])
    assert not util.has_any_role_id(mock_member, {28, 4, 18})


@pytest.mark.parametrize(
    'duration,expected',
    [
        ('42s', pendulum.duration(seconds=42)),
        ('12m', pendulum.duration(minutes=12)),
        ('20h', pendulum.duration(hours=20)),
        ('7d', pendulum.duration(days=7)),
        ('2w', pendulum.duration(weeks=2)),
        ('1y', pendulum.duration(years=1)),
        ('12m30s', pendulum.duration(seconds=30, minutes=12)),
        ('20h5m', pendulum.duration(hours=20, minutes=5)),
        ('7d10h12s', pendulum.duration(seconds=12, days=7, hours=10)),
        ('2m1y', pendulum.duration(years=1, seconds=120)),
        (' 2m  1y ', pendulum.duration(years=1, seconds=120)),
    ],
)
def test_parse_duration(duration: str, expected: pendulum.Duration) -> None:
    assert util.parse_duration(duration) == expected


@pytest.mark.parametrize(
    'duration,message',
    [
        ('42 s', 'Invalid duration'),
        ('42p', 'Invalid duration'),
        ('invalid', 'Invalid duration'),
        ('', 'No duration provided.'),
        ('   ', 'No duration provided.'),
    ],
)
def test_parse_duration_failures(duration: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        util.parse_duration(duration)


@pytest.mark.asyncio
async def test_race(
    event_loop: asyncio.AbstractEventLoop, advance_time: ClockAdvancer
) -> None:
    async def one() -> int:
        await asyncio.sleep(100, loop=event_loop)
        return 1

    async def two() -> int:
        await asyncio.sleep(50, loop=event_loop)
        return 2

    async def three() -> int:
        await asyncio.sleep(25, loop=event_loop)
        return 3

    task = event_loop.create_task(util.race([one(), two(), three()], loop=event_loop))
    await advance_time(35)
    await advance_time(60)
    await advance_time(110)
    assert task.result() == 3


@pytest.mark.asyncio
async def test_race_timeout(
    event_loop: asyncio.AbstractEventLoop, advance_time: ClockAdvancer
) -> None:
    async def one() -> int:
        await asyncio.sleep(100, loop=event_loop)
        return 1

    async def two() -> int:
        await asyncio.sleep(50, loop=event_loop)
        return 2

    task = event_loop.create_task(
        util.race([one(), two()], timeout=25, loop=event_loop)
    )
    await advance_time(30)
    assert isinstance(task.exception(), asyncio.TimeoutError)
