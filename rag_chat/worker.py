import time
from rag_chat.db.connection import init_db, upgrade_db
from rag_chat.db.chat_session import get_pending_sessions, update_summary_status
from rag_chat.db.chat_turn import get_turns_for_session
from rag_chat.db.chat_summary import save_chat_summary, summary_exists
from rag_chat.config.settings import SUMMARIZER_MODEL_NAME, SUMMARIZER_API_URL, OPENAI_API_KEY

try:
    import openai
except ImportError:
    openai = None

POLL_INTERVAL = 10  # seconds

# import pdb; pdb.set_trace()  # DEBUG: Uncomment to debug this function

def summarize_chat(session_id, turns):
    chat_text = "\n".join([
        f"User: {t['user_msg']}\nAssistant: {t['assistant_msg']}" for t in turns
    ])
    summary_prompt = (
        "Summarize the following chat conversation in a concise, informative way, "
        "highlighting all key information, user questions, and important answers. "
        "Format the summary for business/industrial use.\n\nChat:\n" + chat_text
    )
    if 'openai' in SUMMARIZER_API_URL or SUMMARIZER_API_URL.startswith('https://api.openai.com'):
        if openai is None:
            return "[Error] openai package not installed"
        openai.api_key = OPENAI_API_KEY
        try:
            response = openai.ChatCompletion.create(
                model=SUMMARIZER_MODEL_NAME,
                messages=[{"role": "user", "content": summary_prompt}],
                stream=False
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"[Error] {e}"
    else:
        from rag_chat.core.llm_api import query_llm_response
        return query_llm_response(summary_prompt, model=SUMMARIZER_MODEL_NAME, url=SUMMARIZER_API_URL)

def main():
    print("[Worker] Starting background summarization worker...")
    upgrade_db()
    init_db()
    while True:
        pending_sessions = get_pending_sessions()
        for session_id in pending_sessions:
            if summary_exists(session_id):
                update_summary_status(session_id, 'done')
                continue
            turns = get_turns_for_session(session_id)
            if not turns:
                continue
            print(f"[Worker] Summarizing session {session_id}...")
            summary = summarize_chat(session_id, turns)
            save_chat_summary(session_id, summary)
            update_summary_status(session_id, 'done')
            print(f"[Worker] Summary saved for session {session_id}.")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main() 