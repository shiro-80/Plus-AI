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
MODEL = "openai/gpt-oss-20b"

# ---------------- THEMES ----------------
THEMES = {
    "dark": {
        "bg": "#000000",
        "text": "#f2f2f2",
        "accent": "#9bb7d4",
        "bubble_assistant": "rgba(255,255,255,0.03)",
        "border": "rgba(255,255,255,0.08)",
        "muted": "#888888",
    },
    "light": {
        "bg": "radial-gradient(circle at 50% -10%, #ffffff 0%, #f2f3f5 55%, #e9eaee 100%)",
        "text": "#1a1a1a",
        "accent": "#3b6ea5",
        "bubble_assistant": "rgba(0,0,0,0.02)",
        "border": "rgba(0,0,0,0.10)",
        "muted": "#666666",
    },
    "ocean": {
        "bg": "radial-gradient(circle at 50% -10%, #06222f 0%, #021620 55%, #00090d 100%)",
        "text": "#e6f6ff",
        "accent": "#33c6ff",
        "bubble_assistant": "rgba(51,198,255,0.04)",
        "border": "rgba(51,198,255,0.18)",
        "muted": "#7fb3c9",
    },
    "sunset": {
        "bg": "radial-gradient(circle at 50% -10%, #2b0f1a 0%, #1a0a12 55%, #0a0306 100%)",
        "text": "#ffece0",
        "accent": "#ff8c5a",
        "bubble_assistant": "rgba(255,140,90,0.05)",
        "border": "rgba(255,140,90,0.2)",
        "muted": "#c98f7a",
    },
    "forest": {
        "bg": "radial-gradient(circle at 50% -10%, #0e1f14 0%, #07140c 55%, #020805 100%)",
        "text": "#e8f5e9",
        "accent": "#5fd38a",
        "bubble_assistant": "rgba(95,211,138,0.04)",
        "border": "rgba(95,211,138,0.2)",
        "muted": "#8fb89c",
    },
}
THEME_ORDER = list(THEMES.keys())

