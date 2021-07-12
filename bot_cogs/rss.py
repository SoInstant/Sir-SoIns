import feedparser
import discord.ext.commands as commands
import discord

from parameters import ICON_URL

RSS_LINKS = {
    "st": {
        "world": "https://www.straitstimes.com/news/world/rss.xml",
        "business": "https://www.straitstimes.com/news/business/rss.xml",
        "sport": "https://www.straitstimes.com/news/sport/rss.xml",
        "life": "https://www.straitstimes.com/news/life/rss.xml",
        "opinion": "https://www.straitstimes.com/news/opinion/rss.xml",
        "sg": "https://www.straitstimes.com/news/singapore/rss.xml",
        "asia": "https://www.straitstimes.com/news/asia/rss.xml",
        "tech": "https://www.straitstimes.com/news/tech/rss.xml",
        "multimedia": "https://www.straitstimes.com/news/multimedia/rss.xml",
    },
    "cna": {
        "latest": "https://www.channelnewsasia.com/rssfeeds/8395986",
        "asia": "https://www.channelnewsasia.com/rssfeeds/8395744",
        "business": "https://www.channelnewsasia.com/rssfeeds/8395954",
        "sg": "https://www.channelnewsasia.com/rssfeeds/8396082",
        "sport": "https://www.channelnewsasia.com/rssfeeds/8395838",
        "world": "https://www.channelnewsasia.com/rssfeeds/8395884",
    },
}

news_feed = feedparser.parse("https://www.straitstimes.com/news/world/rss.xml")


class RSS(commands.Cog):
    """Commands to access news articles"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="rss",
        invoke_without_command=True,
        help="Base command for rss.",
    )
    async def rss(self, ctx):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Invalid/missing subcommand!"
        )

    @rss.command(name="st")
    async def st(self, ctx, mode):
        embed = discord.Embed(
            title="**World news**", url="https://www.straitstimes.com/world"
        )
        embed.set_author(
            name="Straits Times",
            url="https://www.straitstimes.com",
            icon_url="https://soinstant.ml/st_icon.png",
        )
        embed.add_field(name="[title](link)", value="Summary", inline=False)
        embed.set_footer(text="Generated by Sir SoInstant", icon_url=ICON_URL)
        await ctx.channel.send(embed=embed)
