import os
from datetime import datetime
import logging
from time import sleep

from discord.ext import commands, timers
import discord
from dotenv import load_dotenv

import keep_alive
import utils

# Env Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID"))
REMINDERS_CHANNEL_ID = int(os.getenv("REMINDERS_CHANNEL_ID"))
NAME_URL = "https://soinstant.ml"
ICON_URL = "https://i.pinimg.com/originals/7d/41/f4/7d41f4a15bd89da6a65856e69cc6e2cc.png"
EMBED_COLOR = 0xB7CAE2
ONLINE_TIME = datetime.utcnow().timestamp()

# Create Bot instance
bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    status=discord.Activity(type=discord.ActivityType.watching, name="over SoInstant"),
)
bot.timer_manager = timers.TimerManager(bot)

# Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=f"./logs/discord-{ONLINE_TIME}.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


@bot.check
async def block_dms(ctx):
    return ctx.guild != None


@bot.check
async def block_all(ctx):
    return ctx.author.id == OWNER_ID


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await bot.get_channel(OUTPUT_CHANNEL_ID).send(content=f"Bot is now online! Time: {ONLINE_TIME}")
    tasks = utils.get_reminders()
    for task in tasks:
        bot.timer_manager.create_timer(
            "reminder",
            task["time_warn"] - int(datetime.now().timestamp()),
            args=(task["task"], utils.unix_to_timestamp(task["time_due"])),
        )


@bot.event
async def on_reminder(task, time):
    await bot.get_channel(REMINDERS_CHANNEL_ID).send(f'<@{OWNER_ID}> The task "{task}" is due at {time}!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(content=":negative_squared_cross_mark: No such command exists!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(content=":negative_squared_cross_mark: Missing parameters!")
    else:
        print(error)


@bot.command(help="Clears n messages from the channel.")
async def clearmsg(ctx, n=None):
    if n:
        n = int(n)
    counter = 0
    async for message in ctx.channel.history(limit=n):
        counter += 1
        await message.delete()
        sleep(0.5)
    if counter == 1:
        await ctx.channel.send(content=":white_check_mark: 1 message has been deleted!")
    else:
        await ctx.channel.send(content=f":white_check_mark: {counter} messages have been deleted!")


@bot.command(name="help", help="Shows this message.")
async def help(ctx, *args):
    current_level = {_command.name: {"_help": _command.help, "_command": _command} for _command in bot.commands}
    for arg in args:
        try:
            _command = current_level[arg]["_command"]
            if isinstance(_command, commands.Group):
                current_level = {
                    subcommand.name: {"_help": subcommand.help, "_command": subcommand}
                    for subcommand in _command.commands
                }
            else:
                current_level = dict([(_command.name, {"_help": _command.help, "_command": _command})])
        except KeyError:
            await ctx.channel.send(content=f":negative_squared_cross_mark: No such command exists!")

    if not args:
        embed = discord.Embed(title="Bot commands", color=EMBED_COLOR)
    else:
        embed = discord.Embed(title="!" + " ".join(args), description=_command.help, color=EMBED_COLOR)

    embed.set_author(name="Sir SoInstant", url=NAME_URL, icon_url=ICON_URL)

    if args == () or isinstance(_command, commands.Group):
        for key in sorted(current_level):
            embed.add_field(name=key, value=f"```{current_level[key]['_help']}```", inline=False)
    embed.set_footer(text="Type !help command for more info on a command.")

    await ctx.channel.send(embed=embed)


@bot.command(name="skylea", help="Links the sky.shiiyu.moe website of the user.")
async def skylea(ctx, username):
    await ctx.channel.send(content=f"https://sky.shiiyu.moe/stats/{username}")


@bot.group(
    name="reminders",
    aliases=["r"],
    invoke_without_command=True,
    help="Base command for reminders.",
)
async def reminders(ctx):
    await ctx.channel.send(content=":negative_squared_cross_mark: Invalid/missing subcommand!")


@reminders.command(name="list", aliases=["l"], help="Lists all pending tasks.")
async def list_reminders(ctx):
    reminders = utils.get_reminders()
    if reminders == []:
        await ctx.channel.send(content="You have no current tasks to complete! :tada:")
    else:
        embed = discord.Embed(title="__Here are your pending tasks:__", color=EMBED_COLOR)
        embed.set_author(
            name="Sir SoInstant",
            url=NAME_URL,
            icon_url=ICON_URL,
        )
        for i, document in enumerate(reminders):
            embed.add_field(
                name=f"{i+1}. **{document['task']}** (Due on {utils.unix_to_timestamp(document['time_due'])})",
                value=f"- {document['description']}",
                inline=False,
            )
        embed.set_footer(text="'You probably won't remember me' - You Meet in Paris")
        await ctx.channel.send(embed=embed)


@reminders.command(
    name="add",
    help="Adds a task. Argument must be in the format of '<name of task>' '<date due, in the format of %Y/%m/%D %H:%M>' '<date warn>' '<description of task>'",
)
async def add_reminder(ctx, task: str, due: str, warn: str, desc: str):
    utils.add_reminder(task=task, due=due, warn=warn, desc=desc)
    await ctx.channel.send(content=":white_check_mark: Your reminder has been added!")
    bot.timer_manager.create_timer(
        "reminder",
        utils.timestamp_to_unix(warn) - int(datetime.now().timestamp()),
        args=(task, due),
    )


@reminders.command(
    name="delete",
    aliases=["del", "d"],
    help="Deletes a task. The argument, n, is the index of the task from !reminders list",
)
async def delete_reminder(ctx, n: int):
    if utils.delete_reminder(n):
        await ctx.channel.send(content=f":white_check_mark: Reminder no. {n} has been deleted!")
    else:
        await ctx.channel.send(content=f":negative_squared_cross_mark: Index out of bounds!")


@reminders.command(name="cleardone", help="Clears all completed tasks from the DB.")
async def clear(ctx):
    if utils.clear_finished():
        await ctx.channel.send(content=":white_check_mark: Successfully cleared completed tasks!")
    else:
        await ctx.channel.send(content="Something went wrong!")


if __name__ == "__main__":
    keep_alive.keep_alive()
    bot.run(TOKEN)
    # dont put anything here, it won't be executed
