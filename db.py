import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)

conn.autocommit = True
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS episodes (
    guid TEXT PRIMARY KEY,
    podcast TEXT,
    title TEXT,
    pub_date TEXT,
    audio_url TEXT,
    transcript TEXT,
    summary TEXT
)
''')

def already_processed(guid):
    cursor.execute("SELECT 1 FROM episodes WHERE guid = %s", (guid,))
    return cursor.fetchone() is not None

def save_episode(guid, podcast, title, pub_date, audio_url, transcript, summary):
    cursor.execute("""
        INSERT INTO episodes (guid, podcast, title, pub_date, audio_url, transcript, summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (guid, podcast, title, pub_date, audio_url, transcript, summary))
