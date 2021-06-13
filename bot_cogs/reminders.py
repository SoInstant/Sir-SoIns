import discord
import discord.ext.commands as commands

import utils
from parameters import *


class Reminders(commands.Cog):
    """
    Commands to help keep track of reminders.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="reminders",
        aliases=["r"],
        invoke_without_command=True,
        help="Base command for reminders.",
    )
    async def reminders(self, ctx):
        await ctx.channel.send(
            content=":negative_squared_cross_mark: Invalid/missing subcommand!"
        )

    @reminders.command(name="list", aliases=["l"], help="Lists all pending tasks.")
    async def list_reminders(self, ctx):
        reminders = utils.get_reminders()
        if reminders == []:
            await ctx.channel.send(
                content="You have no current tasks to complete! :tada:"
            )
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
    async def add_reminder(self, ctx, task: str, due: str, warn: str, desc: str):
        utils.add_reminder(task=task, due=due, warn=warn, desc=desc)
        await ctx.channel.send(content=f"{CHECKMARK} Your reminder has been added!")
        self.bot.timer_manager.create_timer(
            "reminder",
            utils.timestamp_to_unix(warn) - int(datetime.now().timestamp()),
            args=(task, desc, due),
        )

    @reminders.command(
        name="delete",
        aliases=["del", "d"],
        help="Deletes a task. The argument, n, is the index of the task from !reminders list",
    )
    async def delete_reminder(self, ctx, n: int):
        if utils.delete_reminder(n):
            await ctx.channel.send(
                content=f"{CHECKMARK} Reminder no. {n} has been deleted!"
            )
        else:
            await ctx.channel.send(
                content=":negative_squared_cross_mark: Index out of bounds!"
            )

    @reminders.command(name="cleardone", help="Clears all completed tasks from the DB.")
    async def clear(self, ctx):
        if utils.clear_finished():
            await ctx.channel.send(
                content=f"{CHECKMARK} Successfully cleared completed tasks!"
            )
        else:
            await ctx.channel.send(content="Something went wrong!")
