from __future__ import annotations

from .. import client
from .base import AutoShardedClientMixin, ClientMixin


class Client(ClientMixin, client.Client):
    ...


class AutoShardedClient(AutoShardedClientMixin, client.AutoShardedClient):
    ...
