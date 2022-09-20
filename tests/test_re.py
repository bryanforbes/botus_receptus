from __future__ import annotations

import re as _re_stdlib

import pytest

from botus_receptus import re


def test_combine() -> None:
    assert re.combine('a', 'b', 'c') == 'abc'
    assert re.combine('a', 'b', 'c', joiner='|') == 'a|b|c'
    assert re.combine('abc', 'd', joiner='|') == 'abc|d'
    assert re.combine('abc', 'd', joiner='|') == 'abc|d'
    assert re.combine(_re_stdlib.compile(r'\w+'), 'abc', joiner=',') == r'\w+,abc'


@pytest.mark.parametrize(
    'args,flags,expected',
    [
        (['a', 'b', 'c'], 0, _re_stdlib.compile(r'abc', flags=0)),
        (
            ['abc', 'd', 'e'],
            re.IGNORECASE,
            _re_stdlib.compile(r'abcde', flags=re.IGNORECASE),
        ),
        (
            ['abc', _re_stdlib.compile('(?:d|f)'), 'e'],
            re.IGNORECASE,
            _re_stdlib.compile(r'abc(?:d|f)e', flags=re.IGNORECASE),
        ),
    ],
)
def test_compile(
    args: list[str | re.Pattern[str]],
    flags: int | re.RegexFlag,
    expected: re.Pattern[str],
) -> None:
    actual = re.compile(*args, flags=flags)

    assert actual.pattern == expected.pattern
    assert actual.flags == expected.flags


def test_group() -> None:
    assert re.group('a', 'b', 'c') == r'(?:abc)'
    assert re.group('(?:a', 'bc)') == r'(?:abc)'
    assert re.group('abc', 'd', 'e', joiner='|') == r'(?:abc|d|e)'
    assert (
        re.group('abc', _re_stdlib.compile('(?:d|f)'), 'e', start='(')
        == r'(abc(?:d|f)e)'
    )
    assert (
        re.group(
            'abc', _re_stdlib.compile('(?:d|f)'), 'e', start='(?P<foo>', joiner=','
        )
        == r'(?P<foo>abc,(?:d|f),e)'
    )


def test_capture() -> None:
    assert re.capture('a', 'b', 'c') == r'(abc)'
    assert re.capture('(?:a', 'bc)') == r'(abc)'
    assert re.capture('abc', _re_stdlib.compile('(?:d|f)'), 'e') == r'(abc(?:d|f)e)'


def test_either() -> None:
    assert re.either('a', 'b', 'c') == r'(?:a|b|c)'
    assert re.either('(?:a', 'bc)') == r'(?:a|bc)'
    assert re.either(r'\*', _re_stdlib.compile('a*'), 'a') == r'(?:\*|a*|a)'


def test_named_group() -> None:
    assert re.named_group('foo')('a', 'b', 'c') == r'(?P<foo>abc)'
    assert (
        re.named_group('bar')('abc', _re_stdlib.compile('(?:d|f)'), 'e', joiner='|')
        == r'(?P<bar>abc|(?:d|f)|e)'
    )


def test_is_atomic() -> None:
    assert re.is_atomic('(wat)')
    assert re.is_atomic('[wat]')
    assert re.is_atomic('(oh(what)now)')
    assert re.is_atomic('([wat])')
    assert re.is_atomic('[(wat)]')
    assert re.is_atomic('a')
    assert re.is_atomic(r'\n')
    assert not re.is_atomic(r'(wat)*')
    assert not re.is_atomic('[wat][oh]')
    assert not re.is_atomic('now(oh(what))')
    assert not re.is_atomic('(ok)([wat])')
    assert not re.is_atomic('aa')
    assert not re.is_atomic('\n')


def test_atomic() -> None:
    assert re.atomic('(wat)') == '(wat)'
    assert re.atomic('[wat]') == '[wat]'
    assert re.atomic('(oh(what)now)') == '(oh(what)now)'
    assert re.atomic('([wat])') == '([wat])'
    assert re.atomic('[(wat)]') == '[(wat)]'
    assert re.atomic('a') == 'a'
    assert re.atomic(r'(wat)\*') == r'(?:(wat)\*)'
    assert re.atomic('[wat][oh]') == '(?:[wat][oh])'
    assert re.atomic('now(oh(what))') == '(?:now(oh(what)))'
    assert re.atomic('(ok)([wat])') == '(?:(ok)([wat]))'
    assert re.atomic('aa') == '(?:aa)'


def test_optional() -> None:
    assert re.optional('wat') == '(?:wat)?'
    assert re.optional(r'wat\*') == r'(?:wat\*)?'
    assert re.optional(r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp)?'
    assert re.optional('wat', greedy=False) == '(?:wat)??'
    assert re.optional(r'wat\*', greedy=False) == r'(?:wat\*)??'
    assert (
        re.optional(r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp)??'
    )


def test_one_or_more() -> None:
    assert re.one_or_more('wat') == '(?:wat)+'
    assert re.one_or_more(r'wat\*') == r'(?:wat\*)+'
    assert re.one_or_more(r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp)+'
    assert re.one_or_more('wat', greedy=False) == '(?:wat)+?'
    assert re.one_or_more(r'wat\*', greedy=False) == r'(?:wat\*)+?'
    assert (
        re.one_or_more(r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp)+?'
    )


def test_any_number_of() -> None:
    assert re.any_number_of('wat') == '(?:wat)*'
    assert re.any_number_of(r'wat\*') == r'(?:wat\*)*'
    assert re.any_number_of(r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp)*'
    assert re.any_number_of('wat', greedy=False) == '(?:wat)*?'
    assert re.any_number_of(r'wat\*', greedy=False) == r'(?:wat\*)*?'
    assert (
        re.any_number_of(r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp)*?'
    )


