from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, Any, Final, TypedDict, overload
from typing_extensions import NotRequired, TypeVar, Unpack

import discord
import pendulum
from discord.ext import commands

from .embed import AuthorData, Embed, FieldData, FooterData

if TYPE_CHECKING:
    from collections.abc import Awaitable, Container, Iterable, Sequence
    from datetime import datetime

    from pendulum.duration import Duration

    from .types import Coroutine

_T = TypeVar('_T', infer_variance=True)

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
            raise asyncio.TimeoutError  # noqa: TRY301

        return done.pop().result()
    finally:
        for future in pending:
            future.cancel()


class BaseSendKwargs(TypedDict):
    allowed_mentions: NotRequired[discord.AllowedMentions]
    view: NotRequired[discord.ui.View]


class BaseSendMessageableKwargs(BaseSendKwargs):
    delete_after: NotRequired[float]
    nonce: NotRequired[int]
    reference: NotRequired[
        discord.Message | discord.MessageReference | discord.PartialMessage | None
    ]


class BaseSendInteractionKwargs(BaseSendKwargs):
    ephemeral: NotRequired[bool]


class BaseSendWebhookKwargs(BaseSendInteractionKwargs):
    username: NotRequired[str]
    avatar_url: NotRequired[str]
    thread: NotRequired[discord.Thread | discord.Object]


class BaseSendAnyKwargs(BaseSendMessageableKwargs, BaseSendWebhookKwargs):
    ...


class SendKwargs(BaseSendKwargs):
    content: NotRequired[str]
    tts: NotRequired[bool]
    embeds: NotRequired[Sequence[discord.Embed]]
    files: NotRequired[Sequence[discord.File]]


class SendMessageableKwargs(SendKwargs, BaseSendMessageableKwargs):
    ...


class SendInteractionKwargs(SendKwargs, BaseSendInteractionKwargs):
    ...


class SendWebhookKwargs(SendKwargs, BaseSendInteractionKwargs):
    ...


class SendAnyKwargs(SendMessageableKwargs, SendWebhookKwargs):
    ...


def _pop_value(kwargs: TypedDict, key: str, default: object) -> Any:  # noqa: ANN401
    value = kwargs.pop(key, _MISSING)  # pyright: ignore[reportGeneralTypeIssues]
    return default if value is _MISSING else value


async def _send_interaction(
    itx: discord.Interaction,
    /,
    **kwargs: Unpack[SendInteractionKwargs],
) -> discord.Message:
    kwargs['ephemeral'] = _pop_value(kwargs, 'ephemeral', default=False)

    if not itx.response.is_done():
        kwargs['content'] = _pop_value(kwargs, 'content', None)

        await itx.response.send_message(**kwargs)
        return await itx.original_response()

    return await itx.followup.send(**kwargs, wait=True)


@overload
async def send(
    ctx: discord.abc.Messageable | discord.Message,
    /,
    **kwargs: Unpack[SendMessageableKwargs],
) -> discord.Message:
    ...


@overload
async def send(
    ctx: discord.Webhook,
    /,
    **kwargs: Unpack[SendWebhookKwargs],
) -> discord.WebhookMessage:
    ...


@overload
async def send(
    interaction: discord.Interaction,
    /,
    **kwargs: Unpack[SendInteractionKwargs],
) -> discord.Message:
    ...


@overload
async def send(
    ctx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    **kwargs: Unpack[SendAnyKwargs],
) -> discord.Message:
    ...


def send(
    ctx_or_intx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    *,
    content: str = _MISSING,
    tts: bool = False,
    embeds: Sequence[discord.Embed] = _MISSING,
    files: Sequence[discord.File] = _MISSING,
    view: discord.ui.View = _MISSING,
    allowed_mentions: discord.AllowedMentions = _MISSING,
    ephemeral: bool = _MISSING,
    delete_after: float = _MISSING,
    nonce: int = _MISSING,
    reference: discord.Message
    | discord.MessageReference
    | discord.PartialMessage
    | None = _MISSING,
    username: str = _MISSING,
    avatar_url: str = _MISSING,
    thread: discord.Thread | discord.Object = _MISSING,
) -> Coroutine[discord.Message]:
    if not isinstance(ctx_or_intx, discord.Interaction | discord.Webhook):
        messageable = (
            ctx_or_intx
            if isinstance(ctx_or_intx, discord.abc.Messageable)
            else ctx_or_intx.channel
        )

        if reference is _MISSING:
            if isinstance(ctx_or_intx, commands.Context):
                reference = ctx_or_intx.message
            elif isinstance(ctx_or_intx, discord.Message):
                reference = ctx_or_intx
            else:
                reference = None

        return messageable.send(
            content=None if content is _MISSING else content,
            tts=tts,
            embeds=None
            if embeds is _MISSING
            else embeds,  # pyright: ignore[reportGeneralTypeIssues]
            files=None
            if files is _MISSING
            else files,  # pyright: ignore[reportGeneralTypeIssues]
            delete_after=(
                None
                if delete_after is _MISSING
                else delete_after  # pyright: ignore[reportGeneralTypeIssues]
            ),
            nonce=None
            if nonce is _MISSING
            else nonce,  # pyright: ignore[reportGeneralTypeIssues]
            allowed_mentions=(
                None
                if allowed_mentions is _MISSING
                else allowed_mentions  # pyright: ignore[reportGeneralTypeIssues]
            ),
            reference=reference,  # pyright: ignore[reportGeneralTypeIssues]
            view=None
            if view is _MISSING
            else view,  # pyright: ignore[reportGeneralTypeIssues]
        )

    if isinstance(ctx_or_intx, discord.Webhook):
        return ctx_or_intx.send(
            content=content,
            tts=tts,
            embeds=embeds,
            files=files,
            view=view,
            allowed_mentions=allowed_mentions,
            ephemeral=False if ephemeral is _MISSING else ephemeral,
            wait=True,
            username=username,
            avatar_url=avatar_url,
            thread=thread,
        )

    return _send_interaction(
        ctx_or_intx,
        content=content,
        tts=tts,
        embeds=embeds,
        files=files,
        view=view,
        allowed_mentions=allowed_mentions,
        ephemeral=ephemeral,
    )


