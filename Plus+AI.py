import streamlit as st
import os
from groq import Groq

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Plus+AI",
    layout="wide"
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.markdown(
        "<div style='color:#f2f2f2; background:#111; border:1px solid #333; "
        "padding:14px 18px; border-radius:10px; max-width:420px; margin:10vh auto; "
        "text-align:center; font-size:14px;'>GROQ_API_KEY is missing</div>",
        unsafe_allow_html=True
    )
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"  # use a real Groq model

# ---------------- PURE DARK THEME CSS ----------------
def inject_css():
    st.markdown(
        """
        <style>
        /* Global overrides */
        .stApp {
            background: #000000;
            color: #f2f2f2;
        }
        header[data-testid="stHeader"] { background: transparent; }

        /* Hide sidebar completely */
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="collapsedControl"] { display: none; }

        .block-container {
            max-width: 760px;
            padding-top: 2.2rem;
            padding-bottom: 6rem;
        }

        /* Login card */
        .login-wrap { display: flex; justify-content: center; margin-top: 8vh; }
        .login-card {
            width: 100%;
            max-width: 380px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 36px 32px 28px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
            text-align: center;
        }
        .login-title { font-size: 22px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px; color: #f2f2f2; }
        .login-sub { font-size: 13px; color: #888; margin-bottom: 22px; }

        /* Chat header */
        .chat-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 4px 4px 18px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 18px;
        }
        .chat-header .name { font-size: 18px; font-weight: 600; color: #f2f2f2; letter-spacing: 0.3px; }
        .chat-header .status { font-size: 12px; color: #888; }

        /* Message bubbles */
        .msg-row { display: flex; margin: 10px 0; }
        .msg-row.user { justify-content: flex-end; }
        .msg-row.assistant { justify-content: flex-start; }
        .msg-bubble {
            max-width: 78%;
            padding: 10px 14px;
            border-radius: 14px;
            font-size: 15px;
            line-height: 1.55;
            word-wrap: break-word;
            border: 1px solid transparent;
        }
        .msg-bubble.user {
            background: #1c1c1e;
            color: #f2f2f2;
            border-color: #9bb7d4;
        }
        .msg-bubble.assistant {
            background: #f2f2f2;
            color: #111;
            border-color: rgba(255,255,255,0.1);
        }
        .msg-label {
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Empty state */
        .empty-state { text-align: center; color: #888; margin-top: 16vh; font-size: 14px; }
        .empty-state .big { font-size: 17px; color: #f2f2f2; margin-bottom: 6px; font-weight: 500; }
        .empty-state .hint { font-size: 12px; margin-top: 14px; color: #888; opacity: 0.8; }

        /* Buttons */
        .stButton button {
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.03);
            color: #f2f2f2;
        }
        .stButton button:hover {
            border-color: #9bb7d4;
        }

        /* Inputs */
        textarea, input {
            color: #f2f2f2 !important;
        }

        /* ERADICATE RED and default grey bars */
        div[data-testid="stAlert"] {
            background-color: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: #f2f2f2 !important;
        }
        div[data-testid="stAlert"] * {
            color: #f2f2f2 !important;
        }
        div[data-testid="stAlertContentError"],
        div[data-testid="stAlertContainer"] {
            background-color: transparent !important;
        }
        div[data-testid="stAlert"] svg {
            fill: #9bb7d4 !important;
        }

        /* Remove grey backdrop behind chat input */
        div[data-testid="stBottomBlockContainer"],
        div[data-testid="stBottom"],
        div[data-testid="stChatInputContainer"] {
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border-top: none !important;
        }
        div[data-testid="stBottomBlockContainer"] *,
        div[data-testid="stBottom"] * {
            background-color: transparent !important;
        }

        /* Chat input styling */
        div[data-testid="stChatInput"] {
            background-color: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 14px !important;
        }
        div[data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            color: #f2f2f2 !important;
        }
        div[data-testid="stChatInput"] textarea::placeholder {
            color: #888 !important;
        }
        div[data-testid="stChatInput"] button svg {
            fill: #9bb7d4 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_css()

# ---------------- STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "last_processed_input" not in st.session_state:
    st.session_state.last_processed_input = None   # ← fix infinite reruns

# ---------------- LOGIN ----------------
if not st.session_state.current_user:
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">Plus+AI</div>
            <div class="login-sub">Sign in to continue</div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("Username", label_visibility="collapsed", placeholder="Username")
    password = ""

    if username.lower() == "vool":
        password = st.text_input(
            "Password", type="password",
            label_visibility="collapsed", placeholder="Password"
        )

    login_clicked = st.button("Sign in", use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    if login_clicked:
        if not username.strip():
            st.warning("Enter a username")
            st.stop()
        if username.lower() == "vool" and password != "8712":
            st.warning("Incorrect password")
            st.stop()

        st.session_state.current_user = username

        if username not in st.session_state.users:
            st.session_state.users[username] = {
                "messages": [],
                "system_prompt": (
                    f"You are Plus+, a personal AI assistant. "
                    f"You are speaking directly to {username}. "
                    "Never refer to the user in the third person. "
                    "Be clear, calm, and intelligent."
                )
            }
        st.rerun()
    st.stop()

user = st.session_state.users[st.session_state.current_user]

# ---------------- CHAT HEADER ----------------
st.markdown(
    """
    <div class="chat-header">
        <div class="name">Plus+</div>
        <div class="status">Online</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- CHAT HISTORY ----------------
if not user["messages"]:
    st.markdown(
        """
        <div class="empty-state">
            <div class="big">Start a conversation</div>
            Ask anything — Plus+ is listening.
            <div class="hint">
                Tip: type <code>/clear</code> to wipe this conversation, <code>/logout</code> to sign out.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    rows_html = []
    for m in user["messages"]:
        role = "user" if m["role"] == "user" else "assistant"
        label = "You" if role == "user" else "Plus+"
        safe_content = (
            m["content"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        rows_html.append(
            f"""<div class="msg-row {role}">
                <div>
                    <div class="msg-label">{label}</div>
                    <div class="msg-bubble {role}">{safe_content}</div>
                </div>
            </div>"""
        )
    st.markdown("".join(rows_html), unsafe_allow_html=True)

# ---------------- COMMAND HANDLING ----------------
def handle_command(text: str) -> bool:
    stripped = text.strip()
    lower = stripped.lower()

    if lower == "/clear":
        user["messages"] = []
        st.session_state.last_processed_input = None   # allow next message
        st.rerun()
        return True

    if lower == "/logout":
        st.session_state.current_user = None
        st.session_state.last_processed_input = None
        st.rerun()
        return True

    return False

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("Message Plus+..."):
    # Guard against duplicate processing after reruns
    if prompt == st.session_state.last_processed_input:
        st.stop()
    st.session_state.last_processed_input = prompt

    if not handle_command(prompt):
        user["messages"].append({"role": "user", "content": prompt})

        with st.spinner("Plus+ is thinking..."):
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": user["system_prompt"]}]
                + user["messages"][-10:]
            )
            answer = response.choices[0].message.content

        user["messages"].append({"role": "assistant", "content": answer})
        st.rerun()