def test_exactly() -> None:
    assert re.exactly(3, 'wat') == '(?:wat){3}'
    assert re.exactly(2, r'wat\*') == r'(?:wat\*){2}'
    assert re.exactly(5, r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp){5}'
    assert re.exactly(3, 'wat', greedy=False) == '(?:wat){3}?'
    assert re.exactly(2, r'wat\*', greedy=False) == r'(?:wat\*){2}?'
    assert (
        re.exactly(5, r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp){5}?'
    )


def test_at_least() -> None:
    assert re.at_least(3, 'wat') == '(?:wat){3,}'
    assert re.at_least(2, r'wat\*') == r'(?:wat\*){2,}'
    assert re.at_least(5, r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp){5,}'
    assert re.at_least(3, 'wat', greedy=False) == '(?:wat){3,}?'
    assert re.at_least(2, r'wat\*', greedy=False) == r'(?:wat\*){2,}?'
    assert (
        re.at_least(5, r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp){5,}?'
    )


def test_between() -> None:
    assert re.between(2, 3, 'wat') == '(?:wat){2,3}'
    assert re.between(1, 2, r'wat\*') == r'(?:wat\*){1,2}'
    assert (
        re.between(2, 5, r'wat\*', _re_stdlib.compile('yarp')) == r'(?:wat\*yarp){2,5}'
    )
    assert re.between(2, 3, 'wat', greedy=False) == '(?:wat){2,3}?'
    assert re.between(1, 2, r'wat\*', greedy=False) == r'(?:wat\*){1,2}?'
    assert (
        re.between(2, 5, r'wat\*', _re_stdlib.compile('yarp'), greedy=False)
        == r'(?:wat\*yarp){2,5}?'
    )


def test_escape_all() -> None:
    assert list(re.escape_all(['sup+', 'sup*', _re_stdlib.compile(r'sup\+')])) == [
        r'sup\+',
        r'sup\*',
        r'sup\+',
    ]


def test_if_group() -> None:
    assert re.if_group('name', 'a') == '(?(name)a|)'
    assert re.if_group('name', _re_stdlib.compile('ab'), 'cd') == '(?(name)ab|cd)'
    assert (
        re.if_group('name', _re_stdlib.compile('a|b'), 'c|d')
        == '(?(name)(?:a|b)|(?:c|d))'
    )


def test_composition() -> None:
    assert re.optional(re.combine('a', _re_stdlib.compile('bc'))) == r'(?:abc)?'
    assert re.optional(re.either('a', _re_stdlib.compile('bc'))) == r'(?:a|bc)?'
    assert re.capture(re.either('a', _re_stdlib.compile('bc'))) == r'(a|bc)'
    assert (
        re.either(r'sup\+', re.either('a', _re_stdlib.compile('bc')))
        == r'(?:sup\+|(?:a|bc))'
    )
    assert (
        re.capture(re.either(_re_stdlib.compile('butts'), 'lol|buttocks'))
        == r'(butts|(?:lol|buttocks))'
    )
    assert (
        re.combine(
            re.named_group('book')(re.either('Gen', 'Genesis')), re.optional(re.DOT)
        )
    ) == r'(?P<book>Gen|Genesis)\.?'

    _book_re = re.compile(
        re.named_group('book')(re.either('Gen', 'Genesis')),
        re.optional(re.DOT),
    )
    _book_re_str = r'(?P<book>Gen|Genesis)\.?'
    assert _book_re.pattern == _book_re_str

    _colon = re.combine(
        re.any_number_of(re.WHITESPACE), ':', re.any_number_of(re.WHITESPACE)
    )
    _colon_str = r'\s*:\s*'
    assert _colon == _colon_str

    _one_or_more_digit = re.one_or_more(re.DIGIT)
    _one_or_more_digit_str = r'\d+'
    assert _one_or_more_digit == _one_or_more_digit_str

    _dashes_str = '\u2013\u2014'

    _reference_re = re.compile(
        _book_re,
        re.one_or_more(re.WHITESPACE),
        re.named_group('chapter_start')(_one_or_more_digit),
        _colon,
        re.named_group('verse_start')(_one_or_more_digit),
        re.optional(
            re.any_number_of(re.WHITESPACE),
            '[',
            re.DASH,
            '\u2013',
            '\u2014',
            ']',
            re.any_number_of(re.WHITESPACE),
            re.optional(re.named_group('chapter_end')(_one_or_more_digit), _colon),
            re.named_group('verse_end')(_one_or_more_digit),
        ),
    )
    _reference_re_str = (
        rf'(?:{_book_re_str})\s+(?P<chapter_start>{_one_or_more_digit_str}){_colon_str}'
        rf'(?P<verse_start>{_one_or_more_digit_str})(?:\s*[\-{_dashes_str}]\s*'
        rf'(?:(?P<chapter_end>{_one_or_more_digit_str}){_colon_str})?'
        rf'(?P<verse_end>{_one_or_more_digit_str}))?'
    )
    assert _reference_re.pattern == _reference_re_str

    assert (
        re.compile(
            re.optional(
                re.named_group('bracket')(
                    re.LEFT_BRACKET, re.any_number_of(re.WHITESPACE)
                )
            ),
            _reference_re,
            re.if_group(
                'bracket',
                re.combine(
                    re.optional(
                        re.one_or_more(re.WHITESPACE),
                        re.named_group('version')(re.one_or_more(re.ALPHANUMERICS)),
                    ),
                    re.any_number_of(re.WHITESPACE),
                    re.RIGHT_BRACKET,
                ),
            ),
        ).pattern
        == rf'(?P<bracket>\[\s*)?(?:{_reference_re_str})'
        r'(?(bracket)(?:\s+(?P<version>\w+))?\s*\]|)'
    )
