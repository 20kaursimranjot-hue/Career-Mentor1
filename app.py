"""
app.py
------
Streamlit entry-point for the AI Career Mentor & Skill-Gap Agent.

Layout
------
Sidebar  : API key + user profile form
Main     : Two tabs
           Tab 1 – Skill Gap Analysis & 30-Day Roadmap
           Tab 2 – AI Career Coach Chat

Run with:  streamlit run app.py
"""

import streamlit as st

from agent.mentor_agent import run_gap_analysis, run_chat_turn

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Mentor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session-state initialisation ───────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history: list = []

if "roadmap_result" not in st.session_state:
    st.session_state.roadmap_result: str = ""

if "profile_ready" not in st.session_state:
    st.session_state.profile_ready: bool = False


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🎯 Career Mentor AI")
    st.caption("Powered by Groq · Qwen3 32B")
    st.divider()

    # ── API Key ────────────────────────────────────────────────────────────────
    st.subheader("🔑 Groq API Key")
    api_key = st.text_input(
        label="Enter your Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Your key is used only for this session and is never stored or logged.",
    )

    st.divider()

    # ── User Profile Form ──────────────────────────────────────────────────────
    st.subheader("👤 Your Career Profile")

    target_role = st.text_input(
        label="🎯 Target Job Role",
        placeholder="e.g. Senior Data Scientist, Cloud DevOps Engineer",
        help="The role you are working towards.",
    )

    experience_level = st.selectbox(
        label="📊 Current Experience Level",
        options=["Beginner", "Intermediate", "Advanced"],
        index=0,
    )

    current_skills = st.text_area(
        label="🛠️ Current Core Skills",
        placeholder="e.g. Python, SQL, Excel, Basic ML",
        height=100,
        help="Comma-separated list of your strongest skills right now.",
    )

    weekly_hours = st.select_slider(
        label="⏱️ Weekly Time Commitment",
        options=[
            "2 hours/week",
            "5 hours/week",
            "8 hours/week",
            "10 hours/week",
            "15 hours/week",
            "20 hours/week",
            "25+ hours/week",
        ],
        value="8 hours/week",
    )

    st.divider()

    # ── Save profile ───────────────────────────────────────────────────────────
    if st.button("💾 Save Profile", use_container_width=True, type="primary"):
        missing = []
        if not api_key.strip():
            missing.append("Groq API Key")
        if not target_role.strip():
            missing.append("Target Job Role")
        if not current_skills.strip():
            missing.append("Current Core Skills")

        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            st.session_state.profile_ready = True
            st.session_state.chat_history = []          # reset chat on profile change
            st.session_state.roadmap_result = ""        # reset roadmap on profile change
            st.success("Profile saved! Head to the tabs →")

    # ── Profile status badge ───────────────────────────────────────────────────
    if st.session_state.profile_ready:
        st.info(
            f"**Active Profile**\n\n"
            f"🎯 {target_role}\n\n"
            f"📊 {experience_level}  ·  ⏱️ {weekly_hours}",
            icon="✅",
        )

    st.divider()
    st.caption(
        "⚠️ This tool provides educational career guidance only. "
        "No employment outcomes are guaranteed."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
st.title("🚀 AI Career Mentor & Skill-Gap Agent")
st.caption(
    "An Agentic AI application that analyses your skill gaps, "
    "builds a personalised learning roadmap, and coaches you towards your target role."
)
st.divider()

# Guard: require profile before showing main UI
if not st.session_state.profile_ready:
    st.info(
        "👈  **Get started:** Fill in your profile in the sidebar and click **Save Profile**.",
        icon="ℹ️",
    )
    st.stop()

# Rebuild profile dict from sidebar values
user_profile = {
    "target_role":        target_role,
    "experience_level":   experience_level,
    "current_skills":     current_skills,
    "weekly_hours":       weekly_hours,
}

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_roadmap, tab_chat = st.tabs(
    ["📋 Skill Gap Analysis & 30-Day Roadmap", "💬 AI Career Coach Chat"]
)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — Skill Gap Analysis & 30-Day Roadmap
# ══════════════════════════════════════════════════════════════════════════════
with tab_roadmap:
    st.header("📋 Skill Gap Analysis & 30-Day Roadmap")
    st.markdown(
        "The AI agent will:\n"
        "1. **Observe** your profile and target role requirements\n"
        "2. **Reason** about which skills you have, partially have, or are missing\n"
        "3. **Act** by producing a structured, week-by-week 30-day learning plan"
    )
    st.divider()

    col_btn, col_hint = st.columns([2, 5])
    with col_btn:
        generate_btn = st.button(
            "🔍 Analyse & Generate Roadmap",
            type="primary",
            use_container_width=True,
        )
    with col_hint:
        st.caption(
            "⏳ This may take 15–30 seconds — the agent reasons step-by-step "
            "before generating your plan."
        )

    if generate_btn:
        with st.spinner("🤖 Agent is analysing your skill profile and building your roadmap…"):
            result = run_gap_analysis(api_key=api_key, user_profile=user_profile)
        st.session_state.roadmap_result = result
        st.success("✅ Analysis complete!")

    if st.session_state.roadmap_result:
        st.divider()
        st.markdown(st.session_state.roadmap_result)

        st.divider()
        st.download_button(
            label="⬇️ Download Roadmap as Markdown",
            data=st.session_state.roadmap_result,
            file_name=f"career_roadmap_{target_role.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=False,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — AI Career Coach Chat
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.header("💬 AI Career Coach Chat")
    st.markdown(
        "Chat with your personal AI Career Coach. You can:\n"
        "- 🎤 **Practice mock interviews** — type *\"Start a mock interview\"*\n"
        "- 📝 **Get resume feedback** — paste a bullet point and type *\"Review this resume bullet\"*\n"
        "- ❓ **Ask career questions** — anything about your target role or learning path"
    )
    st.divider()

    # ── Chat controls ──────────────────────────────────────────────────────────
    col_clear, _ = st.columns([2, 6])
    with col_clear:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # ── Display conversation history ───────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.info(
                "👋 Hello! I'm your AI Career Coach. How can I help you today?\n\n"
                "Try asking: *\"What are the most important skills for a "
                f"{target_role}?\"* or *\"Start a mock interview for me.\"*"
            )
        else:
            for msg in st.session_state.chat_history:
                role  = msg["role"]
                content = msg["content"]
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                elif role == "assistant":
                    with st.chat_message("assistant", avatar="🎯"):
                        st.markdown(content)

    # ── Input box ──────────────────────────────────────────────────────────────
    user_input = st.chat_input(
        placeholder="Ask your career coach anything…  (e.g. 'Start a mock interview')",
    )

    if user_input:
        # Show user message immediately
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # Call agent
        with st.spinner("🤖 Career Coach is thinking…"):
            reply = run_chat_turn(
                api_key      = api_key,
                user_profile = user_profile,
                chat_history = st.session_state.chat_history,
                user_message = user_input,
            )

        # Persist both turns
        st.session_state.chat_history.append({"role": "user",      "content": user_input})
        st.session_state.chat_history.append({"role": "assistant",  "content": reply})

        # Re-render with updated history
        st.rerun()
