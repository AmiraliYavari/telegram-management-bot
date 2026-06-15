"""
Moderation commands: warn, unwarn, ban, unban, mute, unmute
+ automatic link/spam filter.
"""

import re
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from utils.database import (
    add_warning, clear_warnings, count_warnings,
    log_message, recent_message_count
)
from utils.helpers import is_admin, get_target_user, MUTE_PERMISSIONS, FULL_PERMISSIONS
from config import WARN_LIMIT, SPAM_THRESHOLD, SPAM_WINDOW_SEC

URL_RE = re.compile(r"(https?://|t\.me/|@\w{5,})", re.IGNORECASE)


# ── /warn ─────────────────────────────────────────────────────────────────────

async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن اخطار بدن.")

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده. روی پیامش ریپلای کن.")

    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "—"
    total = add_warning(update.effective_chat.id, uid, reason)

    if total >= WARN_LIMIT:
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        clear_warnings(update.effective_chat.id, uid)
        await update.message.reply_text(
            f"🚫 <b>{name}</b> بعد از {total} اخطار از گروه بن شد.",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"⚠️ <b>{name}</b> اخطار گرفت ({total}/{WARN_LIMIT})\n"
            f"📝 دلیل: {reason}",
            parse_mode="HTML"
        )


# ── /unwarn ───────────────────────────────────────────────────────────────────

async def cmd_unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده.")

    clear_warnings(update.effective_chat.id, uid)
    await update.message.reply_text(f"✅ همه اخطارهای <b>{name}</b> پاک شد.", parse_mode="HTML")


# ── /ban ──────────────────────────────────────────────────────────────────────

async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده.")

    await context.bot.ban_chat_member(update.effective_chat.id, uid)
    await update.message.reply_text(f"🚫 <b>{name}</b> بن شد.", parse_mode="HTML")


# ── /unban ────────────────────────────────────────────────────────────────────

async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده.")

    await context.bot.unban_chat_member(update.effective_chat.id, uid, only_if_banned=True)
    await update.message.reply_text(f"✅ <b>{name}</b> آنبن شد.", parse_mode="HTML")


# ── /mute ─────────────────────────────────────────────────────────────────────

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده.")

    # Optional duration: /mute @user 30m  or  /mute @user 2h
    until = None
    duration_arg = context.args[-1] if context.args else ""
    match = re.match(r"^(\d+)([mh])$", duration_arg)
    if match:
        amount, unit = int(match.group(1)), match.group(2)
        delta = timedelta(minutes=amount) if unit == "m" else timedelta(hours=amount)
        until = datetime.utcnow() + delta

    await context.bot.restrict_chat_member(
        update.effective_chat.id, uid, MUTE_PERMISSIONS, until_date=until
    )
    duration_text = f" به مدت {duration_arg}" if until else ""
    await update.message.reply_text(
        f"🔇 <b>{name}</b>{duration_text} میوت شد.", parse_mode="HTML"
    )


# ── /unmute ───────────────────────────────────────────────────────────────────

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    uid, name = await get_target_user(update, context)
    if not uid:
        return await update.message.reply_text("❓ کاربری مشخص نشده.")

    await context.bot.restrict_chat_member(update.effective_chat.id, uid, FULL_PERMISSIONS)
    await update.message.reply_text(f"🔊 <b>{name}</b> آنمیوت شد.", parse_mode="HTML")


# ── Auto filter (links & spam) ────────────────────────────────────────────────

async def filter_links_and_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Admins are exempt
    if await is_admin(update, context):
        log_message(chat_id, user_id)
        return

    # Link filter
    if URL_RE.search(msg.text):
        await msg.delete()
        await context.bot.send_message(
            chat_id,
            f"🔗 {update.effective_user.mention_html()}, ارسال لینک در این گروه مجاز نیست.",
            parse_mode="HTML"
        )
        add_warning(chat_id, user_id, "ارسال لینک")
        return

    # Spam filter
    log_message(chat_id, user_id)
    count = recent_message_count(chat_id, user_id, SPAM_WINDOW_SEC)
    if count > SPAM_THRESHOLD:
        until = datetime.utcnow() + timedelta(minutes=5)
        await context.bot.restrict_chat_member(chat_id, user_id, MUTE_PERMISSIONS, until_date=until)
        await context.bot.send_message(
            chat_id,
            f"🚨 {update.effective_user.mention_html()}, اسپم شناسایی شد. ۵ دقیقه میوت شدی.",
            parse_mode="HTML"
        )
