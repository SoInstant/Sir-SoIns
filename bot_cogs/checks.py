import discord.ext.commands as commands

from parameters import OWNER_ID


class Checks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.bot_check()
    async def block_dms(self, ctx):
        return ctx.guild != None

    @commands.Cog.bot_check()
    async def block_all(self, ctx):
        return ctx.author.id == OWNER_ID