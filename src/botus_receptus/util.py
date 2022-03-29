from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Container, Iterable, Sequence
from datetime import datetime
from typing import Any, Final, TypedDict, TypeVar

import discord
import pendulum
from discord.ext import commands
from pendulum.duration import Duration

T = TypeVar('T')


def has_any_role(member: discord.Member, roles: Container[str], /) -> bool:
    return discord.utils.find(lambda role: role.name in roles, member.roles) is not None


def has_any_role_id(member: discord.Member, ids: Container[int], /) -> bool:
    return discord.utils.find(lambda role: role.id in ids, member.roles) is not None


UNITS: Final = {
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds',
    'd': 'days',
    'w': 'weeks',
    'y': 'years',
}


# Adapted from https://github.com/python-discord/site/blob/master/pysite/utils/time.py
def parse_duration(duration: str, /) -> Duration:
    duration = duration.strip()

    if not duration:
        raise ValueError('No duration provided.')

    args: dict[str, int] = {}
    digits = ''

    for char in duration:
        if char.isdigit():
            digits += char
            continue

        if char == ' ':
            if len(digits) > 0:
                raise ValueError('Invalid duration')

            continue  # pragma: no cover

        if char not in UNITS or not digits:
            raise ValueError('Invalid duration')

        args[UNITS[char]] = int(digits)
        digits = ''

    return pendulum.duration(**args)


async def race(
    futures: Iterable[asyncio.Future[T] | Awaitable[T]],
    /,
    *,
    timeout: float | None = None,
) -> T:
    tasks = {future for future in futures}

    done, pending = await asyncio.wait(
        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )

    try:
        if len(pending) == len(tasks):
            raise asyncio.TimeoutError()

        return done.pop().result()
    finally:
        for future in pending:
            future.cancel()


class FooterData(TypedDict, total=False):
    text: str
    icon_url: str


class UrlData(TypedDict, total=False):
    url: str


class AuthorDataBase(TypedDict):
    name: str


class AuthorData(AuthorDataBase, UrlData, total=False):
    icon_url: str


class FieldDataBase(TypedDict):
    name: str
    value: str


class FieldData(FieldDataBase, total=False):
    inline: bool


def create_embed(
    *,
    description: str,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
) -> discord.Embed:
    embed = discord.Embed(description=description)

    if title is not None:
        embed.title = title
    if color is not None:
        embed.color = color
    if footer is not None:
        if isinstance(footer, str):
            embed.set_footer(text=footer)
        else:
            embed.set_footer(**footer)
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if author is not None:
        if isinstance(author, str):
            embed.set_author(name=author)
        else:
            embed.set_author(**author)
    if image is not None:
        embed.set_image(url=image)
    if timestamp is not None:
        embed.timestamp = timestamp
    if fields is not None:
        embed._fields = [field for field in fields]  # type: ignore

    return embed


async def send_context(
    ctx: commands.Context[Any],
    /,
    *,
    description: str,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = False,
    file: discord.File | None = None,
    files: Sequence[discord.File] | None = None,
    embed: discord.Embed | None = None,
    embeds: Sequence[discord.Embed] | None = None,
    delete_after: float | None = None,
    nonce: int | None = None,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage
    | None = None,
    view: discord.ui.View | None = None,
) -> discord.Message:
    return await ctx.send(  # type: ignore
        tts=tts,
        embed=create_embed(
            description=description,
            title=title,
            color=color,
            footer=footer,
            thumbnail=thumbnail,
            author=author,
            image=image,
            timestamp=timestamp,
            fields=fields,
        )
        if embed is None and embeds is None
        else embed,
        embeds=embeds,
        file=file,
        files=files,
        delete_after=delete_after,
        nonce=nonce,
        reference=ctx.message if reference is None else reference,
        view=view,
    )


async def send_context_error(
    ctx: commands.Context[Any],
    /,
    *,
    description: str,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = False,
    file: discord.File | None = None,
    files: Sequence[discord.File] | None = None,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage
    | None = None,
    view: discord.ui.View | None = None,
) -> discord.Message:
    return await send_context(
        ctx,
        description=description,
        title=title,
        color=discord.Color.red() if color is None else color,
        footer=footer,
        thumbnail=thumbnail,
        author=author,
        image=image,
        timestamp=timestamp,
        fields=fields,
        tts=tts,
        file=file,
        files=files,
        reference=reference,
        view=view,
    )


async def send_interaction(
    interaction: discord.Interaction,
    /,
    *,
    description: str,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = False,
    file: discord.File = discord.utils.MISSING,
    files: Sequence[discord.File] = discord.utils.MISSING,
    embed: discord.Embed = discord.utils.MISSING,
    embeds: Sequence[discord.Embed] = discord.utils.MISSING,
    view: discord.ui.View = discord.utils.MISSING,
    allowed_mentions: discord.AllowedMentions = discord.utils.MISSING,
    ephemeral: bool = discord.utils.MISSING,
) -> None:
    ephemeral = False if ephemeral is discord.utils.MISSING else ephemeral
    embed = (
        create_embed(
            description=description,
            title=title,
            color=color,
            footer=footer,
            thumbnail=thumbnail,
            author=author,
            image=image,
            timestamp=timestamp,
            fields=fields,
        )
        if embed is None and embeds is None
        else embed
    )
    if not interaction.response.is_done():
        await interaction.response.send_message(
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=view,
            allowed_mentions=allowed_mentions,
            ephemeral=ephemeral,
        )
    else:
        await interaction.followup.send(
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=view,
            allowed_mentions=allowed_mentions,
            ephemeral=ephemeral,
        )


async def send_interaction_error(
    interaction: discord.Interaction,
    /,
    *,
    description: str,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = False,
    file: discord.File = discord.utils.MISSING,
    files: Sequence[discord.File] = discord.utils.MISSING,
    embed: discord.Embed = discord.utils.MISSING,
    embeds: Sequence[discord.Embed] = discord.utils.MISSING,
    view: discord.ui.View = discord.utils.MISSING,
    allowed_mentions: discord.AllowedMentions = discord.utils.MISSING,
    ephemeral: bool = discord.utils.MISSING,
) -> None:
    return await send_interaction(
        interaction,
        description=description,
        title=title,
        color=discord.Color.red() if color is None else color,
        footer=footer,
        thumbnail=thumbnail,
        author=author,
        image=image,
        timestamp=timestamp,
        fields=fields,
        tts=tts,
        file=file,
        files=files,
        embed=embed,
        embeds=embeds,
        view=view,
        allowed_mentions=allowed_mentions,
        ephemeral=True if ephemeral is discord.utils.MISSING else ephemeral,
    )
