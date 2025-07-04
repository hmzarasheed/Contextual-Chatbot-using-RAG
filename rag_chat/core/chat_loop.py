from rag_chat.core.llm_api import query_llm_stream_with_callback
from rag_chat.utils.input_handler import get_user_input
from rag_chat.memory.logger import log_turn
from datetime import datetime
import uuid
import os
import json
from rag_chat.config.settings import LLM_MODEL_NAME, LLM_API_URL
from rag_chat.agent import retrieval_agent
from rag_chat.memory.vector_store import print_vector_db_stats

PENDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'pending_chats')

# import pdb; pdb.set_trace()  # DEBUG: Uncomment to debug this function

def start_chat():
    print("🤖 Chat started | Type 'exit' to quit\n")
    # print("[DEBUG] Vector DB stats:")
    turn_count = 0
    turns = []
    session_id = str(uuid.uuid4())

    while True:
        user_input = get_user_input()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        # Use the retrieval agent to decide what to retrieve and construct the prompt
        prompt, debug_info = retrieval_agent.decide_and_retrieve(user_input, top_k=5)
        print(debug_info)

        print("Assistant: ", end="", flush=True)
        response_text = []

        def on_token(token):
            print(token, end="", flush=True)
            response_text.append(token)

        query_llm_stream_with_callback(prompt, on_token, model=LLM_MODEL_NAME, url=LLM_API_URL)

        full_response = "".join(response_text)
        turn_id = f"turn_{turn_count}"
        log_turn(turn_id, user_input, full_response)
        turns.append({
            "turn_id": turn_id,
            "user_msg": user_input,
            "assistant_msg": full_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        turn_count += 1
        print()

    # Save the chat session and turns to a JSON file in pending_chats
    if turns:
        os.makedirs(PENDING_DIR, exist_ok=True)
        data = {"session_id": session_id, "turns": turns}
        file_path = os.path.join(PENDING_DIR, f"{session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Chat] Session saved to {file_path} for background processing.")


def needs_context(user_input: str) -> bool:
    # Simple heuristic: look for pronouns or references to previous context
    keywords = [
        'it', 'that', 'those', 'them', 'earlier', 'previous', 'before', 'last time', 'you said', 'we discussed', 'the above', 'the previous', 'the earlier', 'the context', 'the conversation'
    ]
    user_input_lower = user_input.lower()
    return any(kw in user_input_lower for kw in keywords)

def wants_summary(user_input: str) -> bool:
    keywords = [
        'overview', 'summary', 'summarize', 'recap', 'brief', 'in short', 'in summary', 'summarise'
    ]
    user_input_lower = user_input.lower()
    return any(kw in user_input_lower for kw in keywords)

def wants_full_details(user_input: str) -> bool:
    keywords = [
        'everything', 'all details', 'full conversation', 'every message', 'all turns', 'complete history', 'tell me all', 'entire conversation', 'all responses', 'all exchanges'
    ]
    user_input_lower = user_input.lower()
    return any(kw in user_input_lower for kw in keywords)
