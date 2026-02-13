import io
import os
import re
import time
import json
import random
from datetime import datetime
import streamlit as st
from PyPDF2 import PdfReader
from config import DATA_FILE, VECTORSTORE_DIR
from vectorstore_utils import create_vectorstore, load_vectorstore
from rag_chain import get_rag_chain
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, MODEL_NAME

# Page config
st.set_page_config(
    page_title="Exam Assistant AI Pro", 
    layout="wide", 
    page_icon="🎓", 
    initial_sidebar_state="expanded"
)

# Enhanced CSS with animations
st.markdown(
    """
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
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
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0e1324 0%, #0b0f19 80%); 
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    .page-title { 
        font-size: 42px; 
        font-weight: 800; 
        background: linear-gradient(90deg,#a78bfa,#ff8ae2,#00e5ff); 
        background-size: 200% auto;
        -webkit-background-clip: text; 
        background-clip: text; 
        color: transparent; 
        animation: shimmer 3s linear infinite;
        margin-bottom: 10px;
    }
    
    .feature-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(167,139,250,0.4);
        border-color: rgba(167,139,250,0.6);
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(255,138,226,0.15));
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(167,139,250,0.3);
    }
    
    .msg {
        border-radius: 16px;
        padding: 12px 16px;
        margin: 8px 0;
        line-height: 1.6;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        transition: all 0.3s ease;
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
    
    .stButton>button {
        background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%);
        color: #fff;
        border: 0;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(167,139,250,0.6);
    }
    
    .quiz-option {
        background: rgba(255,255,255,0.05);
        border: 2px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quiz-option:hover {
        border-color: rgba(167,139,250,0.6);
        background: rgba(167,139,250,0.1);
        transform: translateX(5px);
    }
    
    .bookmark-btn {
        background: rgba(255,215,0,0.2);
        border: 1px solid rgba(255,215,0,0.4);
        border-radius: 8px;
        padding: 5px 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .bookmark-btn:hover {
        background: rgba(255,215,0,0.3);
        transform: scale(1.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
def init_session_state():
    defaults = {
        "messages": [],
        "question_count": 0,
        "uploads": [],
        "greeted": False,
        "indexed_files": set(),
        "vectorstore": None,
        "bookmarks": [],
        "quiz_mode": False,
        "quiz_questions": [],
        "quiz_score": 0,
        "study_stats": {"total_time": 0, "questions_asked": 0, "topics_covered": set()},
        "suggested_questions": [],
        "current_document": None,
        "theme": "dark"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Load vectorstore
    if st.session_state.vectorstore is None:
        vs = None
        try:
            if os.path.exists(VECTORSTORE_DIR):
                vs = load_vectorstore()
        except Exception:
            vs = None
        if vs is None and os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                base_text = f.read()
            vs = create_vectorstore(base_text)
        st.session_state.vectorstore = vs

init_session_state()

# Utility functions
def parse_pdf_info(file):
    data = file.read()
    reader = PdfReader(io.BytesIO(data))
    pages = len(reader.pages)
    text = ""
    for page in reader.pages:
        t = page.extract_text() or ""
        text += t + "\n"
    return text.strip(), pages

def detect_marks(q):
    ql = q.lower()
    patterns = [
        r"(\b1\b|\b2\b|\b5\b|\b10\b|\b12\b)\s*mark",
        r"(\b5\b|\b10\b|\b12\b)\s*marks",
        r"\bfor\s*(1|2|5|10|12)\s*marks?\b"
    ]
    for pattern in patterns:
        m = re.search(pattern, ql)
        if m:
            return int(m.group(1))
    return None

def format_question(q):
    mk = detect_marks(q)
    if mk is None:
        return q
    guide = {
        1: "Provide a one-line definition suitable for 1 mark.",
        2: "Provide 2–3 concise bullet points suitable for 2 marks.",
        5: "Provide a structured explanation with key points suitable for 5 marks.",
        10: "Provide a detailed, structured explanation suitable for 10 marks.",
        12: "Provide a comprehensive, well-structured explanation suitable for 12 marks."
    }[mk]
    return f"{q}\n\nMarks: {mk}\n{guide}"

def generate_quiz_questions(vectorstore, num_questions=5):
    """Generate quiz questions from the syllabus"""
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.7)
    
    prompt = f"""Based on the syllabus content, generate {num_questions} multiple-choice questions.
    Format each question as:
    Q: [question]
    A) [option]
    B) [option]
    C) [option]
    D) [option]
    Correct: [A/B/C/D]
    
    Make questions challenging and exam-oriented."""
    
    try:
        response = llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        # Parse questions
        questions = []
        current_q = {}
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    questions.append(current_q)
                current_q = {'question': line[2:].strip(), 'options': []}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_q['options'].append(line)
            elif line.startswith('Correct:'):
                current_q['correct'] = line.split(':')[1].strip()
        if current_q:
            questions.append(current_q)
        return questions[:num_questions]
    except:
        return []

def export_chat_history(format_type="txt"):
    """Export chat history to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history_{timestamp}.{format_type}"
    
    content = f"Exam Assistant AI - Chat History\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "="*50 + "\n\n"
    
    for msg in st.session_state.messages:
        role = msg["role"].upper()
        content += f"{role}:\n{msg['content']}\n\n"
        content += "-"*50 + "\n\n"
    
    return content, filename

