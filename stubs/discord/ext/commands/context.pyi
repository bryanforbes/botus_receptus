from typing import Any, Optional, List, Dict, Union

import discord
from .core import Command
from .bot import Bot


class Context(discord.abc.Messageable):
    message: discord.Message
    bot: Bot
    args: List[Any]
    kwargs: Dict[str, Any]
    prefix: str
    command: Command
    invoked_with: Optional[str]
    invoked_subcommand: Optional[Command]
    subcommand_passed: Optional[str]
    command_failed: bool

    def __init__(self, *, prefix: str, message: discord.Message = ..., bot: Bot = ...,
                 args: List[Any] = ..., kwargs: Dict[str, Any] = ..., command: Command = ...,
                 invoked_with: str = ..., invoked_subcommand: str = ...,
                 subcommand_passed: str = ..., command_failed: bool = ...) -> None: ...

    async def invoke(self, command: Command, *args, **kwargs) -> Any: ...

    @property
    def valid(self) -> bool: ...

    @property
    def guild(self) -> Optional[discord.Guild]: ...

    @property
    def channel(self) -> Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]: ...

    @property
    def author(self) -> Union[discord.Member, discord.User]: ...

    @property
    def me(self) -> Union[discord.Member, discord.ClientUser]: ...

    @property
    def voice_client(self) -> Optional[discord.VoiceClient]: ...
