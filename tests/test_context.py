from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
import pendulum
import pytest
from attrs import define
from discord.ext.commands.view import (  # pyright: ignore[reportMissingTypeStubs]
    StringView,
)

from botus_receptus.context import EmbedContext, PaginatedContext

if TYPE_CHECKING:
    from unittest.mock import AsyncMock

    from botus_receptus.bot import Bot

    from .types import MockerFixture


@define
class MockBot: ...


@define
class MockUser:
    bot: bool | None = None
    id: int | None = None
    mention: str | None = None


@define
class MockMessage:
    author: MockUser | None = None
    content: str | None = None
    channel: discord.abc.GuildChannel | None = None
    _state: Any | None = None


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


class TestEmbedContext:
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

        assert isinstance(
            mock_context_send.call_args_list[0][1]['embeds'][0], discord.Embed
        )
        assert mock_context_send.call_args_list[0][1]['embeds'][0].to_dict() == {
            'description': 'baz',
            'type': 'rich',
            'flags': 0,
        }
        mock_context_send.assert_called_once_with(
            content=None,
            tts=False,
            embeds=[mocker.ANY],
            files=None,
            delete_after=None,
            nonce=None,
            reference=mock_message,
            allowed_mentions=None,
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

        time = pendulum.now(pendulum.UTC)
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
            reference=mock_message,
            view=view,
        )

        assert mock_context_send.call_args_list[0][1]['embeds'][0].to_dict() == {
            'type': 'rich',
            'flags': 0,
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
            content=None,
            tts=False,
            embeds=[mocker.ANY],
            files=None,
            delete_after=None,
            nonce=None,
            reference=mock_message,
            allowed_mentions=None,
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

        await ctx.send_embed(
            'foo',
            footer={'text': 'bar', 'icon_url': 'baz'},
            author={'name': 'ham', 'url': 'spam', 'icon_url': 'lamb'},
            reference=mock_message_2,
            view=view,
        )

        assert mock_context_send.call_args_list[0][1]['embeds'][0].to_dict() == {
            'type': 'rich',
            'flags': 0,
            'description': 'foo',
            'footer': {'text': 'bar', 'icon_url': 'baz'},
            'author': {'name': 'ham', 'url': 'spam', 'icon_url': 'lamb'},
        }
        mock_context_send.assert_called_once_with(
            content=None,
            tts=False,
            embeds=[mocker.ANY],
            files=None,
            delete_after=None,
            nonce=None,
            reference=mock_message_2,
            allowed_mentions=None,
            view=view,
        )


class TestPaginatedContext:
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
