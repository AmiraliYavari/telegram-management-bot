"""
Welcome new members with a friendly message.
"""

from telegram import Update, ChatMemberUpdated
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus


def _extract_status_change(update: ChatMemberUpdated):
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status
    return old_status, new_status


async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    old_status, new_status = _extract_status_change(result)

    # Someone just joined (or was added)
    if old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED) and \
       new_status == ChatMemberStatus.MEMBER:

        user = result.new_chat_member.user
        chat = result.chat

        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"👋 سلام {user.mention_html()}!\n"
                f"به گروه <b>{chat.title}</b> خوش اومدی 🎉\n\n"
                "📌 لطفاً قوانین گروه رو مطالعه کن و از بحث‌های سازنده لذت ببر."
            ),
            parse_mode="HTML"
        )
