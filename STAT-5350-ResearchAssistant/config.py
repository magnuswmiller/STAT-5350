'''
config.py

TODO Write summary here
'''
# Import Libraries
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Default configuration (override via .env)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL","http://localhost:11434/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3")
USE_OPENAI = os.getenv("USE_OPENAI", "FALSE").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBED_MODEL  = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL   = os.getenv("OPENAI_CHAT_MODEL",  "gpt-4o-mini")
TOP_K               = int(os.getenv("TOP_K", "5"))   # chunks returned per query