"""
Configuration — values are read from environment variables.
Copy .env.example to .env and fill in your values.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]          # @BotFather token

# Proxy (optional) — e.g. socks5://127.0.0.1:7890
PROXY_URL: str = os.getenv("PROXY_URL", "")

# Warn threshold before auto-ban
WARN_LIMIT: int = int(os.getenv("WARN_LIMIT", "3"))

# Max identical messages in a short window (anti-spam)
SPAM_THRESHOLD: int = int(os.getenv("SPAM_THRESHOLD", "5"))
SPAM_WINDOW_SEC: int = int(os.getenv("SPAM_WINDOW_SEC", "10"))

# SQLite database path
DB_PATH: str = os.getenv("DB_PATH", "data/bot.db")

# XP awarded per (non-spam) text message
XP_PER_MESSAGE: int = int(os.getenv("XP_PER_MESSAGE", "10"))

# Minimum seconds between XP awards for the same user (anti-farming)
XP_COOLDOWN_SEC: int = int(os.getenv("XP_COOLDOWN_SEC", "60"))