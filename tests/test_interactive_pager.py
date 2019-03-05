from __future__ import annotations

import pytest
import asyncio
import discord

from typing import Any, List
from aioitertools import list as alist
from dataclasses import dataclass
from dataslots import with_slots
from botus_receptus.interactive_pager import (
    PageSource,
    ListPageSource,
    FieldPageSource,
    InteractivePager,
    CannotPaginateReason,
    CannotPaginate,
)

from .mocks import MockUser, MockPermissions, MockGuild, MockContext


@with_slots
@dataclass
class MockReaction(object):
    message: Any
    emoji: str

    @classmethod
    def create(cls, emoji: str, message_id: int) -> MockReaction:
        return MockReaction(message=discord.Object(message_id), emoji=emoji)


@with_slots
@dataclass
class SubPageSource(PageSource[str]):
    strings: List[str]

    def get_page_items(self, page: int) -> List[str]:
        base = (page - 1) * self.per_page
        return self.strings[base : base + self.per_page]


@with_slots
@dataclass
class SubFieldPageSource(FieldPageSource[str]):
    strings: List[str]

    def get_page_items(self, page: int) -> List[str]:
        base = (page - 1) * self.per_page
        return self.strings[base : base + self.per_page]


class TestPageSource(object):
    @pytest.mark.parametrize(
        'per_page,max_pages,paginated',
        [(2, 4, True), (3, 3, True), (4, 2, True), (10, 1, False)],
    )
    def test_init(self, per_page, max_pages, paginated):
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = SubPageSource(
            total=len(strings),
            per_page=per_page,
            show_entry_count=False,
            strings=strings,
        )

        assert source.max_pages == max_pages
        assert source.paginated == paginated

    @pytest.mark.parametrize('show_entry_count', [False, True])
    @pytest.mark.parametrize('per_page,max_pages', [(2, 4), (3, 3), (4, 2), (10, 1)])
    @pytest.mark.asyncio
    async def test_get_page(self, per_page, max_pages, show_entry_count):
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = SubPageSource(
            total=len(strings),
            per_page=per_page,
            show_entry_count=show_entry_count,
            strings=strings,
        )

        page = await source.get_page(0)

        if show_entry_count and max_pages >= 2:
            assert page['footer_text'] is not None

        lines = '\n'.join(
            [f'{index}. {string}' for index, string in source.get_page_items(0)]
        )

        assert page['entry_text'] == lines


class TestListPageSource(object):
    @pytest.mark.parametrize(
        'per_page,max_pages,paginated',
        [(2, 4, True), (3, 3, True), (4, 2, True), (10, 1, False)],
    )
    def test_init(self, per_page, max_pages, paginated):
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = ListPageSource.create(strings, per_page)

        assert source.total == len(strings)
        assert source.max_pages == max_pages
        assert source.paginated == paginated

    @pytest.mark.parametrize('show_entry_count', [False, True])
    @pytest.mark.parametrize('per_page', [2, 3, 4, 10])
    @pytest.mark.asyncio
    async def test_get_page(self, per_page, show_entry_count):
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = ListPageSource.create(
            strings, per_page, show_entry_count=show_entry_count
        )

        page = await source.get_page(0)

        if show_entry_count and source.max_pages >= 2:
            assert page['footer_text'] is not None

        lines = '\n'.join(
            [f'{index}. {string}' for index, string in source.get_page_items(0)]
        )

        assert page['entry_text'] == lines


class TestFieldPageSource(object):
    @pytest.mark.parametrize('show_entry_count', [False, True])
    @pytest.mark.parametrize('per_page,max_pages', [(2, 4), (3, 3), (4, 2), (10, 1)])
    @pytest.mark.asyncio
    async def test_get_page(self, per_page, max_pages, show_entry_count):
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = SubFieldPageSource(
            total=len(strings),
            per_page=per_page,
            show_entry_count=show_entry_count,
            strings=strings,
        )

        page = await source.get_page(0)

        assert page['entry_text'] == ''
        if show_entry_count and max_pages >= 2:
            assert page['footer_text'] is not None

        expected_fields = [
            (index, string) for index, string in enumerate(source.get_page_items(0))
        ]
        actual_fields = await alist(page['fields'])

        assert actual_fields == expected_fields


