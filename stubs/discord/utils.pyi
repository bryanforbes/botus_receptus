from typing import Optional, TypeVar, Callable, Iterable, Any
from datetime import datetime
from .permissions import Permissions
from .guild import Guild


DISCORD_EPOCH: int


def oauth_url(client_id: str,
              permissions: Optional[Permissions] = ...,
              guild: Optional[Guild] = ...,
              redirect_uri: Optional[str] = ...) -> str: ...


def snowflake_time(id: int) -> datetime: ...


T = TypeVar('T')


def find(predicate: Callable[[T], bool], seq: Iterable[T]) -> Optional[T]: ...


def get(iterable: Iterable[T], **attrs: Any) -> Optional[T]: ...
