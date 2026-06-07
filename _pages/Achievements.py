import streamlit as st
from utils import load_questions, clean_question, clean_text, get_rank

st.title("🏆 Achievements")
st.caption("Earn badges by practising and completing challenges.")

solved  = st.session_state.get("questions_solved", 0)
correct = st.session_state.get("correct_answers", 0)
tests   = st.session_state.get("tests_taken", 0)
streak  = st.session_state.get("streak", 0)
xp      = st.session_state.get("xp", 0)
ts      = st.session_state.get("topic_stats", {})
daily_done = st.session_state.get("daily_done", False)
speed_best = st.session_state.get("speed_best", 0)

def badge(emoji, name, desc, unlocked):
    icon   = emoji if unlocked else "🔒"
    status = "✅ Unlocked" if unlocked else "🔒 Locked"
    bg     = "#dcfce7" if unlocked else "#f1f5f9"
    st.markdown(
        f"""<div style='background:{bg};border-radius:12px;padding:16px;margin-bottom:8px;'>
        <span style='font-size:2em'>{icon}</span>&nbsp;
        <strong>{name}</strong>&nbsp;&nbsp;<span style='color:gray;font-size:0.9em'>{status}</span><br>
        <span style='color:#475569'>{desc}</span>
        </div>""",
        unsafe_allow_html=True
    )

BADGES = [
    ("🏅", "First Question",         "Solve your first question",           solved >= 1),
    ("📝", "First Test",             "Complete your first mock test",       tests >= 1),
    ("💯", "Century",                "Solve 100 questions",                 solved >= 100),
    ("🚀", "On a Roll",              "Solve 500 questions",                 solved >= 500),
    ("🌟", "Aptitude Champion",      "Solve 1000 questions",                solved >= 1000),
    ("🎯", "Sharp Shooter",          "Achieve 90%+ accuracy (50+ solved)",  (correct/solved*100 >= 90 if solved >= 50 else False)),
    ("🔥", "3-Day Streak",           "Maintain a 3-day streak",             streak >= 3),
    ("🗓️", "7-Day Streak",           "Maintain a 7-day streak",             streak >= 7),
    ("📅", "30-Day Streak",          "Maintain a 30-day streak",            streak >= 30),
    ("⚡", "Speed Demon",            "Score 10+ in Speed Challenge",        speed_best >= 10),
    ("🚀", "Speed Champion",         "Score 20+ in Speed Challenge",        speed_best >= 20),
    ("☀️", "Daily Devotee",         "Complete the Daily Challenge",        daily_done),
    ("🧮", "Number System Master",   "Solve 50+ Number System questions",   ts.get("Number System",{}).get("solved",0) >= 50),
    ("💰", "Profit & Loss Pro",      "Solve 30+ Profit & Loss questions",   ts.get("Profit & Loss",{}).get("solved",0) >= 30),
    ("⏱️", "Time Lord",             "Solve 30+ Time & Distance questions", ts.get("Time & Distance",{}).get("solved",0) >= 30),
    ("📊", "Percentage Pundit",      "Solve 30+ Percentage questions",      ts.get("Percentage",{}).get("solved",0) >= 30),
    ("🏆", "XP Master",             "Earn 1000+ XP",                       xp >= 1000),
    ("👑", "XP Champion",           "Earn 5000+ XP",                       xp >= 5000),
]

unlocked_count = sum(1 for *_, u in BADGES if u)
total_count    = len(BADGES)

st.metric("Achievements Unlocked", f"{unlocked_count} / {total_count}")
st.progress(unlocked_count / total_count,
            text=f"{unlocked_count}/{total_count} badges earned")
st.divider()

# Show unlocked first, then locked
st.subheader("🏅 Your Badges")
for emoji, name, desc, unlocked in sorted(BADGES, key=lambda x: not x[3]):
    badge(emoji, name, desc, unlocked)
