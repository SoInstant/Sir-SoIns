"""
This file contains the shared variables for the bot.
"""
from datetime import datetime

# Bot Parameters
NAME_URL = "https://soinstant.ml"
ICON_URL = "https://soinstant.ml/static/icon.png"
LOFI_URL = "https://www.youtube.com/watch?v=VfW86fnQL5w"
EMBED_COLOR = 0xB7CAE2
ONLINE_TIME = datetime.utcnow().timestamp()
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