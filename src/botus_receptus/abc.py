from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generic, List, Optional, TypeVar, Union

import discord

CT_contra = TypeVar('CT_contra', contravariant=True)


TextChannel = Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]
GuildChannel = Union[
    discord.TextChannel,
    discord.VoiceChannel,
    discord.CategoryChannel,
    discord.StoreChannel,
]
PrivateChannel = Union[discord.DMChannel, discord.GroupChannel]
User = Union[discord.User, discord.Member]


class OnCommandError(Generic[CT_contra]):
    @abstractmethod
    async def on_command_error(self, context: CT_contra, exception: Exception) -> None:
        ...


class OnCommand(Generic[CT_contra]):
    @abstractmethod
    async def on_command(self, context: CT_contra) -> None:
        ...


class OnCommandCompletion(Generic[CT_contra]):
    @abstractmethod
    async def on_command_completion(self, context: CT_contra) -> None:
        ...


class OnConnect(metaclass=ABCMeta):
    @abstractmethod
    async def on_connect(self) -> None:
        ...


class OnDisconnect(metaclass=ABCMeta):
    @abstractmethod
    async def on_disconnect(self) -> None:
        ...


class OnReady(metaclass=ABCMeta):
    @abstractmethod
    async def on_ready(self) -> None:
        ...


class OnShardReady(metaclass=ABCMeta):
    @abstractmethod
    async def on_shard_ready(self, shard_id: int) -> None:
        ...


class OnResumed(metaclass=ABCMeta):
    @abstractmethod
    async def on_resumed(self) -> None:
        ...


class OnTyping(metaclass=ABCMeta):
    @abstractmethod
    async def on_typing(
        self,
        channels: TextChannel,
        users: User,
        when: datetime,
    ) -> None:
        ...


class OnMessage(metaclass=ABCMeta):
    @abstractmethod
    async def on_message(self, message: discord.Message) -> None:
        ...


class OnMessageDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_message_delete(self, message: discord.Message) -> None:
        ...


class OnBulkMessageDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_bulk_message_delete(self, messages: List[discord.Message]) -> None:
        ...


class OnRawMessageDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        ...


class OnRawBulkMessageDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_bulk_message_delete(
        self, payload: discord.RawBulkMessageDeleteEvent
    ) -> None:
        ...


class OnMessageEdit(metaclass=ABCMeta):
    @abstractmethod
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        ...


class OnRawMessageEdit(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        ...


class OnReactionAdd(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_add(self, reaction: discord.Reaction, user: User) -> None:
        ...


class OnRawReactionAdd(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        ...


class OnReactionRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_remove(self, reaction: discord.Reaction, user: User) -> None:
        ...


class OnRawReactionRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        ...


class OnReactionClear(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_clear(
        self, message: discord.Message, reactions: List[discord.Reaction]
    ) -> None:
        ...


class OnRawReactionClear(metaclass=ABCMeta):
    @abstractmethod
    async def on_raw_reaction_clear(
        self, payload: discord.RawReactionClearEvent
    ) -> None:
        ...


class OnReactionClearEmoji(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_clear_emoji(self, reaction: discord.Reaction) -> None:
        ...


class OnRawReactionClearEmoji(metaclass=ABCMeta):
    @abstractmethod
    async def on_reaction_clear(
        self, payload: discord.RawReactionClearEmojiEvent
    ) -> None:
        ...


class OnPrivateChannelDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_private_channel_delete(self, channel: PrivateChannel) -> None:
        ...


class OnPrivateChannelCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_private_channel_create(self, channel: PrivateChannel) -> None:
        ...


class OnPrivateChannelUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_private_channel_update(
        self, before: PrivateChannel, after: PrivateChannel
    ) -> None:
        ...


class OnPrivateChannelPinsUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_private_channel_pins_update(
        self, channel: PrivateChannel, last_pin: Optional[datetime]
    ) -> None:
        ...


class OnGuildChannelDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_delete(self, channel: GuildChannel) -> None:
        ...


class OnGuildChannelCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_create(self, channel: GuildChannel) -> None:
        ...


class OnGuildChannelUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_update(
        self, before: GuildChannel, after: GuildChannel
    ) -> None:
        ...


class OnGuildChannelPinsUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_channel_pins_update(
        self, channel: GuildChannel, last_pin: Optional[datetime]
    ) -> None:
        ...


class OnGuildIntegrationsUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_integrations_update(self, guild: discord.Guild) -> None:
        ...


class OnWebhooksUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_webhooks_update(self, channel: GuildChannel) -> None:
        ...


class OnMemberJoin(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_join(self, member: discord.Member) -> None:
        ...


class OnMemberRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_remove(self, member: discord.Member) -> None:
        ...


class OnMemberUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        ...


class OnUserUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        ...


class OnGuildJoin(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_join(self, guild: discord.Guild) -> None:
        ...


class OnGuildRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        ...


class OnGuildUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_update(
        self, before: discord.Guild, after: discord.Guild
    ) -> None:
        ...


class OnGuildAvailable(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_available(self, guild: discord.Guild) -> None:
        ...


class OnGuildUnavailable(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_unavailable(self, guild: discord.Guild) -> None:
        ...


class OnGuildRoleCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_create(self, role: discord.Role) -> None:
        ...


class OnGuildRoleDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        ...


class OnGuildRoleUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_role_update(
        self, before: discord.Role, after: discord.Role
    ) -> None:
        ...


class OnGuildEmojisUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_guild_emojis_update(
        self,
        guild: discord.Guild,
        before: List[discord.Emoji],
        after: List[discord.Emoji],
    ) -> None:
        ...


class OnMemberBan(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_ban(self, guild: discord.Guild, user: User) -> None:
        ...


class OnMemberUnban(metaclass=ABCMeta):
    @abstractmethod
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        ...


class OnVoiceStateUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        ...


class OnInviteCreate(metaclass=ABCMeta):
    @abstractmethod
    async def on_invite_create(self, invite: discord.Invite) -> None:
        ...


class OnInviteDelete(metaclass=ABCMeta):
    @abstractmethod
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        ...


class OnGroupJoin(metaclass=ABCMeta):
    @abstractmethod
    async def on_group_join(
        self, channel: discord.GroupChannel, user: discord.User
    ) -> None:
        ...


class OnGroupRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_group_remove(
        self, channel: discord.GroupChannel, user: discord.User
    ) -> None:
        ...


class OnRelationshipAdd(metaclass=ABCMeta):
    @abstractmethod
    async def on_relationship_add(self, relationship: discord.Relationship) -> None:
        ...


class OnRelationshipRemove(metaclass=ABCMeta):
    @abstractmethod
    async def on_relationship_remove(self, relationship: discord.Relationship) -> None:
        ...


class OnRelationshipUpdate(metaclass=ABCMeta):
    @abstractmethod
    async def on_relationship_update(
        self, before: discord.Relationship, after: discord.Relationship
    ) -> None:
        ...
