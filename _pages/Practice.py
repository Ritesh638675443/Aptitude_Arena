import streamlit as st
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()
topics = list(data.keys())

st.title("📚 Practice Mode")

# ── Topic selector ─────────────────────────────────────────────────────────────
if "practice_topic" not in st.session_state:
    st.session_state["practice_topic"] = topics[0]
if "practice_idx" not in st.session_state:
    st.session_state["practice_idx"] = 0
if "practice_submitted" not in st.session_state:
    st.session_state["practice_submitted"] = False
if "practice_choice" not in st.session_state:
    st.session_state["practice_choice"] = None
if "practice_bookmarks" not in st.session_state:
    st.session_state["practice_bookmarks"] = set()
if "practice_palette" not in st.session_state:
    # status: 0=unseen, 1=correct, 2=wrong, 3=marked
    st.session_state["practice_palette"] = {}

col_sel, col_go = st.columns([4, 1])
with col_sel:
    new_topic = st.selectbox("Select Topic", topics,
                             index=topics.index(st.session_state["practice_topic"]))
with col_go:
    st.write("")
    if st.button("Load Topic", type="primary"):
        st.session_state["practice_topic"] = new_topic
        st.session_state["practice_idx"] = 0
        st.session_state["practice_submitted"] = False
        st.session_state["practice_choice"] = None
        st.session_state["practice_palette"] = {}
        st.rerun()

topic   = st.session_state["practice_topic"]
qs      = data[topic]
idx     = st.session_state["practice_idx"]
total_q = len(qs)
q       = qs[idx]

# ── Progress ──────────────────────────────────────────────────────────────────
st.progress((idx) / total_q, text=f"Question {idx+1} of {total_q}  |  Topic: {topic}")

# ── Question palette ──────────────────────────────────────────────────────────
st.subheader("Question Palette")
palette = st.session_state["practice_palette"]
cols_per_row = 10
rows = (total_q + cols_per_row - 1) // cols_per_row
for r in range(min(rows, 5)):          # show first 50 for large topics
    pcols = st.columns(cols_per_row)
    for c in range(cols_per_row):
        qi = r * cols_per_row + c
        if qi >= total_q:
            break
        status = palette.get(qi, 0)
        if status == 1:   label = f"✅{qi+1}"
        elif status == 2: label = f"❌{qi+1}"
        elif status == 3: label = f"🟡{qi+1}"
        else:             label = f"{qi+1}"
        if pcols[c].button(label, key=f"pal_{r}_{c}"):
            st.session_state["practice_idx"] = qi
            st.session_state["practice_submitted"] = False
            st.session_state["practice_choice"] = None
            st.rerun()

st.divider()

# ── Question display ──────────────────────────────────────────────────────────
st.markdown(f"### Q{idx+1}. {clean_question(q['question'])}")

options     = q["options"]
option_keys = list(options.keys())
option_labels = [f"**{k}**. {clean_text(options[k])}" for k in option_keys]

submitted = st.session_state["practice_submitted"]
choice    = st.session_state["practice_choice"]

if not submitted:
    sel = st.radio("Choose your answer:", option_labels, index=None, key=f"radio_{idx}")
    if sel is not None:
        sel_key = option_keys[option_labels.index(sel)]
        st.session_state["practice_choice"] = sel_key

    col_sub, col_bk, col_mark = st.columns([2, 1, 1])
    with col_sub:
        if st.button("✅ Submit", type="primary", disabled=st.session_state["practice_choice"] is None):
            st.session_state["practice_submitted"] = True
            chosen = st.session_state["practice_choice"]
            correct_key = q["answer"]
            is_correct  = (chosen == correct_key)

            # update palette
            palette[idx] = 1 if is_correct else 2

            # update stats
            st.session_state["questions_solved"] += 1
            topic_stats = st.session_state["topic_stats"]
            if topic not in topic_stats:
                topic_stats[topic] = {"solved": 0, "correct": 0}
            topic_stats[topic]["solved"] += 1

            if is_correct:
                st.session_state["correct_answers"] += 1
                topic_stats[topic]["correct"] += 1
                st.session_state["xp"] += 10

            st.rerun()

    with col_bk:
        bm_label = "🔖 Bookmarked" if idx in st.session_state["practice_bookmarks"] else "🔖 Bookmark"
        if st.button(bm_label):
            bms = st.session_state["practice_bookmarks"]
            if idx in bms:
                bms.discard(idx)
            else:
                bms.add(idx)
                # also store in global bookmarks list
                bm_entry = {"topic": topic, "idx": idx,
                            "question": q["question"][:100]}
                if bm_entry not in st.session_state["bookmarks"]:
                    st.session_state["bookmarks"].append(bm_entry)
            st.rerun()

    with col_mark:
        if st.button("🟡 Mark for Review"):
            palette[idx] = 3
            st.rerun()

else:
    # show result
    chosen     = st.session_state["practice_choice"]
    correct_key = q["answer"]
    is_correct  = (chosen == correct_key)

    if is_correct:
        st.success(f"✅ Correct! The answer is **{correct_key}**: {clean_text(options[correct_key])}")
    else:
        st.error(f"❌ Incorrect. You chose **{chosen}**: {clean_text(options.get(chosen, ''))}")
        st.info(f"✔️ Correct answer: **{correct_key}**: {clean_text(options[correct_key])}")

    with st.expander("💡 Show Explanation"):
        st.markdown(clean_text(q.get("explanation", "No explanation available.")))

    # Navigation
    col_prev, col_next = st.columns(2)
    with col_prev:
        if idx > 0:
            if st.button("⬅ Previous"):
                st.session_state["practice_idx"] -= 1
                st.session_state["practice_submitted"] = False
                st.session_state["practice_choice"] = None
                st.rerun()
    with col_next:
        if idx < total_q - 1:
            if st.button("Next ➡", type="primary"):
                st.session_state["practice_idx"] += 1
                st.session_state["practice_submitted"] = False
                st.session_state["practice_choice"] = None
                st.rerun()
        else:
            st.success("🎉 You've completed all questions in this topic!")

# ── Bookmarks ─────────────────────────────────────────────────────────────────
if st.session_state["bookmarks"]:
    st.divider()
    with st.expander(f"🔖 Your Bookmarks ({len(st.session_state['bookmarks'])})"):
        for bm in st.session_state["bookmarks"][-10:]:
            st.write(f"**{bm['topic']}** — {bm['question']}...")
