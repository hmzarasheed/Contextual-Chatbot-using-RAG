# RAG Chat System

This project implements a Retrieval-Augmented Generation (RAG) chat system with background summarization and embedding workers, using a PostgreSQL database and FAISS for vector search.

## Features
- Chat interface with context retrieval
- Background summarization of chat sessions
- Embedding of chat summaries and turns
- Vector search using FAISS
- Modular codebase for easy extension

## Project Structure
```
rag_chat/
  main.py              # Start the chat interface
  worker.py            # Background summarization worker
  embedder_worker.py   # Embedding worker for summaries and turns
  saver.py             # Moves pending chat sessions into the database
  agent/               # Retrieval agent logic
  config/              # Settings and environment config
  core/                # Chat loop and LLM API
  db/                  # Database models and logic
  memory/              # Embedding, retrieval, vector store
  utils/               # Input handling utilities
faiss_db/              # FAISS index and ID map files (auto-generated)
pending_chats/         # Temporary storage for chat sessions (auto-generated)
requirements.txt       # Python dependencies
```

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables** (create a `.env` file in the root):
   ```env
   DATABASE_URL=postgresql://user:password@host:port/dbname
   LLM_API_URL=...
   LLM_MODEL_NAME=...
   SUMMARIZER_API_URL=...
   SUMMARIZER_MODEL_NAME=...
   EMBEDDER_MODEL_NAME=...
   OPENAI_API_KEY=...
   ```

## Usage
- **Start the chat interface:**
  ```bash
  python -m rag_chat.main
  ```
- **Run the background summarization worker:**
  ```bash
  python -m rag_chat.worker
  ```
- **Run the embedding worker:**
  ```bash
  python -m rag_chat.embedder_worker
  ```
- **Run the saver (to move pending chats to the database):**
  ```bash
  python -m rag_chat.saver
  ```

## Notes
- `faiss_db/` and `pending_chats/` are auto-generated and can be added to `.gitignore`.
- The project requires a running PostgreSQL database and appropriate model endpoints.
- Debugger breakpoints are included (commented out) in key scripts for future troubleshooting.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for improvements or bug fixes.

## Contact
For questions or support, please open an issue in this repository.


[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hamza-rasheed-6a9b3b23a?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github&logoColor=white)](https://github.com/hmzarasheed)

---

*This README is specific to the current project scope and codebase.* 