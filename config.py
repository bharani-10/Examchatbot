import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _get_secret(key: str) -> str:
    """Read from Streamlit secrets first, then fall back to environment variables."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

# These are resolved at runtime (inside Streamlit context)
def get_groq_api_key():
    return _get_secret("GROQ_API_KEY")

# For backward compatibility with existing imports
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

MODEL_NAME      = "llama-3.1-8b-instant"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = "vectorstore"
DATA_FILE       = "syllabus.txt"
