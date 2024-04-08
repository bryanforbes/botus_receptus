from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, cast
from typing_extensions import override

import discord
import pytest
from aioitertools.builtins import list as alist
from attrs import define

from botus_receptus.interactive_pager import (
    CannotPaginate,
    CannotPaginateReason,
    FieldPageSource,
    InteractivePager,
    ListPageSource,
    PageSource,
)

from .mocks import (
    MockChannel,
    MockContext,
    MockGuild,
    MockMessage,
    MockPermissions,
    MockUser,
)

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

    from .types import ClockAdvancer, MockerFixture


@define
class MockReaction:
    message: Any
    emoji: str

    @classmethod
    def create(cls, emoji: str, message_id: int) -> MockReaction:
        return MockReaction(message=discord.Object(message_id), emoji=emoji)


@define
class SubPageSource(PageSource[str]):
    strings: list[str]

    @override
    def get_page_items(self, page: int) -> list[str]:
        base = (page - 1) * self.per_page
        return self.strings[base : base + self.per_page]


@define
class SubFieldPageSource(FieldPageSource[str]):
    strings: list[str]

    @override
    def get_page_items(self, page: int) -> list[str]:
        base = (page - 1) * self.per_page
        return self.strings[base : base + self.per_page]


class TestPageSource:
    @pytest.mark.parametrize(
        'per_page,max_pages,paginated',
        [(2, 4, True), (3, 3, True), (4, 2, True), (10, 1, False)],
    )
    def test_init(self, per_page: int, max_pages: int, paginated: bool) -> None:
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
    async def test_get_page(
        self, per_page: int, max_pages: int, show_entry_count: bool
    ) -> None:
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


class TestListPageSource:
    @pytest.mark.parametrize(
        'per_page,max_pages,paginated',
        [(2, 4, True), (3, 3, True), (4, 2, True), (10, 1, False)],
    )
    def test_init(self, per_page: int, max_pages: int, paginated: bool) -> None:
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = ListPageSource[str].create(strings, per_page)

        assert source.total == len(strings)
        assert source.max_pages == max_pages
        assert source.paginated == paginated

    @pytest.mark.parametrize('show_entry_count', [False, True])
    @pytest.mark.parametrize('per_page', [2, 3, 4, 10])
    async def test_get_page(self, per_page: int, show_entry_count: bool) -> None:
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = ListPageSource[str].create(
            strings, per_page, show_entry_count=show_entry_count
        )

        page = await source.get_page(0)

        if show_entry_count and source.max_pages >= 2:
            assert page['footer_text'] is not None

        lines = '\n'.join(
            [f'{index}. {string}' for index, string in source.get_page_items(0)]
        )

        assert page['entry_text'] == lines


class TestFieldPageSource:
    @pytest.mark.parametrize('show_entry_count', [False, True])
    @pytest.mark.parametrize('per_page,max_pages', [(2, 4), (3, 3), (4, 2), (10, 1)])
    async def test_get_page(
        self, per_page: int, max_pages: int, show_entry_count: bool
    ) -> None:
        strings = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        source = SubFieldPageSource(
            total=len(strings),
            per_page=per_page,
            show_entry_count=show_entry_count,
            strings=strings,
        )

        page = await source.get_page(0)

        assert not page['entry_text']
        if show_entry_count and max_pages >= 2:
            assert page['footer_text'] is not None

        expected_fields = [
            (str(index), str(string))
            for index, string in enumerate(source.get_page_items(0))
        ]
        actual_fields = await alist(page['fields'])

        assert actual_fields == expected_fields


