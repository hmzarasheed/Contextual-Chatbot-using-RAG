from rag_chat.memory.embedder import embed_text

# Call this after every assistant response
def log_turn(turn_id: str, user_msg: str, assistant_msg: str):
    combined = f"User: {user_msg}\nAssistant: {assistant_msg}"
    embedding = embed_text(combined)
    # No vector DB logging here; handled by embedder worker
