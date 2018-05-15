from typing import Callable
from mypy_extensions import Arg, DefaultNamedArg

from . import re

PluralizerType = Callable[[Arg(int, 'value'),
                           DefaultNamedArg(bool, 'include_number')], str]


def pluralizer(word: str, suffix: str = 's') -> PluralizerType:
    def pluralize(value: int, *, include_number: bool = True) -> str:
        if include_number:
            result = f'{value} {word}'
        else:
            result = word

        if value == 0 or value > 1:
            result = f'{result}{suffix}'

        return result

    return pluralize


_mention_pattern_re = re.compile(
    '@', re.named_group('target')(re.one_or_more(re.ANY_CHARACTER))
)

_formatting_re = re.compile(
    re.named_group('target')('[`*_~]')
)


def remove_mentions(string: str) -> str:
    return _mention_pattern_re.sub('@\u200b\\g<target>', string)


def error(text: str) -> str:
    return f'\N{NO ENTRY} {text}'


def warning(text: str) -> str:
    return f'\N{WARNING SIGN} {text}'


def info(text: str) -> str:
    return f'\N{INFORMATION SOURCE} {text}'


def bold(text: str) -> str:
    return f'**{text}**'


def italics(text: str) -> str:
    return f'*{text}*'


def strikethrough(text: str) -> str:
    return f'~~{text}~~'


def underline(text: str) -> str:
    return f'__{text}__'


def inline_code(text: str) -> str:
    return f'`{text}`'


def code_block(text: str, language: str = '') -> str:
    return f'```{language}\n{text}\n```'


def escape(text: str, *, mentions: bool = False, formatting: bool = False) -> str:
    if mentions:
        text = _mention_pattern_re.sub('@\u200b\\g<target>', text)
    if formatting:
        text = _formatting_re.sub('\\\\g<target>', text)

    return text
