import os
from datetime import datetime, timezone, timedelta

import pymongo
from dotenv import load_dotenv

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
    desc = desc.replace("\n", "\n- ")
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


if __name__ == "__main__":
    print(unix_to_timestamp(1609459200))
    print(timestamp_to_unix("2021/1/1 00:00"))
