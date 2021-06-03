from flask import Flask
from threading import Thread
from bot import keep_alive

app = Flask("")


@app.route("/")
def main():
    return "The Bot is alive"


@app.route("/bot")
def bot_page():
    return "Bot page"


keep_alive()
app.run()
