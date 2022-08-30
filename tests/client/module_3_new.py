from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botus_receptus.client import Client


async def setup(client: Client) -> None:
    client.module_3_setup_2 = True  # pyright: ignore
    raise TypeError


async def teardown(client: Client) -> None:
    client.module_3_torn_down_2 = True  # pyright: ignore
