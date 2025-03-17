from __future__ import annotations

from datetime import datetime
from typing import Any

import discord
import pytest

from botus_receptus.embed import Embed


class TestEmbed:
    @pytest.mark.parametrize(
        'kwargs,expected',
        [
            ({}, {'type': 'rich', 'flags': 0}),
            (
                {'description': 'baz'},
                {'description': 'baz', 'type': 'rich', 'flags': 0},
            ),
            (
                {
                    'title': 'bar',
                    'color': discord.Color.default(),
                    'footer': 'baz',
                    'thumbnail': 'ham',
                    'author': 'spam',
                    'image': 'blah',
                    'timestamp': datetime.fromisoformat(
                        '2022-04-14T16:54:40.595227+00:00'
                    ),
                    'fields': [{'name': 'one', 'value': 'one', 'inline': True}],
                },
                {
                    'type': 'rich',
                    'flags': 0,
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
                    'flags': 0,
                    'footer': {'text': 'baz', 'icon_url': 'bar'},
                    'author': {'name': 'spam', 'url': 'foo', 'icon_url': 'blah'},
                },
            ),
        ],
    )
    def test_init(self, kwargs: dict[str, Any], expected: dict[str, Any]) -> None:
        embed = Embed(**kwargs)
        assert isinstance(embed, discord.Embed)
        assert embed.to_dict() == expected
