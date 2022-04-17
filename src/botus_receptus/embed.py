from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any, TypedDict
from typing_extensions import NotRequired

import discord
from discord.types.embed import EmbedType


class FooterData(TypedDict):
    text: NotRequired[str | None]
    icon_url: NotRequired[str | None]


class AuthorData(TypedDict):
    name: str
    url: NotRequired[str | None]
    icon_url: NotRequired[str | None]


class FieldData(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class Embed(discord.Embed):
    def __init__(
        self,
        /,
        *,
        type: EmbedType = 'rich',
        description: Any | None = None,
        title: Any | None = None,
        colour: discord.Color | int | None = None,
        color: discord.Color | int | None = None,
        url: Any | None = None,
        timestamp: datetime | None = None,
        footer: str | FooterData | None = None,
        author: str | AuthorData | None = None,
        thumbnail: str | None = None,
        image: str | None = None,
        fields: Iterable[FieldData] | None = None,
    ) -> None:
        super().__init__(
            type=type,
            description=description,
            title=title,
            colour=colour,
            color=color,
            url=url,
            timestamp=timestamp,
        )

        if footer is not None:
            if isinstance(footer, str):
                self.set_footer(text=footer)
            else:
                self.set_footer(**footer)

        if author is not None:
            if isinstance(author, str):
                self.set_author(name=author)
            else:
                self.set_author(**author)

        if thumbnail is not None:
            self.set_thumbnail(url=thumbnail)

        if image is not None:
            self.set_image(url=image)

        if fields is not None:
            for field in fields:
                self.add_field(**field)
