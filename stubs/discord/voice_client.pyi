from typing import Optional, Callable
from asyncio import AbstractEventLoop
from .abc import Connectable
from .guild import Guild
from .user import ClientUser
from .channel import VoiceChannel
from .player import AudioSource


class VoiceClient:
    session_id: str
    token: str
    endpoint: str
    channel: Connectable
    loop: AbstractEventLoop
    source: Optional[AudioSource]

    @property
    def guild(self) -> Optional[Guild]: ...

    @property
    def user(self) -> ClientUser: ...

    async def disconnect(self, *, force: bool = ...) -> None: ...

    async def move(self, channel: VoiceChannel) -> None: ...

    def is_connected(self) -> bool: ...

    def play(self, source: AudioSource, *, after: Optional[Callable[[Optional[Exception]], None]] = ...) -> None: ...

    def is_playing(self) -> bool: ...

    def is_paused(self) -> bool: ...

    def stop(self) -> None: ...

    def pause(self) -> None: ...

    def resume(self) -> None: ...

    def send_audio_packet(self, data: bytes, *, encode: bool = ...) -> None: ...
