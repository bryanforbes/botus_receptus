from typing import Optional, List
from .abc import Messageable, GuildChannel, Connectable
from .mixins import Hashable
from .member import Member
from .voice_client import VoiceClient


class TextChannel(Messageable, GuildChannel, Hashable):
    id: int
    category_id: int
    topic: Optional[str]

    def is_nsfw(self) -> bool: ...


class VoiceChannel(Connectable, GuildChannel, Hashable):
    bitrate: int
    user_limit: int
    members: List[Member]

    async def connect(self, *, timeout: float = ..., reconnect: bool = ...) -> VoiceClient: ...


class CategoryChannel(GuildChannel, Hashable):
    ...


class DMChannel(Messageable, Hashable):
    ...


class GroupChannel(Messageable, Hashable):
    ...
