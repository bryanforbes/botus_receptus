from __future__ import annotations

from typing import Container
import discord


def has_any_role(member: discord.Member, roles: Container[str]) -> bool:
    return discord.utils.find(lambda role: role.name in roles, member.roles) is not None


def has_any_role_id(member: discord.Member, ids: Container[int]) -> bool:
    return discord.utils.find(lambda role: role.id in ids, member.roles) is not None
