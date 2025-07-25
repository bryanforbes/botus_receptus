from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol

from attrs import define, field

from . import re

if TYPE_CHECKING:
    from collections.abc import Iterator


@define
class Paginator:
    prefix: str | None = '```'
    suffix: str | None = '```'
    max_size: int = 2000
    _real_max_size: int = field(init=False)
    _current_page: list[str] = field(init=False)
    _count: int = field(init=False)
    _pages: list[str] = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.clear()

        prefix_size = 0 if self.prefix is None else len(self.prefix) + 1
        suffix_size = 0 if self.suffix is None else len(self.suffix) + 1

        self._real_max_size = self.max_size - (prefix_size + suffix_size)

    def clear(self) -> None:
        if self.prefix is not None:
            self._current_page = [self.prefix]
        else:
            self._current_page = []

        self._count = 0
        self._pages = []

    def _add_line(self, line: str = '', /, *, empty: bool = False) -> None:
        if self._count + len(line) > self._real_max_size:
            self.close_page()

        self._current_page.append(line)
        self._count += len(line) + 1

        if empty:
            self._current_page.append('')
            self._count += 1

    def add_line(self, line: str = '', /, *, empty: bool = False) -> None:
        if len(line) == 0:
            self._add_line(line, empty=empty)
            return

        while len(line) > 0:
            # if the line is too long, paginate it
            if len(line) > self._real_max_size:
                index = line.rfind(' ', 0, self._real_max_size + 1)
                sub_line = line[:index]
                sub_empty = False
                line = line[index + 1 :]
            else:
                sub_line = line
                sub_empty = empty
                line = ''

            self._add_line(sub_line, empty=sub_empty)

    def close_page(self) -> None:
        if self.suffix is not None:
            self._current_page.append(self.suffix)
        self._pages.append('\n'.join(self._current_page))

        if self.prefix is not None:
            self._current_page = [self.prefix]
        else:
            self._current_page = []

        self._count = 0

    def __len__(self) -> int:
        total = sum(len(p) for p in self._pages)
        prefix_length = (len(self.prefix) + 1) if self.prefix is not None else 0
        return total + self._count + prefix_length

    @property
    def pages(self) -> list[str]:
        if self.prefix is not None:
            if len(self._current_page) > 1:
                self.close_page()
        elif len(self._current_page) > 0:
            self.close_page()

        return self._pages

    def __iter__(self) -> Iterator[str]:
        return self.pages.__iter__()


@define
class EmbedPaginator(Paginator):
    prefix: str | None = None
    suffix: str | None = None
    max_size: int = 4096


class PluralizerType(Protocol):
    def __call__(self, value: int, /, *, include_number: bool = True) -> str: ...


def pluralizer(word: str, suffix: str = 's') -> PluralizerType:
    def pluralize(value: int, /, *, include_number: bool = True) -> str:
        result = f'{value} {word}' if include_number else word

        if value == 0 or value > 1:
            result = f'{result}{suffix}'

        return result

    return pluralize


_mass_mention_pattern_re: Final = re.compile(
    '@', re.named_group('target')(re.either('everyone', 'here'))
)

_formatting_re: Final = re.compile(re.named_group('target')('[`*_~]'))


def remove_mass_mentions(string: str, /) -> str:
    return _mass_mention_pattern_re.sub('@\u200b' r'\g<target>', string)  # noqa: ISC001


def error(text: str, /) -> str:
    return f'\N{NO ENTRY} {text}'


def warning(text: str, /) -> str:
    return f'\N{WARNING SIGN} {text}'


def info(text: str, /) -> str:
    return f'\N{INFORMATION SOURCE} {text}'


def bold(text: str, /) -> str:
    return f'**{text}**'


def italics(text: str, /) -> str:
    return f'*{text}*'


def strikethrough(text: str, /) -> str:
    return f'~~{text}~~'


def underline(text: str, /) -> str:
    return f'__{text}__'


def inline_code(text: str, /) -> str:
    return f'`{text}`'


def code_block(text: str, language: str = '', /) -> str:
    return f'```{language}\n{text}\n```'


def escape(
    text: str, /, *, mass_mentions: bool = False, formatting: bool = False
) -> str:
    if mass_mentions:
        text = remove_mass_mentions(text)
    if formatting:
        text = _formatting_re.sub(r'\\\g<target>', text)

    return text


def ellipsize(text: str, /, *, max_length: int) -> str:
    if len(text) > max_length:
        return f'{text[: max_length - 1].strip()}…'

    return text
