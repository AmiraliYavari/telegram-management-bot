"""
🤖 Telegram Admin Bot
Main entry point
"""

import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ChatMemberHandler, filters
)
from handlers.welcome import welcome_new_member
from handlers.moderation import (
    cmd_warn, cmd_unwarn, cmd_ban, cmd_unban,
    cmd_mute, cmd_unmute, filter_links_and_spam
)
from handlers.stats import cmd_stats
from handlers.schedule import cmd_open, cmd_close, cmd_schedule
from utils.database import init_db
from config import BOT_TOKEN, PROXY_URL

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    init_db()
    logger.info("✅ Database initialized")

    builder = ApplicationBuilder().token(BOT_TOKEN)

    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
        logger.info(f"🔗 Using proxy: {PROXY_URL}")

    app = builder.build()

    # ── Welcome ──────────────────────────────────────────────
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

    # ── Moderation commands ──────────────────────────────────
    app.add_handler(CommandHandler("warn",   cmd_warn))
    app.add_handler(CommandHandler("unwarn", cmd_unwarn))
    app.add_handler(CommandHandler("ban",    cmd_ban))
    app.add_handler(CommandHandler("unban",  cmd_unban))
    app.add_handler(CommandHandler("mute",   cmd_mute))
    app.add_handler(CommandHandler("unmute", cmd_unmute))

    # ── Stats ────────────────────────────────────────────────
    app.add_handler(CommandHandler("stats", cmd_stats))

    # ── Group open/close ─────────────────────────────────────
    app.add_handler(CommandHandler("open",     cmd_open))
    app.add_handler(CommandHandler("close",    cmd_close))
    app.add_handler(CommandHandler("schedule", cmd_schedule))

    # ── Message filter (links & spam) ────────────────────────
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, filter_links_and_spam))

    logger.info("🚀 Bot is running...")
    app.run_polling(allowed_updates=["message", "chat_member"])


if __name__ == "__main__":
    main()