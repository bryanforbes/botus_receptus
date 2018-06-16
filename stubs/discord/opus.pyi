from .errors import DiscordException


def load_opus(name: str) -> None: ...


def is_loaded() -> bool: ...


class OpusError(DiscordException):
    ...


class OpusNotLoaded(DiscordException):
    ...
