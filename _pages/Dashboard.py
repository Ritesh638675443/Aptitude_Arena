import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_questions, clean_question, clean_text, get_rank
import pandas as pd

# load_questions and session already initialised by app.py when exec'd
data = load_questions()

st.markdown("""
<div style="margin-bottom: 0.5rem;">
    <h1 style="margin-bottom: 0.1rem;">🏠 Welcome to Aptitude Arena</h1>
    <p style="font-size: 1.15rem; font-weight: 600; color: #2563EB; margin: 0;">
        Placement &amp; Career Support
    </p>
    <p style="font-size: 1rem; color: #64748b; margin: 0;">
        Department of Industrial Engineering &nbsp;|&nbsp; Anna University
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Top metrics ───────────────────────────────────────────────────────────────
total_topics     = len(data)
total_questions  = sum(len(v) for v in data.values())
tests_taken      = st.session_state["tests_taken"]
qs_solved        = st.session_state["questions_solved"]
correct          = st.session_state["correct_answers"]
accuracy         = round(correct / qs_solved * 100, 1) if qs_solved else 0
streak           = st.session_state["streak"]
xp               = st.session_state["xp"]
rank             = get_rank(xp)

c1, c2, c3, c4 = st.columns(4)
c1.metric("📚 Total Topics",     total_topics)
c2.metric("❓ Total Questions",  f"{total_questions:,}")
c3.metric("📝 Tests Taken",      tests_taken)
c4.metric("✅ Questions Solved", f"{qs_solved:,}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("🎯 Accuracy",         f"{accuracy}%")
c6.metric("🔥 Streak",           f"{streak} days")
c7.metric("⚡ XP Points",        f"{xp:,}")
c8.metric("🏆 Rank",             rank)

# ── Recent tests ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Recent Tests")
recent = st.session_state.get("recent_tests", [])
if recent:
    df_recent = pd.DataFrame(recent[-10:][::-1])
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No tests taken yet. Head over to Mock Tests to get started!")

# ── Search ────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("🔍 Quick Search")
query = st.text_input("Search questions by keyword or topic", placeholder="e.g. HCF, trains, percentage...")
if query and len(query) >= 2:
    results = []
    q_lower = query.lower()
    for topic, qs in data.items():
        if q_lower in topic.lower():
            for q in qs[:5]:
                results.append({"Topic": topic, "Question": q["question"][:120] + "..."})
        else:
            for q in qs:
                if q_lower in q["question"].lower():
                    results.append({"Topic": topic, "Question": q["question"][:120] + "..."})
                if len(results) >= 20:
                    break
        if len(results) >= 20:
            break
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    else:
        st.warning("No questions matched your search.")
