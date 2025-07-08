from rag_chat.memory.retriever import retrieve_context
from rag_chat.config.settings import LLM_MODEL_NAME, LLM_API_URL, OPENAI_API_KEY
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def llm_choose_tool(user_input: str) -> str:
    """
    Use the LLM to decide which tool to use: 'retrieve_summary', 'retrieve_turns', or 'direct_answer'.
    Returns the tool name as a string.
    """
    system_prompt = (
        "You are an agent that decides which tool to use based on the user's request.\n"
        "Available tools:\n"
        "- retrieve_summary: Get a summary of previous conversations about a topic.\n"
        "- retrieve_turns: Get the full turn-by-turn chat history about a topic.\n"
        "- direct_answer: Answer the user's question directly, without retrieving any previous conversation context, if the user is not asking about previous chats.\n"
        "Respond with only the tool name: either 'retrieve_summary', 'retrieve_turns', or 'direct_answer'."
    )
    if OpenAI is None:
        # Fallback: default to direct_answer
        return "direct_answer"
    client = OpenAI(api_key=OPENAI_API_KEY or os.getenv('OPENAI_API_KEY'))
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User request: {user_input}"}
            ],
            max_tokens=10,
            temperature=0
        )
        tool_name = response.choices[0].message.content.strip().lower()
        if "turn" in tool_name:
            return "retrieve_turns"
        if "summary" in tool_name:
            return "retrieve_summary"
        return "direct_answer"
    except Exception as e:
        # Fallback: default to direct_answer
        return "direct_answer"

def decide_and_retrieve(user_input: str, top_k: int = 1):
    """
    Use the LLM to decide what to retrieve (summary, turns, or nothing) based on user input.
    Returns: (prompt, debug_info)
    """
    tool = llm_choose_tool(user_input)
    if tool == "retrieve_turns":
        context = retrieve_context(user_input, top_k=top_k)
        context_text = "\n".join([
            f"Turn: {t}" for t in context["turns"]
        ])
        debug_info = f"[DEBUG] [LLM] Retrieved only turns. Context window size: {len(context_text)} characters\n" \
                     f"[DEBUG] Context preview: {context_text[:200]}{'...' if len(context_text) > 200 else ''}"
        prompt = (
            f"IMPORTANT: Use the following full conversation history from previous chats to answer the user's question.\n"
            f"Turns:\n{context_text}\n"
            f"User: {user_input}"
        )
    elif tool == "retrieve_summary":
        context = retrieve_context(user_input, top_k=top_k)
        context_text = "\n".join([
            f"Summary: {s}" for s in context["summaries"]
        ])
        debug_info = f"[DEBUG] [LLM] Retrieved only summaries. Context window size: {len(context_text)} characters\n" \
                     f"[DEBUG] Context preview: {context_text[:200]}{'...' if len(context_text) > 200 else ''}"
        prompt = (
            f"IMPORTANT: Use the following summary of previous chats to answer the user's question.\n"
            f"Summary:\n{context_text}\n"
            f"User: {user_input}"
        )
    else:  # direct_answer
        debug_info = "[DEBUG] [LLM] No context retrieved; sending only user question to LLM."
        prompt = user_input
    return prompt, debug_info 