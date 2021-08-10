import os
from datetime import datetime, timezone, timedelta
import time
import calendar as cal

import pymongo
import requests
from dotenv import load_dotenv
from feedparser import parse
from bs4 import BeautifulSoup

from parameters import RSS_LINKS

load_dotenv()
USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")

client = pymongo.MongoClient(
    f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.7ivzo.mongodb.net/<dbname>?authSource=admin&replicaSet=atlas-9wc5l5-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true"
)

db = client["app"]


def get_reminders():
    """Returns a list of pending tasks

    Params:
        None

    Returns:
        A list of documents containing information about the tasks
    """
    col = db["reminders"]
    results = [
        document
        for document in col.find({"completed": False}, {"completed": 0}).sort(
            "time_due", 1
        )
    ]
    return results


def add_reminder(task, due, warn, desc):
    """Adds a task

    Params:
        task (str): The name of the task
        due (str): The date the task is due, in the format of '%Y/%m/%d %H:%M'
        warn (str): The date to warn about the task, in the format of '%Y/%m/%d %H:%M'
        desc (str): Any additional information pertaining to the task

    Returns:
        A boolean which indicates if the insert operation was successful.
    """
    col = db["reminders"]
    desc = desc.split("\n")
    op = col.insert_one(
        {
            "task": task,
            "time_due": timestamp_to_unix(due),
            "time_warn": timestamp_to_unix(warn),
            "description": desc,
            "completed": False,
        }
    )
    return op.acknowledged == True


def delete_reminder(index):
    """Marks a task as complete

    Params:
        index (int): Index of the task to be marked as complete

    Returns:
        A boolean which indicates if the update operation was successful.
    """
    reminders = get_reminders()
    if index < 0 or index > len(reminders):
        return False

    col = db["reminders"]
    op = col.update_one(
        {"_id": reminders[index - 1]["_id"]}, {"$set": {"completed": True}}
    )
    return op.acknowledged == True


def clear_finished():
    """Deletes all completed tasks from the MongoDB

    Params:
        None

    Return:
        A boolean indicating if the delete operation was successful.
    """
    col = db["reminders"]
    op = col.delete_many({"completed": True})
    return op.acknowledged == True


def unix_to_timestamp(unix_time):
    """Converts Unix time to a timestamp

    Params:
        unix_time (int): The Unix time to be converted

    Returns:
        A string representing the converted timestamp, in the format of '%Y/%m/%d %H:%M'
    """
    dtobj = datetime.fromtimestamp(unix_time, timezone.utc) + timedelta(hours=8)
    return dtobj.isoformat(sep=" ", timespec="minutes").replace("-", "/")[:-6]


def timestamp_to_unix(timestamp):
    """Takes a timestamp and converts it to Unix time

    Params:
        timestamp (str): The timestamp to be converted, in the format of
            '%Y/%m/%d %H:%M'

    Returns:
        An integer representing the Unix time
    """
    dt = datetime.strptime(timestamp, "%Y/%m/%d %H:%M") - timedelta(hours=8)
    return int((dt - datetime(1970, 1, 1)).total_seconds())


def get_quote():
    data = requests.get("https://api.quotable.io/random").json()
    return f'"{data["content"]}" - {data["author"]}'


def check_news(timestamp: int) -> None:
    """Fetches news from RSS feed(s) published after a certain time

    Args:
        timestamp (int): The timestamp to be checked

    Returns:
        An string representing the timestamp that the feed(s) was last checked.
    """
    last_checked = int(datetime.now().timestamp())
    WEBHOOK_URL = os.getenv("NEWS_WEBHOOK")

    list_of_embeds = []  # Store embeds first

    # Generate embeds
    for news_source, links in RSS_LINKS.items():
        for category, link in links.items():
            feed = parse(link)

            if feed.entries == []:
                break

            for entry in feed.entries:
                if cal.timegm(entry["published_parsed"]) < timestamp:
                    continue

                embed_value = time.strftime(
                    "%B %d, %Y %I:%M %p", entry["published_parsed"]
                )

                if "summary" in entry and entry["summary"] != "":
                    embed_value = BeautifulSoup(
                        entry["summary"], features="html.parser"
                    ).get_text("\n")
                if news_source == "st":
                    embed_author = {
                        "name": "The Straits Times",
                        "url": "https://www.straitstimes.com",
                        "icon_url": "https://soinstant.ml/static/st_icon.png",
                    }
                else:
                    embed_author = {
                        "name": "Channel NewsAsia",
                        "url": "https://www.channelnewsasia.com",
                        "icon_url": "https://soinstant.ml/static/cna_icon.png",
                    }

                list_of_embeds.append(
                    {
                        "author": embed_author,
                        "title": entry["title"],
                        "url": entry["link"],
                        "color": 12045026,
                        "fields": [
                            {
                                "name": "Summary",
                                "value": embed_value,
                                "inline": True,
                            },
                            {
                                "name": "Category",
                                "value": category,
                                "inline": True,
                            },
                        ],
                        "footer": {
                            "text": "Written by SoInstant",
                            "icon_url": "https://soinstant.ml/static/bot_icon.png",
                        },
                    }
                )

    for payload in [
        list_of_embeds[i : i + 10] for i in range(0, len(list_of_embeds), 10)
    ]:
        requests.post(url=WEBHOOK_URL, json={"embeds": payload})
    print(
        f"[ INFO ] Checked at {last_checked} | No. of messages sent: {len(list_of_embeds)}"
    )
    return last_checked


if __name__ == "__main__":
    pass
