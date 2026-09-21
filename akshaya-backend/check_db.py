import sqlite3
from pathlib import Path

db_path = Path("data/akshaya.db")
if not db_path.exists():
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = ["messages", "message_sources", "query_audit_log", "feedback"]
for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"Table {table}: {count} rows")
    if count > 0:
        c.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1")
        print(f"  Latest: {c.fetchone()}")

conn.close()
