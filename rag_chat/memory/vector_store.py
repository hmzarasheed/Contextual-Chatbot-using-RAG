import faiss
import numpy as np
import os
import pickle

EMBEDDING_DIM = 384  # Change if your embeddings have a different dimension
PERSIST_DIR = os.path.abspath("faiss_db")
INDEX_PATH_SUMMARY = os.path.join(PERSIST_DIR, "summary.index")
INDEX_PATH_TURN = os.path.join(PERSIST_DIR, "turn.index")
IDMAP_PATH_SUMMARY = os.path.join(PERSIST_DIR, "summary_idmap.pkl")
IDMAP_PATH_TURN = os.path.join(PERSIST_DIR, "turn_idmap.pkl")

os.makedirs(PERSIST_DIR, exist_ok=True)

N_LIST = 100  # Number of clusters for IVF index, tune as needed

# Helper to create a new IVF index
def create_ivf_index():
    quantizer = faiss.IndexFlatL2(EMBEDDING_DIM)
    return faiss.IndexIVFFlat(quantizer, EMBEDDING_DIM, N_LIST, faiss.METRIC_L2)

# Load or create FAISS indices
if os.path.exists(INDEX_PATH_SUMMARY):
    summary_index = faiss.read_index(INDEX_PATH_SUMMARY)
else:
    summary_index = create_ivf_index()

if os.path.exists(INDEX_PATH_TURN):
    turn_index = faiss.read_index(INDEX_PATH_TURN)
else:
    turn_index = create_ivf_index()

# Load or create ID-to-text maps
if os.path.exists(IDMAP_PATH_SUMMARY):
    with open(IDMAP_PATH_SUMMARY, "rb") as f:
        summary_idmap = pickle.load(f)
else:
    summary_idmap = {}

if os.path.exists(IDMAP_PATH_TURN):
    with open(IDMAP_PATH_TURN, "rb") as f:
        turn_idmap = pickle.load(f)
else:
    turn_idmap = {}

# --- Index Training ---
def is_trained(index):
    attr = getattr(index, 'is_trained', None)
    if attr is None:
        return True  # Assume trained if attribute doesn't exist
    if callable(attr):
        return attr()
    return attr

def train_index(index, embeddings):
    np_embeddings = np.array(embeddings).astype('float32')
    if not is_trained(index):
        index.train(np_embeddings)

# --- Saving/Loading ---
def save_all():
    faiss.write_index(summary_index, INDEX_PATH_SUMMARY)
    faiss.write_index(turn_index, INDEX_PATH_TURN)
    with open(IDMAP_PATH_SUMMARY, "wb") as f:
        pickle.dump(summary_idmap, f)
    with open(IDMAP_PATH_TURN, "wb") as f:
        pickle.dump(turn_idmap, f)
    # print("[DEBUG] FAISS DB contents:", os.listdir(PERSIST_DIR))

# --- Add Vectors ---
# import pdb; pdb.set_trace()  # DEBUG: Uncomment to debug this function
def add_summary_vector(session_id: str, summary_text: str, embedding: list):
    np_embedding = np.array([embedding]).astype('float32')
    if not is_trained(summary_index):
        # Collect all embeddings for training
        all_embeddings = [embedding]
        for idx in range(len(summary_idmap)):
            all_embeddings.append(get_summary_embedding(idx))
        train_index(summary_index, all_embeddings)
    summary_index.add(np_embedding)
    summary_idmap[len(summary_idmap)] = (session_id, summary_text)
    # Do NOT call save_all here for performance

def add_turn_vector(turn_id: str, turn_text: str, embedding: list):
    np_embedding = np.array([embedding]).astype('float32')
    if not is_trained(turn_index):
        all_embeddings = [embedding]
        for idx in range(len(turn_idmap)):
            all_embeddings.append(get_turn_embedding(idx))
        train_index(turn_index, all_embeddings)
    turn_index.add(np_embedding)
    turn_idmap[len(turn_idmap)] = (turn_id, turn_text)
    # Do NOT call save_all here for performance

# --- Retrieval ---
def search_similar_summaries(query_embedding: list, top_k: int = 3):
    if summary_index.ntotal == 0:
        return []
    np_query = np.array([query_embedding]).astype('float32')
    distances, indices = summary_index.search(np_query, top_k)
    results = []
    for idx in indices[0]:
        if idx in summary_idmap:
            results.append(summary_idmap[idx][1])
    return results

def search_similar_turns(query_embedding: list, top_k: int = 3):
    if turn_index.ntotal == 0:
        return []
    np_query = np.array([query_embedding]).astype('float32')
    distances, indices = turn_index.search(np_query, top_k)
    results = []
    for idx in indices[0]:
        if idx in turn_idmap:
            results.append(turn_idmap[idx][1])
    return results

# --- Utility Functions ---
def print_vector_db_stats():
    print("Summary collection count:", summary_index.ntotal)
    print("Turn collection count:", turn_index.ntotal)
    # print("[DEBUG] FAISS DB contents:", os.listdir(PERSIST_DIR))

def manual_save():
    save_all()

# --- Embedding Recovery (for training) ---
def get_summary_embedding(idx):
    # Placeholder: implement if you store embeddings elsewhere
    # For now, return zeros (should be replaced with real embeddings)
    return np.zeros(EMBEDDING_DIM, dtype='float32')

def get_turn_embedding(idx):
    # Placeholder: implement if you store embeddings elsewhere
    return np.zeros(EMBEDDING_DIM, dtype='float32')

# --- Batch Training Function ---
def batch_train_summary_index(embeddings):
    train_index(summary_index, embeddings)

def batch_train_turn_index(embeddings):
    train_index(turn_index, embeddings)

# --- End of file ---
