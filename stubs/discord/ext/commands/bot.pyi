from typing import Callable, Union, Awaitable, List, Any, Optional, Dict, Set, TypeVar, Type, overload
from .core import GroupMixin, Command
from .context import Context
from .formatter import HelpFormatter
import discord

CommandPrefix = Union[
    str,
    Callable[['Bot', discord.Message], Union[str, Awaitable[str]]]]


def when_mentioned(bot: 'Bot', msg: discord.Message) -> List[str]: ...


def when_mentioned_or(*prefixes) -> Callable[['Bot', discord.Message], List[str]]: ...


ContextType = TypeVar('ContextType', bound=Context)


class BotBase(GroupMixin):
    command_prefix: CommandPrefix
    case_insensitive: bool
    description: str
    self_bot: bool
    formatter: HelpFormatter  # noqa
    pm_help: Optional[bool]
    help_attrs: Dict[str, Any]
    command_not_found: str
    command_has_no_subcommands: str
    owner_id: Optional[int]

    def __init__(self, command_prefix: CommandPrefix, **options) -> None: ...

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None: ...

    async def on_command_error(self, context: Any, exception: Exception) -> None: ...

    async def is_owner(self, user: Union[discord.User, discord.Member]) -> bool: ...

    def add_cog(self, cog: Any) -> None: ...

    def get_cog(self, name: str) -> Any: ...

    def get_cog_commands(self, name: str) -> Set[Command]: ...

    def remove_cog(self, name: str) -> None: ...

    def load_extension(self, name: str) -> None: ...

    def unload_extension(self, name: str) -> None: ...

    async def get_prefix(self, message: discord.Message) -> Union[List[str], str]: ...

    @overload
    async def get_context(self, message: discord.Message) -> Context: ...

    @overload  # noqa: F811
    async def get_context(self, message: discord.Message, *, cls: Type[ContextType]) -> ContextType: ...

    async def invoke(self, ctx: Context) -> None: ...

    async def process_commands(self, message: discord.Message) -> None: ...

    async def on_message(self, message: discord.Message) -> None: ...


class Bot(BotBase, discord.Client):
    ...


class AutoShardedBot(BotBase, discord.AutoShardedClient):
    ...
