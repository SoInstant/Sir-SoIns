"""
This file contains the shared variables for the bot.
"""
from datetime import datetime

# Bot Parameters
NAME_URL = "https://soinstant.ml"
ICON_URL = "https://soinstant.ml/static/bot_icon.png"
LOFI_URL = "https://www.youtube.com/watch?v=VfW86fnQL5w"
EMBED_COLOR = 0xB7CAE2
ONLINE_TIME = datetime.now().timestamp()
YTDL_FORMAT_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}
FFMPEG_OPTIONS = {
    "options": "-vn",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}

# Emojis
CHECKMARK = "<a:check:845921511252033587>"
LOADING = "<a:typing:845909278463492126>"

# Constants
RSS_LINKS = {
    "st": {
        "world": "https://www.straitstimes.com/news/world/rss.xml",
        "business": "https://www.straitstimes.com/news/business/rss.xml",
        "sport": "https://www.straitstimes.com/news/sport/rss.xml",
        "life": "https://www.straitstimes.com/news/life/rss.xml",
        "opinion": "https://www.straitstimes.com/news/opinion/rss.xml",
        "sg": "https://www.straitstimes.com/news/singapore/rss.xml",
        "asia": "https://www.straitstimes.com/news/asia/rss.xml",
        "tech": "https://www.straitstimes.com/news/tech/rss.xml",
        "multimedia": "https://www.straitstimes.com/news/multimedia/rss.xml",
    },
    "cna": {
        "latest": "https://www.channelnewsasia.com/rssfeeds/8395986",
        "asia": "https://www.channelnewsasia.com/rssfeeds/8395744",
        "business": "https://www.channelnewsasia.com/rssfeeds/8395954",
        "sg": "https://www.channelnewsasia.com/rssfeeds/8396082",
        "sport": "https://www.channelnewsasia.com/rssfeeds/8395838",
        "world": "https://www.channelnewsasia.com/rssfeeds/8395884",
    },
}