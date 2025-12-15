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
            handoff_at TEXT,
            handoff_count INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def save_message(wa_id, name, sender, message):
    ts = datetime.now(ARG_TZ).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (wa_id, name, sender, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (wa_id, name, sender, message, ts))
    conn.commit()
    conn.close()


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


def get_recent_chats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            m.wa_id,
            m.name,
            MAX(m.timestamp),
            COALESCE(c.handoff_human, 0)
        FROM messages m
        LEFT JOIN chat_state c ON m.wa_id = c.wa_id
        GROUP BY m.wa_id
        ORDER BY MAX(m.timestamp) DESC
        LIMIT 30
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# =====================
# HANDOFF
# =====================

def set_handoff(wa_id, value: bool):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    if value:
        cursor.execute("""
            INSERT INTO chat_state (wa_id, handoff_human, handoff_at, handoff_count)
            VALUES (?, 1, ?, 1)
            ON CONFLICT(wa_id)
            DO UPDATE SET
                handoff_human = 1,
                handoff_at = ?,
                handoff_count = handoff_count + 1
        """, (wa_id, now, now))
    else:
        cursor.execute("""
            UPDATE chat_state
            SET handoff_human = 0,
                handoff_at = NULL
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

    handoff, started = row

    if handoff == 1 and started:
        t = datetime.fromisoformat(started)
        if datetime.utcnow() - t > timedelta(hours=timeout_hours):
            set_handoff(wa_id, False)
            return False

    return handoff == 1
