from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from functools import partial
from typing import TYPE_CHECKING, Final, Protocol, Union, cast

if TYPE_CHECKING:
    from typing_extensions import TypeAlias


# Inspired by https://github.com/TehShrike/regex-fun


_ReOrStrType: TypeAlias = Union[str, re.Pattern[str]]


class _ReOrStrFuncType(Protocol):
    def __call__(self, /, *args: _ReOrStrType) -> str:
        ...


class _ReOrStrGreedyFuncType(Protocol):
    def __call__(self, /, *args: _ReOrStrType, greedy: bool = True) -> str:
        ...


class _GrouperType(Protocol):
    def __call__(self, /, *args: _ReOrStrType, joiner: str = '') -> str:
        ...


A: Final = re.A
ASCII: Final = re.ASCII
DEBUG: Final = re.DEBUG
I: Final = re.I  # noqa: E741
IGNORECASE: Final = re.IGNORECASE
L: Final = re.L
LOCALE: Final = re.LOCALE
M: Final = re.M
MULTILINE: Final = re.MULTILINE
S: Final = re.S
DOTALL: Final = re.DOTALL
X: Final = re.X
VERBOSE: Final = re.VERBOSE


def compile(*args: _ReOrStrType, flags: int = 0) -> re.Pattern[str]:
    return re.compile(combine(*args), flags=flags)


def _to_str(reOrStr: _ReOrStrType, /) -> str:
    if isinstance(reOrStr, str):
        return reOrStr
    else:
        return str(reOrStr.pattern)


def combine(*args: _ReOrStrType, joiner: str = '') -> str:
    return joiner.join(map(_to_str, args))


def group(*args: _ReOrStrType, start: str = '(?:', joiner: str = '') -> str:
    return start + combine(*args, joiner=joiner) + ')'


capture: Final = cast(_ReOrStrFuncType, partial(group, start='('))
either: Final = cast(_ReOrStrFuncType, partial(group, joiner='|'))


def named_group(name: str, /) -> _GrouperType:
    def grouper(*args: _ReOrStrType, joiner: str = '') -> str:
        return group(*args, start=f'(?P<{name}>', joiner=joiner)

    return grouper


def atomic(string: str, /) -> str:
    if len(string) == 2 and string[0] == '\\':
        return string

    if (string[0] == '(' and string[-1] == ')') or (
        string[0] == '[' and string[-1] == ']'
    ):
        return string

    return group(string)


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
