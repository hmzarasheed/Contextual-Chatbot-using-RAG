from rag_chat.db.connection import get_connection
from rag_chat.config.settings import PG_SUMMARY_TABLE
from datetime import datetime

def save_chat_summary(session_id: str, summary: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {PG_SUMMARY_TABLE} (session_id, summary, created_at) VALUES (%s, %s, %s)",
        (session_id, summary, datetime.utcnow())
    )
    conn.commit()
    cur.close()
    conn.close()

def summary_exists(session_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM {PG_SUMMARY_TABLE} WHERE session_id = %s", (session_id,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def get_pending_summaries():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT session_id, summary FROM {PG_SUMMARY_TABLE} WHERE embedded = FALSE")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def mark_summary_embedded(session_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {PG_SUMMARY_TABLE} SET embedded = TRUE WHERE session_id = %s", (session_id,))
    conn.commit()
    cur.close()
    conn.close()

def reset_all_summary_embedded_flags():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {PG_SUMMARY_TABLE} SET embedded = FALSE")
    conn.commit()
    cur.close()
    conn.close() 