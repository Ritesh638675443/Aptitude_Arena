import streamlit as st
from datetime import date
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()

st.title("🔥 Daily Challenge")
st.caption("One question per day. +50 XP reward!")

today = str(date.today())

# pick deterministic question from date seed
all_qs = [{"topic": t, **q} for t, qs in data.items() for q in qs]
seed   = int(today.replace("-", ""))
q      = all_qs[seed % len(all_qs)]

already_done = (st.session_state["daily_done"] and
                st.session_state["daily_date"] == today)

st.markdown(f"### 📅 Challenge for {today}")
st.markdown(f"**Topic:** {q['topic']}")
st.divider()

st.markdown(f"### {clean_question(q['question'])}")

options      = q["options"]
option_keys  = list(options.keys())
option_labels = [f"**{k}**. {clean_text(options[k])}" for k in option_keys]

if already_done:
    st.success("✅ You already completed today's challenge! Come back tomorrow.")
    st.info(f"Correct Answer: **{q['answer']}** — {clean_text(options[q['answer']])}")
    with st.expander("💡 Explanation"):
        st.markdown(clean_text(q.get("explanation", "No explanation available.")))
else:
    if "daily_choice" not in st.session_state:
        st.session_state["daily_choice"] = None
    if "daily_submitted" not in st.session_state:
        st.session_state["daily_submitted"] = False

    if not st.session_state["daily_submitted"]:
        sel = st.radio("Your answer:", option_labels, index=None, key="daily_radio")
        if sel is not None:
            st.session_state["daily_choice"] = option_keys[option_labels.index(sel)]

        if st.button("🚀 Submit Answer", type="primary",
                     disabled=st.session_state["daily_choice"] is None):
            st.session_state["daily_submitted"] = True
            st.rerun()
    else:
        chosen     = st.session_state["daily_choice"]
        correct_k  = q["answer"]
        is_correct = (chosen == correct_k)

        if is_correct:
            st.success(f"🎉 Correct! **{correct_k}**: {clean_text(options[correct_k])}")
            st.balloons()
        else:
            st.error(f"❌ Wrong. You chose **{chosen}**: {clean_text(options.get(chosen,''))}")
            st.info(f"✔️ Correct: **{correct_k}**: {clean_text(options[correct_k])}")

        with st.expander("💡 Explanation"):
            st.markdown(clean_text(q.get("explanation", "No explanation available.")))

        if st.button("✅ Claim +50 XP", type="primary"):
            st.session_state["xp"]           += 50
            st.session_state["daily_done"]    = True
            st.session_state["daily_date"]    = today
            st.session_state["questions_solved"] += 1
            if is_correct:
                st.session_state["correct_answers"] += 1
            st.rerun()
