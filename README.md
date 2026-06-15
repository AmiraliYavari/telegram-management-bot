<div align="center">

# 🤖 Telegram Admin Bot

**ربات مدیریت گروه تلگرام — ساخته‌شده با Python**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://python.org)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21.6-blue?logo=telegram)](https://python-telegram-bot.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../pulls)

</div>

---

## ✨ قابلیت‌ها

| قابلیت | توضیح |
|---|---|
| 👋 **خوش‌آمدگویی خودکار** | پیام سفارشی برای هر عضو جدید |
| ⚠️ **سیستم اخطار (Warn)** | بعد از ۳ اخطار → بن خودکار |
| 🔗 **فیلتر لینک** | حذف خودکار لینک‌ها و یوزرنیم‌ها |
| 🚨 **ضد اسپم** | تشخیص پیام‌های سریع و میوت موقت |
| 📊 **آمار گروه** | فعال‌ترین اعضا در ۷ روز گذشته |
| ⏰ **تایمر گروه** | باز/بسته کردن خودکار گروه طبق ساعت |

---

## 🚀 راه‌اندازی سریع

### ۱. پیش‌نیازها
```
Python 3.11+
```

### ۲. کلون و نصب
```bash
git clone https://github.com/YOUR_USERNAME/telegram-admin-bot.git
cd telegram-admin-bot

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### ۳. تنظیم توکن
```bash
cp .env.example .env
```
فایل `.env` را باز کن و توکن بات را وارد کن:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

> 💡 توکن را از [@BotFather](https://t.me/BotFather) بگیر.

### ۴. اجرا
```bash
python bot.py
```

---

## 📋 دستورات

> فقط ادمین‌های گروه می‌توانند از این دستورات استفاده کنند.

### 🛡️ مدیریت کاربران

| دستور | توضیح | مثال |
|---|---|---|
| `/warn` | اخطار به کاربر | ریپلای روی پیام |
| `/unwarn` | پاک‌کردن اخطارها | ریپلای روی پیام |
| `/ban` | بن دائمی | `/ban @username` |
| `/unban` | رفع بن | `/unban @username` |
| `/mute` | میوت (اختیاری با مدت) | `/mute @user 30m` |
| `/unmute` | رفع میوت | ریپلای روی پیام |

### 📊 آمار و برنامه‌ریزی

| دستور | توضیح | مثال |
|---|---|---|
| `/stats` | آمار فعالیت ۷ روز | `/stats` |
| `/open` | باز کردن گروه | `/open` |
| `/close` | بستن گروه | `/close` |
| `/schedule` | زمان‌بندی باز/بسته | `/schedule open 09:00` |

---

## ⚙️ تنظیمات

تمام تنظیمات در فایل `.env` قابل تغییر هستند:

```env
BOT_TOKEN=        # توکن ربات (اجباری)
WARN_LIMIT=3      # تعداد اخطار تا بن
SPAM_THRESHOLD=5  # تعداد پیام در بازه زمانی
SPAM_WINDOW_SEC=10 # بازه زمانی ضد اسپم (ثانیه)
DB_PATH=data/bot.db # مسیر دیتابیس
```

---

## 📁 ساختار پروژه

```
telegram-admin-bot/
├── bot.py                  # نقطه ورود اصلی
├── config.py               # تنظیمات و متغیرها
├── requirements.txt
├── .env.example
├── handlers/
│   ├── welcome.py          # خوش‌آمدگویی
│   ├── moderation.py       # warn, ban, mute, فیلتر
│   ├── stats.py            # آمار گروه
│   └── schedule.py         # باز/بسته زمان‌بندی
└── utils/
    ├── database.py         # SQLite helpers
    └── helpers.py          # توابع مشترک
```

---

## 🛠️ توسعه

**اضافه کردن دستور جدید:**

```python
# در handlers/my_handler.py
from telegram import Update
from telegram.ext import ContextTypes

async def cmd_hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋")
```

```python
# در bot.py
from handlers.my_handler import cmd_hello
app.add_handler(CommandHandler("hello", cmd_hello))
```

---

## 📜 مجوز

این پروژه تحت [مجوز MIT](LICENSE) منتشر شده است.

---

<div align="center">
ساخته‌شده با ❤️ و Python
</div>
