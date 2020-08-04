from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from unittest.mock import Mock

from attr import attrib, dataclass

from .types import CoroutineMock, Mocker


@dataclass(slots=True)
class MockUser(object):
    id: int
    bot: Optional[bool] = None
    mention: Optional[str] = None


@dataclass(slots=True)
class MockPermissions(object):
    embed_links: bool = True
    send_messages: bool = True
    add_reactions: bool = True
    read_message_history: bool = True
    manage_messages: bool = True


@dataclass(slots=True)
class MockGuild(object):
    me: Optional[MockUser] = None
    owner: Optional[MockUser] = None


@dataclass
class MockChannel(object):
    permissions_for: Mock = attrib(init=False)
    send: CoroutineMock = attrib(init=False)
    delete_messages: CoroutineMock = attrib(init=False)

    @staticmethod
    def create(
        mocker: Mocker, permissions: MockPermissions, bot_user: MockUser
    ) -> MockChannel:
        channel = MockChannel()

        def send_side_effect(*args: Any, **kwargs: Any) -> Any:
            return MockMessage.create(mocker, 11, bot_user, channel, '')

        channel.permissions_for = mocker.Mock(return_value=permissions)
        channel.send = mocker.CoroutineMock(side_effect=send_side_effect)
        channel.delete_messages = mocker.CoroutineMock()

        return channel


@dataclass
class MockBot(object):
    user: MockUser
    loop: Any
    advance_time: Callable[[float], Awaitable[None]]
    _listeners: Dict[
        str, List[Tuple['asyncio.Future[Any]', Callable[..., Any]]]
    ] = attrib(factory=dict)

    async def _dispatch_wait_for(self, event: str, *args: Any) -> None:
        listeners = self._listeners.setdefault(event, [])

        if listeners:
            removed = []
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
        check: Optional[Callable[..., Any]] = None,
        timeout: Optional[float] = None,
    ) -> 'asyncio.Future[Any]':
        future = self.loop.create_future()

        if check is None:

            def _check(*args: Any) -> bool:
                return True

            check = _check

        ev = event.lower()
        listeners = self._listeners.setdefault(ev, [])
        listeners.append((future, check))

        return asyncio.wait_for(future, timeout, loop=self.loop)

    @staticmethod
    def create(
        mocker: Mocker,
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

    async def edit(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def remove_reaction(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def delete(self, *args: Any, **kwargs: Any) -> None:
        pass

    @staticmethod
    def create(
        mocker: Mocker, id: int, author: MockUser, channel: MockChannel, content: str
    ) -> MockMessage:
        message = MockMessage(
            id=id,
            author=author,
            channel=channel,
            content=content,
            add_reaction=mocker.CoroutineMock(return_value=None),
            clear_reactions=mocker.CoroutineMock(return_value=None),
        )
        mocker.patch.object(message, 'edit', return_value=None)
        mocker.patch.object(message, 'remove_reaction', return_value=None)
        mocker.patch.object(message, 'delete', return_value=None)
        return message


@dataclass(slots=True)
class MockContext(object):
    bot: MockBot
    author: MockUser
    message: MockMessage
    channel: MockChannel
    guild: Optional[MockGuild]

    @staticmethod
    def create(
        mocker: Mocker,
        event_loop: Any,
        advance_time: Callable[[float], Awaitable[None]],
        bot_user: MockUser,
        permissions: MockPermissions,
        guild: Optional[MockGuild] = None,
    ) -> MockContext:
        author = MockUser(id=1)
        channel = MockChannel.create(mocker, permissions, bot_user)
        message = MockMessage.create(mocker, 10, author, channel, 'foo')

        return MockContext(
            bot=MockBot.create(mocker, bot_user, event_loop, advance_time),
            author=author,
            message=message,
            channel=channel,
            guild=guild,
        )
