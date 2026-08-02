"""
/setlang    — admins pick the group's language for bot-generated messages.
/setwelcome — admins set a custom welcome message for new members.
"""

from telegram import Update
from telegram.ext import ContextTypes

from utils.database import set_language, set_welcome_message
from utils.helpers import is_admin
from utils.i18n import t, available_languages


async def cmd_setlang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not await is_admin(update, context):
        return await update.message.reply_text(t(chat_id, "setlang_admin_only"))

    langs = available_languages()

    if not context.args:
        return await update.message.reply_text(
            t(chat_id, "setlang_usage", languages=", ".join(langs))
        )

    lang_code = context.args[0].lower()
    if lang_code not in langs:
        return await update.message.reply_text(
            t(chat_id, "setlang_invalid", languages=", ".join(langs))
        )

    set_language(chat_id, lang_code)
    # Confirm in the *new* language so the admin sees it took effect.
    await update.message.reply_text(t(chat_id, "setlang_success", lang=lang_code))


async def cmd_setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not await is_admin(update, context):
        return await update.message.reply_text(t(chat_id, "welcome_admin_only"))

    if not context.args:
        return await update.message.reply_text(t(chat_id, "welcome_set_usage"))

    text = " ".join(context.args)

    if text.strip().lower() == "reset":
        set_welcome_message(chat_id, None)
        return await update.message.reply_text(t(chat_id, "welcome_set_reset"))

    set_welcome_message(chat_id, text)
    await update.message.reply_text(t(chat_id, "welcome_set_success"))