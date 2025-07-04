import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
url = urlparse(DATABASE_URL)

PG_HOST = url.hostname
PG_PORT = url.port or 5432
PG_DB = url.path[1:]
PG_USER = url.username
PG_PASSWORD = url.password
PG_CHAT_TABLE = "chats"
PG_TURN_TABLE = "chat_turns"
PG_SUMMARY_TABLE = "chat_summaries"

# Model/endpoint config for chat and summarizer
LLM_API_URL = os.environ["LLM_API_URL"]
LLM_MODEL_NAME = os.environ["LLM_MODEL_NAME"]

SUMMARIZER_API_URL = os.environ["SUMMARIZER_API_URL"]
SUMMARIZER_MODEL_NAME = os.environ["SUMMARIZER_MODEL_NAME"]

EMBEDDER_MODEL_NAME = os.environ["EMBEDDER_MODEL_NAME"]

# OpenAI API key for chat if using OpenAI backend
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
