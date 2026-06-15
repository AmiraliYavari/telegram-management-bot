"""
SQLite database — all schema creation and query helpers live here.
"""

import sqlite3
from config import DB_PATH


def _conn() -> sqlite3.Connection:
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
                filter_spam  INTEGER DEFAULT 1
            );
        """)


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
