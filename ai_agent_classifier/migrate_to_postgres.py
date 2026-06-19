"""
One-time migration: copies all rows from local SQLite agents.db into the Railway PostgreSQL database.
Run with DATABASE_URL set in your environment:
    $env:DATABASE_URL = "postgresql://..."
    python migrate_to_postgres.py
"""
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "instance", "agents.db")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise SystemExit("ERROR: DATABASE_URL environment variable is not set.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Read from SQLite
sqlite_conn = sqlite3.connect(SQLITE_PATH)
sqlite_conn.row_factory = sqlite3.Row
rows = sqlite_conn.execute("SELECT * FROM agents").fetchall()
print(f"Found {len(rows)} agents in SQLite.")

# Connect to Postgres
pg_conn = psycopg2.connect(DATABASE_URL)
pg_cur = pg_conn.cursor()

# Create table if it doesn't exist
pg_cur.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        url VARCHAR(500),
        description TEXT,
        rationale TEXT,
        key_features TEXT,
        advantage VARCHAR(20),
        autonomy VARCHAR(10),
        agent_type VARCHAR(20),
        complexity VARCHAR(20),
        stages TEXT,
        category_id VARCHAR(50),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# Insert rows
inserted = 0
skipped = 0
for row in rows:
    pg_cur.execute("SELECT id FROM agents WHERE id = %s", (row["id"],))
    if pg_cur.fetchone():
        skipped += 1
        continue
    pg_cur.execute("""
        INSERT INTO agents (id, name, url, description, rationale, key_features,
                            advantage, autonomy, agent_type, complexity, stages,
                            category_id, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["id"], row["name"], row["url"], row["description"], row["rationale"],
        row["key_features"], row["advantage"], row["autonomy"], row["agent_type"],
        row["complexity"], row["stages"], row["category_id"], row["status"],
        row["created_at"],
    ))
    inserted += 1

# Sync the auto-increment sequence so new inserts don't collide with migrated IDs
pg_cur.execute("SELECT setval('agents_id_seq', (SELECT MAX(id) FROM agents))")

pg_conn.commit()
pg_cur.close()
pg_conn.close()
sqlite_conn.close()

print(f"Done. Inserted: {inserted}, Skipped (already existed): {skipped}")
