from __future__ import annotations

from typing import (
    Any,
    Optional,
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
    Generator,
    Awaitable,
    cast,
    overload,
)
import asyncio
import builtins
import discord
import inspect
import pendulum

T = TypeVar('T')
R = TypeVar('R')
FutureT = Union['asyncio.Future[T]', Generator[Any, None, T], Awaitable[T]]


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


@overload
async def maybe_await(object: Awaitable[T]) -> T:
    ...


@overload  # noqa: F811
async def maybe_await(object: T) -> T:
    ...


async def maybe_await(object: Union[Awaitable[T], T]) -> T:  # noqa: F811
    if inspect.isawaitable(object):
        return await object  # type: ignore
    return object  # type: ignore


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


async def wait_for_first(
    futures: Iterable[FutureT[T]],
    *,
    timeout: Optional[float] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> T:
    if loop is None:
        loop = asyncio.get_running_loop()

    tasks = {future for future in futures}

    done, pending = await asyncio.wait(
        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )

    try:
        if len(pending) == len(tasks):
            raise asyncio.TimeoutError()

        return done.pop().result()
    finally:
        for future in pending:
            future.cancel()
