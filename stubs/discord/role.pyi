from typing import Any, List, Optional
from datetime import datetime
from .mixins import Hashable
from .permissions import Permissions
from .member import Member
from .colour import Colour
from .guild import Guild


class Role(Hashable):
    id: int
    name: str
    permissions: Permissions
    guild: Guild
    colour: Colour
    color: Colour
    hoist: bool
    position: int
    managed: bool
    mentionable: bool

    def __lt__(self, other: Any) -> bool: ...

    def __le__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...

    def __ge__(self, other: Any) -> bool: ...

    @property
    def created_at(self) -> datetime: ...

    @property
    def mention(self) -> str: ...

    @property
    def members(self) -> List[Member]: ...

    async def edit(self, *, name: str, permissions: Any, colour: Any, hoist: bool, mentionable: bool,
                   position: int, reason: Optional[str] = ...) -> None: ...

    async def delete(self, *, reason: Optional[str] = ...) -> None: ...
