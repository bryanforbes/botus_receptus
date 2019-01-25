from __future__ import annotations

from typing import (
    Any,
    TypeVar,
    Union,
    Container,
    Dict,
    Tuple,
    List,
    Iterable,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Coroutine,
    cast,
)
import asyncio
import discord
import pendulum
import builtins

T = TypeVar('T')
R = TypeVar('R')


def has_any_role(member: discord.Member, roles: Container[str]) -> bool:
    return discord.utils.find(lambda role: role.name in roles, member.roles) is not None


def has_any_role_id(member: discord.Member, ids: Container[int]) -> bool:
    return discord.utils.find(lambda role: role.id in ids, member.roles) is not None


UNITS = {
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
    'd': 'days',
    'w': 'weeks',
    'y': 'years',
}


# Adapted from https://github.com/python-discord/site/blob/master/pysite/utils/time.py
def parse_duration(duration: str) -> pendulum.Duration:
    duration = duration.strip()

    if not duration:
        raise ValueError('No duration provided.')

    args: Dict[str, int] = {}
    digits = ''

    for char in duration:
        if char.isdigit():
            digits += char
            continue

        if char == ' ':
            if len(digits) > 0:
                raise ValueError('Invalid duration')

            continue  # pragma: no cover

        if char not in UNITS or not digits:
            raise ValueError('Invalid duration')

        args[UNITS[char]] = int(digits)
        digits = ''

    return pendulum.duration(**args)


async def maybe_await(object: Any) -> Any:
    if asyncio.iscoroutine(object):
        return await object
    else:
        return object


SyncOrAsyncIterable = Union[Iterable[T], AsyncIterable[T]]
SyncOrAsyncIterableIterable = Union[
    Iterable[SyncOrAsyncIterable[T]], AsyncIterable[SyncOrAsyncIterable[T]]
]
SyncOrAsyncFunction = Union[Callable[..., R], Callable[..., Coroutine[Any, Any, R]]]


def iter(iterable: SyncOrAsyncIterable[T]) -> AsyncIterator[T]:
    if isinstance(iterable, AsyncIterator):
        return iterable

    if isinstance(iterable, AsyncIterable):
        return iterable.__aiter__()

    async def gen() -> AsyncIterator[T]:
        for item in cast(Iterable[T], iterable):
            yield item

    return gen()


async def list(iterable: SyncOrAsyncIterable[T]) -> List[T]:
    return [item async for item in iter(iterable)]


async def tuple(iterable: SyncOrAsyncIterable[T]) -> Tuple[T, ...]:
    return builtins.tuple([item async for item in iter(iterable)])


async def enumerate(
    iterable: SyncOrAsyncIterable[T], start: int = 0
) -> AsyncIterator[Tuple[int, T]]:
    async for item in iter(iterable):
        yield start, item
        start += 1


async def starmap(
    fn: SyncOrAsyncFunction[R], iterable: SyncOrAsyncIterable[Iterable[T]]
) -> AsyncIterator[R]:
    async for inner_iterable in iter(iterable):
        args = await list(inner_iterable)
        result = fn(*args)
        yield await maybe_await(result)
