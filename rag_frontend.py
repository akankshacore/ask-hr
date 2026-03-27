import streamlit as st
from rag_backend import hr_index, hr_rag_response, check_aws_access

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0A0C10;
    color: #E2E8F0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 900px; margin: auto; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D0F14;
    border-right: 1px solid #1E2330;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

/* ── Title ── */
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #34D399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}
.hero-sub {
    color: #64748B;
    font-size: 0.9rem;
    font-weight: 300;
    margin-bottom: 2rem;
}

/* ── Chat messages ── */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.msg {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-avatar {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.msg-avatar.user { background: #1E3A5F; }
.msg-avatar.bot  { background: #1A2740; border: 1px solid #2D4A6E; }
.msg-bubble {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    line-height: 1.6;
    font-size: 0.92rem;
    max-width: 85%;
}
.msg-bubble.user {
    background: #1A2740;
    border: 1px solid #2D4A6E;
    color: #BAE6FD;
}
.msg-bubble.bot {
    background: #111318;
    border: 1px solid #1E2330;
    color: #CBD5E1;
}
.msg-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
    color: #475569;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #111318 !important;
    border: 1px solid #1E2330 !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #7C3AED) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s, transform 0.1s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Status / alerts ── */
.status-ok {
    background: #052E16; border: 1px solid #166534;
    border-radius: 8px; padding: 0.6rem 1rem;
    color: #4ADE80; font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
}
.status-err {
    background: #1C0A0A; border: 1px solid #7F1D1D;
    border-radius: 8px; padding: 0.6rem 1rem;
    color: #FCA5A5; font-size: 0.82rem;
    font-family: 'JetBrains Mono', monospace;
}
.tip-box {
    background: #0D1B2A; border: 1px solid #1E3A5F;
    border-radius: 10px; padding: 1rem 1.2rem;
    font-size: 0.83rem; color: #7DD3FC; margin-top: 1rem;
}
.tip-box strong { color: #60A5FA; }

/* ── Divider ── */
hr { border-color: #1E2330 !important; margin: 1.5rem 0 !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #60A5FA !important; }

/* ── Source badge ── */
.src-badge {
    display: inline-block;
    background: #0F172A; border: 1px solid #1E3A5F;
    border-radius: 6px; padding: 0.2rem 0.6rem;
    font-size: 0.72rem; color: #60A5FA;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    # AWS Status
    st.markdown("**AWS Connection**")
    if st.button("🔍 Check AWS Access", use_container_width=True):
        ok, msg = check_aws_access()
        if ok:
            st.markdown(f'<div class="status-ok">✅ {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-err">{msg}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Document Source**")
    st.caption("📄 UPL HR Leave Policy (India)")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#334155; line-height:1.6;'>
    <strong style='color:#475569;'>Powered by</strong><br>
    🟠 Amazon Bedrock<br>
    🟣 Claude 3 Haiku<br>
    🔵 Titan Embeddings v2<br>
    ⚡ FAISS Vector Store<br>
    🦜 LangChain
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="tip-box">
    <strong>💡 Fix AccessDenied Error</strong><br><br>
    1. Add payment method in <strong>AWS Billing</strong><br>
    2. Go to <strong>Bedrock → Model Access</strong><br>
    3. Enable <code>Titan Embed v2</code> & <code>Claude 3 Haiku</code><br>
    4. Wait ~2 mins, then retry
    </div>
    """, unsafe_allow_html=True)


# ==============================
# MAIN CONTENT
# ==============================
st.markdown('<div class="hero-title">HR Policy Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Ask anything about the UPL India Leave Policy — powered by RAG + Claude</div>', unsafe_allow_html=True)

# Load index
@st.cache_resource(show_spinner=False)
def load_index():
    return hr_index()

# Init chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "index_loaded" not in st.session_state:
    st.session_state.index_loaded = False

# Load index with status
if not st.session_state.index_loaded:
    with st.spinner("📚 Loading HR policy document and building vector index..."):
        try:
            index = load_index()
            st.session_state.index_loaded = True
        except Exception as e:
            st.error(f"**Failed to load document:** {str(e)}")
            st.stop()
else:
    index = load_index()


# ── Chat history display ──
if st.session_state.chat_history:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"""
            <div class="msg">
                <div class="msg-avatar user">🧑</div>
                <div>
                    <div class="msg-label">You</div>
                    <div class="msg-bubble user">{message}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg">
                <div class="msg-avatar bot">🤖</div>
                <div>
                    <div class="msg-label">HR Assistant</div>
                    <div class="msg-bubble bot">{message}</div>
                    <span class="src-badge">📄 Leave Policy India PDF</span>
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Empty state
    st.markdown("""
    <div style='text-align:center; padding: 3rem 1rem; color:#334155;'>
        <div style='font-size:2.5rem; margin-bottom:1rem;'>📋</div>
        <div style='font-size:1rem; font-weight:600; color:#475569; margin-bottom:0.5rem;'>No questions yet</div>
        <div style='font-size:0.85rem;'>Try asking about leave types, eligibility, or approval processes.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Input ──
col1, col2 = st.columns([5, 1])
with col1:
    user_question = st.text_input(
        label="question",
        placeholder="e.g. How many sick leaves am I entitled to per year?",
        label_visibility="collapsed"
    )
with col2:
    ask_btn = st.button("Ask →", use_container_width=True)

# Suggested questions
st.markdown("""
<div style='display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:0.5rem;'>
    <span style='background:#111318; border:1px solid #1E2330; border-radius:6px; padding:0.3rem 0.7rem; font-size:0.75rem; color:#64748B; cursor:default;'>
        💼 How many casual leaves are allowed?
    </span>
    <span style='background:#111318; border:1px solid #1E2330; border-radius:6px; padding:0.3rem 0.7rem; font-size:0.75rem; color:#64748B; cursor:default;'>
        🤒 What is the sick leave policy?
    </span>
    <span style='background:#111318; border:1px solid #1E2330; border-radius:6px; padding:0.3rem 0.7rem; font-size:0.75rem; color:#64748B; cursor:default;'>
        ✈️ How do I apply for earned leave?
    </span>
</div>
""", unsafe_allow_html=True)


# ── Process question ──
if ask_btn:
    if user_question.strip():
        with st.spinner("Searching policy document and generating answer..."):
            try:
                response = hr_rag_response(index, user_question)
                st.session_state.chat_history.append(("You", user_question))
                st.session_state.chat_history.append(("Bot", response))
                st.rerun()
            except Exception as e:
                err = str(e)
                if "AccessDeniedException" in err or "INVALID_PAYMENT_INSTRUMENT" in err:
                    st.error("""
**AWS Access Denied** — Your Bedrock model access is blocked.

**Steps to fix:**
1. Go to [AWS Billing](https://console.aws.amazon.com/billing) → add a valid payment method
2. Go to [Bedrock Model Access](https://console.aws.amazon.com/bedrock/home#/modelaccess)
3. Enable **Titan Embed Text v2** and **Claude 3 Haiku**
4. Wait 2 minutes, then try again
                    """)
                elif "NoCredentialsError" in err or "credentials" in err.lower():
                    st.error("**AWS credentials not found.** Run `aws configure` in your terminal.")
                else:
                    st.error(f"**Error:** {err}")
    else:
        st.warning("Please type a question first.")