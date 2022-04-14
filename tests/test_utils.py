from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import ANY, Mock

import discord
import pendulum
import pytest
from attrs import define, field
from discord.ext import commands
from pendulum.duration import Duration

from botus_receptus import utils

from .types import ClockAdvancer, MockerFixture


@define
class MockRole(object):
    id: int = 0
    name: str = ''


@define
class MockMember(object):
    roles: list[MockRole] = field(factory=list)


@pytest.fixture
def mock_member() -> MockMember:
    return MockMember(
        roles=[
            MockRole(id=1, name='foo'),
            MockRole(id=2, name='bar'),
            MockRole(id=3, name='baz'),
        ]
    )


@pytest.fixture
def mock_context(mocker: MockerFixture) -> Mock:
    mock: Mock = mocker.create_autospec(commands.Context)
    mock.message = mocker.MagicMock()
    mock.send.return_value = mocker.sentinel.send_return  # type: ignore

    return mock


@pytest.fixture
def mock_interaction(mocker: MockerFixture) -> Mock:
    mock: Mock = mocker.create_autospec(discord.Interaction)
    mock.response = mocker.create_autospec(discord.InteractionResponse)
    mock.followup = mocker.create_autospec(discord.Webhook)
    mock.followup.send.return_value = (  # type: ignore
        mocker.sentinel.followup_send_return
    )
    mock.original_message.return_value = (  # type: ignore
        mocker.sentinel.original_message_return
    )

    return mock


def test_has_any_role(mock_member: discord.Member) -> None:
    assert utils.has_any_role(mock_member, ['ham', 'spam', 'bar'])
    assert not utils.has_any_role(mock_member, ['ham', 'spam', 'blah'])


def test_has_any_role_id(mock_member: discord.Member) -> None:
    assert utils.has_any_role_id(mock_member, [2, 4, 18])
    assert not utils.has_any_role_id(mock_member, {28, 4, 18})


@pytest.mark.parametrize(
    'duration,expected',
    [
        ('42s', pendulum.duration(seconds=42)),
        ('12m', pendulum.duration(minutes=12)),
        ('20h', pendulum.duration(hours=20)),
        ('7d', pendulum.duration(days=7)),
        ('2w', pendulum.duration(weeks=2)),
        ('1y', pendulum.duration(years=1)),
        ('12m30s', pendulum.duration(seconds=30, minutes=12)),
        ('20h5m', pendulum.duration(hours=20, minutes=5)),
        ('7d10h12s', pendulum.duration(seconds=12, days=7, hours=10)),
        ('2m1y', pendulum.duration(years=1, seconds=120)),
        (' 2m  1y ', pendulum.duration(years=1, seconds=120)),
    ],
)
def test_parse_duration(duration: str, expected: Duration) -> None:
    assert utils.parse_duration(duration) == expected


