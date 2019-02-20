from __future__ import annotations

import pytest
import asyncio

from botus_receptus.interactive_pager import (
    ListPageSource,
    InteractivePager,
    CannotPaginateReason,
    CannotPaginate,
)

from .mocks import MockUser, MockPermissions, MockGuild, MockContext


class TestPaginator(object):
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
    async def test_paginate_timeout(self, event_loop, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert p.paginating
        await p.paginate()
        assert not p.paginating
        context.channel.send.assert_awaited_once()
        assert p.message.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_awaited_once_with()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5, 6], 3]], indirect=['fetcher'])
    @pytest.mark.asyncio
    async def test_paginate_two_pages_timeout(self, event_loop, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert p.paginating
        await p.paginate()
        assert not p.paginating
        context.channel.send.assert_awaited_once()
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
        context.channel.send.assert_awaited_once()
        assert p.message.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_awaited_once_with()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5], 10]], indirect=['fetcher'])
    @pytest.mark.asyncio
    async def test_paginate_not_paginated(self, event_loop, context, fetcher):
        p = InteractivePager.create(context, fetcher)

        assert not p.paginating
        await p.paginate()
        assert not p.paginating
        assert context.message is p.message
        context.channel.send.assert_awaited_once()
        p.message.add_reaction.assert_not_awaited()
        p.message.clear_reactions.assert_not_awaited()
        p.message.clear_reactions.assert_not_awaited()
        p.message.remove_reaction.assert_not_awaited()
        assert p.match is None
