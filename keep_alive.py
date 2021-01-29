from flask import Flask, send_file
from threading import Thread

app = Flask("")


@app.route("/")
def main():
    return "The Bot is alive"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()
