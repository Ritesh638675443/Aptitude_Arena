import streamlit as st
import os
from datetime import date
from utils import load_questions, clean_question, clean_text, get_rank, fix_math

st.set_page_config(
    page_title="Aptitude Arena",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state defaults ──────────────────────────────────────────────────

def init_session():
    defaults = {
        "xp": 0,
        "tests_taken": 0,
        "questions_solved": 0,
        "correct_answers": 0,
        "streak": 0,
        "last_active_date": str(date.today()),
        "topic_stats": {},
        "achievements": [],
        "bookmarks": [],
        "dark_mode": True,
        "daily_done": False,
        "daily_date": "",
        "recent_tests": [],
        "speed_best": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Streak logic ─────────────────────────────────────────────────────────────
today_str = str(date.today())
if st.session_state["last_active_date"] != today_str:
    from datetime import datetime
    last = datetime.fromisoformat(st.session_state["last_active_date"])
    diff = (datetime.today() - last).days
    if diff == 1:
        st.session_state["streak"] += 1
    elif diff > 1:
        st.session_state["streak"] = 0
    st.session_state["last_active_date"] = today_str

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    pages = {
        "🏠 Dashboard":        "_pages/Dashboard.py",
        "📚 Practice Mode":    "_pages/Practice.py",
        "📝 Mock Tests":       "_pages/Mock_Test.py",
        "🏢 Company Tests":    "_pages/Company_Tests.py",
        "🔥 Daily Challenge":  "_pages/Daily_Challenge.py",
        "⚡ Speed Challenge":  "_pages/Speed_Challenge.py",
        "📊 Analytics":        "_pages/Analytics.py",
        "🏆 Achievements":     "_pages/Achievements.py",
        "⚙️ Settings":         "_pages/Settings.py",
    }

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "🏠 Dashboard"

    for label in pages:
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state["current_page"] == label else "secondary"):
            st.session_state["current_page"] = label
            for key in ["practice_idx", "practice_submitted", "mock_answers",
                        "mock_started", "speed_active"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ── Page routing ──────────────────────────────────────────────────────────────
page = st.session_state["current_page"]
_dir = os.path.dirname(os.path.abspath(__file__))

_g = globals()

if page == "🏠 Dashboard":
    exec(open(os.path.join(_dir, "_pages", "Dashboard.py")).read(), _g)
elif page == "📚 Practice Mode":
    exec(open(os.path.join(_dir, "_pages", "Practice.py")).read(), _g)
elif page == "📝 Mock Tests":
    exec(open(os.path.join(_dir, "_pages", "Mock_Test.py")).read(), _g)
elif page == "🏢 Company Tests":
    exec(open(os.path.join(_dir, "_pages", "Company_Tests.py")).read(), _g)
elif page == "🔥 Daily Challenge":
    exec(open(os.path.join(_dir, "_pages", "Daily_Challenge.py")).read(), _g)
elif page == "⚡ Speed Challenge":
    exec(open(os.path.join(_dir, "_pages", "Speed_Challenge.py")).read(), _g)
elif page == "📊 Analytics":
    exec(open(os.path.join(_dir, "_pages", "Analytics.py")).read(), _g)
elif page == "🏆 Achievements":
    exec(open(os.path.join(_dir, "_pages", "Achievements.py")).read(), _g)
elif page == "⚙️ Settings":
    exec(open(os.path.join(_dir, "_pages", "Settings.py")).read(), _g)
