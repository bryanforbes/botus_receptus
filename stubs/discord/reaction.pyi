from typing import Union, Optional, Any
from mypy_extensions import TypedDict

from .member import Member
from .message import Message
from .emoji import Emoji
from .iterators import ReactionIterator


class _RequiredReactionData(TypedDict):
    me: bool


class _ReactionData(_RequiredReactionData, total=False):
    count: int


class Reaction:
    message: Message
    count: int
    emoji: Union[Emoji, str]
    me: bool

    def __init__(self, *, message: Message, data: _ReactionData, emoji: Optional[Emoji] = ...) -> None: ...

    @property
    def custom_emoji(self) -> bool: ...

    def __eq__(self, other: Any) -> bool: ...

    def __ne__(self, other: Any) -> bool: ...

    def __hash__(self) -> int: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def users(self, limit: Optional[int] = ..., after: Optional[Member] = ...) -> ReactionIterator: ...
