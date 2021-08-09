from quart import Quart

app = Quart(__name__)
app.config["SERVER_NAME"] = "soinstant.ml"


@app.route("/")
async def main():
    return "Home Page"


@app.route("/", subdomain="bot")
async def bot_page():
    return "Bot page"


@app.route("/", subdomain="api")
async def api_page():
    return "API page"