from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from botus_receptus.client import Client


async def setup(client: Client) -> None:
    client.module_2_setup = True  # pyright: ignore


async def teardown(client: Client) -> None:
    client.module_2_torn_down = True  # pyright: ignore
