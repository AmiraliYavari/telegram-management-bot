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


def _load_locale(lang_code: str) -> dict:
    if lang_code in _cache:
        return _cache[lang_code]
    path = LOCALES_DIR / f"{lang_code}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _cache[lang_code] = data
    return data


def available_languages() -> list[str]:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))


def t(chat_id: int, key: str, **kwargs) -> str:
    """Translate `key` for the group's language, falling back to Persian."""
    lang = get_language(chat_id)
    strings = _load_locale(lang) or _load_locale(DEFAULT_LANG)
    text = strings.get(key) or _load_locale(DEFAULT_LANG).get(key) or key
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError):
        return text