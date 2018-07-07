from typing import Any
from .context import Context
from ...member import Member
from ...user import User
from ...channel import TextChannel, VoiceChannel, CategoryChannel
from ...colour import Colour
from ...role import Role
from ...activity import Game
from ...invite import Invite
from ...emoji import Emoji, PartialEmoji


class Converter:
    async def convert(self, ctx: Context, argument: str) -> Any: ...


class IDConverter(Converter):
    ...


class MemberConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> Member: ...


class UserConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> User: ...


class TextChannelConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> TextChannel: ...


class VoiceChannelConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> VoiceChannel: ...


class CategoryChannelConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> CategoryChannel: ...


class ColourConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> Colour: ...


class RoleConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> Role: ...


class GameConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> Game: ...


class InviteConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> Invite: ...


class EmojiConverter(IDConverter):
    async def convert(self, ctx: Context, argument: str) -> Emoji: ...


class PartialEmojiConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> PartialEmoji: ...


class clean_content(Converter):
    def __init__(self, *, fix_channel_mentions: bool = ...,
                 use_nicknames: bool = ..., escape_markdown: bool = ...) -> None: ...

    async def convert(self, ctx: Context, argument: str) -> str: ...
