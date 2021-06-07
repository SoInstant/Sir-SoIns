import os
import sys
from datetime import datetime
import asyncio
from threading import Thread

from discord.ext import commands, timers, tasks
import discord
import youtube_dl
from dotenv import load_dotenv
from quart import Quart

import utils

# ENV Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
REMINDERS_CHANNEL_ID = int(os.getenv("REMINDERS_CHANNEL_ID"))

# Parameters
NAME_URL = "https://soinstant.ml"
ICON_URL = "https://soinstant.ml/static/icon.png"
LOFI_URL = "https://www.youtube.com/watch?v=VfW86fnQL5w"
EMBED_COLOR = 0xB7CAE2
ONLINE_TIME = datetime.utcnow().timestamp()
ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}
ffmpeg_options = {
    "options": "-vn",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Emojis
CHECKMARK = "<a:check:845921511252033587>"
LOADING = "<a:typing:845909278463492126>"

# Custom Classes
class YTDLSource(discord.PCMVolumeTransformer):
    # This was taken from Rapptz/discord.py/examples/basic_voice.py
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# Create Web Server
app = Quart(__name__)


@app.route("/")
async def main():
    return "The Bot is alive"


@app.route("/bot")
async def bot_page():
    return "Bot page"


# Create Bot instance
bot = commands.Bot(command_prefix="!", help_command=None)
bot.timer_manager = timers.TimerManager(bot)


@bot.check
async def block_dms(ctx):
    return ctx.guild != None


@bot.check
async def block_all(ctx):
    return ctx.author.id == OWNER_ID


@tasks.loop(minutes=1)
async def water_break():
    if datetime.utcnow().hour < 14 and datetime.now().minute % 20 == 0:
        temp_msg = await bot.get_channel(REMINDERS_CHANNEL_ID).send(
            f"<@{OWNER_ID}> Water break! :droplet:"
        )
        await asyncio.sleep(200)
        await temp_msg.delete()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await bot.get_channel(OUTPUT_CHANNEL_ID).send(
        content=f"Bot is now online! Time: {ONLINE_TIME}"
    )
    water_break.start()
    pending_tasks = utils.get_reminders()
    for task in pending_tasks:
        bot.timer_manager.create_timer(
            "reminder",
            task["time_warn"] - int(datetime.now().timestamp()),
            args=(
                task["task"],
                task["description"],
                utils.unix_to_timestamp(task["time_due"]),
            ),
        )
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over SoInstant",
            start=datetime.utcnow(),
        )
    )


