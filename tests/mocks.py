from __future__ import annotations

import asyncio
import builtins
from typing import Any
from unittest.mock import AsyncMock, Mock

from attr import attrib, dataclass

from botus_receptus.compat import Awaitable, Callable, dict, list, tuple

from .types import MockerFixture


@dataclass(slots=True)
class MockUser(object):
    id: int
    bot: bool | None = None
    mention: str | None = None


@dataclass(slots=True)
class MockPermissions(object):
    embed_links: bool = True
    send_messages: bool = True
    add_reactions: bool = True
    read_message_history: bool = True
    manage_messages: bool = True


@dataclass(slots=True)
class MockGuild(object):
    me: MockUser | None = None
    owner: MockUser | None = None


@dataclass
class MockChannel(object):
    permissions_for: Mock = attrib(init=False)
    send: AsyncMock = attrib(init=False)
    delete_messages: AsyncMock = attrib(init=False)

    @staticmethod
    def create(
        mocker: MockerFixture,
        permissions: MockPermissions,
    ) -> MockChannel:
        channel = MockChannel()

        channel.permissions_for = mocker.Mock(return_value=permissions)
        channel.send = mocker.AsyncMock()
        channel.delete_messages = mocker.AsyncMock()

        return channel


@dataclass
class MockBot(object):
    user: MockUser
    loop: Any
    advance_time: Callable[[float], Awaitable[None]]
    _listeners: dict[
        str, list[tuple[asyncio.Future[Any], Callable[..., Any]]]
    ] = attrib(factory=builtins.dict)

    async def _dispatch_wait_for(self, event: str, *args: Any) -> None:
        listeners = self._listeners.setdefault(event, [])

        if listeners:
            removed: list[int] = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        await self.advance_time(0)

    def wait_for(
        self,
        event: str,
        *,
        check: Callable[..., Any] | None = None,
        timeout: float | None = None,
    ) -> Awaitable[Any]:
        future = self.loop.create_future()

        if check is None:

            def _check(*args: Any) -> bool:
                return True

            check = _check

        ev = event.lower()
        listeners = self._listeners.setdefault(ev, [])
        listeners.append((future, check))

        return asyncio.wait_for(future, timeout)

    @staticmethod
    def create(
        mocker: MockerFixture,
        user: MockUser,
        loop: Any,
        advance_time: Callable[[float], Awaitable[None]],
    ) -> MockBot:
        return MockBot(user=user, loop=loop, advance_time=advance_time)


@dataclass
class MockMessage(object):
    id: int
    author: MockUser
    channel: MockChannel
    content: str
    add_reaction: Any
    clear_reactions: Any

    edit: AsyncMock
    remove_reaction: AsyncMock
    delete: AsyncMock

    @staticmethod
    def create(
        mocker: MockerFixture,
        id: int,
        author: MockUser,
        channel: MockChannel,
        content: str,
    ) -> MockMessage:
        message = MockMessage(
            id=id,
            author=author,
            channel=channel,
            content=content,
            add_reaction=mocker.AsyncMock(return_value=None),
            clear_reactions=mocker.AsyncMock(return_value=None),
            edit=mocker.AsyncMock(return_value=None),
            remove_reaction=mocker.AsyncMock(return_value=None),
            delete=mocker.AsyncMock(return_value=None),
        )
        return message


@dataclass(slots=True)
class MockContext(object):
    bot: MockBot
    author: MockUser
    message: MockMessage
    channel: MockChannel
    guild: MockGuild | None

    @staticmethod
    def create(
        mocker: MockerFixture,
        event_loop: Any,
        advance_time: Callable[[float], Awaitable[None]],
        bot_user: MockUser,
        permissions: MockPermissions,
        guild: MockGuild | None = None,
    ) -> MockContext:
        author = MockUser(id=1)
        channel = MockChannel.create(mocker, permissions)
        message = MockMessage.create(mocker, 10, author, channel, 'foo')

        return MockContext(
            bot=MockBot.create(mocker, bot_user, event_loop, advance_time),
            author=author,
            message=message,
            channel=channel,
            guild=guild,
        )
