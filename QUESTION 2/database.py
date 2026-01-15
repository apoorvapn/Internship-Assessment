import sqlite3
import json
import time

DB_FILE = "events.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            metadata TEXT
        )
    """)
    conn.commit()
    return conn

def insert_batch(conn, events):
    cursor = conn.cursor()

    # 🔥 Uncomment this to simulate DB outage
    # time.sleep(5)

    cursor.executemany(
        "INSERT INTO events (user_id, timestamp, metadata) VALUES (?, ?, ?)",
        [
            (e["user_id"], e["timestamp"], json.dumps(e["metadata"]))
            for e in events
        ]
    )
    conn.commit()