@bot.event
async def on_reminder(task, description, time_due):
    embed = discord.Embed(title=task, description=f"Due at: {time_due}")
    embed.set_author(name="Sir SoInstant", url=NAME_URL, icon_url=ICON_URL)
    for n, subtask in enumerate(description):
        embed.add_field(name=f"Subtask {n + 1}", value=subtask, inline=False)
    embed.set_footer(text=utils.get_quote())
    await bot.get_channel(REMINDERS_CHANNEL_ID).send(
        content=f"<@{OWNER_ID}> The task {task} is due at {time_due}!", embed=embed
    )


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.channel.send(
#             content=":negative_squared_cross_mark: No such command exists!"
#         )
#     elif isinstance(error, commands.MissingRequiredArgument):
#         await ctx.channel.send(
#             content=":negative_squared_cross_mark: Missing parameters!"
#         )
#     elif isinstance(error, discord.errors.HTTPException):
#         pass
#     else:
#         print(error)


@bot.command(help="Clears n messages from the channel.")
async def clearmsg(ctx, n=None):
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


@bot.command(name="help", help="Shows this message.")
async def help(ctx, *args):
    current_level = {
        _command.name: {
            "_help": _command.help,
            "_command": _command,
            "aliases": _command.aliases,
        }
        for _command in bot.commands
    }
    for arg in args:
        try:
            _command = current_level[arg]["_command"]
            if isinstance(_command, commands.Group):
                current_level = {
                    subcommand.name: {
                        "_help": subcommand.help,
                        "_command": subcommand,
                        "aliases": subcommand.aliases,
                    }
                    for subcommand in _command.commands
                }
            else:
                current_level = dict(
                    [
                        (
                            _command.name,
                            {
                                "_help": _command.help,
                                "_command": _command,
                                "aliases": _command.aliases,
                            },
                        )
                    ]
                )
        except KeyError:
            await ctx.channel.send(
                content=":negative_squared_cross_mark: No such command exists!"
            )

    if not args:
        embed = discord.Embed(title="Bot commands", color=EMBED_COLOR)
    else:
        embed = discord.Embed(
            title="!" + " ".join(args), description=_command.help, color=EMBED_COLOR
        )

    embed.set_author(name="Sir SoInstant", url=NAME_URL, icon_url=ICON_URL)

    if args == () or isinstance(_command, commands.Group):
        for key in sorted(current_level):
            aliases = None
            if current_level[key]["aliases"] != []:
                aliases = ", ".join(current_level[key]["aliases"])
            embed.add_field(
                name=key,
                value=f"```{current_level[key]['_help']}\nAliases: {aliases}```",
                inline=False,
            )
    embed.set_footer(text="Type !help command for more info on a command.")

    await ctx.channel.send(embed=embed)


@bot.command(name="stats", help="Links the skyshiiyu and plancke pages of the user.")
async def skylea(ctx, username="SoInstantPlayz"):
    await ctx.channel.send(content=f"https://sky.shiiyu.moe/stats/{username}")
    await ctx.channel.send(
        content=f"https://plancke.io/hypixel/player/stats/{username}"
    )


@bot.command(name="restart", help="Restarts the application")
async def restart(ctx):
    await ctx.channel.send(f":hourglass: Restarting bot {LOADING}")
    os.execv(sys.executable, ["python"] + sys.argv)


@bot.command(
    name="clearlogs", help="Clears the logs folder of any logs older than a week"
)
async def clearlogs(ctx):
    now = datetime.utcnow().timestamp()
    counter = 0
    bot_message = await ctx.channel.send(content=f":hourglass: Deleting logs {LOADING}")
    for i in os.listdir("./logs"):
        filename, file_ext = os.path.splitext(i)
        if now - float(filename) > 86400:
            os.remove(os.path.join("./logs", i))
            counter += 1
    await bot_message.edit(
        content=f"{CHECKMARK} {counter} old log(s) have been deleted!"
    )


@bot.group(name="lofi", invoke_without_command=True, help="Base command for lofi.")
async def lofi(ctx):
    await ctx.channel.send(
        content=":negative_squared_cross_mark: Invalid/missing subcommand!"
    )


@lofi.command(
    name="start", help="Joins a voice channel and plays the lofi stream by Chillhop"
)
async def lofi_start(ctx):
    if not ctx.author.voice:
        return await ctx.channel.send(
            content="You are not in a voice channel right now!"
        )
    channel = ctx.author.voice.channel
    await channel.connect()
    async with ctx.typing():
        temp_msg = await ctx.channel.send(content=f"Loading stream {LOADING}")
        player = await YTDLSource.from_url(LOFI_URL, loop=bot.loop, stream=True)
        ctx.voice_client.play(
            player, after=lambda e: print(f"Player error: {e}") if e else None
        )

    await temp_msg.edit(content=f"Now playing: {player.title}")


@lofi.command(name="stop", help="Stops the lofi player, if playing currently.")
async def lofi_stop(ctx):
    await ctx.voice_client.disconnect()


@bot.group(
    name="reminders",
    aliases=["r"],
    invoke_without_command=True,
    help="Base command for reminders.",
)
async def reminders(ctx):
    await ctx.channel.send(
        content=":negative_squared_cross_mark: Invalid/missing subcommand!"
    )


@reminders.command(name="list", aliases=["l"], help="Lists all pending tasks.")
async def list_reminders(ctx):
    reminders = utils.get_reminders()
    if reminders == []:
        await ctx.channel.send(content="You have no current tasks to complete! :tada:")
    else:
        embed = discord.Embed(
            title="__Here are your pending tasks:__", color=EMBED_COLOR
        )
        embed.set_author(
            name="Sir SoInstant",
            url=NAME_URL,
            icon_url=ICON_URL,
        )
        for i, document in enumerate(reminders):
            embed.add_field(
                name=f"{i+1}. **{document['task']}** (Due on {utils.unix_to_timestamp(document['time_due'])})",
                value="- " + "\n- ".join(document["description"]),
                inline=False,
            )
        embed.set_footer(text=utils.get_quote())
        await ctx.channel.send(embed=embed)


@reminders.command(
    name="add",
    help="Adds a task. Argument must be in the format of '<name of task>' '<date due, in the format of %Y/%m/%D %H:%M>' '<date warn>' '<description of task>'",
)
async def add_reminder(ctx, task: str, due: str, warn: str, desc: str):
    utils.add_reminder(task=task, due=due, warn=warn, desc=desc)
    await ctx.channel.send(content=f"{CHECKMARK} Your reminder has been added!")
    bot.timer_manager.create_timer(
        "reminder",
        utils.timestamp_to_unix(warn) - int(datetime.now().timestamp()),
        args=(task, desc, due),
    )


@reminders.command(
    name="delete",
    aliases=["del", "d"],
    help="Deletes a task. The argument, n, is the index of the task from !reminders list",
)
async def delete_reminder(ctx, n: int):
    if utils.delete_reminder(n):
        await ctx.channel.send(
            content=f"{CHECKMARK} Reminder no. {n} has been deleted!"
        )
    else:
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Index out of bounds!"
        )


@reminders.command(name="cleardone", help="Clears all completed tasks from the DB.")
async def clear(ctx):
    if utils.clear_finished():
        await ctx.channel.send(
            content=f"{CHECKMARK} Successfully cleared completed tasks!"
        )
    else:
        await ctx.channel.send(content="Something went wrong!")


PORT = os.getenv("PORT")
bot.loop.create_task(app.run_task(host="0.0.0.0", port=PORT))
bot.run(TOKEN)
