# 🚀 راهنمای Push به GitHub

## مرحله ۱ — Git را راه‌اندازی کن

```bash
cd telegram-admin-bot

git init
git add .
git commit -m "feat: initial commit — telegram admin bot"
```

## مرحله ۲ — ریپو بساز

۱. به [github.com/new](https://github.com/new) برو
۲. نام ریپو: `telegram-admin-bot`
۳. گزینه **Public** یا **Private** رو انتخاب کن
۴. **هیچ فایلی (README, .gitignore) اضافه نکن** — خودمون داریم
۵. روی **Create repository** کلیک کن

## مرحله ۳ — Push کن

```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-admin-bot.git
git branch -M main
git push -u origin main
```

## مرحله ۴ (اختیاری) — توضیحات ریپو

در صفحه ریپو کنار **About** روی چرخ‌دنده کلیک کن و بنویس:

> 🤖 ربات مدیریت گروه تلگرام | Telegram group admin bot with warn system, anti-spam, link filter & scheduler

**Topics پیشنهادی:**
```
telegram-bot  python  bot  admin  moderation  telegram
```

---

## دستورات روزمره git

```bash
# بعد از هر تغییر
git add .
git commit -m "feat: describe what you changed"
git push

# مشاهده وضعیت
git status
git log --oneline
```

## قرارداد نام‌گذاری commit

| پیشوند | کاربرد |
|---|---|
| `feat:` | قابلیت جدید |
| `fix:` | رفع باگ |
| `docs:` | تغییر مستندات |
| `refactor:` | بازنویسی بدون تغییر رفتار |
| `chore:` | کارهای جانبی (نصب پکیج و...) |
