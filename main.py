import os
from datetime import datetime

from discord.ext import commands, timers
import discord
from dotenv import load_dotenv

import keep_alive
import utils

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = commands.Bot(command_prefix="!", help_command=None)
bot.timer_manager = timers.TimerManager(bot)


@bot.check
async def block_dms(ctx):
    return ctx.guild != None


@bot.check
async def block_all(ctx):
    return ctx.author.id == OWNER_ID


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="over SoInstant"
        )
    )
    await bot.get_channel(CHANNEL_ID).send(content=f"<@{OWNER_ID}> Bot is now online!")
    tasks = utils.get_reminders()
    for task in tasks:
        bot.timer_manager.create_timer(
            "reminder",
            task["time_warn"] - int(datetime.now().timestamp()),
            args=(task["task"], utils.unix_to_timestamp(task["time_due"])),
        )


@bot.event
async def on_reminder(task, time):
    await bot.get_channel(CHANNEL_ID).send(
        f'<@{OWNER_ID}> The task "{task}" is due at {time}!'
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


@bot.command(help="Clears n messages from the channel.")
async def clearmsg(ctx, n=None):
    if n:
        n = int(n)
    counter = 0
    async for message in ctx.channel.history(limit=n):
        counter += 1
        await message.delete()
    if counter == 1:
        await ctx.channel.send(content=":white_check_mark: 1 message has been deleted!")
    else:
        await ctx.channel.send(
            content=f":white_check_mark: {counter} messages have been deleted!"
        )

@bot.command(name="help", help="Shows this message.")
async def help(ctx, *args):
    commands = dict([(command.name, command) for command in bot.commands])
    if args == []:
        print(1)

# @bot.command(name="watch")
# async def watch(ctx):
#     await bot.change_presence(
#         activity=discord.Activity(
#             type=discord.ActivityType.watching,
#             name=f"over #{ctx.channel}"
#         )
#     )
#     await ctx.channel.send(content="This channel is now under watch by the moderators.")


@bot.group(
    name="reminders",
    aliases=["r"],
    invoke_without_command=True,
    help="Base command for reminders",
    description="Base command for reminders.",
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
            title="__Here are your pending tasks:__", color=discord.Color(0xB7CAE2)
        )
        embed.set_author(
            name="Sir SoInstant",
            url="https://soinstant.ml",
            icon_url="https://i.pinimg.com/originals/7d/41/f4/7d41f4a15bd89da6a65856e69cc6e2cc.png",
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
        await ctx.channel.send(
            content=f":white_check_mark: Reminder no. {n} has been deleted!"
        )
    else:
        await ctx.channel.send(
            content=f":negative_squared_cross_mark: Index out of bounds!"
        )


@reminders.command(name="cleardone", help="Clears all completed tasks from the DB.")
async def clear(ctx):
    if utils.clear_finished():
        await ctx.channel.send(
            content=":white_check_mark: Successfully cleared completed tasks!"
        )
    else:
        await ctx.channel.send(content="Something went wrong!")


if __name__ == "__main__":
    keep_alive.keep_alive()
    print([command for command in bot.commands])
    bot.run(TOKEN)
    # dont put anything here
