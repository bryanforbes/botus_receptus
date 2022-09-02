from __future__ import annotations

from typing import Any

from discord.ext import commands


class OnlyDirectMessage(commands.CheckFailure):
    ...


class NotGuildOwner(commands.CheckFailure):
    ...


class BotusReceptusException(Exception):
    ...


class ExtensionError(BotusReceptusException):
    def __init__(self, message: str | None = None, /, *args: Any, name: str) -> None:
        self.name: str = name
        message = message or f'Extension {name!r} had an error.'
        # clean-up @everyone and @here mentions
        m = message.replace('@everyone', '@\u200beveryone').replace(
            '@here', '@\u200bhere'
        )
        super().__init__(m, *args)


class ExtensionAlreadyLoaded(ExtensionError):
    def __init__(self, name: str, /) -> None:
        super().__init__(f'Extension {name!r} has not been loaded.', name=name)


class ExtensionNotLoaded(ExtensionError):
    def __init__(self, name: str, /) -> None:
        super().__init__(f'Extension {name!r} has not been loaded.', name=name)


class NoEntryPointError(ExtensionError):
    def __init__(self, name: str, /) -> None:
        super().__init__(f"Extension {name!r} has no 'setup' function.", name=name)


class ExtensionFailed(ExtensionError):
    def __init__(self, name: str, original: Exception, /) -> None:
        self.original: Exception = original
        msg = (
            f'Extension {name!r} raised an error: '
            f'{original.__class__.__name__}: {original}'
        )
        super().__init__(msg, name=name)


class ExtensionNotFound(ExtensionError):
    def __init__(self, name: str, /) -> None:
        msg = f'Extension {name!r} could not be loaded.'
        super().__init__(msg, name=name)
