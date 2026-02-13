import os
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
VECTORSTORE_DIR = "vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Get embeddings model with caching"""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def create_vectorstore(text):
    """Create a new vectorstore from text content"""
    try:
        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(text)
        
        if not chunks:
            raise ValueError("No text chunks created")
        
        # Create embeddings
        embeddings = get_embeddings()
        
        # Create vectorstore
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Save vectorstore
        if not os.path.exists(VECTORSTORE_DIR):
            os.makedirs(VECTORSTORE_DIR)
        vectorstore.save_local(VECTORSTORE_DIR)
        
        return vectorstore
        
    except Exception as e:
        st.error(f"Error creating vectorstore: {str(e)}")
        return None

def load_vectorstore():
    """Load existing vectorstore"""
    try:
        if not os.path.exists(VECTORSTORE_DIR):
            return None
            
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(
            VECTORSTORE_DIR, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        return vectorstore
        
    except Exception as e:
        st.error(f"Error loading vectorstore: {str(e)}")
        return None
    if not os.path.exists(VECTORSTORE_DIR):
        os.makedirs(VECTORSTORE_DIR)
    
    vectorstore.save_local(VECTORSTORE_DIR)
    
    return vectorstore


def load_vectorstore():
    """
    Load existing vectorstore from disk
    """
    if not os.path.exists(VECTORSTORE_DIR):
        raise FileNotFoundError(f"Vectorstore directory '{VECTORSTORE_DIR}' not found")
    
    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Load vectorstore
    vectorstore = FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    return vectorstore
