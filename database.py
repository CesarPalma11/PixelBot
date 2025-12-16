import sqlite3
from datetime import datetime, timedelta

DB = "pixelbot.db"

def conn():
    return sqlite3.connect(DB)


def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        wa_id TEXT PRIMARY KEY,
        name TEXT,
        handoff INTEGER DEFAULT 0,
        handoff_until TEXT,
        last_message_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wa_id TEXT,
        sender TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    c.commit()
    c.close()


# =====================
# MENSAJES
# =====================

def save_message(wa_id, name, sender, message):
    ts = datetime.utcnow().isoformat()
    c = conn()
    cur = c.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO chats (wa_id, name)
    VALUES (?, ?)
    """, (wa_id, name))

    cur.execute("""
    INSERT INTO messages (wa_id, sender, message, timestamp)
    VALUES (?, ?, ?, ?)
    """, (wa_id, sender, message, ts))

    cur.execute("""
    UPDATE chats SET last_message_at = ?
    WHERE wa_id = ?
    """, (ts, wa_id))

    c.commit()
    c.close()


def get_chat(wa_id):
    c = conn()
    cur = c.cursor()
    cur.execute("""
    SELECT sender, message, timestamp
    FROM messages
    WHERE wa_id = ?
    ORDER BY id ASC
    """, (wa_id,))
    rows = cur.fetchall()
    c.close()
    return rows


def get_recent_chats():
    c = conn()
    cur = c.cursor()
    cur.execute("""
    SELECT wa_id, name, last_message_at, handoff
    FROM chats
    ORDER BY last_message_at DESC
    """)
    rows = cur.fetchall()
    c.close()
    return rows


# =====================
# HANDOFF
# =====================

def set_handoff(wa_id, minutes=60):
    until = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
    c = conn()
    cur = c.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO chats (wa_id)
    VALUES (?)
    """, (wa_id,))

    cur.execute("""
    UPDATE chats
    SET handoff = 1, handoff_until = ?
    WHERE wa_id = ?
    """, (until, wa_id))

    c.commit()
    c.close()


def disable_handoff(wa_id):
    c = conn()
    cur = c.cursor()
    cur.execute("""
    UPDATE chats
    SET handoff = 0, handoff_until = NULL
    WHERE wa_id = ?
    """, (wa_id,))
    c.commit()
    c.close()


def is_handoff(wa_id):
    c = conn()
    cur = c.cursor()
    cur.execute("""
    SELECT handoff, handoff_until
    FROM chats
    WHERE wa_id = ?
    """, (wa_id,))
    row = cur.fetchone()
    c.close()

    if not row or not row[0]:
        return False

    if row[1] and datetime.utcnow() > datetime.fromisoformat(row[1]):
        disable_handoff(wa_id)
        return False

    return True
