"""
Shared helper functions.
"""

from telegram import Update, Chat, ChatPermissions
from telegram.ext import ContextTypes


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Return True if the user who sent the command is an admin/owner."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")


async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Resolve the target user from a reply or a username/id argument.
    Returns (user_id, first_name) or (None, None).
    """
    msg = update.effective_message

    if msg.reply_to_message:
        u = msg.reply_to_message.from_user
        return u.id, u.first_name

    if context.args:
        arg = context.args[0].lstrip("@")
        try:
            uid = int(arg)
            member = await context.bot.get_chat_member(update.effective_chat.id, uid)
            return uid, member.user.first_name
        except (ValueError, Exception):
            pass

    return None, None


FULL_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

MUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
)
