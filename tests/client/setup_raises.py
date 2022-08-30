from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botus_receptus.client import Client


async def setup(client: Client) -> None:
    raise TypeError
