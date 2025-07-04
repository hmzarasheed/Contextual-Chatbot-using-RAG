import os
import json
import time
from rag_chat.db.connection import init_db, upgrade_db
from rag_chat.db.chat_session import save_chat_session
from rag_chat.db.chat_turn import save_chat_turns

# import pdb; pdb.set_trace()  # DEBUG: Uncomment to debug this function

PENDING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pending_chats')
POLL_INTERVAL = 5  # seconds

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    session_id = data['session_id']
    turns = data['turns']
    save_chat_session(session_id)
    save_chat_turns(session_id, turns)
    print(f"[Saver] Saved session {session_id} to database.")
    os.remove(file_path)
    print(f"[Saver] Removed file {file_path}.")

def main():
    print("[Saver] Starting chat session saver worker...")
    upgrade_db()
    init_db()
    os.makedirs(PENDING_DIR, exist_ok=True)
    while True:
        files = [f for f in os.listdir(PENDING_DIR) if f.endswith('.json')]
        for filename in files:
            file_path = os.path.join(PENDING_DIR, filename)
            try:
                process_file(file_path)
            except Exception as e:
                print(f"[Saver] Error processing {file_path}: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main() 