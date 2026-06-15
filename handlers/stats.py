"""
/stats — show top active members in the last 7 days.
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.database import get_stats
from utils.helpers import is_admin


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن آمار ببینن.")

    chat_id = update.effective_chat.id
    rows = get_stats(chat_id, days=7)

    if not rows:
        return await update.message.reply_text("📊 هنوز داده‌ای برای نمایش وجود ندارد.")

    medals = ["🥇", "🥈", "🥉"] + ["👤"] * 10
    lines = ["<b>📊 آمار ۷ روز گذشته — فعال‌ترین اعضا</b>\n"]

    for i, row in enumerate(rows):
        try:
            member = await context.bot.get_chat_member(chat_id, row["user_id"])
            name = member.user.full_name
        except Exception:
            name = f"کاربر {row['user_id']}"
        lines.append(f"{medals[i]} <b>{name}</b> — {row['msg_count']} پیام")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