def suggest_questions(vectorstore):
    """Generate suggested questions based on syllabus"""
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.6)
    
    prompt = """Based on the syllabus, suggest 5 important exam questions that students should practice.
    List them as:
    1. [question]
    2. [question]
    etc."""
    
    try:
        response = llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        questions = [line.strip() for line in content.split('\n') if line.strip() and line[0].isdigit()]
        return questions[:5]
    except:
        return []

# Sidebar
with st.sidebar:
    st.markdown('<h2 style="color: #a78bfa;">⚙️ Control Panel</h2>', unsafe_allow_html=True)
    
    # Mode selection
    mode = st.selectbox(
        "🎯 Select Mode",
        ["💬 Chat Mode", "📝 Quiz Mode", "📊 Analytics", "🔖 Bookmarks", "📚 Documents"]
    )
    
    st.markdown("---")
    
    # Stats
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.metric("Questions Asked", st.session_state.question_count)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.metric("Documents", len(st.session_state.uploads))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="stat-box">', unsafe_allow_html=True)
    st.metric("Bookmarks", len(st.session_state.bookmarks))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()
    
    if st.button("💾 Export Chat"):
        content, filename = export_chat_history("txt")
        st.download_button(
            label="📥 Download TXT",
            data=content,
            file_name=filename,
            mime="text/plain"
        )
    
    if st.button("🔄 Generate Suggestions"):
        if st.session_state.vectorstore:
            with st.spinner("Generating..."):
                st.session_state.suggested_questions = suggest_questions(st.session_state.vectorstore)
            st.success("✅ Suggestions ready!")

# Main content
st.markdown('<div class="page-title">🎓 Exam Assistant AI Pro</div>', unsafe_allow_html=True)
st.caption("Advanced AI-powered exam preparation assistant with quiz mode, analytics, and more")

