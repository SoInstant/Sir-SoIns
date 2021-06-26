import discord.ext.commands as commands


class Checks(commands.Cog):
    def __init__(self, bot, owner_id):
        self.bot = bot
        self.OWNER_ID = owner_id

    @commands.Cog.bot_check()
    async def block_dms(self, ctx):
        return ctx.guild != None

    @commands.Cog.bot_check()
    async def block_all(self, ctx):
        return ctx.author.id == self.OWNER_ID