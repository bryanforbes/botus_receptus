import pytest  # type: ignore
import attr
import pendulum  # type: ignore
from typing import AsyncIterator
import asyncio

from botus_receptus.util import (
    has_any_role,
    has_any_role_id,
    parse_duration,
    iter as util_iter,
    enumerate,
    starmap,
    list as util_list,
    tuple as util_tuple,
    maybe_await,
    wait_for_first,
)


@attr.s(slots=True, auto_attribs=True)
class MockRole(object):
    id: int = 0
    name: str = ''


@attr.s(slots=True)
class MockMember(object):
    roles = attr.ib(default=attr.Factory(list))


class async_iterator:
    def __init__(self, items):
        self.iter = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class async_iterable:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return async_iterator(self.items)


def concat(*args):
    return ''.join(args)


async def async_concat(*args):
    return ''.join(args)


async def gen():
    yield ['A', 'B']
    yield ['B', 'C']
    yield ['A', 'B', 'C']


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
async def test_maybe_await():
    assert (await maybe_await(4)) == 4


@pytest.mark.asyncio
async def test_maybe_await_coroutine():
    async def func():
        return 4

    assert (await maybe_await(func())) == 4


@pytest.mark.asyncio
async def test_iter_list():
    items = ['A', 'B', 'C']
    aitems = util_iter(items)

    assert isinstance(aitems, AsyncIterator)

    assert [item async for item in aitems] == items


@pytest.mark.asyncio
async def test_iter_range():
    items = range(3)
    aitems = util_iter(items)

    assert isinstance(aitems, AsyncIterator)

    assert [item async for item in aitems] == list(items)


@pytest.mark.asyncio
async def test_iter_async_iterable():
    items = ['A', 'B', 'C']

    assert [item async for item in util_iter(async_iterable(items))] == items


@pytest.mark.asyncio
async def test_iter_async_iterator():
    items = ['A', 'B', 'C']

    assert [item async for item in util_iter(async_iterator(items))] == items


@pytest.mark.asyncio
async def test_iter_async_generator():
    async def async_gen():
        yield 1
        yield 2

    assert [item async for item in util_iter(async_gen())] == [1, 2]


@pytest.mark.asyncio
async def test_list():
    assert (await util_list(('A', 'B', 'C'))) == ['A', 'B', 'C']


@pytest.mark.asyncio
async def test_tuple():
    assert (await util_tuple(['A', 'B', 'C'])) == ('A', 'B', 'C')


@pytest.mark.asyncio
async def test_enumerate():
    assert [item async for item in enumerate(['A', 'B', 'C'])] == [
        (0, 'A'),
        (1, 'B'),
        (2, 'C'),
    ]


@pytest.mark.asyncio
async def test_enumerate_start():
    assert [item async for item in enumerate(['A', 'B', 'C'], 4)] == [
        (4, 'A'),
        (5, 'B'),
        (6, 'C'),
    ]


@pytest.mark.parametrize(
    'concat,data',
    [
        (concat, [['A', 'B'], ['B', 'C'], ['A', 'B', 'C']]),
        (async_concat, [['A', 'B'], ['B', 'C'], ['A', 'B', 'C']]),
        (concat, gen()),
        (async_concat, gen()),
    ],
)
@pytest.mark.asyncio
async def test_starmap(concat, data):
    assert [item async for item in starmap(concat, data)] == ['AB', 'BC', 'ABC']


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
