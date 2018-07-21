from typing import Any, Optional, List, Union
from .abc import User as _BaseUser, Messageable, GuildChannel
from .activity import Activity, Game, Streaming, Spotify
from .enums import Status
from .colour import Colour
from .message import Message
from .role import Role
from .permissions import Permissions
from .channel import VoiceChannel
from .guild import Guild
from datetime import datetime


class VoiceState:
    deaf: bool
    mute: bool
    self_mute: bool
    self_deaf: bool
    afk: bool
    channel: VoiceChannel


class Member(Messageable, _BaseUser):
    roles: List[Role]
    joined_at: datetime
    status: Status
    activity: Union[Activity, Game, Streaming, Spotify]
    nick: Optional[str]
    guild: Guild

    # From BaseUser:
    name: str
    id: int
    discriminator: str
    avatar: Optional[str]
    bot: bool

    @property
    def avatar_url(self) -> str: ...

    def is_avatar_animated(self) -> bool: ...

    def avatar_url_as(self, *, format: Optional[str] = ..., static_format: str = ...,
                      size: int = ...) -> str: ...

    @property
    def default_avatar(self) -> str: ...

    @property
    def default_avatar_url(self) -> str: ...

    @property
    def mention(self) -> str: ...

    def permissions_in(self, channel: GuildChannel) -> Permissions: ...

    @property
    def created_at(self) -> datetime: ...

    @property
    def display_name(self) -> str: ...

    def mentioned_in(self, message: Message) -> bool: ...
    # End From: BaseUser

    def __eq__(self, other: Any) -> bool: ...

    def __ne__(self, other: Any) -> bool: ...

    def __hash__(self) -> int: ...

    @property
    def colour(self) -> Colour: ...

    color = colour

    @property
    def top_role(self) -> Role: ...

    @property
    def guild_permissions(self) -> Permissions: ...

    @property
    def voice(self) -> VoiceState: ...

    async def ban(self, *, reason: Optional[str] = ..., delete_message_days: int = ...) -> None: ...

    async def unban(self, *, reason: Optional[str] = ...) -> None: ...

    async def kick(self, *, reason: Optional[str] = ...) -> None: ...

    async def edit(self, *, reason: Optional[str] = ..., nick: Optional[str] = ..., mute: bool = ...,
                   deafen: bool = ..., roles: List[Role] = ..., voice_channel: VoiceChannel = ...) -> None: ...

    async def move_to(self, channel: VoiceChannel, *, reason: Optional[str] = ...) -> None: ...

    async def add_roles(self, *roles: Role, reason: Optional[str] = ..., atomic: bool = ...) -> None: ...

    async def remove_roles(self, *roles: Role, reason: Optional[str] = ..., atomic: bool = ...) -> None: ...