class TestInteractivePager(object):
    @pytest.fixture(autouse=True)
    def wait_for_first(self, mocker):
        return mocker.patch('botus_receptus.interactive_pager.wait_for_first')

    @pytest.fixture
    def fetcher(self, request):
        return ListPageSource.create(
            *getattr(request, 'param', [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4])
        )

    @pytest.fixture
    def permissions(self, request):
        return MockPermissions(**getattr(request, 'param', {}))

    @pytest.fixture
    def bot_user(self):
        return MockUser(id=0)

    @pytest.fixture
    def me_user(self, bot_user):
        return bot_user

    @pytest.fixture
    def guild(self, me_user):
        return MockGuild(me=me_user)

    @pytest.fixture
    def context(self, mocker, bot_user, event_loop, permissions, guild):
        return MockContext.create(mocker, event_loop, bot_user, permissions, guild)

    @pytest.mark.parametrize('me_user', [MockUser(id=400)])
    def test_create(self, context, fetcher):
        InteractivePager.create(context, fetcher)

        context.channel.permissions_for.assert_called_with(context.guild.me)

    @pytest.mark.parametrize('guild,me_user', [(None, MockUser(id=400))])
    def test_create_no_guild(self, context, fetcher, guild):
        InteractivePager.create(context, fetcher)

        context.channel.permissions_for.assert_called_with(context.bot.user)

    @pytest.mark.parametrize(
        'permissions,reason',
        [
            (dict(embed_links=False), CannotPaginateReason.embed_links),
            (dict(send_messages=False), CannotPaginateReason.send_messages),
            (dict(add_reactions=False), CannotPaginateReason.add_reactions),
            (
                dict(read_message_history=False),
                CannotPaginateReason.read_message_history,
            ),
        ],
        indirect=['permissions'],
    )
    def test_create_fail(self, context, fetcher, reason):
        with pytest.raises(CannotPaginate) as excinfo:
            InteractivePager.create(context, fetcher)

        assert excinfo.value.reason == reason

    @pytest.mark.asyncio
    async def test_paginate_timeout(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert p.paginating
        await p.paginate()
        assert not p.paginating
        page = await fetcher.get_page(1)
        assert p.embed.description == '\n'.join(
            [
                page['entry_text'],
                '',
                'Confused? React with \N{INFORMATION SOURCE} for more info.',
            ]
        )
        assert not hasattr(p.embed._footer, 'text')
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert p.message.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_awaited_once_with()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5, 6], 3]], indirect=['fetcher'])
    @pytest.mark.asyncio
    async def test_paginate_two_pages_timeout(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert p.paginating
        await p.paginate()
        assert not p.paginating
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert p.message.add_reaction.await_count == 5
        context.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_awaited_once_with()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize(
        'permissions', [dict(manage_messages=False)], indirect=['permissions']
    )
    @pytest.mark.asyncio
    async def test_paginate_timeout_no_manage_messages(
        self, mocker, context, event_loop, fetcher, wait_for_first
    ):
        mocker.patch.object(context.bot, 'wait_for')

        future = event_loop.create_future()
        wait_for_first.return_value = asyncio.wait_for(future, 1, loop=event_loop)
        p = InteractivePager.create(context, fetcher)

        assert p.paginating
        await p.paginate()
        assert not p.paginating
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert p.message.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_awaited_once_with()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5], 10]], indirect=['fetcher'])
    @pytest.mark.asyncio
    async def test_paginate_not_paginated(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert not p.paginating
        await p.paginate()
        assert not p.paginating
        page = await fetcher.get_page(1)
        assert p.embed.description == page['entry_text']
        assert context.message is p.message
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        p.message.add_reaction.assert_not_awaited()
        p.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_not_awaited()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.asyncio
    async def test_react_stop(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)
        reaction = MockReaction.create('\N{BLACK SQUARE FOR STOP}', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert not p.paginating
        p.message.delete.assert_awaited_once_with()
        p.message.remove_reaction.assert_awaited_once_with(reaction, context.author)

    @pytest.mark.parametrize(
        'emoji,expected_page',
        [
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', 2),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', 3),
        ],
        ids=['next', 'last'],
    )
    @pytest.mark.asyncio
    async def test_react_once(self, context, fetcher, emoji, expected_page):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)
        reaction = MockReaction.create(emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == expected_page
        page = await fetcher.get_page(expected_page)
        assert p.embed.description == page['entry_text']
        p.message.edit.assert_awaited_once_with(embed=p.embed)
        await asyncio.sleep(0.5)

    @pytest.mark.parametrize(
        'first_emoji,second_emoji,expected_page',
        [
            (
                '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                '\N{BLACK LEFT-POINTING TRIANGLE}',
                2,
            ),
            (
                '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                '\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
                1,
            ),
        ],
        ids=['previous', 'first'],
    )
    @pytest.mark.asyncio
    async def test_react_twice(
        self, context, fetcher, first_emoji, second_emoji, expected_page
    ):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)
        reaction = MockReaction.create(first_emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        reaction = MockReaction.create(second_emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == expected_page
        assert p.message.edit.await_count == 2
        p.message.edit.assert_awaited_with(embed=p.embed)
        await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_paginate_previous_checked(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)
        reaction = MockReaction.create('\N{BLACK LEFT-POINTING TRIANGLE}', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == 1
        assert p.message.edit.await_count == 0
        await asyncio.sleep(0.5)

    @pytest.mark.asyncio
    async def test_paginate_next_checked(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING TRIANGLE}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == 3
        assert p.message.edit.await_count == 1
        await asyncio.sleep(0.5)

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5, 6], 3]], indirect=['fetcher'])
    @pytest.mark.asyncio
    async def test_paginate_react_check_fails(self, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        asyncio.create_task(p.paginate())
        await asyncio.sleep(0.1)

        # mismatching author id
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING TRIANGLE}', p.message.id
        )
        await context.bot._dispatch_wait_for(
            'reaction_add', reaction, discord.Object(400)
        )
        assert p.message.edit.await_count == 0

        # mismatching message id
        reaction = MockReaction.create('\N{BLACK RIGHT-POINTING TRIANGLE}', 400)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.message.edit.await_count == 0

        # mismatching reaction emoji
        reaction = MockReaction.create('stuff', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.message.edit.await_count == 0

        # reaction emoji that isn't used
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.message.edit.await_count == 0

        await asyncio.sleep(0.5)
