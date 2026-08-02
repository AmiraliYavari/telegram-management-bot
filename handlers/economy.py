"""
Lightweight XP / leveling system for active members.

- Every non-command text message earns XP_PER_MESSAGE points, subject to a
  per-user cooldown (XP_COOLDOWN_SEC) so people can't farm levels by
  spamming — the anti-spam filter would catch that anyway, but the cooldown
  keeps XP meaningful on its own.
- Levels follow a simple curve (see utils.database._level_for_xp): each
  level requires progressively more XP than the last.
- /rank            → your own level, XP and position on the leaderboard.
- /top             → top 10 members in the group by XP.
- On level-up, the bot posts a small congratulation message in the group.
"""

from telegram import Update
from telegram.ext import ContextTypes

from utils.database import add_xp, get_user_xp, get_user_rank, get_message_leaderboard
from utils.i18n import t
from config import XP_PER_MESSAGE, XP_COOLDOWN_SEC

MEDALS = ["🥇", "🥈", "🥉"] + ["👤"] * 10


async def track_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attach this as a (low-priority) group handler for text messages."""
    msg = update.effective_message
    if not msg or not msg.text or not update.effective_user:
        return
    if update.effective_user.is_bot:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    result = add_xp(chat_id, user_id, XP_PER_MESSAGE, XP_COOLDOWN_SEC)
    if result and result["leveled_up"]:
        await context.bot.send_message(
            chat_id,
            t(chat_id, "level_up",
              mention=update.effective_user.mention_html(),
              level=result["level"]),
            parse_mode="HTML"
        )


async def cmd_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    row = get_user_xp(chat_id, user.id)
    if not row:
        return await update.message.reply_text(t(chat_id, "rank_none"))

    rank = get_user_rank(chat_id, user.id)
    await update.message.reply_text(
        t(chat_id, "rank_title", name=user.full_name) + "\n" +
        t(chat_id, "rank_line", rank=rank, level=row["level"], xp=row["xp"]),
        parse_mode="HTML"
    )


async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ranks members by how many messages they've actually sent."""
    chat_id = update.effective_chat.id
    rows = get_message_leaderboard(chat_id, limit=10)

    if not rows:
        return await update.message.reply_text(t(chat_id, "leaderboard_empty"))

    lines = [t(chat_id, "leaderboard_title")]
    for i, row in enumerate(rows):
        try:
            member = await context.bot.get_chat_member(chat_id, row["user_id"])
            name = member.user.full_name
        except Exception:
            name = f"User {row['user_id']}"
        lines.append(
            t(chat_id, "leaderboard_line", medal=MEDALS[i], name=name, count=row["msg_count"])
        )

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")