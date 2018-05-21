from typing import (
    TYPE_CHECKING, AsyncContextManager, Awaitable, Any, Generator, Optional, Callable, List, Sequence, Tuple, Dict
)
from asyncpg import Connection
from discord.ext import commands
from mypy_extensions import VarArg, DefaultNamedArg, NamedArg

import attr

from . import util

if TYPE_CHECKING:
    from .bot import Bot  # noqa


@attr.s(slots=True, auto_attribs=True)
class AquireContextManager(AsyncContextManager[Connection], Awaitable[Connection]):
    ctx: 'Context'
    timeout: Optional[float] = None

    def __await__(self) -> Generator[Any, None, Connection]:
        return self.ctx._acquire(self.timeout).__await__()

    async def __aenter__(self) -> Connection:
        return await self.ctx._acquire(self.timeout)

    async def __aexit__(self, *args: Any) -> None:
        await self.ctx.release()


def dbmethod(name: str) -> Callable[..., Awaitable[Any]]:
    async def method_wrapper(self: 'Context', *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, 'db'):
            raise RuntimeError('No database object available; ensure acquire() was called')

        return await getattr(util, name)(self.db, *args, **kwargs)

    return method_wrapper


class Context(commands.Context):
    bot: 'Bot'
    db: Connection

    async def _acquire(self, timeout: Optional[float]) -> Connection:
        if not hasattr(self, 'db'):
            self.db = await self.bot.pool.acquire(timeout=timeout)

        return self.db

    def acquire(self, *, timeout: Optional[float] = None) -> AquireContextManager:
        return AquireContextManager(self, timeout)

    async def release(self) -> None:
        if hasattr(self, 'db'):
            await self.bot.pool.release(self.db)
            del self.db

    select_all: Callable[
        [VarArg(Any),
         DefaultNamedArg(Optional[Sequence[str]], 'columns'),
         NamedArg(str, 'table'),
         DefaultNamedArg(Optional[str], 'order_by'),
         DefaultNamedArg(Optional[Sequence[str]], 'where'),
         DefaultNamedArg(Optional[Sequence[Tuple[str, str]]], 'joins')],
        Awaitable[List[Any]]] = dbmethod('select_all')
    select_one: Callable[
        [VarArg(Any),
         DefaultNamedArg(Optional[Sequence[str]], 'columns'),
         NamedArg(str, 'table'),
         DefaultNamedArg(Optional[Sequence[str]], 'where'),
         DefaultNamedArg(Optional[Sequence[Tuple[str, str]]], 'joins')],
        Awaitable[Any]] = dbmethod('select_one')
    search: Callable[
        [VarArg(Any),
         DefaultNamedArg(Optional[Sequence[str]], 'columns'),
         NamedArg(str, 'table'),
         NamedArg(Sequence[str], 'search_columns'),
         NamedArg(Sequence[str], 'terms'),
         DefaultNamedArg(Optional[str], 'order_by'),
         DefaultNamedArg(Optional[Sequence[str]], 'where'),
         DefaultNamedArg(Optional[Sequence[Tuple[str, str]]], 'joins')],
        Awaitable[List[Any]]] = dbmethod('search')
    insert_into: Callable[
        [NamedArg(str, 'table'),
         NamedArg(Dict[str, Any], 'values'),
         DefaultNamedArg(str, 'extra')],
        Awaitable[None]] = dbmethod('insert_into')
    delete_from: Callable[
        [VarArg(Any),
         NamedArg(str, 'table'),
         NamedArg(Sequence[str], 'where')],
        Awaitable[None]] = dbmethod('delete_from')
