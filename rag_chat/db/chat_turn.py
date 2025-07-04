from rag_chat.db.connection import get_connection
from psycopg2.extras import execute_values
from rag_chat.config.settings import PG_TURN_TABLE
from datetime import datetime

def save_chat_turns(session_id: str, turns: list):
    conn = get_connection()
    cur = conn.cursor()
    turn_values = [
        (
            session_id,
            t["turn_id"],
            t["user_msg"],
            t["assistant_msg"],
            datetime.fromisoformat(t["timestamp"])
        ) for t in turns
    ]
    execute_values(
        cur,
        f"INSERT INTO {PG_TURN_TABLE} (session_id, turn_id, user_msg, assistant_msg, timestamp) VALUES %s",
        turn_values
    )
    conn.commit()
    cur.close()
    conn.close()

def get_turns_for_session(session_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT turn_id, user_msg, assistant_msg, timestamp FROM {PG_TURN_TABLE} WHERE session_id = %s ORDER BY id ASC", (session_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "turn_id": row[0],
            "user_msg": row[1],
            "assistant_msg": row[2],
            "timestamp": row[3].isoformat() if row[3] else None
        }
        for row in rows
    ]

def get_pending_turns():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT turn_id, user_msg, assistant_msg FROM {PG_TURN_TABLE} WHERE embedded = FALSE")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [(row[0], f"User: {row[1]}\nAssistant: {row[2]}") for row in rows]

def mark_turn_embedded(turn_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {PG_TURN_TABLE} SET embedded = TRUE WHERE turn_id = %s", (turn_id,))
    conn.commit()
    cur.close()
    conn.close()

def reset_all_turn_embedded_flags():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {PG_TURN_TABLE} SET embedded = FALSE")
    conn.commit()
    cur.close()
    conn.close() 