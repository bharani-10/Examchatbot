import io
import os
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
from config import DATA_FILE, VECTORSTORE_DIR
from vectorstore_utils import create_vectorstore, load_vectorstore
from rag_chain import get_rag_chain
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, MODEL_NAME

st.set_page_config(page_title="Exam Assistant AI", layout="wide", page_icon="🎓", initial_sidebar_state="expanded")

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
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
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
    
    .stApp {
        background: transparent;
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0e1324 0%, #0b0f19 80%); 
        border-right: 1px solid rgba(255,255,255,0.08);
        animation: fadeIn 0.5s ease-in;
    }
    
    [data-testid="stSidebar"] .block-container { padding: 16px; }
    
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
    
    [data-testid="stFileUploader"] { 
        background: rgba(255,255,255,0.05); 
        border: 1px dashed rgba(255,255,255,0.18); 
        border-radius: 14px; 
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(167,139,250,0.5);
        background: rgba(167,139,250,0.08);
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
    
    .stButton>button:active {
        transform: translateY(0);
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
    
    .stMarkdown a { 
        color: #00e5ff !important; 
        text-decoration: underline;
        transition: color 0.2s ease;
    }
    
    .stMarkdown a:hover {
        color: #33f0ff !important;
    }
    
    .stChatMessage {
        background: transparent !important;
    }
    
    .chips { 
        display:flex; 
        gap:8px; 
        flex-wrap:wrap; 
        margin: 8px 0 16px 0;
        animation: fadeIn 0.6s ease-out;
    }
    
    .chip { 
        background:rgba(167,139,250,0.18); 
        border:1px solid rgba(167,139,250,0.35); 
        border-radius:999px; 
        padding:8px 12px; 
        box-shadow:0 4px 12px rgba(0,0,0,.25); 
        cursor:pointer; 
        display:inline-flex; 
        align-items:center; 
        color:#fff;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chip:hover { 
        border-color:#a78bfa; 
        transform: translateY(-2px) scale(1.05);
        box-shadow:0 6px 16px rgba(167,139,250,.45);
        background:rgba(167,139,250,0.25);
    }
    
    .attachments { 
        display:flex; 
        gap:8px; 
        flex-wrap:wrap; 
        margin: 6px 0 14px 0;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .attachment { 
        background:rgba(255,255,255,0.06); 
        border:1px solid rgba(255,255,255,0.14); 
        border-radius:12px; 
        padding:8px 10px; 
        box-shadow:0 4px 12px rgba(0,0,0,.25); 
        display:inline-flex; 
        gap:8px; 
        align-items:center; 
        color:#eaeaf6;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
    }
    
    .attachment:hover {
        transform: translateY(-2px);
        border-color: rgba(167,139,250,0.4);
        background:rgba(167,139,250,0.1);
    }
    
    .attachment .name { 
        font-weight:600; 
        color:#eaeaf6; 
    }
    
    .attachment .meta { 
        font-size:12px; 
        color:#b7b7c6; 
    }
    
    .input-row { 
        display:flex; 
        gap:10px; 
        align-items:center; 
        margin-top:8px;
        animation: fadeInUp 0.7s ease-out;
    }
    
    .input-hint { 
        font-size:12px; 
        color:#b7b7c6; 
        margin-top:4px; 
    }
    
    .typing-indicator {
        display: inline-flex;
        gap: 4px;
        padding: 8px 12px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #a78bfa;
        animation: pulse 1.4s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Smooth scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #a78bfa !important;
    }
    
    /* Toast notifications */
    [data-testid="stToast"] {
        animation: slideInRight 0.3s ease-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    m = re.search(r"(\b1\b|\b2\b|\b10\b|\b12\b)\s*mark", ql)
    if m:
        return int(m.group(1))
    m2 = re.search(r"(\b10\b|\b12\b)\s*marks", ql)
    if m2:
        return int(m2.group(1))
    m3 = re.search(r"\bfor\s*(1|2|10|12)\s*marks?\b", ql)
    if m3:
        return int(m3.group(1))
    return None

def format_question(q):
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "prefill" not in st.session_state:
    st.session_state.prefill = None
if "uploads" not in st.session_state:
    st.session_state.uploads = []
if "greeted" not in st.session_state:
    st.session_state.greeted = False
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()
if "vectorstore" not in st.session_state:
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

with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 Session Stats</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat">Questions asked: {st.session_state.question_count}</div>', unsafe_allow_html=True)

st.markdown('<div class="page-title">🎓 Exam Assistant AI</div>', unsafe_allow_html=True)
st.caption("Chat with your syllabus using RAG and get mark-based responses")

container = st.container()
with container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if st.session_state.uploads and not st.session_state.messages:
        st.markdown('<div class="attachments">', unsafe_allow_html=True)
        for u in st.session_state.uploads[-3:]:
            size_kb = int(u["size"]/1024)
            st.markdown(
                f'<div class="attachment"><span>📄</span><span class="name">{u["name"]}</span><span class="meta">{u["pages"]} pages • {size_kb} KB</span></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    if not st.session_state.messages and not st.session_state.greeted:
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I’m your Exam Assistant. How can I help you today?"})
        st.session_state.greeted = True
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    up_inline = st.file_uploader("Attach syllabus PDF", type=["pdf"], key="uploader")
    st.markdown('</div>', unsafe_allow_html=True)
    if up_inline is not None and up_inline.name not in st.session_state.indexed_files:
        with st.spinner("Processing PDF..."):
            text, pages = parse_pdf_info(up_inline)
            st.session_state.vectorstore = create_vectorstore(text)
            time.sleep(0.2)
        st.session_state.uploads.append({"name": up_inline.name, "size": up_inline.size, "pages": pages})
        st.session_state.indexed_files.add(up_inline.name)
        st.toast(f"Indexed {up_inline.name} ({pages} pages)")
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        avatar = "🧑‍🎓" if role == "user" else "🤖"
        typ = "user-msg" if role == "user" else "bot-msg"
        st.markdown(
            f'<div class="msg {typ}"><div class="role"><span class="avatar">{avatar}</span>{role.title()}</div>{content}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

prompt = st.chat_input("Ask any question")

def process_prompt(p):
    st.session_state.messages.append({"role": "user", "content": p})
    st.session_state.question_count += 1
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="msg user-msg"><div class="role"><span class="avatar">🧑‍🎓</span>User</div>{p}</div>',
        unsafe_allow_html=True,
    )
    def is_smalltalk(text):
        t = text.strip().lower()
        keywords = ["hi", "hii", "hiii", "hello", "hey", "good morning", "good evening", "thanks", "thank you"]
        return any(k in t for k in keywords)
    def smalltalk_template(text):
        t = text.strip().lower()
        if any(k in t for k in ["hi", "hii", "hiii", "hello", "hey"]):
            return "Hii! How can I help you today?"
        if "exam" in t and ("tomorrow" in t or "today" in t or "help me" in t):
            return "Okay, let’s focus! Upload your syllabus or tell me the subject, and I’ll guide you with quick 1–2 mark definitions, and 10–12 mark explanations. What topic do you want to start with?"
        if "thanks" in t or "thank you" in t:
            return "You’re welcome! Do you want to practice a few more questions?"
        return None
    def chat_llm(text):
        llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.5)
        q = format_question(text)
        try:
            resp = llm.invoke(q)
            return getattr(resp, "content", str(resp))
        except Exception:
            return "There was an error generating the answer."
    if is_smalltalk(p):
        ans = smalltalk_template(p) or chat_llm(p)
    elif not st.session_state.vectorstore:
        with st.spinner("Thinking..."):
            ans = chat_llm(p)
            time.sleep(0.2)
    else:
        with st.spinner("Thinking..."):
            chain = get_rag_chain(st.session_state.vectorstore)
            q = format_question(p)
            try:
                ans = chain.invoke(q)
            except Exception:
                ans = "There was an error generating the answer."
            time.sleep(0.2)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.markdown(
        f'<div class="msg bot-msg"><div class="role"><span class="avatar">🤖</span>Assistant</div>{ans}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

if prompt:
    process_prompt(prompt)
elif st.session_state.prefill:
    process_prompt(st.session_state.prefill)
    st.session_state.prefill = None
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.question_count += 1
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="msg user-msg"><div class="role"><span class="avatar">👤</span>User</div>{prompt}</div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.vectorstore:
        st.markdown(
            f'<div class="msg bot-msg"><div class="role"><span class="avatar">🤖</span>Assistant</div>Upload a syllabus PDF or ensure a data file is available.</div>',
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("Thinking..."):
            chain = get_rag_chain(st.session_state.vectorstore)
            q = format_question(prompt)
            try:
                ans = chain.invoke(q)
            except Exception as e:
                ans = "There was an error generating the answer."
            time.sleep(0.2)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.markdown(
            f'<div class="msg bot-msg"><div class="role"><span class="avatar">🤖</span>Assistant</div>{ans}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
