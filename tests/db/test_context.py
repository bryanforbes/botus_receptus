from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
import pytest
from attrs import define
from discord.ext.commands.view import StringView  # type: ignore

from botus_receptus.db import Context

if TYPE_CHECKING:
    from discord.ext import commands

    from ..types import MockerFixture


@define
class MockBot:
    pool: Any


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
    _state: Any = None


@define
class MockCommand:
    ...


class TestContext:
    @pytest.fixture
    def mock_bot(self, mocker: MockerFixture) -> MockBot:
        class MockPool:
            acquire = mocker.AsyncMock()
            release = mocker.AsyncMock()

        return MockBot(pool=MockPool())

    @pytest.fixture
    def mock_mesage(self) -> MockMessage:
        return MockMessage()

    @pytest.fixture
    def mock_command(self) -> MockCommand:
        return MockCommand()

    @pytest.fixture
    def mock_select_all(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.select_all', new_callable=mocker.AsyncMock
        )

    @pytest.fixture
    def mock_select_one(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.select_one', new_callable=mocker.AsyncMock
        )

    @pytest.fixture
    def mock_search(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.search', new_callable=mocker.AsyncMock
        )

    @pytest.fixture
    def mock_update(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.update', new_callable=mocker.AsyncMock
        )

    @pytest.fixture
    def mock_insert_into(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.insert_into', new_callable=mocker.AsyncMock
        )

    @pytest.fixture
    def mock_delete_from(self, mocker: MockerFixture) -> Any:
        return mocker.patch(
            'botus_receptus.db.context.delete_from', new_callable=mocker.AsyncMock
        )

    async def test_acquire(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        async with ctx.acquire():
            assert hasattr(ctx, 'db')
            db = await ctx.acquire()
            assert db == ctx.db
        assert not hasattr(ctx, 'db')

        await ctx.release()

    async def test_select_all(
        self,
        mocker: Any,
        mock_bot: Any,
        mock_select_all: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.select_all(table='foo', columns=['col1'])

        async with ctx.acquire():
            await ctx.select_all(table='foo', columns=['col1'])
            mock_select_all.assert_called_once_with(
                ctx.db,
                table='foo',
                columns=['col1'],
                order_by=None,
                where=None,
                joins=None,
                group_by=None,
                record_class=None,
            )

    async def test_select_one(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_select_one: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.select_one(table='foo', columns=['col1'])

        async with ctx.acquire():
            await ctx.select_one(table='foo', columns=['col1'])
            mock_select_one.assert_called_once_with(
                ctx.db,
                table='foo',
                columns=['col1'],
                where=None,
                joins=None,
                group_by=None,
                record_class=None,
            )

    async def test_search(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_search: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.search(
                table='foo', columns=['col1'], search_columns=['bar'], terms=['baz']
            )

        async with ctx.acquire():
            await ctx.search(
                table='foo', columns=['col1'], search_columns=['bar'], terms=['baz']
            )
            mock_search.assert_called_once_with(
                ctx.db,
                table='foo',
                columns=['col1'],
                search_columns=['bar'],
                terms=['baz'],
                where=None,
                order_by=None,
                joins=None,
                group_by=None,
                record_class=None,
            )

    async def test_update(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_update: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.update(table='foo', values={'bar': 'baz'}, where=['spam = "ham"'])

        async with ctx.acquire():
            await ctx.update(table='foo', values={'bar': 'baz'}, where=['spam = "ham"'])
            mock_update.assert_called_once_with(
                ctx.db, table='foo', values={'bar': 'baz'}, where=['spam = "ham"']
            )

    async def test_insert_into(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_insert_into: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.insert_into(table='foo', values={'bar': 'baz'})

        async with ctx.acquire():
            await ctx.insert_into(table='foo', values={'bar': 'baz'})
            mock_insert_into.assert_called_once_with(
                ctx.db, table='foo', values={'bar': 'baz'}, extra=''
            )

    async def test_delete_from(
        self,
        mocker: MockerFixture,
        mock_bot: Any,
        mock_delete_from: Any,
        mock_mesage: discord.Message,
        mock_command: commands.Command[Any, ..., Any],
    ) -> None:
        ctx = Context(
            prefix='~',
            message=mock_mesage,
            bot=mock_bot,
            command=mock_command,
            view=StringView(''),
        )

        with pytest.raises(RuntimeError):
            await ctx.delete_from(table='foo', where='bar')

        async with ctx.acquire():
            await ctx.delete_from(table='foo', where='bar')
            mock_delete_from.assert_called_once_with(ctx.db, table='foo', where='bar')
