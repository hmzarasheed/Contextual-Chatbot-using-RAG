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
        "Summarize the following chat conversation in a short paragraph (no more than 5 sentences). "
        "Focus only on the most important information, user questions, and key answers. "
        "Be concise and avoid unnecessary details.\n\nChat:\n" + chat_text
    )
    if 'openai' in SUMMARIZER_API_URL or SUMMARIZER_API_URL.startswith('https://api.openai.com'):
        if openai is None:
            # print(f"[ERROR] openai package not installed for session {session_id}")
            return "[Error] openai package not installed"
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=SUMMARIZER_MODEL_NAME,
                messages=[{"role": "user", "content": summary_prompt}],
                stream=False
            )
            summary = response.choices[0].message.content
            # print(f"[DEBUG] Generated summary for session {session_id}: {summary[:200]}{'...' if len(summary) > 200 else ''}")
            return summary
        except Exception as e:
            # print(f"[ERROR] Exception during summary generation for session {session_id}: {e}")
            return f"[Error] {e}"
    else:
        from rag_chat.core.llm_api import query_llm_response
        summary = query_llm_response(summary_prompt, model=SUMMARIZER_MODEL_NAME, url=SUMMARIZER_API_URL)
        # print(f"[DEBUG] Generated summary for session {session_id}: {summary[:200]}{'...' if len(summary) > 200 else ''}")
        return summary

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
            # print(f"[DEBUG] FULL GENERATED SUMMARY for session {session_id}:\n{summary}\n{'-'*60}")
            # print(f"[DEBUG] Generated summary for session {session_id}: {summary[:200]}{'...' if len(summary) > 200 else ''}")
            # print(f"[ERROR] openai package not installed for session {session_id}")
            # print(f"[ERROR] Exception during summary generation for session {session_id}: {e}")
            # print(f"[DEBUG] Attempting to save summary for session {session_id}.")
            # print(f"[DEBUG] Saved summary for session {session_id} to database.")
            # print(f"[ERROR] Failed to save summary for session {session_id}: {e}")
            try:
                save_chat_summary(session_id, summary)
                # print(f"[DEBUG] Saved summary for session {session_id} to database.")
            except Exception as e:
                # print(f"[ERROR] Failed to save summary for session {session_id}: {e}")
                pass
            update_summary_status(session_id, 'done')
            print(f"[Worker] Summary saved for session {session_id}.")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main() 