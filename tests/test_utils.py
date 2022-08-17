from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from unittest.mock import ANY, AsyncMock, Mock

import discord
import pendulum
import pytest
from attrs import define, field
from discord.ext import commands

from botus_receptus import utils

if TYPE_CHECKING:
    from pendulum.duration import Duration

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
    mock.original_response.return_value = (  # type: ignore
        mocker.sentinel.original_response_return
    )

    return mock


@pytest.fixture
def mock_send(mocker: MockerFixture) -> AsyncMock:
    return mocker.patch(
        'botus_receptus.utils.send', return_value=mocker.sentinel.utils_send_return
    )


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
    'kwargs,expected_args,expected_embed',
    [
        (
            {'content': 'asdf'},
            {
                'content': 'asdf',
                'tts': False,
                'file': None,
                'files': None,
                'embed': None,
                'embeds': None,
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
                'ephemeral': False,
            },
            None,
        ),
        (
            {'embeds': [discord.Embed()]},
            {
                'content': None,
                'tts': False,
                'file': None,
                'files': None,
                'embed': None,
                'embeds': [ANY],
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {'reference': object(), 'ephemeral': True},
            {
                'content': None,
                'tts': False,
                'file': None,
                'files': None,
                'embed': None,
                'embeds': None,
                'delete_after': None,
                'nonce': None,
                'allowed_mentions': None,
                'reference': ANY,
                'view': None,
                'ephemeral': True,
            },
            None,
        ),
    ],
)
async def test_send_with_context(
    mocker: MockerFixture,
    mock_context: Mock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any] | None,
) -> None:
    assert (await utils.send(mock_context, **kwargs)) is mocker.sentinel.send_return

    mock_context.send.assert_awaited_once_with(**expected_args)  # type: ignore

    if expected_embed is None:
        assert mock_context.send.await_args_list[0][1]['embeds'] is None  # type: ignore
    else:
        assert (
            mock_context.send.await_args_list[0][1]['embeds'][  # type: ignore
                0
            ].to_dict()
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
            {'content': 'asdf'},
            False,
            {
                'content': 'asdf',
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': discord.utils.MISSING,
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            None,
        ),
        (
            {'embeds': [discord.Embed()]},
            False,
            {
                'content': None,
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {'ephemeral': True},
            False,
            {
                'content': None,
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': discord.utils.MISSING,
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            None,
        ),
        (
            {'content': 'asdf'},
            True,
            {
                'content': 'asdf',
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': discord.utils.MISSING,
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            None,
        ),
        (
            {'embeds': [discord.Embed()]},
            True,
            {
                'content': discord.utils.MISSING,
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich'},
        ),
        (
            {'ephemeral': True},
            True,
            {
                'content': discord.utils.MISSING,
                'tts': False,
                'file': discord.utils.MISSING,
                'files': discord.utils.MISSING,
                'embed': discord.utils.MISSING,
                'embeds': discord.utils.MISSING,
                'allowed_mentions': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            None,
        ),
    ],
)
async def test_send_with_interaction(
    mocker: MockerFixture,
    mock_interaction: Mock,
    kwargs: dict[str, Any],
    is_done: bool,
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any] | None,
) -> None:
    mock_interaction.configure_mock(**{'response.is_done.return_value': is_done})
    assert (await utils.send(mock_interaction, **kwargs)) is (
        mocker.sentinel.original_response_return
        if not is_done
        else mocker.sentinel.followup_send_return
    )

    if not is_done:
        mock_interaction.response.send_message.assert_awaited_once_with(  # type: ignore
            **expected_args
        )

        if expected_embed is None:
            assert (
                mock_interaction.response.send_message.await_args_list[  # type: ignore
                    0
                ][1]['embeds']
                is discord.utils.MISSING
            )
        else:
            assert (
                mock_interaction.response.send_message.await_args_list[  # type: ignore
                    0
                ][1]['embeds'][0].to_dict()
                == expected_embed
            )

        mock_interaction.followup.send.assert_not_awaited()  # type: ignore
    else:
        mock_interaction.response.send_message.assert_not_awaited()  # type: ignore
        mock_interaction.original_response.assert_not_awaited()  # type: ignore
        mock_interaction.followup.send.assert_awaited_once_with(  # type: ignore
            wait=True, **expected_args
        )

        if expected_embed is None:
            assert (
                mock_interaction.followup.send.await_args_list[0][1][  # type: ignore
                    'embeds'
                ]
                is discord.utils.MISSING
            )
        else:
            assert (
                mock_interaction.followup.send.await_args_list[0][1][  # type: ignore
                    'embeds'
                ][0].to_dict()
                == expected_embed
            )


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': discord.utils.MISSING,
            },
            {'type': 'rich'},
        ),
        (
            {'description': 'asdf'},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': discord.utils.MISSING,
            },
            {'type': 'rich', 'description': 'asdf'},
        ),
        (
            {'reference': [object()]},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': ANY,
                'view': discord.utils.MISSING,
                'ephemeral': discord.utils.MISSING,
            },
            {'type': 'rich'},
        ),
    ],
)
async def test_send_embed_with_context(
    mocker: MockerFixture,
    mock_context: Mock,
    mock_send: AsyncMock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (
        await utils.send_embed(mock_context, **kwargs)
    ) is mocker.sentinel.utils_send_return

    mock_send.assert_awaited_once_with(mock_context, **expected_args)

    assert mock_send.await_args_list[0][1]['embeds'][0].to_dict() == expected_embed


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': discord.utils.MISSING,
            },
            {'type': 'rich'},
        ),
        (
            {'description': 'asdf', 'ephemeral': False},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf'},
        ),
    ],
)
async def test_send_embed_with_interaction(
    mocker: MockerFixture,
    mock_interaction: Mock,
    mock_send: AsyncMock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (
        await utils.send_embed(mock_interaction, **kwargs)
    ) is mocker.sentinel.utils_send_return

    mock_send.assert_awaited_once_with(mock_interaction, **expected_args)

    assert mock_send.await_args_list[0][1]['embeds'][0].to_dict() == expected_embed


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': 15158332},
        ),
        (
            {'description': 'asdf'},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'description': 'asdf', 'color': 15158332},
        ),
        (
            {'reference': [object()]},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': ANY,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': 15158332},
        ),
        (
            {'color': discord.Color.blue()},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': 3447003},
        ),
    ],
)
async def test_send_embed_error_with_context(
    mocker: MockerFixture,
    mock_context: Mock,
    mock_send: AsyncMock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (
        await utils.send_embed_error(mock_context, **kwargs)
    ) is mocker.sentinel.utils_send_return

    mock_send.assert_awaited_once_with(mock_context, **expected_args)

    assert mock_send.await_args_list[0][1]['embeds'][0].to_dict() == expected_embed


@pytest.mark.parametrize(
    'kwargs,expected_args,expected_embed',
    [
        (
            {},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'color': discord.Color.red().value},
        ),
        (
            {'description': 'asdf', 'ephemeral': False},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': False,
            },
            {'type': 'rich', 'description': 'asdf', 'color': discord.Color.red().value},
        ),
        (
            {'title': 'asdf', 'color': discord.Color.blue()},
            {
                'embeds': [ANY],
                'allowed_mentions': discord.utils.MISSING,
                'reference': discord.utils.MISSING,
                'view': discord.utils.MISSING,
                'ephemeral': True,
            },
            {'type': 'rich', 'title': 'asdf', 'color': discord.Color.blue().value},
        ),
    ],
)
async def test_send_embed_error_with_interaction(
    mocker: MockerFixture,
    mock_interaction: Mock,
    mock_send: AsyncMock,
    kwargs: dict[str, Any],
    expected_args: dict[str, Any],
    expected_embed: dict[str, Any],
) -> None:
    assert (
        await utils.send_embed_error(mock_interaction, **kwargs)
    ) is mocker.sentinel.utils_send_return

    mock_send.assert_awaited_once_with(mock_interaction, **expected_args)

    assert mock_send.await_args_list[0][1]['embeds'][0].to_dict() == expected_embed
