from sentence_transformers import SentenceTransformer
from rag_chat.config.settings import EMBEDDER_MODEL_NAME

# Load the embedding model once
model = SentenceTransformer(EMBEDDER_MODEL_NAME)

def embed_text(text: str):
    return model.encode(text).tolist()
