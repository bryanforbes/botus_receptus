import pytest  # typing: ignore
import discord
from typing import Any, Optional
from attr import dataclass
from botus_receptus.context import EmbedContext, PaginatedContext
from datetime import datetime


@dataclass(slots=True)
class MockUser(object):
    bot: bool = None
    id: int = None
    mention: str = None


@dataclass(slots=True)
class MockMessage(object):
    author: MockUser = None
    content: str = None
    channel: Optional[discord.abc.GuildChannel] = None
    _state: Optional[Any] = None


@pytest.fixture
def mock_context_send(mocker):
    return mocker.patch('discord.ext.commands.Context.send')


class TestEmbedContext(object):
    @pytest.mark.asyncio
    async def test_send_embed_description_only(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

        await ctx.send_embed('baz')

        assert type(mock_context_send.call_args_list[0][1]['embed']) == discord.Embed
        assert mock_context_send.call_args_list[0][1]['embed'].to_dict() == {
            'description': 'baz',
            'type': 'rich',
        }
        mock_context_send.assert_called_once_with(
            tts=False,
            embed=mocker.ANY,
            file=None,
            files=None,
            delete_after=None,
            nonce=None,
        )

    @pytest.mark.asyncio
    async def test_send_embed_args(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

        obj = mocker.sentinel.TEST_OBJECT
        time = datetime.now()
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
            tts=True, embed=mocker.ANY, file=obj, files=obj, delete_after=1.0, nonce=200
        )

    @pytest.mark.asyncio
    async def test_send_embed_other_args(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

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
        )

        assert mock_context_send.call_args_list[0][1]['embed'].to_dict() == {
            'type': 'rich',
            'description': 'foo',
            'footer': {'text': 'bar', 'icon_url': 'baz'},
            'author': {'name': 'ham', 'url': 'spam', 'icon_url': 'lamb'},
        }
        mock_context_send.assert_called_once_with(
            tts=True, embed=mocker.ANY, file=obj, files=obj, delete_after=1.0, nonce=200
        )


class TestPaginatedContext(object):
    @pytest.fixture
    def mock_paginator(self, mocker):
        return ['```\nasdf\n```', '```\nqwerty foo\n```']

    @pytest.mark.asyncio
    async def test_send_pages(self, mocker, mock_context_send, mock_paginator):
        ctx = PaginatedContext(prefix='~', message=MockMessage())

        messages = await ctx.send_pages(mock_paginator)
        assert len(messages) == 2
        mock_context_send.assert_has_calls(
            [
                mocker.call('```\nasdf\n```', tts=False, delete_after=None, nonce=None),
                mocker.call(
                    '```\nqwerty foo\n```', tts=False, delete_after=None, nonce=None
                ),
            ]
        )

    @pytest.mark.asyncio
    async def test_send_pages_args(self, mocker, mock_context_send, mock_paginator):
        ctx = PaginatedContext(prefix='~', message=MockMessage())

        messages = await ctx.send_pages(
            mock_paginator, tts=True, delete_after=1.0, nonce=200
        )
        assert len(messages) == 2
        mock_context_send.assert_has_calls(
            [
                mocker.call('```\nasdf\n```', tts=True, delete_after=1.0, nonce=200),
                mocker.call(
                    '```\nqwerty foo\n```', tts=True, delete_after=1.0, nonce=200
                ),
            ]
        )
