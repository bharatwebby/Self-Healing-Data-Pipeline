import sqlite3
from datetime import datetime

DB_PATH = "pipeline.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS target_records (
            external_id INTEGER PRIMARY KEY,
            display_name TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def write_records(records):
    """records: a list of validated TargetRecord objects."""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()
    for r in records:
        conn.execute("""
            INSERT INTO target_records (external_id, display_name, amount_cents, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(external_id) DO UPDATE SET
                display_name = excluded.display_name,
                amount_cents = excluded.amount_cents,
                last_updated = excluded.last_updated
        """, (r.external_id, r.display_name, r.amount_cents, now))
    conn.commit()
    conn.close()

def count_records() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT COUNT(*) FROM target_records")
    count = cur.fetchone()[0]
    conn.close()
    return count