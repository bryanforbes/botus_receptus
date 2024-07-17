from __future__ import annotations

import re
from functools import partial
from re import (
    ASCII as ASCII,  # noqa: PLC0414
    DEBUG as DEBUG,  # noqa: PLC0414
    DOTALL as DOTALL,  # noqa: PLC0414
    IGNORECASE as IGNORECASE,  # noqa: PLC0414
    LOCALE as LOCALE,  # noqa: PLC0414
    MULTILINE as MULTILINE,  # noqa: PLC0414
    VERBOSE as VERBOSE,  # noqa: PLC0414
    A as A,  # noqa: PLC0414
    I as I,  # noqa: PLC0414
    L as L,  # noqa: PLC0414
    M as M,  # noqa: PLC0414
    Match as Match,  # noqa: PLC0414
    Pattern as Pattern,  # noqa: PLC0414
    RegexFlag as RegexFlag,  # noqa: PLC0414
    S as S,  # noqa: PLC0414
    X as X,  # noqa: PLC0414
)
from typing import TYPE_CHECKING, Final, Protocol, TypeAlias, cast

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

# Inspired by https://github.com/TehShrike/regex-fun


_ReOrStrType: TypeAlias = str | re.Pattern[str]


class _ReOrStrFuncType(Protocol):
    def __call__(self, /, *args: _ReOrStrType) -> str: ...


class _ReOrStrGreedyFuncType(Protocol):
    def __call__(self, /, *args: _ReOrStrType, greedy: bool = True) -> str: ...


class _GrouperType(Protocol):
    def __call__(self, /, *args: _ReOrStrType, joiner: str = '') -> str: ...


def compile(*args: _ReOrStrType, flags: int | re.RegexFlag = 0) -> re.Pattern[str]:
    return re.compile(combine(*args), flags=flags)


def _to_str(re_or_str: _ReOrStrType, /) -> str:
    if isinstance(re_or_str, str):
        return re_or_str

    return str(re_or_str.pattern)


def _no_top_level_ors(string: str, /) -> str:
    if '|' in string:
        return atomic(string)

    return string


def combine(*args: _ReOrStrType, joiner: str = '') -> str:
    return joiner.join(map(_no_top_level_ors, map(_to_str, args)))


_non_capturing_group_re: Final = re.compile(r'^\(\?:(.+)\)$')


def _remove_non_capturing_group(string: str, /) -> str:
    if match := _non_capturing_group_re.match(string):
        return match[1]

    return string


def group(*args: _ReOrStrType, start: str = '(?:', joiner: str = '') -> str:
    body = combine(*args, joiner=joiner)

    if is_atomic(body):
        body = _remove_non_capturing_group(body)

    return f'{start}{body})'


capture: Final = cast(_ReOrStrFuncType, partial(group, start='('))
either: Final = cast(_ReOrStrFuncType, partial(group, joiner='|'))


def named_group(name: str, /) -> _GrouperType:
    def grouper(*args: _ReOrStrType, joiner: str = '') -> str:
        return group(*args, start=f'(?P<{name}>', joiner=joiner)

    return grouper


_atomic_re: Final = re.compile(r'^(?:\\.|\w)$')
_closing_chars: Final = {'(': ')', '[': ']'}


def _is_closed_before_end_of_string(
    string: str, opening_char: str, closing_char: str, /
) -> bool:
    depth = 0

    for character in string[:-1]:
        if character == opening_char:
            depth += 1
        elif character == closing_char:
            depth -= 1

        if depth == 0:
            return True

    return False


def _is_enclosed_by_top_level_chars(string: str, /) -> bool:
    opening_char = string[0]
    closing_char = _closing_chars.get(opening_char)

    if closing_char is None or string[-1] != closing_char:
        return False

    return not _is_closed_before_end_of_string(string, opening_char, closing_char)


def is_atomic(string: str, /) -> bool:
    return (_atomic_re.match(string) is not None) or _is_enclosed_by_top_level_chars(
        string
    )


def atomic(string: str, /) -> str:
    if is_atomic(string):
        return string

    return rf'(?:{string})'


def _suffix(*args: _ReOrStrType, suffix: str, greedy: bool = True) -> str:
    return f'{atomic(combine(*args))}{suffix}{"" if greedy else "?"}'


optional: Final = cast(_ReOrStrGreedyFuncType, partial(_suffix, suffix='?'))
one_or_more: Final = cast(_ReOrStrGreedyFuncType, partial(_suffix, suffix='+'))
any_number_of: Final = cast(_ReOrStrGreedyFuncType, partial(_suffix, suffix='*'))


def exactly(n: int, /, *args: _ReOrStrType, greedy: bool = True) -> str:
    return _suffix(*args, suffix=f'{{{n}}}', greedy=greedy)


def at_least(n: int, /, *args: _ReOrStrType, greedy: bool = True) -> str:
    return _suffix(*args, suffix=f'{{{n},}}', greedy=greedy)


def between(n: int, m: int, /, *args: _ReOrStrType, greedy: bool = True) -> str:
    return _suffix(*args, suffix=f'{{{n},{m}}}', greedy=greedy)


escape: Final = re.escape


def escape_all(patterns: Iterable[str | re.Pattern[str]], /) -> Iterator[str]:
    for pattern in patterns:
        if isinstance(pattern, str):
            yield re.escape(pattern)
        else:
            yield pattern.pattern


def if_group(
    name: int | str, yes_pattern: _ReOrStrType, no_pattern: _ReOrStrType = '', /
) -> str:
    return group(
        _to_str(yes_pattern), _to_str(no_pattern), start=f'(?({name})', joiner='|'
    )


START: Final = '^'
END: Final = '$'
BACKSLASH: Final = '\\'
METACHARACTERS: Final = r'.^$*+?{}[]\|()-'
DIGIT: Final = r'\d'
DIGITS: Final = DIGIT
WHITESPACE: Final = r'\s'
ALPHANUMERIC = r'\w'
ALPHANUMERICS: Final = ALPHANUMERIC
ALPHA: Final = r'[a-zA-Z]'
ALPHAS: Final = ALPHA
A_TO_Z: Final = ALPHA
IDENTIFIER: Final = r'[a-zA-Z_][\w_]*'
WORD_BOUNDARY: Final = r'\b'
DOT: Final = r'\.'
UNDERSCORE: Final = r'_'
DASH: Final = r'\-'
ANYTHING: Final = r'.*'
ANY_CHARACTER: Final = r'.'
NEWLINE: Final = r'\\n'
TAB: Final = r'\\t'
LEFT_BRACKET: Final = r'\['
RIGHT_BRACKET: Final = r'\]'
