from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Container, Iterable, Sequence
from datetime import datetime
from typing import Any, Final, TypedDict, TypeVar, overload
from typing_extensions import NotRequired

import discord
import pendulum
from discord.ext import commands
from pendulum.duration import Duration

_T = TypeVar('_T')

_MISSING: Final = discord.utils.MISSING


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
    futures: Iterable[asyncio.Future[_T] | Awaitable[_T]],
    /,
    *,
    timeout: float | None = None,
) -> _T:
    tasks = {
        asyncio.create_task(future) if inspect.iscoroutine(future) else future
        for future in futures
    }

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


class FooterData(TypedDict):
    text: NotRequired[str | None]
    icon_url: NotRequired[str | None]


class AuthorData(TypedDict):
    name: str
    url: NotRequired[str | None]
    icon_url: NotRequired[str | None]


class FieldData(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


def create_embed(
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    author: str | AuthorData | None = None,
    thumbnail: str | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        description=description, title=title, color=color, timestamp=timestamp
    )

    if footer is not None:
        if isinstance(footer, str):
            embed.set_footer(text=footer)
        else:
            embed.set_footer(**footer)
    if author is not None:
        if isinstance(author, str):
            embed.set_author(name=author)
        else:
            embed.set_author(**author)
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if image is not None:
        embed.set_image(url=image)
    if fields is not None:
        for field in fields:
            embed.add_field(**field)

    return embed


@overload
async def send(
    ctx: commands.Context[Any],
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    content: str = ...,
    tts: bool = ...,
    file: discord.File = ...,
    delete_after: float = ...,
    nonce: int = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send(
    ctx: commands.Context[Any],
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    content: str = ...,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    delete_after: float = ...,
    nonce: int = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send(
    ctx: commands.Context[Any],
    /,
    *,
    content: str = ...,
    tts: bool = ...,
    file: discord.File = ...,
    embeds: Sequence[discord.Embed],
    delete_after: float = ...,
    nonce: int = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send(
    ctx: commands.Context[Any],
    /,
    *,
    content: str = ...,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    embeds: Sequence[discord.Embed],
    delete_after: float = ...,
    nonce: int = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send(
    interaction: discord.Interaction,
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    content: str = ...,
    tts: bool = ...,
    file: discord.File = ...,
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


@overload
async def send(
    interaction: discord.Interaction,
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    content: str = ...,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


@overload
async def send(
    interaction: discord.Interaction,
    /,
    *,
    content: str = ...,
    tts: bool = ...,
    file: discord.File = ...,
    embeds: Sequence[discord.Embed],
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


@overload
async def send(
    interaction: discord.Interaction,
    /,
    *,
    content: str = ...,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    embeds: Sequence[discord.Embed],
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


async def send(
    ctx_or_intx: commands.Context[Any] | discord.Interaction,
    /,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    content: str = _MISSING,
    tts: bool = False,
    file: discord.File = _MISSING,
    files: Sequence[discord.File] = _MISSING,
    embeds: Sequence[discord.Embed] = _MISSING,
    view: discord.ui.View = _MISSING,
    allowed_mentions: discord.AllowedMentions = _MISSING,
    ephemeral: bool = _MISSING,
    delete_after: float = _MISSING,
    nonce: int = _MISSING,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = _MISSING,
) -> discord.Message:
    if (
        description is not None
        or title is not None
        or color is not None
        or footer is not None
        or thumbnail is not None
        or author is not None
        or image is not None
        or timestamp is not None
        or fields is not None
    ) and embeds is not _MISSING:
        raise TypeError(
            'Cannot mix embed content arguments and embeds keyword argument'
        )

    if embeds is _MISSING:
        embed = create_embed(
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

        if embed:
            embeds = [embed]

    if isinstance(ctx_or_intx, commands.Context):
        return await ctx_or_intx.send(
            content=None if content is _MISSING else content,
            tts=tts,
            embeds=None if embeds is _MISSING else embeds,
            file=None if file is _MISSING else file,
            files=None if files is _MISSING else files,
            delete_after=None if delete_after is _MISSING else delete_after,
            nonce=None if nonce is _MISSING else nonce,
            allowed_mentions=None if allowed_mentions is _MISSING else allowed_mentions,
            reference=ctx_or_intx.message if reference is _MISSING else reference,
            view=None if view is _MISSING else view,
        )
    else:
        ephemeral = False if ephemeral is _MISSING else ephemeral

        if not ctx_or_intx.response.is_done():
            await ctx_or_intx.response.send_message(
                content=None if content is _MISSING else content,
                tts=tts,
                embeds=embeds,
                file=file,
                files=files,
                view=view,
                allowed_mentions=allowed_mentions,
                ephemeral=ephemeral,
            )
            return await ctx_or_intx.original_message()
        else:
            return await ctx_or_intx.followup.send(
                content=content,
                tts=tts,
                embeds=embeds,
                file=file,
                files=files,
                view=view,
                allowed_mentions=allowed_mentions,
                ephemeral=ephemeral,
                wait=True,
            )


@overload
async def send_error(
    ctx: commands.Context[Any],
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = ...,
    file: discord.File = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send_error(
    ctx: commands.Context[Any],
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = ...,
    view: discord.ui.View = ...,
) -> discord.Message:
    ...


@overload
async def send_error(
    interaction: discord.Interaction,
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = ...,
    file: discord.File = ...,
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


@overload
async def send_error(
    interaction: discord.Interaction,
    /,
    *,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = ...,
    files: Sequence[discord.File] = ...,
    view: discord.ui.View = ...,
    allowed_mentions: discord.AllowedMentions = ...,
    ephemeral: bool = ...,
) -> discord.Message:
    ...


async def send_error(
    ctx_or_intx: commands.Context[Any] | discord.Interaction,
    /,
    description: str | None = None,
    title: str | None = None,
    color: discord.Color | int | None = None,
    footer: str | FooterData | None = None,
    thumbnail: str | None = None,
    author: str | AuthorData | None = None,
    image: str | None = None,
    timestamp: datetime | None = None,
    fields: Sequence[FieldData] | None = None,
    tts: bool = False,
    file: discord.File = _MISSING,
    files: Sequence[discord.File] = _MISSING,
    view: discord.ui.View = _MISSING,
    allowed_mentions: discord.AllowedMentions = _MISSING,
    ephemeral: bool = _MISSING,
    delete_after: float = _MISSING,
    nonce: int = _MISSING,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage = _MISSING,
) -> discord.Message:
    return await send(  # type: ignore
        ctx_or_intx,
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
        view=view,
        allowed_mentions=allowed_mentions,
        ephemeral=True if ephemeral is _MISSING else ephemeral,
        delete_after=delete_after,
        nonce=nonce,
        reference=reference,
    )