class EmbedKwargs(TypedDict):
    description: NotRequired[str | None]
    title: NotRequired[str | None]
    color: NotRequired[discord.Color | int | None]
    footer: NotRequired[str | FooterData | None]
    thumbnail: NotRequired[str | None]
    author: NotRequired[str | AuthorData | None]
    image: NotRequired[str | None]
    timestamp: NotRequired[datetime | None]
    fields: NotRequired[Sequence[FieldData] | None]


class SendEmbedKwargs(BaseSendKwargs, EmbedKwargs):
    ...


class SendEmbedMessageableKwargs(SendEmbedKwargs, BaseSendMessageableKwargs):
    ...


class SendEmbedWebhookKwargs(SendEmbedKwargs, BaseSendWebhookKwargs):
    ...


class SendEmbedInteractionKwargs(SendEmbedKwargs, BaseSendInteractionKwargs):
    ...


class SendEmbedAnyKwargs(SendEmbedKwargs, BaseSendAnyKwargs):
    ...


@overload
async def send_embed(
    ctx: discord.abc.Messageable | discord.Message,
    /,
    **kwargs: Unpack[SendEmbedMessageableKwargs],
) -> discord.Message:
    ...


@overload
async def send_embed(
    interaction: discord.Webhook, /, **kwargs: Unpack[SendEmbedWebhookKwargs]
) -> discord.WebhookMessage:
    ...


@overload
async def send_embed(
    interaction: discord.Interaction, /, **kwargs: Unpack[SendEmbedInteractionKwargs]
) -> discord.Message:
    ...


@overload
async def send_embed(
    ctx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    **kwargs: Unpack[SendEmbedAnyKwargs],
) -> discord.Message:
    ...


def send_embed(
    ctx_or_intx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    **kwargs: Unpack[SendEmbedAnyKwargs],
) -> Coroutine[discord.Message]:
    embed_kwargs: EmbedKwargs = {}

    if 'description' in kwargs:
        embed_kwargs['description'] = kwargs.pop('description')

    if 'title' in kwargs:
        embed_kwargs['title'] = kwargs.pop('title')

    if 'color' in kwargs:
        embed_kwargs['color'] = kwargs.pop('color')

    if 'footer' in kwargs:
        embed_kwargs['footer'] = kwargs.pop('footer')

    if 'thumbnail' in kwargs:
        embed_kwargs['thumbnail'] = kwargs.pop('thumbnail')

    if 'author' in kwargs:
        embed_kwargs['author'] = kwargs.pop('author')

    if 'image' in kwargs:
        embed_kwargs['image'] = kwargs.pop('image')

    if 'timestamp' in kwargs:
        embed_kwargs['timestamp'] = kwargs.pop('timestamp')

    if 'fields' in kwargs:
        embed_kwargs['fields'] = kwargs.pop('fields')

    return send(ctx_or_intx, embeds=[Embed(**embed_kwargs)], **kwargs)


@overload
async def send_embed_error(
    ctx: discord.abc.Messageable | discord.Message,
    /,
    **kwargs: Unpack[SendEmbedMessageableKwargs],
) -> discord.Message:
    ...


@overload
async def send_embed_error(
    interaction: discord.Webhook, /, **kwargs: Unpack[SendEmbedWebhookKwargs]
) -> discord.WebhookMessage:
    ...


@overload
async def send_embed_error(
    interaction: discord.Interaction, /, **kwargs: Unpack[SendEmbedInteractionKwargs]
) -> discord.Message:
    ...


@overload
async def send_embed_error(
    ctx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    **kwargs: Unpack[SendEmbedAnyKwargs],
) -> discord.Message:
    ...


def send_embed_error(
    ctx_or_intx: discord.abc.Messageable
    | discord.Message
    | discord.Webhook
    | discord.Interaction,
    /,
    **kwargs: Unpack[SendEmbedAnyKwargs],
) -> Coroutine[discord.Message]:
    if 'color' not in kwargs:
        kwargs['color'] = discord.Color.red()

    if 'ephemeral' not in kwargs:
        kwargs['ephemeral'] = True

    return send_embed(ctx_or_intx, **kwargs)
