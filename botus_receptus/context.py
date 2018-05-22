from typing import Optional, List, Iterable

import discord
from discord.ext import commands


class EmbedContext(commands.Context):
    async def send_embed(self, description: Optional[str] = None, *, tts: bool = False,
                         embed: Optional[discord.Embed] = None, file: Optional[object] = None,
                         files: Optional[List[object]] = None, delete_after: Optional[float] = None,
                         nonce: Optional[int] = None) -> discord.Message:
        embed = discord.Embed() if embed is None else discord.Embed.from_data(embed.to_dict())

        if description is not None:
            embed.description = description

        return await self.send(tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce)


class PaginatedContext(commands.Context):
    async def send_pages(self, pages: Iterable[str], *, tts: bool = False, delete_after: Optional[float] = None,
                         nonce: Optional[int] = None) -> List[discord.Message]:
        return [await self.send(page, tts=tts, delete_after=delete_after, nonce=nonce) for page in pages]
