import sqlite3
from core.database import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.execute("SELECT * FROM target_records ORDER BY external_id LIMIT 5")
rows = cur.fetchall()
conn.close()

print(f"Showing first {len(rows)} rows:")
for row in rows:
    print(row)