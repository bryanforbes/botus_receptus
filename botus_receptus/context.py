from typing import Optional, List, Callable, Awaitable, Iterable

import discord
from discord.ext import commands
from mypy_extensions import DefaultArg, DefaultNamedArg


SendFuncType = Callable[[DefaultArg(Optional[str], 'content'),
                         DefaultNamedArg(bool, 'tts'),
                         DefaultNamedArg(Optional[float], 'delete_after'),
                         DefaultNamedArg(Optional[int], 'nonce')], Awaitable[discord.Message]]


class EmbedContext(commands.Context):
    async def send_embed(self, content: Optional[str] = None, *, tts: bool = False,
                         embed: Optional[discord.Embed] = None, file: Optional[object] = None,
                         files: Optional[List[object]] = None, delete_after: Optional[float] = None,
                         nonce: Optional[int] = None) -> discord.Message:
        if content is not None:
            if embed is None:
                embed = discord.Embed()
            embed.description = content

        return await self.send(tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)


class PaginatedContext(commands.Context):
    async def _send_pages(self, pages: Iterable[str], *, tts: bool = False, delete_after: Optional[float] = None,
                          nonce: Optional[int] = None, send: SendFuncType) -> List[discord.Message]:
        return [await send(page, tts=tts, delete_after=delete_after, nonce=nonce) for page in pages]

    async def send_pages(self, pages: Iterable[str], *,
                         tts: bool = False, delete_after: Optional[float] = None,
                         nonce: Optional[int] = None) -> List[discord.Message]:
        return await self._send_pages(pages, tts=tts, delete_after=delete_after, nonce=nonce, send=self.send)


class PaginatedEmbedContext(EmbedContext, PaginatedContext):
    async def send_embed_pages(self, pages: Iterable[str], *, tts: bool = False,
                               delete_after: Optional[float] = None,
                               nonce: Optional[int] = None) -> List[discord.Message]:
        return await self._send_pages(pages, tts=tts, delete_after=delete_after, nonce=nonce, send=self.send_embed)
