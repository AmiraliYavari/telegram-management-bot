"""
SQLite database — all schema creation and query helpers live here.
"""

import os
import sqlite3
from config import DB_PATH


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS warnings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                reason      TEXT,
                warned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                sent_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id     INTEGER PRIMARY KEY,
                is_open     INTEGER DEFAULT 1,
                filter_links INTEGER DEFAULT 1,
                filter_spam  INTEGER DEFAULT 1,
                language     TEXT DEFAULT 'fa',
                welcome_message TEXT
            );

            CREATE TABLE IF NOT EXISTS user_xp (
                chat_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                xp          INTEGER DEFAULT 0,
                level       INTEGER DEFAULT 0,
                last_xp_at  TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            );
        """)
        # Safe upgrade for DBs created before this migration (SQLite has no
        # "ADD COLUMN IF NOT EXISTS", so check pragma info first).
        existing_cols = {row["name"] for row in con.execute("PRAGMA table_info(group_settings)")}
        if "language" not in existing_cols:
            con.execute("ALTER TABLE group_settings ADD COLUMN language TEXT DEFAULT 'fa'")
        if "welcome_message" not in existing_cols:
            con.execute("ALTER TABLE group_settings ADD COLUMN welcome_message TEXT")


# ── Warnings ──────────────────────────────────────────────────────────────────

def add_warning(chat_id: int, user_id: int, reason: str = "") -> int:
    """Add a warning and return the new total count."""
    with _conn() as con:
        con.execute(
            "INSERT INTO warnings (chat_id, user_id, reason) VALUES (?, ?, ?)",
            (chat_id, user_id, reason)
        )
    return count_warnings(chat_id, user_id)


def count_warnings(chat_id: int, user_id: int) -> int:
    with _conn() as con:
        row = con.execute(
            "SELECT COUNT(*) AS c FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        ).fetchone()
    return row["c"]


def clear_warnings(chat_id: int, user_id: int):
    with _conn() as con:
        con.execute(
            "DELETE FROM warnings WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )


# ── Message log (stats + spam detection) ─────────────────────────────────────

def log_message(chat_id: int, user_id: int):
    with _conn() as con:
        con.execute(
            "INSERT INTO messages_log (chat_id, user_id) VALUES (?, ?)",
            (chat_id, user_id)
        )


def get_stats(chat_id: int, days: int = 7) -> list[sqlite3.Row]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT user_id, COUNT(*) AS msg_count
            FROM messages_log
            WHERE chat_id = ?
              AND sent_at >= datetime('now', ? || ' days')
            GROUP BY user_id
            ORDER BY msg_count DESC
            LIMIT 10
            """,
            (chat_id, f"-{days}")
        ).fetchall()
    return rows


def recent_message_count(chat_id: int, user_id: int, window_sec: int) -> int:
    with _conn() as con:
        row = con.execute(
            """
            SELECT COUNT(*) AS c FROM messages_log
            WHERE chat_id=? AND user_id=?
              AND sent_at >= datetime('now', ? || ' seconds')
            """,
            (chat_id, user_id, f"-{window_sec}")
        ).fetchone()
    return row["c"]


# ── Group settings ─────────────────────────────────────────────────────────────

def get_settings(chat_id: int) -> sqlite3.Row:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM group_settings WHERE chat_id=?", (chat_id,)
        ).fetchone()
        if not row:
            con.execute(
                "INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,)
            )
            row = con.execute(
                "SELECT * FROM group_settings WHERE chat_id=?", (chat_id,)
            ).fetchone()
    return row


def set_group_open(chat_id: int, is_open: bool):
    with _conn() as con:
        con.execute(
            "INSERT INTO group_settings (chat_id, is_open) VALUES (?, ?)"
            " ON CONFLICT(chat_id) DO UPDATE SET is_open=excluded.is_open",
            (chat_id, int(is_open))
        )


def get_language(chat_id: int) -> str:
    row = get_settings(chat_id)
    return row["language"] if row and row["language"] else "fa"


def set_language(chat_id: int, lang_code: str):
    get_settings(chat_id)  # ensure the row exists
    with _conn() as con:
        con.execute(
            "UPDATE group_settings SET language=? WHERE chat_id=?",
            (lang_code, chat_id)
        )


def get_welcome_message(chat_id: int):
    row = get_settings(chat_id)
    return row["welcome_message"] if row and row["welcome_message"] else None


def set_welcome_message(chat_id: int, message: str):
    get_settings(chat_id)  # ensure the row exists
    with _conn() as con:
        con.execute(
            "UPDATE group_settings SET welcome_message=? WHERE chat_id=?",
            (message, chat_id)
        )


# ── XP / leveling ────────────────────────────────────────────────────────────

def _level_for_xp(xp: int) -> int:
    """Simple RPG-style curve: level N needs N*100 XP more than level N-1."""
    level = 0
    needed = 100
    remaining = xp
    while remaining >= needed:
        remaining -= needed
        level += 1
        needed += 100
    return level


def add_xp(chat_id: int, user_id: int, amount: int, cooldown_sec: int) -> dict | None:
    """
    Award XP to a user if they're outside the cooldown window (prevents
    farming XP by spamming). Returns a dict describing the update, or None
    if the user is still on cooldown.
    {"xp": total_xp, "level": new_level, "leveled_up": bool}
    """
    with _conn() as con:
        row = con.execute(
            "SELECT xp, level, last_xp_at FROM user_xp WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        ).fetchone()

        if row and row["last_xp_at"] and cooldown_sec > 0:
            still_cooling = con.execute(
                "SELECT 1 FROM user_xp WHERE chat_id=? AND user_id=?"
                " AND last_xp_at >= datetime('now', ?)",
                (chat_id, user_id, f"-{cooldown_sec} seconds")
            ).fetchone()
            if still_cooling:
                return None

        old_xp = row["xp"] if row else 0
        old_level = row["level"] if row else 0
        new_xp = old_xp + amount
        new_level = _level_for_xp(new_xp)

        con.execute(
            """
            INSERT INTO user_xp (chat_id, user_id, xp, level, last_xp_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                xp = excluded.xp,
                level = excluded.level,
                last_xp_at = excluded.last_xp_at
            """,
            (chat_id, user_id, new_xp, new_level)
        )

    return {"xp": new_xp, "level": new_level, "leveled_up": new_level > old_level}


def get_user_xp(chat_id: int, user_id: int) -> sqlite3.Row:
    with _conn() as con:
        row = con.execute(
            "SELECT xp, level FROM user_xp WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        ).fetchone()
    return row


def get_leaderboard(chat_id: int, limit: int = 10) -> list[sqlite3.Row]:
    with _conn() as con:
        rows = con.execute(
            """
            SELECT user_id, xp, level FROM user_xp
            WHERE chat_id=?
            ORDER BY xp DESC
            LIMIT ?
            """,
            (chat_id, limit)
        ).fetchall()
    return rows


def get_user_rank(chat_id: int, user_id: int) -> int:
    """1-based rank of the user in their group's leaderboard (0 if untracked)."""
    with _conn() as con:
        row = con.execute(
            """
            SELECT COUNT(*) + 1 AS rank FROM user_xp
            WHERE chat_id=? AND xp > (
                SELECT xp FROM user_xp WHERE chat_id=? AND user_id=?
            )
            """,
            (chat_id, chat_id, user_id)
        ).fetchone()
    return row["rank"] if row else 0