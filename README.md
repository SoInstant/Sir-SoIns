# Sir-SoIns
A simple discord bot for keeping track of your tasks.
Written in late Dec 2020, updated occasionally.

## Dependencies
```python -m pip install -r requirements.txt```
- [discord-pretty-help](https://pypi.org/project/discord-pretty-help/) (For custom help command)
- [discord-timers](https://pypi.org/project/discord-timers/) (Schedules reminders)
- [discord.py](https://pypi.org/project/discord.py/) (Provides a wrapper for DiscordAPI)
- [dnspython](https://pypi.org/project/dnspython/) (Support for MongoDB)
- [hypercorn](https://pypi.org/project/Hypercorn/) (For deployment on Heroku)
- [PyNaCl](https://pypi.org/project/PyNaCl/) (For voice support)
- [pymongo](https://pypi.org/project/pymongo/) (Wrapper for MongoDB)
- [python-dotenv](https://pypi.org/project/python-dotenv/) (Importing environmental variables)
- [quart](https://pypi.org/project/Quart/) (Keep bot alive)
- [requests](https://pypi.org/project/requests/) (For quotes)
- [youtube-dl](https://pypi.org/project/youtube_dl/) (For streaming Youtube Videos)

## Usage
Once you have cloned this repository, install the dependencies.
You will then need to setup 2 things: a Discord bot account, and a Mongo database.

### Setting up a Discord bot account
Learn how to do so [here](https://realpython.com/how-to-make-a-discord-bot-python/#how-to-make-a-discord-bot-in-the-developer-portal). Follow the tutorial, but make sure to give the bot 'Administrator' permissions when generating the OAuth2 URL. Stop just before the section titled 'How to Make a Discord Bot in Python'.

Next, create a file named '.env' in the directory containing the source code. Open it, and add ```DISCORD_TOKEN={your-bot-token}```. You’ll need to replace ```{your-bot-token}``` with your bot’s token, which you can get by going back to the Bot page on the Developer Portal and clicking Copy under the TOKEN section.

Lastly, you will need to add ```OWNER_ID={your-user-id}```, ```REMINDERS_CHANNEL_ID={channel-id}```, and ```OUTPUT_CHANNEL_ID={channel-id}``` to ```.env```. This is to ensure that only you can interact with the bot, give the bot a default channel to send messages in, and give the bot a channel to send online messages in. Learn how to get your User-ID and the Channel-ID in this [video](https://www.youtube.com/watch?v=NLWtSHWKbAI).

### Setting up MongoDB
Learn how to do so [here](https://docs.atlas.mongodb.com/getting-started). When adding IP addresses, add ```0.0.0.0``` to allow access from anywhere (important!). Add ```DB_USERNAME={username}``` and ```DB_PASSWORD={user-password}``` to ```.env```, making sure to replace ```{username}``` and ```{user-password}``` with those of the DB user that you created in 'Create a Database User for Your Cluster' in the tutorial.

Make sure to replace the connection string with your own in ```utils.py```.

### Optional - Quart Server
Quart (async version of Flask) is only needed if you are hosting on platforms that shut down your program after a certain period of inactivity (e.g. repl.it, Heroku). In this case, UptimeRobot is used to ping the Quart server, to prevent the program from being shut down. Learn how to do so [here](https://repl.it/talk/learn/Hosting-discordpy-bots-with-replit/11008). Skip to 'Step 4: Setting up uptimerobot'.

## Before you go...
Note that the bot is written in the timezone of GMT+8. If you need to change the timezone, change the ```timedelta``` in ```unix_to_timestamp``` and ```timestamp_to_unix``` to suit your timezone.

The default prefix of the bot is '!'. Change it in ```main.py```.

To customise your bot, change the values in ```parameters.py```.

Lastly, enjoy!

## To-dos
- Bot dashboard for a web GUI, using React and Material-ui
- Revamp database schema to allow for the completion of individual subtasks
- Advanced features on streaming yt videos (queue system, fancy embed to display info)
