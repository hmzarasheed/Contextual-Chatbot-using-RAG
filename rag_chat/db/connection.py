import psycopg2
from rag_chat.config.settings import (
    PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD, PG_CHAT_TABLE, PG_TURN_TABLE, PG_SUMMARY_TABLE
)

def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_CHAT_TABLE} (
            session_id VARCHAR(64) PRIMARY KEY,
            created_at TIMESTAMP,
            summary_status VARCHAR(16) DEFAULT 'pending'
        );
    """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_TURN_TABLE} (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(64) REFERENCES {PG_CHAT_TABLE}(session_id),
            turn_id VARCHAR(32),
            user_msg TEXT,
            assistant_msg TEXT,
            timestamp TIMESTAMP
        );
    """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_SUMMARY_TABLE} (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(64) REFERENCES {PG_CHAT_TABLE}(session_id) UNIQUE,
            summary TEXT,
            created_at TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def upgrade_db():
    conn = get_connection()
    cur = conn.cursor()
    # Add summary_status to chats
    try:
        cur.execute(f"ALTER TABLE {PG_CHAT_TABLE} ADD COLUMN summary_status VARCHAR(16) DEFAULT 'pending';")
        print("[DB] Added summary_status column to chats table.")
        conn.commit()
    except psycopg2.errors.DuplicateColumn:
        print("[DB] summary_status column already exists.")
        conn.rollback()
    except Exception as e:
        if 'already exists' in str(e):
            print("[DB] summary_status column already exists.")
            conn.rollback()
        else:
            print(f"[DB] Error during migration: {e}")
            conn.rollback()
    # Add embedded to chat_summaries
    try:
        cur.execute(f"ALTER TABLE {PG_SUMMARY_TABLE} ADD COLUMN embedded BOOLEAN DEFAULT FALSE;")
        print("[DB] Added embedded column to chat_summaries table.")
        conn.commit()
    except psycopg2.errors.DuplicateColumn:
        print("[DB] embedded column already exists in chat_summaries.")
        conn.rollback()
    except Exception as e:
        if 'already exists' in str(e):
            print("[DB] embedded column already exists in chat_summaries.")
            conn.rollback()
        else:
            print(f"[DB] Error during migration: {e}")
            conn.rollback()
    # Add embedded to chat_turns
    try:
        cur.execute(f"ALTER TABLE {PG_TURN_TABLE} ADD COLUMN embedded BOOLEAN DEFAULT FALSE;")
        print("[DB] Added embedded column to chat_turns table.")
        conn.commit()
    except psycopg2.errors.DuplicateColumn:
        print("[DB] embedded column already exists in chat_turns.")
        conn.rollback()
    except Exception as e:
        if 'already exists' in str(e):
            print("[DB] embedded column already exists in chat_turns.")
            conn.rollback()
        else:
            print(f"[DB] Error during migration: {e}")
            conn.rollback()
    cur.close()
    conn.close() 