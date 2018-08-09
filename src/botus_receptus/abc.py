from typing import Generic, TypeVar, Union, List
from abc import abstractmethod, ABCMeta
from datetime import datetime
import discord

CT_contra = TypeVar('CT_contra', contravariant=True)


class OnCommandError(Generic[CT_contra]):
    @abstractmethod
    async def on_command_error(self, context: CT_contra, exception: Exception) -> None: ...


class OnCommand(Generic[CT_contra]):
    @abstractmethod
    async def on_command(self, context: CT_contra) -> None: ...


class OnCommandCompletion(Generic[CT_contra]):
    @abstractmethod
    async def on_command_completion(self, context: CT_contra) -> None: ...


class OnMessageDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_message_delete(self, message: discord.Message) -> None: ...


class OnMessageEdit(metaclass=ABCMeta):
    @abstractmethod
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None: ...


class OnReactionAdd(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.User, discord.Member]) -> None: ...


class OnReactionRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_remove(self, reaction: discord.Reaction,
                                 user: Union[discord.User, discord.Member]) -> None: ...


class OnReactionClear(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_clear(self, message: discord.Message,
                                reactions: List[discord.Reaction]) -> None: ...


class OnGuildChannelDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None: ...


class OnGuildChannelCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None: ...


class OnGuildChannelUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel,
                                      after: discord.abc.GuildChannel) -> None: ...


class OnGuildChannelPinsUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_pins_update(self, channel: discord.abc.GuildChannel,
                                           last_pin: datetime) -> None: ...


class OnMemberJoin(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_join(self, member: discord.Member) -> None: ...


class OnMemberRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_remove(self, member: discord.Member) -> None: ...


class OnMemberUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None: ...


class OnGuildJoin(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_join(self, guild: discord.Guild) -> None: ...


class OnGuildRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_remove(self, guild: discord.Guild) -> None: ...


class OnGuildUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None: ...


class OnGuildAvailable(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_available(self, guild: discord.Guild) -> None: ...


class OnGuildUnavailable(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_unavailable(self, guild: discord.Guild) -> None: ...


class OnGuildRoleCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_create(self, role: discord.Role) -> None: ...


class OnGuildRoleDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_delete(self, role: discord.Role) -> None: ...


class OnGuildRoleUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None: ...


class OnGuildEmojisUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_emojis_update(self, guild: discord.Guild, before: List[discord.Emoji],
                                     after: List[discord.Emoji]) -> None: ...


class OnMemberBan(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]) -> None: ...


class OnMemberUnban(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None: ...


class OnVoiceStateUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState) -> None: ...
