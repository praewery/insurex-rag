import sqlite3
import json
from datetime import datetime
from src.models import LeadInfo

DB_PATH = "leads.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            name        TEXT,
            occupation  TEXT,
            income      TEXT,
            phone       TEXT,
            raw_json    TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_lead(session_id: str, lead: LeadInfo) -> bool:
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT INTO leads (session_id, name, occupation, income, phone, raw_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                lead.name,
                lead.occupation,
                lead.income,
                lead.phone,
                json.dumps(lead.model_dump(), ensure_ascii=False),
                datetime.now().isoformat(),
            )
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving lead: {e}")
        return False


def get_all_leads() -> list[dict]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]
