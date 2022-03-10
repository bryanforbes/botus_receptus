from __future__ import annotations

import asyncio
from typing import Final, TypeVar

import discord
import pendulum
from pendulum.duration import Duration

from .compat import Awaitable, Container, Iterable, dict

T = TypeVar('T')


def has_any_role(member: discord.Member, roles: Container[str], /) -> bool:
    return discord.utils.find(lambda role: role.name in roles, member.roles) is not None


def has_any_role_id(member: discord.Member, ids: Container[int], /) -> bool:
    return discord.utils.find(lambda role: role.id in ids, member.roles) is not None


UNITS: Final = {
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
    'd': 'days',
    'w': 'weeks',
    'y': 'years',
}


# Adapted from https://github.com/python-discord/site/blob/master/pysite/utils/time.py
def parse_duration(duration: str, /) -> Duration:
    duration = duration.strip()

    if not duration:
        raise ValueError('No duration provided.')

    args: dict[str, int] = {}
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


async def race(
    futures: Iterable[asyncio.Future[T] | Awaitable[T]],
    /,
    *,
    timeout: float | None = None,
) -> T:
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
