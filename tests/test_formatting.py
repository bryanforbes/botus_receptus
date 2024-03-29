from __future__ import annotations

from typing import Any

import pytest

from botus_receptus.formatting import (
    EmbedPaginator,
    Paginator,
    bold,
    code_block,
    ellipsize,
    error,
    escape,
    info,
    inline_code,
    italics,
    pluralizer,
    remove_mass_mentions,
    strikethrough,
    underline,
    warning,
)


@pytest.mark.parametrize(
    'pluralizer_args,pluralize_args,pluralize_kwargs,expected',
    [
        (['ham'], [0], {}, '0 hams'),
        (['ham'], [1], {}, '1 ham'),
        (['ham'], [2], {}, '2 hams'),
        (['fish', 'es'], [0], {}, '0 fishes'),
        (['fish', 'es'], [1], {}, '1 fish'),
        (['fish', 'es'], [2], {}, '2 fishes'),
        (['fish', 'es'], [0], {'include_number': False}, 'fishes'),
        (['fish', 'es'], [1], {'include_number': False}, 'fish'),
        (['fish', 'es'], [2], {'include_number': False}, 'fishes'),
    ],
)
def test_pluralizer(
    pluralizer_args: list[str],
    pluralize_args: list[int],
    pluralize_kwargs: dict[str, Any],
    expected: str,
) -> None:
    pluralize = pluralizer(*pluralizer_args)

    assert callable(pluralize) is True
    assert pluralize(*pluralize_args, **pluralize_kwargs) == expected


class TestPaginator:
    def test_add_line_no_args(self) -> None:
        paginator = Paginator(max_size=13)
        paginator.add_line('123 456 789')
        paginator.add_line()
        assert paginator.pages == ['```\n123\n```', '```\n456\n```', '```\n789\n\n```']

    def test_add_line_larger_than_max_size(self) -> None:
        paginator = Paginator(max_size=13)
        paginator.add_line('123 456 789')
        assert len(paginator.pages) == 3

    def test_empty_adds_to_last_page(self) -> None:
        paginator = Paginator(max_size=14)
        paginator.add_line('123 456 789', empty=True)
        assert paginator.pages[0] == '```\n123\n```'
        assert paginator.pages[1] == '```\n456\n```'
        assert paginator.pages[2] == '```\n789\n\n```'

    def test_pages(self) -> None:
        paginator = Paginator(max_size=13)
        paginator.add_line('123 456 789')

        assert paginator.pages == ['```\n123\n```', '```\n456\n```', '```\n789\n```']

    def test_iterate(self) -> None:
        paginator = Paginator(max_size=13)
        paginator.add_line('123 456 789')

        assert list(paginator) == [
            '```\n123\n```',
            '```\n456\n```',
            '```\n789\n```',
        ]

    def test_prefix_suffix(self) -> None:
        paginator = Paginator(prefix=None, suffix=None, max_size=3)
        paginator.add_line('123 456 789')

        assert list(paginator) == ['123', '456', '789']

    def test_len(self) -> None:
        paginator = Paginator(max_size=11)
        paginator.add_line('123 456 789')
        assert len(paginator) == 30
        paginator.add_line('11')
        assert len(paginator) == 40

    def test_len_no_prefix_suffix(self) -> None:
        paginator = Paginator(prefix=None, suffix=None, max_size=3)
        paginator.add_line('123 456 789')
        assert len(paginator) == 10
        paginator.add_line('11')
        assert len(paginator) == 12

    def test_clear(self) -> None:
        paginator = Paginator(max_size=11)
        paginator.add_line('123 456 789')
        paginator.clear()
        assert len(paginator) == 4

    def test_clear_no_prefix_suffix(self) -> None:
        paginator = Paginator(prefix=None, suffix=None, max_size=3)
        paginator.add_line('123 456 789')
        paginator.clear()
        assert len(paginator) == 0


class TestEmbedPaginator:
    def test_iterate(self) -> None:
        paginator = EmbedPaginator()
        paginator.add_line('123 456 789')

        assert paginator.prefix is None
        assert paginator.suffix is None
        assert paginator.max_size == 4096

        assert paginator.pages[0] == '123 456 789'


def test_remove_mentions() -> None:
    result = remove_mass_mentions("hello, @everyone, I'm @here today")

    assert result == "hello, @\u200beveryone, I'm @\u200bhere today"


def test_error() -> None:
    assert error('some text') == '\N{NO ENTRY} some text'


def test_warning() -> None:
    assert warning('some text') == '\N{WARNING SIGN} some text'


def test_info() -> None:
    assert info('some text') == '\N{INFORMATION SOURCE} some text'


def test_bold() -> None:
    assert bold('some text') == '**some text**'


def test_italics() -> None:
    assert italics('some text') == '*some text*'


def test_strikethrough() -> None:
    assert strikethrough('some text') == '~~some text~~'


def test_underline() -> None:
    assert underline('some text') == '__some text__'


def test_inline_code() -> None:
    assert inline_code('some text') == '`some text`'


def test_code_block() -> None:
    assert code_block('one\ntwo') == '```\none\ntwo\n```'
    assert code_block('one\ntwo', 'javascript') == '```javascript\none\ntwo\n```'


def test_escape() -> None:
    assert escape(bold(strikethrough('some text @here'))) == '**~~some text @here~~**'
    assert (
        escape(
            bold(strikethrough('some text @here')), formatting=True, mass_mentions=True
        )
        == r'\*\*\~\~some text @'
        '\u200b'
        r'here\~\~\*\*'
    )


@pytest.mark.parametrize(
    'text, max_length, expected',
    [
        ('asdf asdf asdf', 40, 'asdf asdf asdf'),
        ('asdf asdf asdf', 10, 'asdf asdf…'),
        ('asdf asdf asdf', 11, 'asdf asdf…'),
    ],
)
def test_ellipsize(text: str, max_length: int, expected: str) -> None:
    assert ellipsize(text, max_length=max_length) == expected
