"""
/open, /close, /schedule — manage group send-message permissions.
"""

import re
from datetime import datetime

from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from utils.database import set_group_open
from utils.helpers import is_admin

_OPEN_PERMS = ChatPermissions(can_send_messages=True, can_send_other_messages=True,
                               can_add_web_page_previews=True)
_CLOSE_PERMS = ChatPermissions(can_send_messages=False)


async def cmd_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    await context.bot.set_chat_permissions(update.effective_chat.id, _OPEN_PERMS)
    set_group_open(update.effective_chat.id, True)
    await update.message.reply_text("✅ گروه باز شد. همه می‌تونن پیام بدن.")


async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return

    await context.bot.set_chat_permissions(update.effective_chat.id, _CLOSE_PERMS)
    set_group_open(update.effective_chat.id, False)
    await update.message.reply_text("🔒 گروه بسته شد. فقط ادمین‌ها می‌تونن پیام بدن.")


async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage:
      /schedule open  HH:MM
      /schedule close HH:MM

    Example:
      /schedule open  09:00
      /schedule close 23:00
    """
    if not await is_admin(update, context):
        return

    usage = "استفاده: /schedule open HH:MM  یا  /schedule close HH:MM"

    if len(context.args) < 2:
        return await update.message.reply_text(usage)

    action, time_str = context.args[0].lower(), context.args[1]
    if action not in ("open", "close"):
        return await update.message.reply_text(usage)

    if not re.match(r"^\d{2}:\d{2}$", time_str):
        return await update.message.reply_text("⏰ فرمت زمان اشتباهه. مثال: 09:00")

    hour, minute = map(int, time_str.split(":"))
    chat_id = update.effective_chat.id
    job_name = f"schedule_{chat_id}_{action}"

    # Remove existing job with same name (if rescheduled)
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()

    async def _job(ctx: ContextTypes.DEFAULT_TYPE):
        if action == "open":
            await ctx.bot.set_chat_permissions(chat_id, _OPEN_PERMS)
            set_group_open(chat_id, True)
            await ctx.bot.send_message(chat_id, "✅ گروه طبق برنامه باز شد.")
        else:
            await ctx.bot.set_chat_permissions(chat_id, _CLOSE_PERMS)
            set_group_open(chat_id, False)
            await ctx.bot.send_message(chat_id, "🔒 گروه طبق برنامه بسته شد.")

    context.job_queue.run_daily(
        _job,
        time=datetime.strptime(time_str, "%H:%M").time(),
        name=job_name
    )

    label = "باز شدن" if action == "open" else "بسته شدن"
    await update.message.reply_text(f"⏰ زمان‌بندی {label} گروه در ساعت {time_str} تنظیم شد.")
