import streamlit as st
import random
import time
import plotly.graph_objects as go
from datetime import date
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()

st.title("📝 Mock Test")

# ── Config ────────────────────────────────────────────────────────────────────
if "mock_started" not in st.session_state:
    st.session_state["mock_started"] = False
if "mock_finished" not in st.session_state:
    st.session_state["mock_finished"] = False

def rank_from_score(pct):
    if pct >= 90: return "💎 Diamond"
    if pct >= 80: return "🥇 Platinum"
    if pct >= 70: return "🥇 Gold"
    if pct >= 60: return "🥈 Silver"
    return "🥉 Bronze"

# ── Setup screen ──────────────────────────────────────────────────────────────
if not st.session_state["mock_started"] and not st.session_state["mock_finished"]:
    st.subheader("Configure Your Mock Test")
    num_q = st.selectbox("Number of Questions", [10, 20, 30, 50, 100], index=1)
    time_limit = {10: 10, 20: 20, 30: 30, 50: 45, 100: 90}[num_q]
    st.info(f"⏱️ Time Limit: **{time_limit} minutes**")

    if st.button("🚀 Start Mock Test", type="primary"):
        # pick random questions from all topics
        all_qs = []
        for topic, qs in data.items():
            for q in qs:
                all_qs.append({"topic": topic, **q})
        chosen = random.sample(all_qs, min(num_q, len(all_qs)))
        st.session_state["mock_questions"]  = chosen
        st.session_state["mock_answers"]    = {}          # {i: chosen_key}
        st.session_state["mock_marked"]     = set()
        st.session_state["mock_idx"]        = 0
        st.session_state["mock_start_time"] = time.time()
        st.session_state["mock_time_limit"] = time_limit * 60
        st.session_state["mock_started"]    = True
        st.session_state["mock_finished"]   = False
        st.rerun()

# ── Active test ───────────────────────────────────────────────────────────────
elif st.session_state["mock_started"] and not st.session_state["mock_finished"]:
    qs          = st.session_state["mock_questions"]
    answers     = st.session_state["mock_answers"]
    marked      = st.session_state["mock_marked"]
    idx         = st.session_state["mock_idx"]
    total_q     = len(qs)
    elapsed     = time.time() - st.session_state["mock_start_time"]
    remaining   = max(0, st.session_state["mock_time_limit"] - elapsed)

    # Timer display
    mins = int(remaining // 60)
    secs = int(remaining % 60)
    timer_color = "🔴" if remaining < 120 else "🟡" if remaining < 300 else "🟢"
    st.metric(f"{timer_color} Time Remaining", f"{mins:02d}:{secs:02d}")

    if remaining == 0:
        st.session_state["mock_finished"] = True
        st.session_state["mock_started"]  = False
        st.rerun()

    # Palette
    st.subheader("Question Palette")
    cols_per_row = 10
    rows = (total_q + cols_per_row - 1) // cols_per_row
    for r in range(rows):
        pcols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            qi = r * cols_per_row + c
            if qi >= total_q:
                break
            if qi in marked:          label = f"🟡{qi+1}"
            elif qi in answers:       label = f"✅{qi+1}"
            else:                     label = f"{qi+1}"
            if pcols[c].button(label, key=f"mock_pal_{qi}"):
                st.session_state["mock_idx"] = qi
                st.rerun()

    st.divider()
    q = qs[idx]
    st.markdown(f"### Q{idx+1}/{total_q} — *{q['topic']}*")
    st.markdown(clean_question(q["question"]))

    options      = q["options"]
    option_keys  = list(options.keys())
    option_labels = [f"**{k}**. {clean_text(options[k])}" for k in option_keys]

    cur_ans = answers.get(idx)
    cur_idx = option_keys.index(cur_ans) if cur_ans in option_keys else None
    sel     = st.radio("Choose your answer:", option_labels,
                       index=cur_idx, key=f"mock_radio_{idx}")
    if sel is not None:
        answers[idx] = option_keys[option_labels.index(sel)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if idx > 0 and st.button("⬅ Prev"):
            st.session_state["mock_idx"] -= 1
            st.rerun()
    with col2:
        if idx < total_q - 1 and st.button("Next ➡"):
            st.session_state["mock_idx"] += 1
            st.rerun()
    with col3:
        mk_label = "🟡 Unmark" if idx in marked else "🟡 Mark Review"
        if st.button(mk_label):
            if idx in marked:
                marked.discard(idx)
            else:
                marked.add(idx)
            st.rerun()
    with col4:
        if st.button("🏁 Submit Test", type="primary"):
            st.session_state["mock_finished"] = True
            st.session_state["mock_started"]  = False
            st.rerun()

    answered = len(answers)
    st.progress(answered / total_q, text=f"Answered: {answered}/{total_q}")

# ── Results screen ─────────────────────────────────────────────────────────────
elif st.session_state["mock_finished"]:
    qs      = st.session_state.get("mock_questions", [])
    answers = st.session_state.get("mock_answers", {})
    elapsed = time.time() - st.session_state.get("mock_start_time", time.time())

    correct  = sum(1 for i, q in enumerate(qs) if answers.get(i) == q["answer"])
    wrong    = sum(1 for i in answers if answers[i] != qs[i]["answer"])
    skipped  = len(qs) - len(answers)
    accuracy = round(correct / len(qs) * 100, 1) if qs else 0
    rank_b   = rank_from_score(accuracy)
    elapsed_m = int(elapsed // 60)
    elapsed_s = int(elapsed % 60)

    # award XP
    st.session_state["xp"] += 50
    st.session_state["tests_taken"] += 1
    st.session_state["questions_solved"] += len(answers)
    st.session_state["correct_answers"]  += correct

    # record test
    st.session_state["recent_tests"].append({
        "Date":     str(date.today()),
        "Mode":     "Mock Test",
        "Score":    f"{correct}/{len(qs)}",
        "Accuracy": f"{accuracy}%",
        "Time":     f"{elapsed_m}m {elapsed_s}s"
    })

    st.balloons()
    st.title(f"Test Complete! {rank_b}")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Score",    f"{correct}/{len(qs)}")
    c2.metric("Correct",  correct)
    c3.metric("Wrong",    wrong)
    c4.metric("Skipped",  skipped)
    c5.metric("Accuracy", f"{accuracy}%")
    st.metric("Time Taken", f"{elapsed_m}m {elapsed_s}s")
    st.metric("XP Earned", "+50 XP 🎉")

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=accuracy,
        title={"text": "Accuracy %"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "#2563EB"},
               "steps": [
                   {"range": [0,  60], "color": "#fee2e2"},
                   {"range": [60, 80], "color": "#fef9c3"},
                   {"range": [80, 100], "color": "#dcfce7"},
               ]}
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Per-question review
    with st.expander("📋 Review Answers"):
        for i, q in enumerate(qs):
            your_ans = answers.get(i, "—")
            correct_ans = q["answer"]
            icon = "✅" if your_ans == correct_ans else ("⏭️" if your_ans == "—" else "❌")
            st.markdown(f"**{icon} Q{i+1}** ({q['topic']}): {q['question'][:80]}...")
            st.caption(f"Your: {your_ans} | Correct: {correct_ans} — {q['options'].get(correct_ans, '')}")

    if st.button("🔄 Start New Test", type="primary"):
        for k in ["mock_started", "mock_finished", "mock_questions",
                  "mock_answers", "mock_marked", "mock_idx",
                  "mock_start_time", "mock_time_limit"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
