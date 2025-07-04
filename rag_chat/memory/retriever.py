from rag_chat.memory.embedder import embed_text
from rag_chat.memory.vector_store import search_similar_summaries, search_similar_turns

def retrieve_context(query: str, top_k: int = 3):
    query_embedding = embed_text(query)
    summary_results = search_similar_summaries(query_embedding, top_k=top_k)
    turn_results = search_similar_turns(query_embedding, top_k=top_k)
    # print("DEBUG: Retrieved summaries:", summary_results)
    # print("DEBUG: Retrieved turns:", turn_results)
    return {
        "summaries": summary_results,
        "turns": turn_results
    } 