if mode == "💬 Chat Mode":
    # File uploader
    uploaded_file = st.file_uploader("📄 Upload Syllabus PDF", type=["pdf"])
    
    if uploaded_file and uploaded_file.name not in st.session_state.indexed_files:
        with st.spinner("🔄 Processing PDF..."):
            text, pages = parse_pdf_info(uploaded_file)
            st.session_state.vectorstore = create_vectorstore(text)
            st.session_state.uploads.append({
                "name": uploaded_file.name,
                "size": uploaded_file.size,
                "pages": pages,
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.session_state.indexed_files.add(uploaded_file.name)
            st.success(f"✅ Indexed {uploaded_file.name} ({pages} pages)")
    
    # Suggested questions
    if st.session_state.suggested_questions:
        st.markdown("### 💡 Suggested Questions")
        cols = st.columns(2)
        for idx, q in enumerate(st.session_state.suggested_questions[:4]):
            with cols[idx % 2]:
                if st.button(q, key=f"suggest_{idx}"):
                    st.session_state.messages.append({"role": "user", "content": q})
                    st.rerun()
    
    # Chat messages
    for idx, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        content = msg["content"]
        avatar = "🧑‍🎓" if role == "user" else "🤖"
        typ = "user-msg" if role == "user" else "bot-msg"
        
        col1, col2 = st.columns([0.95, 0.05])
        with col1:
            st.markdown(
                f'<div class="msg {typ}"><strong>{avatar} {role.title()}</strong><br>{content}</div>',
                unsafe_allow_html=True
            )
        with col2:
            if role == "assistant" and st.button("⭐", key=f"bookmark_{idx}"):
                st.session_state.bookmarks.append({"question": st.session_state.messages[idx-1]["content"], "answer": content})
                st.toast("Bookmarked!")
    
    # Chat input
    prompt = st.chat_input("💬 Ask your question...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.question_count += 1
        
        with st.spinner("🤔 Thinking..."):
            if st.session_state.vectorstore:
                chain = get_rag_chain(st.session_state.vectorstore)
                q = format_question(prompt)
                try:
                    answer = chain.invoke(q)
                except:
                    answer = "Error generating answer."
            else:
                llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME)
                answer = llm.invoke(prompt).content
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

elif mode == "📝 Quiz Mode":
    st.markdown("### 📝 Quiz Mode")
    st.write("Test your knowledge with AI-generated questions!")
    
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions", 3, 10, 5)
    with col2:
        if st.button("🎲 Generate Quiz"):
            if st.session_state.vectorstore:
                with st.spinner("Generating quiz..."):
                    st.session_state.quiz_questions = generate_quiz_questions(st.session_state.vectorstore, num_questions)
                    st.session_state.quiz_mode = True
                    st.session_state.quiz_score = 0
                st.success("Quiz ready!")
            else:
                st.error("Please upload a syllabus first!")
    
    if st.session_state.quiz_questions:
        for idx, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**Question {idx+1}:** {q.get('question', 'N/A')}")
            for opt in q.get('options', []):
                st.markdown(f"<div class='quiz-option'>{opt}</div>", unsafe_allow_html=True)
            st.markdown("---")

elif mode == "📊 Analytics":
    st.markdown("### 📊 Study Analytics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.metric("Total Questions", st.session_state.question_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.metric("Documents Uploaded", len(st.session_state.uploads))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.metric("Bookmarked Answers", len(st.session_state.bookmarks))
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 📈 Activity Overview")
    st.info("Keep studying to unlock more insights!")

elif mode == "🔖 Bookmarks":
    st.markdown("### 🔖 Bookmarked Answers")
    
    if st.session_state.bookmarks:
        for idx, bookmark in enumerate(st.session_state.bookmarks):
            with st.expander(f"📌 {bookmark['question'][:50]}..."):
                st.markdown(f"**Q:** {bookmark['question']}")
                st.markdown(f"**A:** {bookmark['answer']}")
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.bookmarks.pop(idx)
                    st.rerun()
    else:
        st.info("No bookmarks yet. Star answers in chat mode to save them!")

elif mode == "📚 Documents":
    st.markdown("### 📚 Document Manager")
    
    if st.session_state.uploads:
        for doc in st.session_state.uploads:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**📄 {doc['name']}**")
                st.caption(f"Pages: {doc['pages']} | Size: {doc['size']//1024} KB | Uploaded: {doc['uploaded_at']}")
            with col2:
                st.button("📖 View", key=f"view_{doc['name']}")
            with col3:
                st.button("🗑️ Delete", key=f"del_{doc['name']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No documents uploaded yet!")
