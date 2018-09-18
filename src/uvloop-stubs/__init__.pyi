import asyncio
from asyncio.events import BaseDefaultEventLoopPolicy as __BasePolicy
from .loop import Loop as __BaseLoop


class Loop(__BaseLoop, asyncio.AbstractEventLoop):
    ...


def new_event_loop() -> Loop: ...


class EventLoopPolicy(__BasePolicy):
    def _loop_factory(self) -> Loop: ...

    def get_child_watcher(self): ...

    def set_child_watcher(self): ...


__all__ = ('new_event_loop', 'EventLoopPolicy')
