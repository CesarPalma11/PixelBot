import sqlite3
from datetime import datetime
import os
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pixelbot.db")

ARG_TZ = pytz.timezone("America/Argentina/Buenos_Aires")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_id TEXT,
            name TEXT,
            sender TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_state (
            wa_id TEXT PRIMARY KEY,
            handoff_human INTEGER DEFAULT 0,
            handoff_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(wa_id, name, sender, message):
    timestamp_local = datetime.now(ARG_TZ).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (wa_id, name, sender, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (wa_id, name, sender, message, timestamp_local))
    conn.commit()
    conn.close()


def get_recent_chats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT wa_id, name, MAX(timestamp)
        FROM messages
        GROUP BY wa_id
        ORDER BY MAX(timestamp) DESC
        LIMIT 30
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_chat(wa_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message, timestamp
        FROM messages
        WHERE wa_id = ?
        ORDER BY timestamp ASC
    """, (wa_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


# =====================
# HANDOFF
# =====================

def set_handoff(wa_id, value: bool):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if value:
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO chat_state (wa_id, handoff_human, handoff_at)
            VALUES (?, 1, ?)
            ON CONFLICT(wa_id)
            DO UPDATE SET handoff_human = 1, handoff_at = ?
        """, (wa_id, now, now))
    else:
        cursor.execute("""
            UPDATE chat_state
            SET handoff_human = 0, handoff_at = NULL
            WHERE wa_id = ?
        """, (wa_id,))

    conn.commit()
    conn.close()


def is_handoff(wa_id, timeout_hours=12):
    from datetime import timedelta

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT handoff_human, handoff_at
        FROM chat_state
        WHERE wa_id = ?
    """, (wa_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    handoff, handoff_at = row

    if handoff == 1 and handoff_at:
        started = datetime.fromisoformat(handoff_at)
        if datetime.utcnow() - started > timedelta(hours=timeout_hours):
            # 🔄 Auto-reactivar bot
            set_handoff(wa_id, False)
            return False

    return handoff == 1
