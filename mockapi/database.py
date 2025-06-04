import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "mockapi.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            methods TEXT NOT NULL,
            response_type TEXT NOT NULL,
            response_body TEXT NOT NULL,
            status_code INTEGER NOT NULL
        )"""
    )
    conn.commit()
    conn.close()
