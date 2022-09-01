from __future__ import annotations

import contextlib
import importlib.util
import sys
import types
from typing import TYPE_CHECKING, Any

import discord

from . import base
from .app_commands import CommandTree
from .exceptions import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    NoEntryPointError,
)

if TYPE_CHECKING:
    import importlib.machinery
    from collections.abc import Mapping
    from typing_extensions import Self

    from .config import Config


class _ClientBase(base.Base):
    __extensions: dict[str, types.ModuleType]
    __tree: CommandTree[Any]

    def __init__(
        self,
        config: Config,
        /,
        *args: Any,
        tree_cls: type[CommandTree[Any]] = CommandTree,
        **kwargs: Any,
    ) -> None:
        self.__extensions = {}

        super().__init__(config, *args, **kwargs)

        self.__tree = tree_cls(self)

    @property
    def tree(self) -> CommandTree[Self]:  # pyright: ignore
        return self.__tree

    @property
    def extensions(self) -> Mapping[str, types.ModuleType]:
        return types.MappingProxyType(self.__extensions)

    async def close(self) -> None:
        for extension in tuple(self.__extensions):
            with contextlib.suppress(Exception):
                await self.unload_extension(extension)

        await super().close()

    async def _remove_module_references(self, name: str, /) -> None:
        self.__tree._remove_with_module(name)

    async def _call_module_finalizers(self, lib: types.ModuleType, key: str, /) -> None:
        try:
            func = lib.teardown
        except AttributeError:
            pass
        else:
            with contextlib.suppress(Exception):
                await func(self)
        finally:
            self.__extensions.pop(key, None)
            sys.modules.pop(key, None)
            name = lib.__name__
            for module in list(sys.modules.keys()):
                if discord.utils._is_submodule(name, module):
                    del sys.modules[module]

    async def _load_from_module_spec(
        self, spec: importlib.machinery.ModuleSpec, key: str, /
    ) -> None:
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            del sys.modules[key]
            raise ExtensionFailed(key, e) from e

        try:
            setup = lib.setup
        except AttributeError:
            del sys.modules[key]
            raise NoEntryPointError(key) from None

        try:
            await setup(self)
        except Exception as e:
            del sys.modules[key]
            await self._remove_module_references(lib.__name__)
            await self._call_module_finalizers(lib, key)
            raise ExtensionFailed(key, e) from e
        else:
            self.__extensions[key] = lib

    def _resolve_name(self, name: str, package: str | None, /) -> str:
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            raise ExtensionNotFound(name) from None

    async def load_extension(self, name: str, /, *, package: str | None = None) -> None:
        name = self._resolve_name(name, package)
        if name in self.__extensions:
            raise ExtensionAlreadyLoaded(name)

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ExtensionNotFound(name)

        await self._load_from_module_spec(spec, name)

    async def unload_extension(
        self, name: str, /, *, package: str | None = None
    ) -> None:
        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise ExtensionNotLoaded(name)

        await self._remove_module_references(lib.__name__)
        await self._call_module_finalizers(lib, name)

    async def reload_extension(
        self, name: str, /, *, package: str | None = None
    ) -> None:
        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise ExtensionNotLoaded(name)

        # get the previous module states from sys modules
        modules = {
            name: module
            for name, module in sys.modules.items()
            if discord.utils._is_submodule(lib.__name__, name)
        }

        try:
            # Unload and then load the module...
            await self._remove_module_references(lib.__name__)
            await self._call_module_finalizers(lib, name)
            await self.load_extension(name)
        except Exception:
            # if the load failed, the remnants should have been
            # cleaned from the load_extension function call
            # so let's load it from our old compiled library.
            await lib.setup(self)
            self.__extensions[name] = lib

            # revert sys.modules back to normal and raise back to caller
            sys.modules.update(modules)
            raise


class Client(_ClientBase, discord.Client):
    ...


class AutoShardedClient(_ClientBase, discord.AutoShardedClient):
    ...
