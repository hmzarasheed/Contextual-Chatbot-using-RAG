from rag_chat.db.connection import get_connection
from datetime import datetime
from rag_chat.config.settings import PG_CHAT_TABLE

def save_chat_session(session_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {PG_CHAT_TABLE} (session_id, created_at, summary_status) VALUES (%s, %s, %s) ON CONFLICT (session_id) DO NOTHING",
        (session_id, datetime.utcnow(), 'pending')
    )
    conn.commit()
    cur.close()
    conn.close()

def get_pending_sessions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT session_id FROM {PG_CHAT_TABLE} WHERE summary_status = 'pending'")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]

def update_summary_status(session_id: str, status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {PG_CHAT_TABLE} SET summary_status = %s WHERE session_id = %s", (status, session_id))
    conn.commit()
    cur.close()
    conn.close() 