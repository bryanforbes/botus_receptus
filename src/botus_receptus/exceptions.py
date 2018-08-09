from discord.ext import commands


class OnlyDirectMessage(commands.CheckFailure):
    pass


class NotGuildOwner(commands.CheckFailure):
    pass
