import os
import time
import streamlit as st
import logging
from typing import Optional

# Import our production modules
from config_prod import GROQ_API_KEY, MODEL_NAME, MAX_CHAT_HISTORY
from utils_prod import (
    parse_pdf_info, format_question, validate_file_upload, 
    sanitize_input, is_smalltalk, get_smalltalk_response
)
from vectorstore_utils import create_vectorstore, load_vectorstore
from rag_chain import get_rag_chain
from langchain_groq import ChatGroq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Exam Assistant AI",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/exam-assistant',
        'Report a bug': 'https://github.com/yourusername/exam-assistant/issues',
        'About': "# Exam Assistant AI\nYour intelligent study companion powered by RAG and LLM technology."
    }
)

# Enhanced CSS with production optimizations
st.markdown("""
<style>
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.main { 
    background: linear-gradient(135deg, #0b0f19 0%, #131a2b 40%, #1a143a 100%); 
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    color: #eaeaf6;
}

.stApp { background: transparent; }

[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0e1324 0%, #0b0f19 80%); 
    border-right: 1px solid rgba(255,255,255,0.08);
    animation: fadeInUp 0.5s ease-in;
}

.sidebar-title { 
    font-weight: 800; 
    color: #a78bfa; 
    font-size: 14px; 
    margin: 8px 0 10px 0; 
    letter-spacing: .3px;
    animation: fadeInUp 0.6s ease-out;
}

.card { 
    background: rgba(255,255,255,0.05); 
    border: 1px solid rgba(255,255,255,0.12); 
    border-radius: 14px; 
    padding: 12px; 
    box-shadow: 0 8px 24px rgba(0,0,0,.25); 
    margin-bottom: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(167,139,250,.35);
    border-color: rgba(167,139,250,0.3);
}

.stButton>button { 
    background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%); 
    color: #fff; 
    border: 0; 
    border-radius: 10px; 
    padding: 8px 12px; 
    box-shadow: 0 6px 18px rgba(167,139,250,.45);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-weight: 600;
}

.stButton>button:hover { 
    background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); 
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(167,139,250,.6);
}

.page-title { 
    font-size: 36px; 
    font-weight: 800; 
    background: linear-gradient(90deg,#a78bfa,#ff8ae2,#00e5ff); 
    background-size: 200% auto;
    -webkit-background-clip: text; 
    background-clip: text; 
    color: transparent; 
    display: inline-flex; 
    align-items: center; 
    gap: 10px;
    animation: fadeInUp 0.8s ease-out, shimmer 3s linear infinite;
}

.chat-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 12px 24px 12px;
}

.msg {
    border-radius: 16px;
    padding: 12px 16px;
    margin: 8px 0;
    line-height: 1.6;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
}

.msg:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
}

.user-msg {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    animation: slideInRight 0.5s ease-out;
}

.bot-msg {
    background: rgba(167,139,250,0.08);
    border: 1px solid rgba(167,139,250,0.28);
    animation: slideInLeft 0.5s ease-out;
}

.role {
    font-weight: 700;
    margin-bottom: 6px;
    color: #c4b5fd;
}

.avatar {
    font-size: 20px;
    margin-right: 8px;
    display: inline-block;
    animation: bounce 2s ease-in-out infinite;
}

.stat { 
    background: rgba(255,255,255,0.05); 
    border: 1px solid rgba(255,255,255,0.12); 
    border-radius: 12px; 
    padding: 10px 12px; 
    margin-bottom: 8px; 
    color: #eaeaf6;
    transition: all 0.3s ease;
    animation: fadeInUp 0.7s ease-out;
}

.stat:hover {
    background: rgba(167,139,250,0.1);
    border-color: rgba(167,139,250,0.3);
    transform: scale(1.02);
}

.error-msg {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 12px;
    margin: 8px 0;
    color: #fca5a5;
}

.success-msg {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 12px;
    padding: 12px;
    margin: 8px 0;
    color: #86efac;
}

.warning-msg {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px;
    padding: 12px;
    margin: 8px 0;
    color: #fbbf24;
}

html { scroll-behavior: smooth; }

/* Loading states */
.stSpinner > div { border-color: #a78bfa !important; }
[data-testid="stToast"] { animation: slideInRight 0.3s ease-out; }

/* Responsive design */
@media (max-width: 768px) {
    .page-title { font-size: 28px; }
    .chat-container { padding: 0 8px 16px 8px; }
    .msg { padding: 10px 12px; }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state with error handling
def initialize_session_state():
    """Initialize session state variables safely"""
    defaults = {
        "messages": [],
        "question_count": 0,
        "uploads": [],
        "greeted": False,
        "indexed_files": set(),
        "vectorstore": None,
        "error_count": 0,
        "last_error": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

@st.cache_resource(show_spinner=False)
def initialize_vectorstore():
    """Initialize vectorstore with caching"""
    try:
        vectorstore_dir = "vectorstore"
        data_file = "syllabus.txt"
        
        # Try to load existing vectorstore
        if os.path.exists(vectorstore_dir):
            return load_vectorstore()
        
        # Try to create from base data file
        if os.path.exists(data_file):
            with open(data_file, "r", encoding="utf-8") as f:
                base_text = f.read()
            return create_vectorstore(base_text)
        
        return None
        
    except Exception as e:
        logger.error(f"Error initializing vectorstore: {str(e)}")
        return None

@st.cache_resource(show_spinner=False)
def get_llm():
    """Get LLM instance with caching"""
    try:
        return ChatGroq(
            groq_api_key=GROQ_API_KEY, 
            model_name=MODEL_NAME, 
            temperature=0.5,
            max_retries=3,
            request_timeout=30
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        st.error("🤖 Failed to initialize AI model. Please check your API key.")
        st.stop()

def process_chat_message(prompt: str) -> str:
    """Process chat message with error handling"""
    try:
        # Sanitize input
        prompt = sanitize_input(prompt)
        if not prompt:
            return "Please enter a valid question."
        
        # Handle smalltalk
        if is_smalltalk(prompt):
            response = get_smalltalk_response(prompt)
            if response:
                return response
        
        # Format question for marks
        formatted_question = format_question(prompt)
        
        # Use vectorstore if available
        if st.session_state.vectorstore:
            try:
                chain = get_rag_chain(st.session_state.vectorstore)
                return chain.invoke(formatted_question)
            except Exception as e:
                logger.error(f"RAG chain error: {str(e)}")
                # Fallback to direct LLM
                pass
        
        # Direct LLM response
        llm = get_llm()
        response = llm.invoke(formatted_question)
        return getattr(response, "content", str(response))
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        st.session_state.error_count += 1
        st.session_state.last_error = str(e)
        return "I encountered an error processing your question. Please try again or rephrase your question."

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Initialize vectorstore
    if st.session_state.vectorstore is None:
        st.session_state.vectorstore = initialize_vectorstore()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.question_count = 0
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session stats
        st.markdown('<div class="sidebar-title">📊 Session Stats</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat">Questions asked: {st.session_state.question_count}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat">Files uploaded: {len(st.session_state.uploads)}</div>', unsafe_allow_html=True)
        
        # Error tracking (for debugging)
        if st.session_state.error_count > 0:
            st.markdown(f'<div class="stat">Errors: {st.session_state.error_count}</div>', unsafe_allow_html=True)
        
        # API status
        try:
            if GROQ_API_KEY:
                st.markdown('<div class="stat">🟢 API Connected</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="stat">🔴 API Not Connected</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="stat">🟡 API Status Unknown</div>', unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div class="page-title">🎓 Exam Assistant AI</div>', unsafe_allow_html=True)
    st.caption("Your intelligent study companion powered by RAG and LLM technology")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📄 Upload your syllabus PDF",
        type=["pdf"],
        help="Upload a PDF file (max 10MB) containing your syllabus or study material"
    )
    
    # Process uploaded file
    if uploaded_file and uploaded_file.name not in st.session_state.indexed_files:
        if validate_file_upload(uploaded_file):
            try:
                with st.spinner("🔄 Processing PDF..."):
                    file_bytes = uploaded_file.read()
                    text, pages = parse_pdf_info(file_bytes, uploaded_file.name)
                    
                    # Create vectorstore
                    st.session_state.vectorstore = create_vectorstore(text)
                    
                    # Update session state
                    st.session_state.uploads.append({
                        "name": uploaded_file.name,
                        "size": uploaded_file.size,
                        "pages": pages
                    })
                    st.session_state.indexed_files.add(uploaded_file.name)
                    
                    st.success(f"✅ Successfully processed {uploaded_file.name} ({pages} pages)")
                    
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
                logger.error(f"PDF processing error: {str(e)}")
    
    # Chat interface
    container = st.container()
    with container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Welcome message
        if not st.session_state.messages and not st.session_state.greeted:
            welcome_msg = {
                "role": "assistant", 
                "content": "Hi! 👋 I'm your Exam Assistant AI. Upload your syllabus PDF and ask me any questions to get started!"
            }
            st.session_state.messages.append(welcome_msg)
            st.session_state.greeted = True
        
        # Display chat messages
        for msg in st.session_state.messages[-MAX_CHAT_HISTORY:]:  # Limit chat history
            role = msg["role"]
            content = msg["content"]
            avatar = "🧑‍🎓" if role == "user" else "🤖"
            msg_class = "user-msg" if role == "user" else "bot-msg"
            
            st.markdown(
                f'<div class="msg {msg_class}">'
                f'<div class="role"><span class="avatar">{avatar}</span>{role.title()}</div>'
                f'{content}</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask any question about your syllabus..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.question_count += 1
        
        # Display user message immediately
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="msg user-msg">'
            f'<div class="role"><span class="avatar">🧑‍🎓</span>User</div>'
            f'{prompt}</div>',
            unsafe_allow_html=True
        )
        
        # Generate and display response
        with st.spinner("🤔 Thinking..."):
            response = process_chat_message(prompt)
            time.sleep(0.1)  # Small delay for better UX
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        st.markdown(
            f'<div class="msg bot-msg">'
            f'<div class="role"><span class="avatar">🤖</span>Assistant</div>'
            f'{response}</div>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Auto-rerun to show the new message
        st.rerun()

if __name__ == "__main__":
    main()