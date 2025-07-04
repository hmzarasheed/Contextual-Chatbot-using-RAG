import time
from rag_chat.db.connection import init_db, upgrade_db
from rag_chat.db.chat_summary import get_pending_summaries, mark_summary_embedded, reset_all_summary_embedded_flags
from rag_chat.db.chat_turn import get_pending_turns, mark_turn_embedded, reset_all_turn_embedded_flags
from rag_chat.memory.embedder import embed_text
from rag_chat.memory.vector_store import add_summary_vector, add_turn_vector, manual_save

POLL_INTERVAL = 10  # seconds

def embed_and_store_summary(session_id, summary_text):
    embedding = embed_text(summary_text)
    add_summary_vector(session_id, summary_text, embedding)
    mark_summary_embedded(session_id)
    print(f"[Embedder] Embedded and stored summary for session {session_id}")

def embed_and_store_turn(turn_id, turn_text):
    embedding = embed_text(turn_text)
    add_turn_vector(turn_id, turn_text, embedding)
    mark_turn_embedded(turn_id)
    print(f"[Embedder] Embedded and stored turn {turn_id}")

def main():
    print("[Embedder] Starting embedding worker...")
    upgrade_db()
    init_db()
    # One-time reset of all embedded flags for summaries and turns. Remove/comment after first run if not needed.
    # reset_all_summary_embedded_flags()
    # reset_all_turn_embedded_flags()
    while True:
        embedded_any = False
        # Embed summaries
        pending_summaries = list(get_pending_summaries())
        for session_id, summary_text in pending_summaries:
            embed_and_store_summary(session_id, summary_text)
            embedded_any = True
        # Embed turns
        pending_turns = list(get_pending_turns())
        for turn_id, turn_text in pending_turns:
            embed_and_store_turn(turn_id, turn_text)
            embedded_any = True
        if embedded_any:
            manual_save()
            print("[Embedder] Saved FAISS index and ID maps.")
        print(f"[Embedder] Remaining to embed: {len(pending_summaries)} summaries, {len(pending_turns)} turns.")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    # import pdb; pdb.set_trace()  # DEBUG: Uncomment to debug this function
    main()
