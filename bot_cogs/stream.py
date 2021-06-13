import asyncio

import discord
import discord.ext.commands as commands
import youtube_dl

from parameters import LOFI_URL, YTDL_FORMAT_OPTIONS, FFMPEG_OPTIONS, LOADING

# Initialise ytdl
ytdl = youtube_dl.YoutubeDL(YTDL_FORMAT_OPTIONS)

# Custom Classes
class YTDLSource(discord.PCMVolumeTransformer):
    # This was taken from https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


class Stream(commands.Cog):
    """
    Commands for streaming a Youtube video into the voice call.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="stream",
        invoke_without_command=True,
        help="Base command for streaming YT videos.",
    )
    async def stream(self, ctx):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Invalid/missing subcommand!"
        )

    @stream.command(
        name="start",
        help="Joins a voice channel and plays the video from the given URL. Defaults to a Lofi stream",
    )
    async def stream_start(self, ctx, link: str = LOFI_URL):
        if not ctx.author.voice:
            return await ctx.channel.send(
                content="You are not in a voice channel right now!"
            )
        channel = ctx.author.voice.channel
        await channel.connect()
        async with ctx.typing():
            temp_msg = await ctx.channel.send(content=f"Loading stream {LOADING}")
            player = await YTDLSource.from_url(link, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await temp_msg.edit(content=f"Now playing: {player.title}")

    @stream.command(name="stop", help="Stops the lofi player, if playing currently.")
    async def stream_stop(self, ctx):
        await ctx.voice_client.disconnect()