class TestInteractivePager:
    @pytest.fixture
    def fetcher(self, request: SubRequest) -> ListPageSource[int]:
        return ListPageSource[int].create(
            *getattr(request, 'param', [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4])
        )

    @pytest.fixture
    def permissions(self, request: SubRequest) -> MockPermissions:
        return MockPermissions(**getattr(request, 'param', {}))

    @pytest.fixture
    def bot_user(self) -> MockUser:
        return MockUser(id=0)

    @pytest.fixture
    def me_user(self, bot_user: MockUser) -> MockUser:
        return bot_user

    @pytest.fixture
    def guild(self, me_user: MockUser) -> MockGuild:
        return MockGuild(me=me_user)

    @pytest.fixture
    async def context(
        self,
        mocker: MockerFixture,
        bot_user: MockUser,
        advance_time: ClockAdvancer,
        permissions: MockPermissions,
        guild: MockGuild,
    ) -> MockContext:
        return MockContext.create(
            mocker,
            asyncio.get_running_loop(),
            advance_time,
            bot_user,
            permissions,
            guild,
        )

    @pytest.fixture
    def channel(self, context: MockContext) -> MockChannel:
        return context.channel

    @pytest.fixture
    def send_result(
        self, mocker: MockerFixture, bot_user: MockUser, channel: MockChannel
    ) -> MockMessage:
        message = MockMessage.create(mocker, 11, bot_user, channel, '')
        channel.send.return_value = message
        return message

    @pytest.mark.parametrize('me_user', [MockUser(id=400)])
    def test_create(self, context: MockContext, fetcher: ListPageSource[int]) -> None:
        InteractivePager[int].create(cast('Any', context), fetcher)

        assert context.guild is not None
        context.channel.permissions_for.assert_called_with(context.guild.me)

    @pytest.mark.parametrize('guild', [None])
    def test_create_no_guild(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        guild: discord.Guild,
    ) -> None:
        InteractivePager[int].create(cast('Any', context), fetcher)

        context.channel.permissions_for.assert_called_with(context.bot.user)

    @pytest.mark.parametrize(
        'permissions,reason',
        [
            ({'embed_links': False}, CannotPaginateReason.embed_links),
            ({'send_messages': False}, CannotPaginateReason.send_messages),
            ({'add_reactions': False}, CannotPaginateReason.add_reactions),
            (
                {'read_message_history': False},
                CannotPaginateReason.read_message_history,
            ),
        ],
        indirect=['permissions'],
    )
    def test_create_fail(
        self,
        context: MockContext,
        fetcher: ListPageSource[str],
        reason: CannotPaginateReason,
    ) -> None:
        with pytest.raises(CannotPaginate) as excinfo:
            InteractivePager[str].create(cast('Any', context), fetcher)

        assert excinfo.value.reason == reason

    @pytest.mark.flaky(reruns=5)
    async def test_paginate_timeout(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        assert p.paginating
        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(70)
        assert p.paginating
        await advance_time(125)
        assert not p.paginating
        page = await fetcher.get_page(1)
        assert p.embed.description == '\n'.join(
            [
                page['entry_text'],
                '',
                'Confused? React with \N{INFORMATION SOURCE} for more info.',
            ]
        )
        assert not hasattr(p.embed.footer.text, 'text')
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert p.message is send_result
        assert send_result.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        send_result.clear_reactions.assert_awaited_once_with()
        send_result.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5, 6], 3]], indirect=['fetcher'])
    @pytest.mark.flaky(reruns=5)
    async def test_paginate_two_pages_timeout(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        assert p.paginating
        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(125)
        assert not p.paginating
        assert isinstance(context, MockContext)
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert isinstance(p.message, MockMessage)
        assert p.message is send_result
        assert send_result.add_reaction.await_count == 5
        context.message.clear_reactions.assert_not_awaited()
        send_result.clear_reactions.assert_awaited_once_with()
        send_result.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize(
        'permissions', [{'manage_messages': False}], indirect=['permissions']
    )
    @pytest.mark.flaky(reruns=5)
    async def test_paginate_timeout_no_manage_messages(
        self,
        mocker: MockerFixture,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        assert p.paginating
        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(125)
        assert not p.paginating
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        assert p.message is send_result
        assert send_result.add_reaction.await_count == 7
        context.message.clear_reactions.assert_not_awaited()
        send_result.clear_reactions.assert_awaited_once_with()
        send_result.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5], 10]], indirect=['fetcher'])
    @pytest.mark.flaky(reruns=5)
    async def test_paginate_not_paginated(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        assert not p.paginating
        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(125)
        assert not p.paginating
        page = await fetcher.get_page(1)
        assert p.embed.description == page['entry_text']
        assert p.message is context.message
        context.channel.send.assert_awaited_once_with(embed=p.embed)
        send_result.add_reaction.assert_not_awaited()
        send_result.clear_reactions.assert_not_awaited()
        send_result.clear_reactions.assert_not_awaited()
        send_result.remove_reaction.assert_not_awaited()
        assert p.match is None

    @pytest.mark.flaky(reruns=5)
    async def test_react_stop(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        asyncio.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)
        reaction = MockReaction.create('\N{BLACK SQUARE FOR STOP}', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert not p.paginating
        assert p.message is send_result
        send_result.delete.assert_awaited_once_with()
        send_result.remove_reaction.assert_awaited_once_with(reaction, context.author)
        await advance_time(125)

    @pytest.mark.parametrize(
        'emoji,expected_page',
        [
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', 2),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', 3),
        ],
        ids=['next', 'last'],
    )
    @pytest.mark.flaky(reruns=5)
    async def test_react_once(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        emoji: str,
        expected_page: int,
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        asyncio.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)
        reaction = MockReaction.create(emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == expected_page
        page = await fetcher.get_page(expected_page)
        assert p.embed.description == page['entry_text']
        assert p.message is send_result
        send_result.edit.assert_awaited_once_with(embed=p.embed)
        await advance_time(125)

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
    @pytest.mark.flaky(reruns=5)
    async def test_react_twice(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        first_emoji: str,
        second_emoji: str,
        expected_page: int,
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        asyncio.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)
        reaction = MockReaction.create(first_emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        reaction = MockReaction.create(second_emoji, p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        assert p.paginating
        assert p.current_page == expected_page
        assert p.message is send_result
        assert send_result.edit.await_count == 2
        send_result.edit.assert_awaited_with(embed=p.embed)
        await advance_time(125)

    @pytest.mark.flaky(reruns=5)
    async def test_paginate_previous_checked(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        asyncio.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)
        reaction = MockReaction.create('\N{BLACK LEFT-POINTING TRIANGLE}', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(5)
        assert p.paginating
        assert p.current_page == 1
        assert p.message is send_result
        assert send_result.edit.await_count == 0
        await advance_time(125)

    @pytest.mark.flaky(reruns=5)
    async def test_paginate_next_checked(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(5)
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING TRIANGLE}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(5)
        assert p.paginating
        assert p.current_page == 3
        assert p.message is send_result
        assert send_result.edit.await_count == 1
        await advance_time(125)

    @pytest.mark.parametrize('fetcher', [[[1, 2, 3, 4, 5, 6], 3]], indirect=['fetcher'])
    @pytest.mark.flaky(reruns=5)
    async def test_paginate_react_check_fails(
        self,
        context: MockContext,
        fetcher: ListPageSource[int],
        advance_time: ClockAdvancer,
        send_result: MockMessage,
    ) -> None:
        event_loop = asyncio.get_running_loop()
        p = InteractivePager[int].create(cast('Any', context), fetcher)

        event_loop.create_task(p.paginate())  # noqa: RUF006
        await advance_time(0)

        # mismatching author id
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING TRIANGLE}', p.message.id
        )
        await context.bot._dispatch_wait_for(
            'reaction_add', reaction, discord.Object(400)
        )
        await advance_time(2)

        assert p.message is send_result
        assert send_result.edit.await_count == 0

        # mismatching message id
        reaction = MockReaction.create('\N{BLACK RIGHT-POINTING TRIANGLE}', 400)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(2)

        assert send_result.edit.await_count == 0

        # mismatching reaction emoji
        reaction = MockReaction.create('stuff', p.message.id)
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(2)

        assert send_result.edit.await_count == 0

        # reaction emoji that isn't used
        reaction = MockReaction.create(
            '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', p.message.id
        )
        await context.bot._dispatch_wait_for('reaction_add', reaction, context.author)
        await advance_time(2)

        assert send_result.edit.await_count == 0

        await advance_time(125)
