from __future__ import annotations

from .. import client
from .base import AutoShardedClientBase, ClientBase


class Client(ClientBase, client.Client):
    ...


class AutoShardedClient(AutoShardedClientBase, client.AutoShardedClient):
    ...
