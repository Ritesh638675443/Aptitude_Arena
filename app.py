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

# ── Page routing ──────────────────────────────────────────────
page = st.session_state["current_page"]
_dir = os.path.dirname(os.path.abspath(__file__))
_g = globals()

def load_page(filename):
    with open(
        os.path.join(_dir, "_pages", filename),
        "r",
        encoding="utf-8"
    ) as f:
        exec(f.read(), _g)

if page == "🏠 Dashboard":
    load_page("Dashboard.py")
elif page == "📚 Practice Mode":
    load_page("Practice.py")
elif page == "📝 Mock Tests":
    load_page("Mock_Test.py")
elif page == "🏢 Company Tests":
    load_page("Company_Tests.py")
elif page == "🔥 Daily Challenge":
    load_page("Daily_Challenge.py")
elif page == "⚡ Speed Challenge":
    load_page("Speed_Challenge.py")
elif page == "📊 Analytics":
    load_page("Analytics.py")
elif page == "🏆 Achievements":
    load_page("Achievements.py")
elif page == "⚙️ Settings":
    load_page("Settings.py")
