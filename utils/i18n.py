"""
Minimal multi-language support.

- Locale strings live in locales/<lang_code>.json (e.g. en.json, fa.json).
- Each group picks its own language with /setlang <code>, stored via
  utils.database.get_language / set_language.
- t(chat_id, key, **kwargs) looks up the group's language and formats the
  string, falling back to Persian (the bot's original language) if the key
  or the language file is missing.

Add a new language by dropping locales/<code>.json with the same keys —
no code changes needed.
"""

import json
from pathlib import Path

from utils.database import get_language

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
DEFAULT_LANG = "fa"

_cache: dict[str, dict] = {}

# Last-resort fallback used only if the locale JSON files can't be found or
# parsed at all — so a missing/misplaced locales/ folder never leaks raw
# keys (like "leaderboard_title") straight into the chat.
_FALLBACK = {
    "welcome_default": "👋 Welcome {mention} to {chat_title}! 🎉",
    "setlang_admin_only": "⛔ Only admins can change the group language.",
    "setlang_usage": "Usage: /setlang <code>",
    "setlang_invalid": "❌ Unknown language code.",
    "setlang_success": "✅ Group language set to {lang}.",
    "welcome_admin_only": "⛔ Only admins can set the welcome message.",
    "welcome_set_usage": "Usage: /setwelcome <text>",
    "welcome_set_success": "✅ Custom welcome message saved.",
    "welcome_set_reset": "✅ Welcome message reset to default.",
    "level_up": "🎉 {mention} leveled up to level {level}!",
    "rank_title": "📈 {name}'s rank",
    "rank_line": "🏅 Rank #{rank} — Level {level} — {xp} XP",
    "rank_none": "You haven't earned any XP yet.",
    "leaderboard_title": "🏆 Top Chatters",
    "leaderboard_line": "{medal}  {name}  {count} msgs",
    "leaderboard_empty": "📊 No data yet.",
}


def _load_locale(lang_code: str) -> dict:
    if lang_code in _cache:
        return _cache[lang_code]
    path = LOCALES_DIR / f"{lang_code}.json"
    if not path.exists():
        print(f"[i18n] WARNING: locale file not found: {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[i18n] WARNING: locale file {path} is not valid JSON: {e}")
        return {}
    _cache[lang_code] = data
    return data


def available_languages() -> list[str]:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))


def t(chat_id: int, key: str, **kwargs) -> str:
    """Translate `key` for the group's language, falling back to Persian,
    then to English, then to a built-in fallback so users never see a raw
    key like 'leaderboard_title'."""
    lang = get_language(chat_id)
    strings = _load_locale(lang) or _load_locale(DEFAULT_LANG)
    text = strings.get(key) or _load_locale(DEFAULT_LANG).get(key) or _FALLBACK.get(key) or key
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError):
        return text