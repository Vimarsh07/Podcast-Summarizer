import os
from dotenv import load_dotenv
load_dotenv()

PGHOST = os.getenv("PGHOST", "").strip()
USE_PG = bool(PGHOST and PGHOST not in ("localhost", "127.0.0.1"))

if USE_PG:
    import psycopg2
    conn = psycopg2.connect(
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=PGHOST,
        port=os.getenv("PGPORT", "5432")
    )
    conn.autocommit = True
    PLACEHOLDER = "%s"
    print(f"[db.py] ▶ Using Postgres at {PGHOST}")
else:
    import sqlite3
    conn = sqlite3.connect("episodes.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    PLACEHOLDER = "?"
    print("[db.py] ▶ No remote PGHOST set (or localhost), using SQLite ‘episodes.db’")

cursor = conn.cursor()
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS episodes (
    guid TEXT PRIMARY KEY,
    podcast TEXT,
    title TEXT,
    pub_date TEXT,
    audio_url TEXT,
    transcript TEXT,
    summary TEXT
)
""")
if not USE_PG:
    conn.commit()

def already_processed(guid: str) -> bool:
    sql = f"SELECT 1 FROM episodes WHERE guid = {PLACEHOLDER}"
    cursor.execute(sql, (guid,))
    return cursor.fetchone() is not None


def save_episode(guid: str, podcast: str, title: str, pub_date: str,
                 audio_url: str, transcript: str, summary: str) -> None:
    placeholders = ", ".join([PLACEHOLDER] * 7)
    sql = f"""
    INSERT INTO episodes (guid, podcast, title, pub_date, audio_url, transcript, summary)
    VALUES ({placeholders})
    """
    cursor.execute(sql, (guid, podcast, title, pub_date, audio_url, transcript, summary))
    if not USE_PG:
        conn.commit()

