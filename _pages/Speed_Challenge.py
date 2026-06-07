import streamlit as st
import random
import time
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()
all_qs = [{"topic": t, **q} for t, qs in data.items() for q in qs]

st.title("⚡ Speed Challenge")
st.caption("60 seconds — answer as many questions as you can!")

if "speed_active" not in st.session_state:
    st.session_state["speed_active"]   = False
if "speed_finished" not in st.session_state:
    st.session_state["speed_finished"] = False

# ── Start screen ──────────────────────────────────────────────────────────────
if not st.session_state["speed_active"] and not st.session_state["speed_finished"]:
    st.markdown("""
    ### Rules:
    - ⏱ **60 seconds** on the clock
    - Answer as many questions as possible
    - **+1 point** for each correct answer
    - Skip any question (counts as wrong)
    - Your best score is saved!
    """)
    st.metric("Your Best Score", st.session_state.get("speed_best", 0))

    if st.button("🚀 Start Speed Challenge!", type="primary"):
        shuffled = random.sample(all_qs, min(60, len(all_qs)))
        st.session_state["speed_qs"]        = shuffled
        st.session_state["speed_idx"]       = 0
        st.session_state["speed_correct"]   = 0
        st.session_state["speed_answered"]  = 0
        st.session_state["speed_start"]     = time.time()
        st.session_state["speed_active"]    = True
        st.session_state["speed_finished"]  = False
        st.rerun()

# ── Active game ────────────────────────────────────────────────────────────────
elif st.session_state["speed_active"] and not st.session_state["speed_finished"]:
    elapsed   = time.time() - st.session_state["speed_start"]
    remaining = max(0, 60 - elapsed)

    if remaining == 0:
        st.session_state["speed_active"]   = False
        st.session_state["speed_finished"] = True
        st.rerun()

    mins = 0
    secs = int(remaining)
    tc   = "🔴" if remaining < 15 else "🟡" if remaining < 30 else "🟢"

    col_t, col_s, col_a = st.columns(3)
    col_t.metric(f"{tc} Time Left", f"{secs}s")
    col_s.metric("✅ Score", st.session_state["speed_correct"])
    col_a.metric("📊 Answered", st.session_state["speed_answered"])

    st.progress(remaining / 60)
    st.divider()

    idx = st.session_state["speed_idx"]
    qs  = st.session_state["speed_qs"]

    if idx >= len(qs):
        st.session_state["speed_active"]   = False
        st.session_state["speed_finished"] = True
        st.rerun()

    q = qs[idx]
    st.markdown(f"### Q{idx+1}. {clean_question(q['question'])}")

    option_keys   = list(q["options"].keys())
    option_labels = [f"**{k}**. {clean_text(q['options'][k])}" for k in option_keys]

    chosen = None
    for i, label in enumerate(option_labels):
        if st.button(label, key=f"speed_{idx}_{i}", use_container_width=True):
            chosen = option_keys[i]
            is_correct = (chosen == q["answer"])
            if is_correct:
                st.session_state["speed_correct"] += 1
            st.session_state["speed_answered"] += 1
            st.session_state["speed_idx"]      += 1
            st.rerun()

    if st.button("⏭️ Skip", key=f"speed_skip_{idx}"):
        st.session_state["speed_idx"]      += 1
        st.session_state["speed_answered"] += 1
        st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────
elif st.session_state["speed_finished"]:
    correct  = st.session_state["speed_correct"]
    answered = st.session_state["speed_answered"]
    best     = st.session_state.get("speed_best", 0)

    if correct > best:
        st.session_state["speed_best"] = correct
        best = correct
        st.balloons()
        st.success("🎉 New Personal Best!")

    st.title("⚡ Speed Challenge Complete!")
    c1, c2, c3 = st.columns(3)
    c1.metric("Questions Answered", answered)
    c2.metric("Correct Answers",    correct)
    c3.metric("Final Score",        correct)

    accuracy = round(correct / answered * 100, 1) if answered else 0
    st.metric("Accuracy",    f"{accuracy}%")
    st.metric("Best Score",  best)

    xp_earned = correct * 2 + 25
    st.session_state["xp"]               += xp_earned
    st.session_state["questions_solved"]  += answered
    st.session_state["correct_answers"]   += correct
    st.info(f"🎁 You earned **+{xp_earned} XP**!")

    if st.button("🔄 Play Again", type="primary"):
        for k in ["speed_active", "speed_finished", "speed_qs", "speed_idx",
                  "speed_correct", "speed_answered", "speed_start"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
