from __future__ import annotations

from typing import Any, Optional
from unittest.mock import AsyncMock

import discord
import pytest
from attr import dataclass
from discord.ext.commands.view import StringView  # type: ignore
from pendulum import now
from pendulum.tz.timezone import UTC

from botus_receptus.bot import Bot
from botus_receptus.compat import list
from botus_receptus.context import EmbedContext, PaginatedContext

from .types import MockerFixture


@dataclass(slots=True)
class MockBot(object):
    ...


@dataclass(slots=True)
class MockUser(object):
    bot: bool | None = None
    id: int | None = None
    mention: str | None = None


@dataclass(slots=True)
class MockMessage(object):
    author: MockUser | None = None
    content: str | None = None
    channel: Optional[discord.abc.GuildChannel] = None
    _state: Optional[Any] = None


@pytest.fixture
def mock_context_send(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch('discord.ext.commands.Context.send')


@pytest.fixture
def mock_bot() -> MockBot:
    return MockBot()


@pytest.fixture
def mock_message() -> MockMessage:
    return MockMessage()


@pytest.fixture
def mock_message_2() -> MockMessage:
    return MockMessage()


@pytest.fixture
def string_view() -> StringView:
    return StringView('')


@pytest.fixture
async def view() -> discord.ui.View:
    return discord.ui.View()


class TestEmbedContext(object):
    async def test_send_embed_description_only(
        self,
        mocker: MockerFixture,
        mock_context_send: AsyncMock,
        mock_bot: Bot,
        mock_message: discord.Message,
        string_view: StringView,
    ) -> None:
        ctx = EmbedContext(
            prefix='~', message=mock_message, bot=mock_bot, view=string_view
        )

        await ctx.send_embed('baz')

        assert type(mock_context_send.call_args_list[0][1]['embed']) == discord.Embed
        assert mock_context_send.call_args_list[0][1]['embed'].to_dict() == {
            'description': 'baz',
            'type': 'rich',
        }
        mock_context_send.assert_called_once_with(
            tts=False,
            embed=mocker.ANY,
            embeds=None,
            file=None,
            files=None,
            delete_after=None,
            nonce=None,
            reference=mock_message,
            view=None,
        )

    async def test_send_embed_args(
        self,
        mocker: MockerFixture,
        mock_context_send: AsyncMock,
        mock_bot: Bot,
        mock_message: discord.Message,
        string_view: StringView,
        view: discord.ui.View,
    ) -> None:
        ctx = EmbedContext(
            prefix='~', message=mock_message, bot=mock_bot, view=string_view
        )

        obj = mocker.sentinel.TEST_OBJECT
        time = now(UTC)
        await ctx.send_embed(
            'foo',
            title='bar',
            color=discord.Color.default(),
            footer='baz',
            thumbnail='ham',
            author='spam',
            image='blah',
            timestamp=time,
            fields=[{'name': 'one', 'value': 'one', 'inline': True}],
            tts=True,
            file=obj,
            files=obj,
            delete_after=1.0,
            nonce=200,
            reference=mock_message,
            view=view,
        )

        assert mock_context_send.call_args_list[0][1]['embed'].to_dict() == {
            'type': 'rich',
            'description': 'foo',
            'title': 'bar',
            'color': 0,
            'footer': {'text': 'baz'},
            'thumbnail': {'url': 'ham'},
            'author': {'name': 'spam'},
            'image': {'url': 'blah'},
            'timestamp': time.isoformat(),
            'fields': [{'name': 'one', 'value': 'one', 'inline': True}],
        }
        mock_context_send.assert_called_once_with(
            tts=True,
            embed=mocker.ANY,
            embeds=None,
            file=obj,
            files=obj,
            delete_after=1.0,
            nonce=200,
            reference=mock_message,
            view=view,
        )

    async def test_send_embed_other_args(
        self,
        mocker: MockerFixture,
        mock_context_send: AsyncMock,
        mock_bot: Bot,
        mock_message: discord.Message,
        mock_message_2: discord.Message,
        string_view: StringView,
        view: discord.ui.View,
    ) -> None:
        ctx = EmbedContext(
            prefix='~', message=mock_message, bot=mock_bot, view=string_view
        )

        obj = mocker.sentinel.TEST_OBJECT
        await ctx.send_embed(
            'foo',
            footer={'text': 'bar', 'icon_url': 'baz'},
            author={'name': 'ham', 'url': 'spam', 'icon_url': 'lamb'},
            tts=True,
            file=obj,
            files=obj,
            delete_after=1.0,
            nonce=200,
            reference=mock_message_2,
            view=view,
        )

        assert mock_context_send.call_args_list[0][1]['embed'].to_dict() == {
            'type': 'rich',
            'description': 'foo',
            'footer': {'text': 'bar', 'icon_url': 'baz'},
            'author': {'name': 'ham', 'url': 'spam', 'icon_url': 'lamb'},
        }
        mock_context_send.assert_called_once_with(
            tts=True,
            embed=mocker.ANY,
            embeds=None,
            file=obj,
            files=obj,
            delete_after=1.0,
            nonce=200,
            reference=mock_message_2,
            view=view,
        )


class TestPaginatedContext(object):
    @pytest.fixture
    def mock_paginator(self) -> list[str]:
        return ['```\nasdf\n```', '```\nqwerty foo\n```']

    async def test_send_pages(
        self,
        mocker: MockerFixture,
        mock_context_send: AsyncMock,
        mock_paginator: list[str],
        mock_bot: Bot,
        mock_message: discord.Message,
        string_view: StringView,
    ) -> None:
        ctx = PaginatedContext(
            prefix='~', message=mock_message, bot=mock_bot, view=string_view
        )

        messages = await ctx.send_pages(mock_paginator)
        assert len(messages) == 2
        mock_context_send.assert_has_calls(
            [
                mocker.call(
                    '```\nasdf\n```',
                    tts=False,
                    delete_after=None,
                    nonce=None,
                    reference=None,
                    view=None,
                ),
                mocker.call(
                    '```\nqwerty foo\n```',
                    tts=False,
                    delete_after=None,
                    nonce=None,
                    reference=None,
                    view=None,
                ),
            ]
        )

    async def test_send_pages_args(
        self,
        mocker: MockerFixture,
        mock_context_send: AsyncMock,
        mock_paginator: list[str],
        mock_bot: Bot,
        mock_message: discord.Message,
        string_view: StringView,
        view: discord.ui.View,
    ) -> None:
        ctx = PaginatedContext(
            prefix='~', message=mock_message, bot=mock_bot, view=string_view
        )

        messages = await ctx.send_pages(
            mock_paginator,
            tts=True,
            delete_after=1.0,
            nonce=200,
            reference=mock_message,
            view=view,
        )
        assert len(messages) == 2
        mock_context_send.assert_has_calls(
            [
                mocker.call(
                    '```\nasdf\n```',
                    tts=True,
                    delete_after=1.0,
                    nonce=200,
                    reference=mock_message,
                    view=view,
                ),
                mocker.call(
                    '```\nqwerty foo\n```',
                    tts=True,
                    delete_after=1.0,
                    nonce=200,
                    reference=mock_message,
                    view=view,
                ),
            ]
        )
