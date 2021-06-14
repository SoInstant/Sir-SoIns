import os

import discord
import requests
import asyncpixel
import discord.ext.commands as commands
from dotenv import load_dotenv

from parameters import NAME_URL, ICON_URL, EMBED_COLOR

load_dotenv()
API_KEY = os.getenv("HYPIXEL_API")


def username_to_uuid(username: str):
    response = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{username}"
    )
    return response.json()["id"]


class Stats(commands.Cog):
    """
    Commands for checking the stats of a player on Hypixel.
    """

    def __init__(self, bot):
        self.bot = bot
        self.api = asyncpixel.Hypixel(api_key=API_KEY)

    @commands.group(
        name="stats",
        invoke_without_subcommand=True,
        help="Base command for Hypixel stat checking.",
    )
    async def stats(self, ctx):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Invalid/missing subcommand!"
        )

    @stats.command(name="general")
    async def stats_general(self, ctx, player):
        uuid = username_to_uuid(player)
        player = self.api.player(uuid)
        embed = discord.Embed(
            title=f"**Stats for {player.displayname}**",
            url="https://plancke.io",
            description="bro",
            color=EMBED_COLOR,
        )
        embed.set_author(name="Sir SoInstant", url=NAME_URL, icon_url=ICON_URL)
        embed.set_thumbnail(url=f"https://crafatar.com/renders/head/{uuid}")
        embed.set_footer(text="Made by SoInstant")
        await ctx.send(embed=embed)

    @stats.command(name="bedwars")
    async def stats_bedwars(self, ctx, player):
        pass

    @stats.command(name="bridge")
    async def stats_bridge(self, ctx, player):
        pass
