from __future__ import annotations

from .. import client
from .base import ClientBase


class Client(ClientBase, client.Client):
    ...


class AutoShardedClient(ClientBase, client.AutoShardedClient):
    ...
