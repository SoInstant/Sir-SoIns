import os
from datetime import datetime
import asyncio

from discord.ext import commands, timers, tasks
import discord
from dotenv import load_dotenv
from pretty_help import PrettyHelp
from quart import Quart

import utils
from parameters import *

from bot_cogs.reminders import Reminders
from bot_cogs.stream import Stream
from bot_cogs.misc import Miscellaneous
from bot_cogs.stats import Stats

# ENV Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
REMINDERS_CHANNEL_ID = int(os.getenv("REMINDERS_CHANNEL_ID"))


# Create Bot instance
bot = commands.Bot(command_prefix="!")
bot.timer_manager = timers.TimerManager(bot)
bot.help_command = PrettyHelp(color=EMBED_COLOR)


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
    embed = discord.Embed(
        title=task, description=f"Due at: {time_due}", color=EMBED_COLOR
    )
    embed.set_author(name="Sir SoInstant", url=NAME_URL, icon_url=ICON_URL)
    for n, subtask in enumerate(description):
        embed.add_field(name=f"Subtask {n + 1}", value=subtask, inline=False)
    embed.set_footer(text=utils.get_quote())
    await bot.get_channel(REMINDERS_CHANNEL_ID).send(
        content=f"<@{OWNER_ID}> The task {task} is due at {time_due}!", embed=embed
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: No such command exists!"
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Missing parameters!"
        )
    elif isinstance(error, discord.errors.HTTPException):
        pass
    else:
        print(error)


# Create Web Server
app = Quart(__name__)


@app.route("/")
async def main():
    return "The Bot is alive"


@app.route("/bot")
async def bot_page():
    return "Bot page"


# Run Quart server to keep bot alive
PORT = os.getenv("PORT")
bot.loop.create_task(app.run_task(host="0.0.0.0", port=PORT))

# Add Cogs
bot.add_cog(Reminders(bot))
bot.add_cog(Stream(bot))
bot.add_cog(Miscellaneous(bot))
bot.add_cog(Stats(bot))
bot.run(TOKEN)
