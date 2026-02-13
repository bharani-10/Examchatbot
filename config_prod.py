import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_groq_api_key():
    """Get GROQ API key from environment or Streamlit secrets"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fallback to environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("🔑 GROQ API Key not found! Please add it to Streamlit secrets or .env file")
            st.info("Get your free API key from: https://console.groq.com/")
            st.stop()
        return api_key

# Configuration
GROQ_API_KEY = get_groq_api_key()
MODEL_NAME = "llama-3.1-8b-instant"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# File paths
VECTORSTORE_DIR = "vectorstore"
DATA_FILE = "syllabus.txt"

# App settings
MAX_FILE_SIZE_MB = 10
SUPPORTED_FILE_TYPES = ["pdf"]
MAX_CHAT_HISTORY = 50