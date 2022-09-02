from __future__ import annotations

from typing import TYPE_CHECKING

from .one import One

if TYPE_CHECKING:
    from botus_receptus.client import Client


async def setup(client: Client) -> None:
    client.one_thing = One()  # pyright: ignore
