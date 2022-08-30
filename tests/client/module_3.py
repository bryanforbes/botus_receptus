from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botus_receptus.client import Client


async def setup(client: Client) -> None:
    if client.module_3_setup_2:  # pyright: ignore
        client.module_3_setup_3 = True  # pyright: ignore
    else:
        client.module_3_setup_1 = True  # pyright: ignore


async def teardown(client: Client) -> None:
    client.module_3_torn_down_1 = True  # pyright: ignore
