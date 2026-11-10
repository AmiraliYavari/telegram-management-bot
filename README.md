# ✦ Telegram Admin Bot

<div align="center">

**A powerful and modular Telegram group management bot built with Python.**

Automate moderation, manage members, prevent spam, track activity, and customize your Telegram community with a flexible administration system.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21.6-26A5E4?logo=telegram&logoColor=white)](https://python-telegram-bot.org/)
[![License](https://img.shields.io/badge/License-MIT-3DA66F.svg)](LICENSE)
[![PyPI Package](https://img.shields.io/badge/PyPI-telegram--group--manager-blue)](https://pypi.org/project/telegram-group-manager/)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](../../pulls)

</div>

---

## Overview

Telegram Admin Bot is a feature-rich group management solution designed to simplify community administration and automate repetitive moderation tasks.

Built with Python and powered by the `python-telegram-bot` framework, the project provides an extensible architecture with moderation tools, automated scheduling, multilingual support, activity statistics, and an integrated XP and leveling system.

## Features

| Feature | Description |
|---|---|
| Welcome Messages | Automatically welcomes new members with customizable messages. |
| Warning System | Tracks user warnings and automatically bans users after reaching the configured limit. |
| Link Filtering | Automatically detects and removes unauthorized links and usernames. |
| Anti-Spam Protection | Detects rapid message activity and applies temporary restrictions. |
| Group Statistics | Tracks member activity and identifies the most active users over the last seven days. |
| Scheduled Management | Automatically opens and closes groups according to configured schedules. |
| Multilingual Support | Supports multiple languages with independent group configurations. |
| Custom Welcome Messages | Allows administrators to configure personalized welcome messages. |
| XP and Level System | Rewards active members with experience points and levels. |
| Leaderboard | Displays the top members based on their accumulated experience. |

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core programming language |
| python-telegram-bot 21.6 | Telegram Bot API integration |
| SQLite | Persistent data storage |
| JSON | Localization and language configuration |
| python-dotenv | Environment variable management |

## Installation

### Requirements

- Python 3.11 or newer
- A Telegram Bot Token
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/telegram-admin-bot.git
cd telegram-admin-bot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your environment configuration file:

```bash
cp .env.example .env
```

On Windows, you can also create the file manually.

Add your Telegram Bot Token:

```env
BOT_TOKEN=your_telegram_bot_token
```

You can obtain a bot token through [@BotFather](https://t.me/BotFather).

### 5. Start the Bot

```bash
python bot.py
```

## Commands

The following commands are available for group administration and member interaction.

### Member Management

| Command | Description | Usage |
|---|---|---|
| `/warn` | Issue a warning to a member. | Reply to a message |
| `/unwarn` | Clear a member's warnings. | Reply to a message |
| `/ban` | Permanently ban a member. | `/ban @username` |
| `/unban` | Remove a member's ban. | `/unban @username` |
| `/mute` | Temporarily or permanently restrict a member. | `/mute @username 30m` |
| `/unmute` | Remove a member's restrictions. | Reply to a message |

### Statistics and Scheduling

| Command | Description | Usage |
|---|---|---|
| `/stats` | Display group activity statistics for the last seven days. | `/stats` |
| `/open` | Allow members to send messages. | `/open` |
| `/close` | Restrict members from sending messages. | `/close` |
| `/schedule` | Configure automatic group opening or closing. | `/schedule open 09:00` |

### Language and Welcome Configuration

| Command | Description | Usage |
|---|---|---|
| `/setlang` | Change the group's language. | `/setlang en` |
| `/setwelcome` | Set a custom welcome message. | `/setwelcome Hello {name}!` |
| `/setwelcome reset` | Restore the default welcome message. | `/setwelcome reset` |

### XP and Ranking System

| Command | Description | Usage |
|---|---|---|
| `/rank` | Display your level, XP, and ranking. | `/rank` |
| `/top` | Display the top ten members in the group. | `/top` |

Members earn experience points through regular participation. An XP cooldown prevents excessive point accumulation from consecutive messages.

The leveling system automatically calculates progression and sends notifications when members reach a new level.

## Configuration

The bot supports environment-based configuration through the `.env` file.

```env
BOT_TOKEN=your_telegram_bot_token

WARN_LIMIT=3

SPAM_THRESHOLD=5
SPAM_WINDOW_SEC=10

DB_PATH=data/bot.db

XP_COOLDOWN_SEC=60
```

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram Bot API token. |
| `WARN_LIMIT` | Maximum warnings before automatic banning. |
| `SPAM_THRESHOLD` | Maximum messages allowed within the spam detection window. |
| `SPAM_WINDOW_SEC` | Spam detection time window in seconds. |
| `DB_PATH` | SQLite database file location. |
| `XP_COOLDOWN_SEC` | Cooldown between XP rewards. |

## Project Structure

```text
telegram-admin-bot/
│
├── bot.py
├── config.py
├── requirements.txt
├── .env.example
├── LICENSE
│
├── handlers/
│   ├── welcome.py
│   ├── moderation.py
│   ├── stats.py
│   ├── schedule.py
│   ├── language.py
│   └── economy.py
│
├── locales/
│   ├── fa.json
│   └── en.json
│
└── utils/
    ├── database.py
    ├── i18n.py
    └── helpers.py
```

## Development

The project follows a modular architecture, making it straightforward to extend and maintain.

### Adding a New Command

Create a new handler inside the `handlers/` directory.

Example:

```python
from telegram import Update
from telegram.ext import ContextTypes

async def cmd_hello(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text("Hello!")
```

Register the command in `bot.py`:

```python
from telegram.ext import CommandHandler
from handlers.my_handler import cmd_hello

app.add_handler(
    CommandHandler("hello", cmd_hello)
)
```

## Package

The project is associated with the `telegram-group-manager` Python package, published on PyPI.

- **Package:** [telegram-group-manager](https://pypi.org/project/telegram-group-manager/)
- **Package Registry:** [PyPI](https://pypi.org/)

For package installation instructions and available releases, refer to its PyPI page.

## Collaboration & Credits

This project was developed with collaboration from **[Kiarash Noori](https://github.com/Kia-ML)**.

Special recognition goes to Kiarash Noori for developing the Python package associated with this project:

[telegram-group-manager on PyPI](https://pypi.org/project/telegram-group-manager/)

**Contributors:**
- [Kiarash Noori](https://github.com/Kia-ML) — Python package development and collaboration.

## Contributing

Contributions, bug reports, and feature requests are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Test your implementation.
5. Submit a pull request.

Please keep contributions consistent with the existing project structure and coding conventions.

## License

This project is distributed under the [MIT License](LICENSE).

---

<div align="center">

**✦ Telegram Admin Bot**

Built with Python.

Developed through collaboration and open-source contributions.

</div>
