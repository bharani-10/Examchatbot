"""
Exam Assistant AI — Streamlit app with Firebase Authentication + Firestore chat history.
"""

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
from firebase_auth import (
    init_auth_state, restore_session, logout,
    sign_up, sign_in, flush_user_profile,
    create_chat_session, save_message, load_messages, get_user_sessions,
)

# ──────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Exam Assistant AI",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Global CSS (same gradient theme + auth screen styles)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(20px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn { from{opacity:0} to{opacity:1} }
@keyframes pulse  { 0%,100%{opacity:1} 50%{opacity:.5} }
@keyframes slideInRight { from{opacity:0;transform:translateX(30px)} to{opacity:1;transform:translateX(0)} }
@keyframes slideInLeft  { from{opacity:0;transform:translateX(-30px)} to{opacity:1;transform:translateX(0)} }
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
@keyframes shimmer { 0%{background-position:-1000px 0} 100%{background-position:1000px 0} }

.main {
    background: linear-gradient(135deg,#0b0f19 0%,#131a2b 40%,#1a143a 100%);
    background-size:200% 200%;
    animation: gradientShift 15s ease infinite;
    color:#eaeaf6;
}
.stApp { background:transparent; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0e1324 0%,#0b0f19 80%);
    border-right:1px solid rgba(255,255,255,0.08);
    animation: fadeIn 0.5s ease-in;
}
[data-testid="stSidebar"] .block-container { padding:16px; }

.sidebar-title {
    font-weight:800; color:#a78bfa; font-size:14px;
    margin:8px 0 10px 0; letter-spacing:.3px;
    animation: fadeInUp 0.6s ease-out;
}
.card {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:14px; padding:12px;
    box-shadow:0 8px 24px rgba(0,0,0,.25); margin-bottom:12px;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeInUp 0.5s ease-out;
}
.card:hover {
    transform:translateY(-2px);
    box-shadow:0 12px 32px rgba(167,139,250,.35);
    border-color:rgba(167,139,250,0.3);
}

/* Auth card */
.auth-card {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(167,139,250,0.25);
    border-radius:20px; padding:36px 32px;
    box-shadow:0 16px 48px rgba(0,0,0,.4);
    max-width:440px; margin:40px auto;
    animation: fadeInUp 0.6s ease-out;
}
.auth-title {
    font-size:26px; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#ff8ae2,#00e5ff);
    -webkit-background-clip:text; background-clip:text; color:transparent;
    text-align:center; margin-bottom:6px;
}
.auth-sub {
    text-align:center; color:#b7b7c6; font-size:14px; margin-bottom:24px;
}
.profile-badge {
    background:rgba(167,139,250,0.12);
    border:1px solid rgba(167,139,250,0.3);
    border-radius:12px; padding:10px 14px;
    margin-bottom:12px; animation: fadeInUp 0.5s ease-out;
}
.profile-name { font-weight:700; color:#c4b5fd; font-size:14px; }
.profile-email { color:#b7b7c6; font-size:12px; }

[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.05);
    border:1px dashed rgba(255,255,255,0.18);
    border-radius:14px; padding:10px; transition:all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color:rgba(167,139,250,0.5);
    background:rgba(167,139,250,0.08);
}
.stat {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:12px; padding:10px 12px; margin-bottom:8px; color:#eaeaf6;
    transition:all 0.3s ease; animation: fadeInUp 0.7s ease-out;
}
.stat:hover {
    background:rgba(167,139,250,0.1);
    border-color:rgba(167,139,250,0.3); transform:scale(1.02);
}
.stButton>button {
    background:linear-gradient(135deg,#6d28d9 0%,#7c3aed 100%);
    color:#fff; border:0; border-radius:10px; padding:8px 12px;
    box-shadow:0 6px 18px rgba(167,139,250,.45);
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1); font-weight:600;
}
.stButton>button:hover {
    background:linear-gradient(135deg,#7c3aed 0%,#8b5cf6 100%);
    transform:translateY(-2px); box-shadow:0 8px 24px rgba(167,139,250,.6);
}
.stButton>button:active { transform:translateY(0); }

.page-title {
    font-size:36px; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#ff8ae2,#00e5ff);
    background-size:200% auto;
    -webkit-background-clip:text; background-clip:text; color:transparent;
    display:inline-flex; align-items:center; gap:10px;
    animation: fadeInUp 0.8s ease-out, shimmer 3s linear infinite;
}
.chat-container { max-width:900px; margin:0 auto; padding:0 12px 24px 12px; }
.msg {
    border-radius:16px; padding:12px 16px; margin:8px 0; line-height:1.6;
    box-shadow:0 8px 20px rgba(0,0,0,0.25);
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeInUp 0.5s ease-out;
}
.msg:hover { transform:translateY(-2px); box-shadow:0 12px 28px rgba(0,0,0,0.35); }
.user-msg {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.12);
    animation: slideInRight 0.5s ease-out;
}
.bot-msg {
    background:rgba(167,139,250,0.08);
    border:1px solid rgba(167,139,250,0.28);
    animation: slideInLeft 0.5s ease-out;
}
.role { font-weight:700; margin-bottom:6px; color:#c4b5fd; }
.avatar { font-size:20px; margin-right:8px; display:inline-block; animation: bounce 2s ease-in-out infinite; }
.stMarkdown a { color:#00e5ff !important; text-decoration:underline; transition:color 0.2s ease; }
.stMarkdown a:hover { color:#33f0ff !important; }
.stChatMessage { background:transparent !important; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 16px 0; animation: fadeIn 0.6s ease-out; }
.chip {
    background:rgba(167,139,250,0.18); border:1px solid rgba(167,139,250,0.35);
    border-radius:999px; padding:8px 12px; box-shadow:0 4px 12px rgba(0,0,0,.25);
    cursor:pointer; display:inline-flex; align-items:center; color:#fff;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.chip:hover {
    border-color:#a78bfa; transform:translateY(-2px) scale(1.05);
    box-shadow:0 6px 16px rgba(167,139,250,.45);
    background:rgba(167,139,250,0.25);
}
.attachments { display:flex; gap:8px; flex-wrap:wrap; margin:6px 0 14px 0; animation: fadeInUp 0.6s ease-out; }
.attachment {
    background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.14);
    border-radius:12px; padding:8px 10px; box-shadow:0 4px 12px rgba(0,0,0,.25);
    display:inline-flex; gap:8px; align-items:center; color:#eaeaf6;
    transition:all 0.3s ease; animation: slideInRight 0.5s ease-out;
}
.attachment:hover { transform:translateY(-2px); border-color:rgba(167,139,250,0.4); background:rgba(167,139,250,0.1); }
.attachment .name { font-weight:600; color:#eaeaf6; }
.attachment .meta { font-size:12px; color:#b7b7c6; }
.input-row { display:flex; gap:10px; align-items:center; margin-top:8px; animation: fadeInUp 0.7s ease-out; }
.input-hint { font-size:12px; color:#b7b7c6; margin-top:4px; }
html { scroll-behavior:smooth; }
.stSpinner > div { border-color:#a78bfa !important; }
[data-testid="stToast"] { animation: slideInRight 0.3s ease-out; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Initialise auth state
# ──────────────────────────────────────────────────────────────────────────────
init_auth_state()

# Try to restore session from persisted refresh token
if not st.session_state.authenticated:
    restore_session()


# ──────────────────────────────────────────────────────────────────────────────
# Auth screens
# ──────────────────────────────────────────────────────────────────────────────

def render_login():
    """Render the Login form."""
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🎓 Exam Assistant AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Sign in to continue</div>', unsafe_allow_html=True)

    email    = st.text_input("Email address", key="login_email",    placeholder="you@example.com")
    password = st.text_input("Password",      key="login_password", type="password", placeholder="Your password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True, key="btn_login"):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner("Signing in…"):
                    result = sign_in(email, password)
                if result["success"]:
                    u = result["user"]
                    st.session_state.authenticated = True
                    st.session_state.user_id        = u["localId"]
                    st.session_state.user_email     = u.get("email", "")
                    st.session_state.user_name      = u.get("displayName") or u.get("email", "User")
                    st.session_state.id_token       = u["idToken"]
                    st.session_state.refresh_token  = u["refreshToken"]
                    # Ensure any pending profile write is flushed
                    flush_user_profile(u["localId"], u["idToken"])
                    st.toast("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error(result["error"])
    with col2:
        if st.button("📝 Sign Up", use_container_width=True, key="btn_goto_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_signup():
    """Render the Sign Up form."""
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🎓 Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Join Exam Assistant AI</div>', unsafe_allow_html=True)

    name     = st.text_input("Full name",     key="signup_name",     placeholder="Your name")
    email    = st.text_input("Email address", key="signup_email",    placeholder="you@example.com")
    password = st.text_input("Password",      key="signup_password", type="password", placeholder="Min. 6 characters")
    confirm  = st.text_input("Confirm password", key="signup_confirm", type="password", placeholder="Re-enter password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Create Account", use_container_width=True, key="btn_signup"):
            if not all([name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with st.spinner("Creating account…"):
                    result = sign_up(email, password, name)
                if result["success"]:
                    u = result["user"]
                    st.session_state.authenticated = True
                    st.session_state.user_id        = u["localId"]
                    st.session_state.user_email     = u.get("email", "")
                    st.session_state.user_name      = name
                    st.session_state.id_token       = u["idToken"]
                    st.session_state.refresh_token  = u["refreshToken"]
                    flush_user_profile(u["localId"], u["idToken"])
                    st.toast("🎉 Account created! Welcome aboard.")
                    st.rerun()
                else:
                    st.error(result["error"])
    with col2:
        if st.button("← Back to Login", use_container_width=True, key="btn_goto_login"):
            st.session_state.auth_page = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Gate: show auth screen if not authenticated
# ──────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    if st.session_state.auth_page == "signup":
        render_signup()
    else:
        render_login()
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# Chatbot session initialisation (runs only when authenticated)
# ──────────────────────────────────────────────────────────────────────────────

def init_chat_state():
    defaults = {
        "messages":      [],
        "question_count": 0,
        "prefill":        None,
        "uploads":        [],
        "greeted":        False,
        "indexed_files":  set(),
        "vectorstore":    None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Load or create a Firestore chat session
    if not st.session_state.get("session_id"):
        uid      = st.session_state.user_id
        id_token = st.session_state.id_token
        sessions = get_user_sessions(uid, id_token)
        if sessions:
            sid = sessions[0]["sessionId"]
            # Restore last session's messages
            stored = load_messages(sid, id_token)
            st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in stored]
            st.session_state.greeted  = True
        else:
            sid = create_chat_session(uid, id_token)
        st.session_state.session_id = sid

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


init_chat_state()


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # User profile badge
    st.markdown(
        f'<div class="profile-badge">'
        f'<div class="profile-name">👤 {st.session_state.user_name}</div>'
        f'<div class="profile-email">{st.session_state.user_email}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Logout
    if st.button("🚪 Logout", use_container_width=True, key="btn_logout"):
        logout()
        st.rerun()

    st.markdown("---")

    # New chat session
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True, key="btn_new_chat"):
        uid      = st.session_state.user_id
        id_token = st.session_state.id_token
        new_sid  = create_chat_session(uid, id_token)
        st.session_state.session_id    = new_sid
        st.session_state.messages      = []
        st.session_state.question_count = 0
        st.session_state.greeted        = False
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear_chat"):
        st.session_state.messages       = []
        st.session_state.question_count = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Session stats
    st.markdown('<div class="sidebar-title">📊 Session Status</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat">Questions asked: {st.session_state.question_count}</div>',
        unsafe_allow_html=True,
    )

    # Previous sessions
    st.markdown('<div class="sidebar-title">🗂️ Previous Chats</div>', unsafe_allow_html=True)
    try:
        sessions = get_user_sessions(st.session_state.user_id, st.session_state.id_token)
        for s in sessions[:5]:
            label = s.get("createdAt", "Session")[:10]
            sid   = s["sessionId"]
            is_active = sid == st.session_state.session_id
            btn_label = f"{'▶ ' if is_active else ''}{label}"
            if st.button(btn_label, key=f"sess_{sid}", use_container_width=True):
                msgs = load_messages(sid, st.session_state.id_token)
                st.session_state.messages    = [{"role": m["role"], "content": m["content"]} for m in msgs]
                st.session_state.session_id  = sid
                st.session_state.greeted     = True
                st.session_state.question_count = sum(1 for m in msgs if m["role"] == "user")
                st.rerun()
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────

def parse_pdf_info(file):
    data   = file.read()
    reader = PdfReader(io.BytesIO(data))
    pages  = len(reader.pages)
    text   = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text.strip(), pages


def detect_marks(q):
    ql = q.lower()
    for pattern in [
        r"(\b1\b|\b2\b|\b10\b|\b12\b)\s*mark",
        r"(\b10\b|\b12\b)\s*marks",
        r"\bfor\s*(1|2|10|12)\s*marks?\b",
    ]:
        m = re.search(pattern, ql)
        if m:
            return int(m.group(1))
    return None


def format_question(q):
    mk = detect_marks(q)
    if mk is None:
        return q
    guide = {
        1:  "Provide a one-line definition suitable for 1 mark.",
        2:  "Provide 2–3 concise bullet points suitable for 2 marks.",
        10: "Provide a structured, detailed explanation suitable for 10 marks.",
        12: "Provide a structured, comprehensive explanation suitable for 12 marks.",
    }.get(mk, "")
    return f"{q}\n\nMarks: {mk}\n{guide}"


def is_smalltalk(text):
    t = text.strip().lower()
    keywords = ["hi", "hii", "hiii", "hello", "hey", "good morning", "good evening", "thanks", "thank you"]
    return any(k in t for k in keywords)


def smalltalk_reply(text):
    t = text.strip().lower()
    if any(k in t for k in ["hi", "hii", "hiii", "hello", "hey"]):
        return "Hii! How can I help you today?"
    if "exam" in t and ("tomorrow" in t or "today" in t or "help me" in t):
        return ("Okay, let's focus! Upload your syllabus or tell me the subject, and I'll guide you with "
                "quick 1–2 mark definitions, and 10–12 mark explanations. What topic do you want to start with?")
    if "thanks" in t or "thank you" in t:
        return "You're welcome! Do you want to practice a few more questions?"
    return None


def chat_llm(text):
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.5)
    q = format_question(text)
    try:
        resp = llm.invoke(q)
        return getattr(resp, "content", str(resp))
    except Exception:
        return "There was an error generating the answer."


def _persist_message(role: str, content: str):
    """Save a message to Firestore if session is active."""
    try:
        save_message(
            st.session_state.session_id,
            role,
            content,
            st.session_state.id_token,
        )
    except Exception:
        pass  # Don't block the UI on Firestore errors


# ──────────────────────────────────────────────────────────────────────────────
# Main chat UI
# ──────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="page-title">🎓 Exam Assistant AI</div>', unsafe_allow_html=True)
st.caption("Chat with your syllabus using RAG and get mark-based responses")

container = st.container()
with container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Attachment badges
    if st.session_state.uploads and not st.session_state.messages:
        st.markdown('<div class="attachments">', unsafe_allow_html=True)
        for u in st.session_state.uploads[-3:]:
            size_kb = int(u["size"] / 1024)
            st.markdown(
                f'<div class="attachment"><span>📄</span>'
                f'<span class="name">{u["name"]}</span>'
                f'<span class="meta">{u["pages"]} pages • {size_kb} KB</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Greeting on first load
    if not st.session_state.messages and not st.session_state.greeted:
        greeting = f"Hi {st.session_state.user_name.split()[0]}! I'm your Exam Assistant. How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.session_state.greeted = True
        _persist_message("assistant", greeting)

    # PDF upload
    st.markdown('<div class="input-row">', unsafe_allow_html=True)
    up_inline = st.file_uploader("Attach syllabus PDF", type=["pdf"], key="uploader")
    st.markdown('</div>', unsafe_allow_html=True)

    if up_inline is not None and up_inline.name not in st.session_state.indexed_files:
        with st.spinner("Processing PDF…"):
            text, pages = parse_pdf_info(up_inline)
            st.session_state.vectorstore = create_vectorstore(text)
            time.sleep(0.2)
        st.session_state.uploads.append({"name": up_inline.name, "size": up_inline.size, "pages": pages})
        st.session_state.indexed_files.add(up_inline.name)
        st.toast(f"Indexed {up_inline.name} ({pages} pages)")

    # Render chat history
    for msg in st.session_state.messages:
        role    = msg["role"]
        content = msg["content"]
        avatar  = "🧑‍🎓" if role == "user" else "🤖"
        typ     = "user-msg" if role == "user" else "bot-msg"
        st.markdown(
            f'<div class="msg {typ}"><div class="role"><span class="avatar">{avatar}</span>'
            f'{role.title()}</div>{content}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Process user prompt
# ──────────────────────────────────────────────────────────────────────────────

def process_prompt(p: str):
    st.session_state.messages.append({"role": "user", "content": p})
    st.session_state.question_count += 1
    _persist_message("user", p)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="msg user-msg"><div class="role"><span class="avatar">🧑‍🎓</span>User</div>{p}</div>',
        unsafe_allow_html=True,
    )

    if is_smalltalk(p):
        ans = smalltalk_reply(p) or chat_llm(p)
    elif not st.session_state.vectorstore:
        with st.spinner("Thinking…"):
            ans = chat_llm(p)
            time.sleep(0.2)
    else:
        with st.spinner("Thinking…"):
            chain = get_rag_chain(st.session_state.vectorstore)
            q = format_question(p)
            try:
                ans = chain.invoke(q)
            except Exception:
                ans = "There was an error generating the answer."
            time.sleep(0.2)

    st.session_state.messages.append({"role": "assistant", "content": ans})
    _persist_message("assistant", ans)

    st.markdown(
        f'<div class="msg bot-msg"><div class="role"><span class="avatar">🤖</span>Assistant</div>{ans}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


prompt = st.chat_input("Ask any question")

if prompt:
    process_prompt(prompt)
elif st.session_state.prefill:
    process_prompt(st.session_state.prefill)
    st.session_state.prefill = None