# ---------------- STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ---------------- STYLE INJECTION ----------------
def inject_css(theme_name: str):
    t = THEMES.get(theme_name, THEMES["dark"])
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {t['bg']};
            color: {t['text']};
        }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        /* Fully remove sidebar and its toggle arrow */
        section[data-testid="stSidebar"] {{ display: none; }}
        div[data-testid="collapsedControl"] {{ display: none; }}

        .block-container {{
            max-width: 760px;
            padding-top: 2.2rem;
            padding-bottom: 6rem;
        }}

        /* Login card */
        .login-wrap {{ display: flex; justify-content: center; margin-top: 8vh; }}
        .login-card {{
            width: 100%;
            max-width: 380px;
            background: {t['bubble_assistant']};
            border: 1px solid {t['border']};
            border-radius: 18px;
            padding: 36px 32px 28px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
            text-align: center;
        }}
        .login-title {{ font-size: 22px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px; color: {t['text']}; }}
        .login-sub {{ font-size: 13px; color: {t['muted']}; margin-bottom: 22px; }}

        /* Chat header bar */
        .chat-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 4px 4px 18px; border-bottom: 1px solid {t['border']}; margin-bottom: 18px;
        }}
        .chat-header .name {{ font-size: 18px; font-weight: 600; color: {t['text']}; letter-spacing: 0.3px; }}
        .chat-header .status {{ font-size: 12px; color: {t['muted']}; }}
        .theme-pill {{
            font-size: 11px; color: {t['muted']}; border: 1px solid {t['border']};
            padding: 3px 10px; border-radius: 999px;
        }}

        /* Message bubbles — text only, no avatars/icons */
        .msg-row {{ display: flex; margin: 10px 0; }}
        .msg-row.user {{ justify-content: flex-end; }}
        .msg-row.assistant {{ justify-content: flex-start; }}
        .msg-bubble {{
            max-width: 78%;
            padding: 10px 14px;
            border-radius: 14px;
            font-size: 15px;
            line-height: 1.55;
            word-wrap: break-word;
            border: 1px solid {t['border']};
        }}
        .msg-bubble.user {{
            background: {t['bubble_assistant']};
            color: {t['text']};
            border-color: {t['accent']};
        }}
        .msg-bubble.assistant {{
            background: transparent;
            color: {t['text']};
        }}
        .msg-label {{
            font-size: 11px;
            color: {t['muted']};
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Empty state */
        .empty-state {{ text-align: center; color: {t['muted']}; margin-top: 16vh; font-size: 14px; }}
        .empty-state .big {{ font-size: 17px; color: {t['text']}; margin-bottom: 6px; font-weight: 500; }}
        .empty-state .hint {{ font-size: 12px; margin-top: 14px; color: {t['muted']}; opacity: 0.8; }}

        .stButton button {{
            border-radius: 10px; border: 1px solid {t['border']};
            background: {t['bubble_assistant']}; color: {t['text']};
        }}
        .stButton button:hover {{ border-color: {t['accent']}; }}

        textarea, input {{ color: {t['text']} !important; }}

        /* Block red anywhere in the UI: re-skin Streamlit's default error/alert styling */
        div[data-testid="stAlert"] {{
            background-color: {t['bubble_assistant']} !important;
            border: 1px solid {t['border']} !important;
            color: {t['text']} !important;
        }}
        div[data-testid="stAlert"] * {{
            color: {t['text']} !important;
        }}
        div[data-testid="stAlertContentError"],
        div[data-testid="stAlertContainer"] {{
            background-color: {t['bubble_assistant']} !important;
            color: {t['text']} !important;
        }}
        div[data-testid="stAlert"] svg {{
            fill: {t['accent']} !important;
        }}

        /* Remove the default gray backdrop behind the chat input bar */
        div[data-testid="stBottomBlockContainer"],
        div[data-testid="stBottom"],
        div[data-testid="stChatInputContainer"] {{
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            border-top: none !important;
        }}
        div[data-testid="stBottomBlockContainer"] *,
        div[data-testid="stBottom"] * {{
            background-color: transparent !important;
        }}

        /* Restyle the chat input box itself to match the theme */
        div[data-testid="stChatInput"] {{
            background-color: {t['bubble_assistant']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 14px !important;
        }}
        div[data-testid="stChatInput"] textarea {{
            background-color: transparent !important;
            color: {t['text']} !important;
        }}
        div[data-testid="stChatInput"] textarea::placeholder {{
            color: {t['muted']} !important;
        }}
        div[data-testid="stChatInput"] button svg {{
            fill: {t['accent']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_css(st.session_state.theme)

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
            st.markdown(
                "<div style='text-align:center; margin-top:10px; font-size:13px; opacity:0.85;'>Enter a username</div>",
                unsafe_allow_html=True
            )
            st.stop()

        if username.lower() == "vool" and password != "8712":
            st.markdown(
                "<div style='text-align:center; margin-top:10px; font-size:13px; opacity:0.85;'>Incorrect password</div>",
                unsafe_allow_html=True
            )
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
    f"""
    <div class="chat-header">
        <div class="name">Plus+</div>
        <div style="display:flex; align-items:center; gap:10px;">
            <span class="theme-pill">{st.session_state.theme}</span>
            <div class="status">Online</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- CHAT HISTORY ----------------
if not user["messages"]:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="big">Start a conversation</div>
            Ask anything — Plus+ is listening.
            <div class="hint">Tip: type <code>/ChangeTheme</code> to cycle themes, or <code>/ChangeTheme ocean</code> to pick one.<br>
            Themes: {", ".join(THEME_ORDER)}. Type <code>/clear</code> to wipe this conversation, <code>/logout</code> to sign out.</div>
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
    """Returns True if input was a command and was handled (no LLM call needed)."""
    stripped = text.strip()
    lower = stripped.lower()

    if lower == "/clear":
        user["messages"] = []
        st.rerun()
        return True

    if lower == "/logout":
        st.session_state.current_user = None
        st.rerun()
        return True

    if lower.startswith("/changetheme"):
        parts = stripped.split(maxsplit=1)
        if len(parts) == 2 and parts[1].strip().lower() in THEMES:
            st.session_state.theme = parts[1].strip().lower()
        else:
            # No valid theme name given -> cycle to next theme
            current_index = THEME_ORDER.index(st.session_state.theme)
            st.session_state.theme = THEME_ORDER[(current_index + 1) % len(THEME_ORDER)]
        st.rerun()
        return True

    return False

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("Message Plus+... (try /ChangeTheme)"):
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
