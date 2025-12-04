import sqlite3
from datetime import datetime
import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pixelbot.db")



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

    conn.commit()
    conn.close()

def save_message(wa_id, name, sender, message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (wa_id, name, sender, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (wa_id, name, sender, message, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def get_recent_chats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wa_id, name, MAX(timestamp) as last_msg
        FROM messages
        GROUP BY wa_id
        ORDER BY last_msg DESC
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
