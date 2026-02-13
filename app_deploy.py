import io
import os
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
def get_groq_api_key():
    """Get GROQ API key from Streamlit secrets or environment"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                return api_key
        except ImportError:
            pass
        st.error("🔑 GROQ API Key not found! Please add it to Streamlit secrets.")
        st.info("Get your free API key from: https://console.groq.com/")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="Exam Assistant AI",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with animations
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

html { scroll-behavior: smooth; }
.stSpinner > div { border-color: #a78bfa !important; }

@media (max-width: 768px) {
    .page-title { font-size: 28px; }
    .chat-container { padding: 0 8px 16px 8px; }
    .msg { padding: 10px 12px; }
}
</style>
""", unsafe_allow_html=True)

# Utility functions
def parse_pdf_info(file):
    """Parse PDF and extract text"""
    try:
        data = file.read()
        reader = PdfReader(io.BytesIO(data))
        pages = len(reader.pages)
        
        if pages > 50:  # Limit for performance
            st.warning(f"⚠️ Large PDF detected ({pages} pages). Processing first 50 pages only.")
            pages = 50
            
        text = ""
        for i, page in enumerate(reader.pages[:pages]):
            page_text = page.extract_text() or ""
            text += page_text + "\n"
            
        return text.strip(), pages
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return "", 0

def detect_marks(q):
    """Detect marks from question"""
    if not q:
        return None
    ql = q.lower()
    patterns = [
        r"(\b1\b|\b2\b|\b10\b|\b12\b)\s*mark",
        r"(\b10\b|\b12\b)\s*marks",
        r"\bfor\s*(1|2|10|12)\s*marks?\b"
    ]
    for pattern in patterns:
        m = re.search(pattern, ql)
        if m:
            return int(m.group(1))
    return None

def format_question(q):
    """Format question with mark guidance"""
    mk = detect_marks(q)
    if mk is None:
        return q
    guide = {
        1: "Provide a one-line definition suitable for 1 mark.",
        2: "Provide 2–3 concise bullet points suitable for 2 marks.",
        10: "Provide a structured, detailed explanation suitable for 10 marks.",
        12: "Provide a structured, comprehensive explanation suitable for 12 marks."
    }[mk]
    return f"{q}\n\nMarks: {mk}\n{guide}"

@st.cache_resource
def get_llm():
    """Get LLM with caching"""
    try:
        from langchain_groq import ChatGroq
        api_key = get_groq_api_key()
        return ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.5,
            max_retries=2
        )
    except ImportError:
        st.error("LangChain not available. Please install required dependencies.")
        st.stop()
    except Exception as e:
        st.error(f"Error initializing AI model: {str(e)}")
        st.stop()

def chat_llm(text):
    """Generate response using LLM"""
    try:
        llm = get_llm()
        q = format_question(text)
        resp = llm.invoke(q)
        return getattr(resp, "content", str(resp))
    except Exception as e:
        logger.error(f"LLM error: {str(e)}")
        return "I encountered an error. Please try again or rephrase your question."

def is_smalltalk(text):
    """Check if text is smalltalk"""
    if not text:
        return False
    t = text.strip().lower()
    keywords = ["hi", "hii", "hello", "hey", "good morning", "good evening", "thanks", "thank you"]
    return any(k in t for k in keywords)

def smalltalk_template(text):
    """Generate smalltalk response"""
    t = text.strip().lower()
    if any(k in t for k in ["hi", "hii", "hello", "hey"]):
        return "Hi there! 👋 I'm your Exam Assistant. Upload your syllabus PDF and ask me any questions!"
    if "exam" in t and ("tomorrow" in t or "today" in t or "help me" in t):
        return "Let's get you ready! 📚 Upload your syllabus PDF and I'll help you with quick definitions (1-2 marks) and detailed explanations (10-12 marks). What topic shall we start with?"
    if "thanks" in t or "thank you" in t:
        return "You're welcome! 😊 Need help with more questions? I'm here to help you ace your exam!"
    return "Hello! How can I help you with your studies today?"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "uploads" not in st.session_state:
    st.session_state.uploads = []
if "greeted" not in st.session_state:
    st.session_state.greeted = False
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# Sidebar
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-title">📊 Session Stats</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat">Questions asked: {st.session_state.question_count}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat">Files uploaded: {len(st.session_state.uploads)}</div>', unsafe_allow_html=True)
    
    # API status
    try:
        get_groq_api_key()
        st.markdown('<div class="stat">🟢 API Connected</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="stat">🔴 API Not Connected</div>', unsafe_allow_html=True)

# Main content
st.markdown('<div class="page-title">🎓 Exam Assistant AI</div>', unsafe_allow_html=True)
st.caption("Your intelligent study companion with beautiful animations")

# File upload
uploaded_file = st.file_uploader(
    "📄 Upload your syllabus PDF",
    type=["pdf"],
    help="Upload a PDF file containing your syllabus or study material"
)

# Process uploaded file
if uploaded_file and uploaded_file.name not in st.session_state.indexed_files:
    if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
        st.error("📄 File too large! Please upload a PDF smaller than 10MB.")
    else:
        try:
            with st.spinner("🔄 Processing PDF..."):
                text, pages = parse_pdf_info(uploaded_file)
                if text:
                    st.session_state.pdf_content = text
                    st.session_state.uploads.append({
                        "name": uploaded_file.name,
                        "size": uploaded_file.size,
                        "pages": pages
                    })
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.success(f"✅ Successfully processed {uploaded_file.name} ({pages} pages)")
                else:
                    st.error("❌ Could not extract text from PDF")
        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")

# Chat interface
container = st.container()
with container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message
    if not st.session_state.messages and not st.session_state.greeted:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hi! 👋 I'm your Exam Assistant AI. Upload your syllabus PDF and ask me any questions to get started!"
        })
        st.session_state.greeted = True
    
    # Display messages
    for msg in st.session_state.messages[-20:]:  # Limit to last 20 messages
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
    
    # Display user message
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="msg user-msg">'
        f'<div class="role"><span class="avatar">🧑‍🎓</span>User</div>'
        f'{prompt}</div>',
        unsafe_allow_html=True
    )
    
    # Generate response
    with st.spinner("🤔 Thinking..."):
        if is_smalltalk(prompt):
            response = smalltalk_template(prompt)
        else:
            # Enhanced prompt with PDF content if available
            if st.session_state.pdf_content:
                enhanced_prompt = f"Based on the following syllabus content, please answer this question:\n\nSyllabus: {st.session_state.pdf_content[:2000]}...\n\nQuestion: {prompt}"
                response = chat_llm(enhanced_prompt)
            else:
                response = chat_llm(prompt)
        
        time.sleep(0.1)  # Small delay for better UX
    
    # Add and display response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(
        f'<div class="msg bot-msg">'
        f'<div class="role"><span class="avatar">🤖</span>Assistant</div>'
        f'{response}</div>',
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.rerun()