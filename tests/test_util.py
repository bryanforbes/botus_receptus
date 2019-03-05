import pytest  # type: ignore
import pendulum  # type: ignore
import asyncio

from typing import List
from dataclasses import dataclass, field
from dataslots import with_slots
from botus_receptus.util import (
    has_any_role,
    has_any_role_id,
    parse_duration,
    wait_for_first,
)


@with_slots
@dataclass
class MockRole(object):
    id: int = 0
    name: str = ''


@with_slots
@dataclass
class MockMember(object):
    roles: List[MockRole] = field(default_factory=list)


def test_has_any_role() -> None:
    assert has_any_role(
        MockMember(
            roles=[MockRole(name='foo'), MockRole(name='bar'), MockRole(name='baz')]
        ),
        ['ham', 'spam', 'bar'],
    )
    assert not has_any_role(
        MockMember(
            roles=[MockRole(name='foo'), MockRole(name='bar'), MockRole(name='baz')]
        ),
        ['ham', 'spam', 'blah'],
    )


def test_has_any_role_id() -> None:
    assert has_any_role_id(
        MockMember(roles=[MockRole(id=1), MockRole(id=2), MockRole(id=3)]), [2, 4, 18]
    )
    assert not has_any_role_id(
        MockMember(roles=[MockRole(id=1), MockRole(id=2), MockRole(id=3)]), {28, 4, 18}
    )


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
def test_parse_duration(duration, expected):
    assert parse_duration(duration) == expected


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
def test_parse_duration_failures(duration, message):
    with pytest.raises(ValueError, message=message):
        parse_duration(duration)


@pytest.mark.asyncio
async def test_wait_for_first():
    async def one():
        await asyncio.sleep(5)
        return 1

    async def two():
        await asyncio.sleep(3)
        return 2

    async def three():
        await asyncio.sleep(0.1)
        return 3

    result = await wait_for_first([one(), two(), three()])
    assert result == 3


@pytest.mark.asyncio
async def test_wait_for_first_timeout(event_loop):
    async def one():
        await asyncio.sleep(5)
        return 1

    async def two():
        await asyncio.sleep(3)
        return 2

    with pytest.raises(asyncio.TimeoutError):
        await wait_for_first([one(), two()], timeout=0.1, loop=event_loop)
