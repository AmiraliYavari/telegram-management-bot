"""
Welcome new members with a friendly message.
"""

from telegram import Update, ChatMemberUpdated
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from utils.database import get_welcome_message
from utils.i18n import t


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

        custom = get_welcome_message(chat.id)
        if custom:
            # Custom templates use plain {name}/{chat_title} placeholders
            # (kept simple on purpose — no HTML mention injection risk).
            text = custom.format(name=user.first_name, chat_title=chat.title)
        else:
            text = t(
                chat.id, "welcome_default",
                mention=user.mention_html(), chat_title=chat.title
            )

        await context.bot.send_message(chat_id=chat.id, text=text, parse_mode="HTML")