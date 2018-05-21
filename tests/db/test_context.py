import pytest  # type: ignore
import attr
import discord
from typing import Any, Optional
from botus_receptus.db.context import Context


@attr.s(slots=True)
class MockBot(object):
    pool = attr.ib()


@attr.s(slots=True, auto_attribs=True)
class MockUser(object):
    bot: Optional[bool] = None
    id: Optional[int] = None
    mention: Optional[str] = None


@attr.s(slots=True, auto_attribs=True)
class MockMessage(object):
    author: Optional[MockUser] = None
    content: Optional[str] = None
    channel: Optional[discord.abc.GuildChannel] = attr.ib(init=False, default=None)
    _state: Any = attr.ib(init=False, default=None)


class TestContext(object):
    @pytest.fixture
    def mock_bot(self, mocker):
        class MockPool:
            acquire = mocker.AsyncMock()
            release = mocker.AsyncMock()

        return MockBot(pool=MockPool())

    @pytest.fixture
    def mock_select_all(self, mocker):
        return mocker.patch('botus_receptus.db.context.util.select_all', new_callable=mocker.AsyncMock)

    @pytest.fixture
    def mock_select_one(self, mocker):
        return mocker.patch('botus_receptus.db.util.select_one', new_callable=mocker.AsyncMock)

    @pytest.fixture
    def mock_search(self, mocker):
        return mocker.patch('botus_receptus.db.util.search', new_callable=mocker.AsyncMock)

    @pytest.fixture
    def mock_insert_into(self, mocker):
        return mocker.patch('botus_receptus.db.util.insert_into', new_callable=mocker.AsyncMock)

    @pytest.fixture
    def mock_delete_from(self, mocker):
        return mocker.patch('botus_receptus.db.util.delete_from', new_callable=mocker.AsyncMock)

    @pytest.mark.asyncio
    async def test_acquire(self, mocker, mock_bot):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        async with ctx.acquire():
            assert hasattr(ctx, 'db')
            db = await ctx.acquire()
            assert db == ctx.db
        assert not hasattr(ctx, 'db')

        await ctx.release()

    @pytest.mark.asyncio
    async def test_select_all(self, mocker, mock_bot, mock_select_all):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        with pytest.raises(RuntimeError):
            await ctx.select_all(table='foo')

        async with ctx.acquire():
            await ctx.select_all(table='foo')
            mock_select_all.assert_called_once_with(ctx.db, table='foo')

    @pytest.mark.asyncio
    async def test_select_one(self, mocker, mock_bot, mock_select_one):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        with pytest.raises(RuntimeError):
            await ctx.select_one(table='foo')

        async with ctx.acquire():
            await ctx.select_one(table='foo')
            mock_select_one.assert_called_once_with(ctx.db, table='foo')

    @pytest.mark.asyncio
    async def test_search(self, mocker, mock_bot, mock_search):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        with pytest.raises(RuntimeError):
            await ctx.search(table='foo')

        async with ctx.acquire():
            await ctx.search(table='foo')
            mock_search.assert_called_once_with(ctx.db, table='foo')

    @pytest.mark.asyncio
    async def test_insert_into(self, mocker, mock_bot, mock_insert_into):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        with pytest.raises(RuntimeError):
            await ctx.insert_into(table='foo')

        async with ctx.acquire():
            await ctx.insert_into(table='foo')
            mock_insert_into.assert_called_once_with(ctx.db, table='foo')

    @pytest.mark.asyncio
    async def test_delete_from(self, mocker, mock_bot, mock_delete_from):
        ctx = Context(prefix='~', message=MockMessage(), bot=mock_bot)

        with pytest.raises(RuntimeError):
            await ctx.delete_from(table='foo')

        async with ctx.acquire():
            await ctx.delete_from(table='foo')
            mock_delete_from.assert_called_once_with(ctx.db, table='foo')