@pytest.mark.parametrize(
    'duration,message',
    [
        ('42 s', 'Invalid duration'),
        ('42p', 'Invalid duration'),
        ('invalid', 'Invalid duration'),
        ('', 'No duration provided.'),
        ('   ', 'No duration provided.'),
    ],
)
def test_parse_duration_failures(duration: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        utils.parse_duration(duration)


async def test_race(
    event_loop: asyncio.AbstractEventLoop, advance_time: ClockAdvancer
) -> None:
    async def one() -> int:
        await asyncio.sleep(100)
        return 1

    async def two() -> int:
        await asyncio.sleep(50)
        return 2

    async def three() -> int:
        await asyncio.sleep(25)
        return 3

    task = event_loop.create_task(utils.race([one(), two(), three()]))
    await advance_time(35)
    await advance_time(60)
    await advance_time(110)
    assert task.result() == 3


async def test_race_timeout(
    event_loop: asyncio.AbstractEventLoop, advance_time: ClockAdvancer
) -> None:
    async def one() -> int:
        await asyncio.sleep(100)
        return 1

    async def two() -> int:
        await asyncio.sleep(50)
        return 2

    task = event_loop.create_task(utils.race([one(), two()], timeout=25))
    await advance_time(30)
    assert isinstance(task.exception(), asyncio.TimeoutError)


@pytest.mark.parametrize(
    'kwargs,expected',
    [
        ({}, {'type': 'rich'}),
        ({'description': 'baz'}, {'description': 'baz', 'type': 'rich'}),
        (
            {
                'title': 'bar',
                'color': discord.Color.default(),
                'footer': 'baz',
                'thumbnail': 'ham',
                'author': 'spam',
                'image': 'blah',
                'timestamp': datetime.fromisoformat('2022-04-14T16:54:40.595227+00:00'),
                'fields': [{'name': 'one', 'value': 'one', 'inline': True}],
            },
            {
                'type': 'rich',
                'title': 'bar',
                'color': 0,
                'footer': {'text': 'baz'},
                'thumbnail': {'url': 'ham'},
                'author': {'name': 'spam'},
                'image': {'url': 'blah'},
                'timestamp': '2022-04-14T16:54:40.595227+00:00',
                'fields': [{'name': 'one', 'value': 'one', 'inline': True}],
            },
        ),
        (
            {
                'footer': {'text': 'baz', 'icon_url': 'bar'},
                'author': {'name': 'spam', 'url': 'foo', 'icon_url': 'blah'},
            },
            {
                'type': 'rich',
                'footer': {'text': 'baz', 'icon_url': 'bar'},
                'author': {'name': 'spam', 'url': 'foo', 'icon_url': 'blah'},
            },
        ),
    ],
)
def test_create_embed(kwargs: dict[str, Any], expected: dict[str, Any]) -> None:
    embed = utils.create_embed(**kwargs)

    assert embed.to_dict() == expected


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich'},
        ),
        (
            {'description': 'asdf'},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich', 'description': 'asdf'},
        ),
        (
            {'embeds': [discord.Embed()]},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich'},
        ),
        (
            {'reference': [object()]},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich'},
        ),
    ],
)
async def test_send_with_context(
    mocker: MockerFixture,
    mock_context: Mock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (await utils.send(mock_context, **kwargs)) is mocker.sentinel.send_return

    mock_context.send.assert_awaited_once_with(**expected_args)  # type: ignore

    assert (
        mock_context.send.await_args_list[0][1]['embeds'][0].to_dict()  # type: ignore
        == expected_embed
    )

    if 'reference' in kwargs:
        assert (
            mock_context.send.await_args_list[0][1]['reference']  # type: ignore
            is kwargs['reference']
        )
    else:
        assert (
            mock_context.send.await_args_list[0][1]['reference']  # type: ignore
            is mock_context.message  # type: ignore
        )


@pytest.mark.parametrize(
    'kwargs,is_done,expected_args,expected_embed',
    [
        (
            {},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {'description': 'asdf'},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf'},
        ),
        (
            {'embeds': [discord.Embed()]},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {'description': 'asdf'},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf'},
        ),
        (
            {'embeds': [discord.Embed()], 'ephemeral': True},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich'},
        ),
    ],
)
async def test_send_with_interaction(
    mocker: MockerFixture,
    mock_interaction: Mock,
    kwargs: dict[str, Any],
    is_done: bool,
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    mock_interaction.configure_mock(**{'response.is_done.return_value': is_done})
    assert (await utils.send(mock_interaction, **kwargs)) is (
        mocker.sentinel.original_message_return
        if not is_done
        else mocker.sentinel.followup_send_return
    )

    if not is_done:
        mock_interaction.response.send_message.assert_awaited_once_with(  # type: ignore
            **expected_args
        )

        assert (
            mock_interaction.response.send_message.await_args_list[0][  # type: ignore
                1
            ]['embeds'][0].to_dict()
            == expected_embed
        )
        mock_interaction.followup.send.assert_not_awaited()  # type: ignore
    else:
        mock_interaction.response.send_message.assert_not_awaited()  # type: ignore
        mock_interaction.original_message.assert_not_awaited()  # type: ignore
        mock_interaction.followup.send.assert_awaited_once_with(  # type: ignore
            wait=True, **expected_args
        )


async def test_send_raises(mock_context: Mock, mock_interaction: Mock) -> None:
    with pytest.raises(
        TypeError,
        match='^Cannot mix embed content arguments and embeds keyword argument',
    ):
        await utils.send(
            mock_context, description='asdf', embeds=[discord.Embed()]  # type: ignore
        )

    with pytest.raises(
        TypeError,
        match='^Cannot mix embed content arguments and embeds keyword argument',
    ):
        await utils.send(
            mock_interaction,
            description='asdf',
            embeds=[discord.Embed()],  # type: ignore
        )


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich', 'color': 15158332},
        ),
        (
            {'description': 'asdf'},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich', 'description': 'asdf', 'color': 15158332},
        ),
        (
            {'reference': [object()]},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich', 'color': 15158332},
        ),
        (
            {'color': discord.Color.blue()},
            {
                'tts': False,
                'file': None,
                'files': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
            },
            {'type': 'rich', 'color': 3447003},
        ),
    ],
)
async def test_send_error_with_context(
    mocker: MockerFixture,
    mock_context: Mock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (
        await utils.send_error(mock_context, **kwargs)
    ) is mocker.sentinel.send_return

    mock_context.send.assert_awaited_once_with(**expected_args)  # type: ignore

    assert (
        mock_context.send.await_args_list[0][1]['embeds'][0].to_dict()  # type: ignore
        == expected_embed
    )

    if 'reference' in kwargs:
        assert (
            mock_context.send.await_args_list[0][1]['reference']  # type: ignore
            is kwargs['reference']
        )
    else:
        assert (
            mock_context.send.await_args_list[0][1]['reference']  # type: ignore
            is mock_context.message  # type: ignore
        )


@pytest.mark.parametrize(
    'kwargs,is_done,expected_args,expected_embed',
    [
        (
            {},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': discord.Color.red().value},
        ),
        (
            {'description': 'asdf', 'ephemeral': False},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf', 'color': discord.Color.red().value},
        ),
        (
            {'title': 'asdf', 'color': discord.Color.blue()},
            False,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'title': 'asdf', 'color': discord.Color.blue().value},
        ),
        (
            {},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': discord.Color.red().value},
        ),
        (
            {'description': 'asdf', 'ephemeral': False},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf', 'color': discord.Color.red().value},
        ),
        (
            {'title': 'asdf', 'color': discord.Color.blue()},
            True,
            {
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'title': 'asdf', 'color': discord.Color.blue().value},
        ),
    ],
)
async def test_send_error_with_interaction(
    mocker: MockerFixture,
    mock_interaction: Mock,
    kwargs: dict[str, Any],
    is_done: bool,
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    mock_interaction.configure_mock(**{'response.is_done.return_value': is_done})
    assert (await utils.send_error(mock_interaction, **kwargs)) is (
        mocker.sentinel.original_message_return
        if not is_done
        else mocker.sentinel.followup_send_return
    )

    if not is_done:
        mock_interaction.response.send_message.assert_awaited_once_with(  # type: ignore
            **expected_args
        )

        assert (
            mock_interaction.response.send_message.await_args_list[0][  # type: ignore
                1
            ]['embeds'][0].to_dict()
            == expected_embed
        )
        mock_interaction.followup.send.assert_not_awaited()  # type: ignore
    else:
        mock_interaction.response.send_message.assert_not_awaited()  # type: ignore
        mock_interaction.original_message.assert_not_awaited()  # type: ignore
        mock_interaction.followup.send.assert_awaited_once_with(  # type: ignore
            wait=True, **expected_args
        )
