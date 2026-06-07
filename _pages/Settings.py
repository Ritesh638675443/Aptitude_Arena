import streamlit as st
import json
import csv
import io
from datetime import date
from utils import load_questions, clean_question, clean_text, get_rank

st.title("⚙️ Settings")

tab1, tab2, tab3 = st.tabs(["General", "Data & Export", "Reset"])

with tab1:
    st.subheader("Appearance")
    dm = st.toggle("Dark Mode (cosmetic — Streamlit handles theming)",
                   value=st.session_state.get("dark_mode", True))
    st.session_state["dark_mode"] = dm
    st.info("To switch between dark/light mode, use Streamlit's built-in menu (⋮) → Settings → Theme.")

    st.subheader("Account Stats")
    solved  = st.session_state.get("questions_solved", 0)
    correct = st.session_state.get("correct_answers", 0)
    tests   = st.session_state.get("tests_taken", 0)
    xp      = st.session_state.get("xp", 0)
    streak  = st.session_state.get("streak", 0)
    acc     = round(correct / solved * 100, 1) if solved else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Questions Solved",  solved)
    c2.metric("Correct Answers",   correct)
    c3.metric("Overall Accuracy",  f"{acc}%")
    c4, c5, c6 = st.columns(3)
    c4.metric("Tests Taken",       tests)
    c5.metric("XP Points",         xp)
    c6.metric("Streak",            f"{streak} days")

with tab2:
    st.subheader("Export Results")
    ts      = st.session_state.get("topic_stats", {})
    recent  = st.session_state.get("recent_tests", [])
    achs    = st.session_state.get("achievements", [])

    # CSV export
    csv_buf = io.StringIO()
    writer  = csv.writer(csv_buf)
    writer.writerow(["Topic", "Solved", "Correct", "Accuracy %"])
    for topic, s in ts.items():
        acc_t = round(s["correct"]/s["solved"]*100,1) if s["solved"] else 0
        writer.writerow([topic, s["solved"], s["correct"], acc_t])
    csv_data = csv_buf.getvalue()

    st.download_button(
        label="📥 Download Topic Performance (CSV)",
        data=csv_data,
        file_name=f"aptitude_arena_results_{date.today()}.csv",
        mime="text/csv"
    )

    # JSON export (full summary)
    summary = {
        "exported_date":      str(date.today()),
        "questions_solved":   solved,
        "correct_answers":    correct,
        "overall_accuracy":   f"{acc}%",
        "tests_taken":        tests,
        "xp":                 xp,
        "streak":             streak,
        "topic_stats":        ts,
        "recent_tests":       recent,
    }
    st.download_button(
        label="📥 Download Full Report (JSON)",
        data=json.dumps(summary, indent=2),
        file_name=f"aptitude_arena_full_{date.today()}.json",
        mime="application/json"
    )

    # Bookmarks export
    bms = st.session_state.get("bookmarks", [])
    if bms:
        bm_buf = io.StringIO()
        bm_writer = csv.DictWriter(bm_buf, fieldnames=["topic","question"])
        bm_writer.writeheader()
        bm_writer.writerows([{"topic": b["topic"], "question": b["question"]} for b in bms])
        st.download_button(
            label=f"📥 Download Bookmarks ({len(bms)}) (CSV)",
            data=bm_buf.getvalue(),
            file_name=f"bookmarks_{date.today()}.csv",
            mime="text/csv"
        )

with tab3:
    st.subheader("⚠️ Reset Progress")
    st.warning("This will permanently clear all your progress, XP, streak, and test history.")
    confirm = st.checkbox("I understand — reset all my data")
    if confirm and st.button("🗑️ Reset Everything", type="primary"):
        keys_to_reset = [
            "xp", "tests_taken", "questions_solved", "correct_answers",
            "streak", "topic_stats", "achievements", "bookmarks",
            "daily_done", "daily_date", "recent_tests", "speed_best",
        ]
        for k in keys_to_reset:
            if k in st.session_state:
                del st.session_state[k]
        st.success("✅ All progress reset. Refresh the page to start fresh.")
        st.rerun()
