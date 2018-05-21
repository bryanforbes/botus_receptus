import pytest  # typing: ignore
import attr
import discord
from typing import Any
from botus_receptus.context import EmbedContext, PaginatedContext, PaginatedEmbedContext


@attr.s(slots=True, auto_attribs=True)
class MockUser(object):
    bot: bool = None
    id: int = None
    mention: str = None


@attr.s(slots=True, auto_attribs=True)
class MockMessage(object):
    author: MockUser = None
    content: str = None
    channel: discord.abc.GuildChannel = attr.ib(init=False, default=None)
    _state: Any = attr.ib(init=False, default=None)


@pytest.fixture
def mock_context_send(mocker):
    return mocker.patch('discord.ext.commands.Context.send', new_callable=mocker.AsyncMock)


class TestEmbedContext(object):
    @pytest.mark.asyncio
    async def test_send_content_only(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

        await ctx.send_embed('baz')

        assert type(mock_context_send.call_args_list[0][1]['embed']) == discord.Embed
        assert mock_context_send.call_args_list[0][1]['embed'].description == 'baz'
        mock_context_send.assert_called_once_with(tts=False, embed=mocker.ANY, file=None, files=None,
                                                  delete_after=None, nonce=None)

    @pytest.mark.asyncio
    async def test_send_embed_only(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

        embed = discord.Embed()
        obj = mocker.sentinel.TEST_OBJECT
        await ctx.send_embed(embed=embed, tts=True, file=obj, files=obj, delete_after=1.0, nonce=200)

        mock_context_send.assert_called_once_with(tts=True, embed=embed, file=obj, files=obj,
                                                  delete_after=1.0, nonce=200)

    @pytest.mark.asyncio
    async def test_send_content_and_embed(self, mocker, mock_context_send):
        ctx = EmbedContext(prefix='~', message=MockMessage())

        embed = discord.Embed()
        embed.description = 'foo'
        obj = mocker.sentinel.TEST_OBJECT
        await ctx.send_embed('bar', embed=embed, tts=True, file=obj, files=obj, delete_after=1.0, nonce=200)

        mock_context_send.assert_called_once_with(tts=True, embed=embed, file=obj, files=obj,
                                                  delete_after=1.0, nonce=200)
        assert embed.description == 'bar'


class TestPaginatedContext(object):
    @pytest.fixture
    def mock_paginator(self, mocker):
        return ['```\nasdf\n```', '```\nqwerty foo\n```']

    @pytest.mark.asyncio
    async def test_send_pages(self, mocker, mock_context_send, mock_paginator):
        ctx = PaginatedContext(prefix='~', message=MockMessage())

        messages = await ctx.send_pages(mock_paginator)
        assert len(messages) == 2
        mock_context_send.assert_has_calls([
            mocker.call('```\nasdf\n```', tts=False, delete_after=None, nonce=None),
            mocker.call('```\nqwerty foo\n```', tts=False, delete_after=None, nonce=None)
        ])

    @pytest.mark.asyncio
    async def test_send_pages_args(self, mocker, mock_context_send, mock_paginator):
        ctx = PaginatedContext(prefix='~', message=MockMessage())

        messages = await ctx.send_pages(mock_paginator, tts=True, delete_after=1.0, nonce=200)
        assert len(messages) == 2
        mock_context_send.assert_has_calls([
            mocker.call('```\nasdf\n```', tts=True, delete_after=1.0, nonce=200),
            mocker.call('```\nqwerty foo\n```', tts=True, delete_after=1.0, nonce=200)
        ])


class TestPaginatedEmbedContext(object):
    @pytest.fixture
    def mock_paginator(self, mocker):
        return ['asdf', 'qwerty foo']

    @pytest.mark.asyncio
    async def test_send_embed_pages(self, mocker, mock_context_send, mock_paginator):
        ctx = PaginatedEmbedContext(prefix='~', message=MockMessage())

        messages = await ctx.send_embed_pages(mock_paginator)
        assert len(messages) == 2

        assert type(mock_context_send.call_args_list[0][1]['embed']) == discord.Embed
        assert mock_context_send.call_args_list[0][1]['embed'].description == 'asdf'
        assert type(mock_context_send.call_args_list[1][1]['embed']) == discord.Embed
        assert mock_context_send.call_args_list[1][1]['embed'].description == 'qwerty foo'

        mock_context_send.assert_has_calls([
            mocker.call(embed=mocker.ANY, tts=False, delete_after=None, nonce=None, file=None, files=None),
            mocker.call(embed=mocker.ANY, tts=False, delete_after=None, nonce=None, file=None, files=None),
        ])
