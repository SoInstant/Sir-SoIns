from datetime import date
import os
import sys
import asyncio
from datetime import datetime

import discord.ext.commands as commands

from parameters import CHECKMARK, LOADING


class Miscellaneous(commands.Cog):
    """
    A set of miscellaneous commands that aid in SoInstant's life.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Clears n messages from the channel.")
    async def clearmsg(self, ctx, n=None):
        bot_message = await ctx.channel.send(
            content=f":hourglass: Deleting messages {LOADING}"
        )
        if n:
            n = int(n)
        counter = 0
        async for message in ctx.channel.history(limit=n):
            if counter == 0:
                counter += 1
                continue
            counter += 1
            await message.delete()
            await asyncio.sleep(0.69)
        if counter == 1:
            await bot_message.edit(content=f"{CHECKMARK} 1 message has been deleted!")
        else:
            await bot_message.edit(
                content=f"{CHECKMARK} {counter} messages have been deleted!"
            )

    # @commands.command(
    #     name="stats", help="Links the skyshiiyu and plancke pages of the user."
    # )
    # async def skylea(self, ctx, username="SoInstantPlayz"):
    #     await ctx.channel.send(content=f"https://sky.shiiyu.moe/stats/{username}")
    #     await ctx.channel.send(
    #         content=f"https://plancke.io/hypixel/player/stats/{username}"
    #     )

    @commands.command(name="restart", help="Restarts the application.")
    async def restart(self, ctx):
        await ctx.channel.send(f":hourglass: Restarting bot {LOADING}")
        os.execv(sys.executable, ["python"] + sys.argv)

    @commands.command(
        name="clearlogs", help="Clears the logs folder of any logs older than a week"
    )
    async def clearlogs(self, ctx):
        now = datetime.utcnow().timestamp()
        counter = 0
        bot_message = await ctx.channel.send(
            content=f":hourglass: Deleting logs {LOADING}"
        )
        for i in os.listdir("./logs"):
            filename, file_ext = os.path.splitext(i)
            if now - float(filename) > 86400:
                os.remove(os.path.join("./logs", i))
                counter += 1
        await bot_message.edit(
            content=f"{CHECKMARK} {counter} old log(s) have been deleted!"
        )
