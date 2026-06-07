import streamlit as st
import random
import time
import plotly.graph_objects as go
from datetime import date
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()

COMPANY_CONFIG = {
    "TCS":        {"questions": 30, "minutes": 40, "emoji": "🔵"},
    "Infosys":    {"questions": 25, "minutes": 35, "emoji": "🟣"},
    "Accenture":  {"questions": 20, "minutes": 25, "emoji": "🟠"},
    "Capgemini":  {"questions": 25, "minutes": 30, "emoji": "🔴"},
    "Cognizant":  {"questions": 20, "minutes": 25, "emoji": "🟢"},
    "Deloitte":   {"questions": 30, "minutes": 45, "emoji": "⚫"},
    "Wipro":      {"questions": 20, "minutes": 25, "emoji": "🟡"},
}

def rank_from_score(pct):
    if pct >= 90: return "💎 Diamond"
    if pct >= 80: return "🥇 Platinum"
    if pct >= 70: return "🥇 Gold"
    if pct >= 60: return "🥈 Silver"
    return "🥉 Bronze"

st.title("🏢 Company Tests")

if "ct_started" not in st.session_state:
    st.session_state["ct_started"]  = False
if "ct_finished" not in st.session_state:
    st.session_state["ct_finished"] = False

# ── Company selection ──────────────────────────────────────────────────────────
if not st.session_state["ct_started"] and not st.session_state["ct_finished"]:
    st.subheader("Choose a Company Aptitude Test")
    cols = st.columns(4)
    for i, (company, cfg) in enumerate(COMPANY_CONFIG.items()):
        with cols[i % 4]:
            st.markdown(f"### {cfg['emoji']} {company}")
            st.write(f"**{cfg['questions']} Qs** | **{cfg['minutes']} min**")
            if st.button(f"Start {company}", key=f"ct_{company}", type="primary"):
                all_qs = [{"topic": t, **q}
                          for t, qs in data.items() for q in qs]
                chosen = random.sample(all_qs, min(cfg["questions"], len(all_qs)))
                st.session_state["ct_company"]     = company
                st.session_state["ct_questions"]   = chosen
                st.session_state["ct_answers"]     = {}
                st.session_state["ct_marked"]      = set()
                st.session_state["ct_idx"]         = 0
                st.session_state["ct_start_time"]  = time.time()
                st.session_state["ct_time_limit"]  = cfg["minutes"] * 60
                st.session_state["ct_started"]     = True
                st.session_state["ct_finished"]    = False
                st.rerun()

# ── Active test ───────────────────────────────────────────────────────────────
elif st.session_state["ct_started"] and not st.session_state["ct_finished"]:
    company  = st.session_state["ct_company"]
    qs       = st.session_state["ct_questions"]
    answers  = st.session_state["ct_answers"]
    marked   = st.session_state["ct_marked"]
    idx      = st.session_state["ct_idx"]
    total_q  = len(qs)
    elapsed  = time.time() - st.session_state["ct_start_time"]
    remaining = max(0, st.session_state["ct_time_limit"] - elapsed)

    cfg = COMPANY_CONFIG[company]
    st.header(f"{cfg['emoji']} {company} Aptitude Test")
    mins = int(remaining // 60)
    secs = int(remaining % 60)
    tc   = "🔴" if remaining < 120 else "🟡" if remaining < 300 else "🟢"
    st.metric(f"{tc} Time Left", f"{mins:02d}:{secs:02d}")

    if remaining == 0:
        st.session_state["ct_finished"] = True
        st.session_state["ct_started"]  = False
        st.rerun()

    # Palette
    cols_per_row = 10
    rows = (total_q + cols_per_row - 1) // cols_per_row
    for r in range(rows):
        pcols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            qi = r * cols_per_row + c
            if qi >= total_q: break
            if qi in marked:       label = f"🟡{qi+1}"
            elif qi in answers:    label = f"✅{qi+1}"
            else:                  label = f"{qi+1}"
            if pcols[c].button(label, key=f"ct_pal_{qi}"):
                st.session_state["ct_idx"] = qi
                st.rerun()

    st.divider()
    q = qs[idx]
    st.markdown(f"### Q{idx+1}/{total_q}")
    st.markdown(clean_question(q["question"]))

    option_keys   = list(q["options"].keys())
    option_labels = [f"**{k}**. {clean_text(q['options'][k])}" for k in option_keys]
    cur_ans = answers.get(idx)
    cur_i   = option_keys.index(cur_ans) if cur_ans in option_keys else None
    sel = st.radio("Choose:", option_labels, index=cur_i, key=f"ct_radio_{idx}")
    if sel is not None:
        answers[idx] = option_keys[option_labels.index(sel)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if idx > 0 and st.button("⬅ Prev", key="ct_prev"): 
            st.session_state["ct_idx"] -= 1; st.rerun()
    with col2:
        if idx < total_q-1 and st.button("Next ➡", key="ct_next"):
            st.session_state["ct_idx"] += 1; st.rerun()
    with col3:
        mk_lbl = "🟡 Unmark" if idx in marked else "🟡 Mark"
        if st.button(mk_lbl, key="ct_mark"):
            marked.discard(idx) if idx in marked else marked.add(idx)
            st.rerun()
    with col4:
        if st.button("🏁 Submit", type="primary", key="ct_submit"):
            st.session_state["ct_finished"] = True
            st.session_state["ct_started"]  = False
            st.rerun()

    st.progress(len(answers)/total_q, text=f"Answered: {len(answers)}/{total_q}")

# ── Results ────────────────────────────────────────────────────────────────────
elif st.session_state["ct_finished"]:
    company  = st.session_state["ct_company"]
    qs       = st.session_state["ct_questions"]
    answers  = st.session_state["ct_answers"]
    elapsed  = time.time() - st.session_state["ct_start_time"]

    correct  = sum(1 for i, q in enumerate(qs) if answers.get(i) == q["answer"])
    wrong    = len(answers) - correct
    accuracy = round(correct / len(qs) * 100, 1) if qs else 0
    rank_b   = rank_from_score(accuracy)
    em       = int(elapsed // 60); es = int(elapsed % 60)

    st.session_state["xp"] += 50
    st.session_state["tests_taken"] += 1
    st.session_state["recent_tests"].append({
        "Date": str(date.today()), "Mode": f"{company} Test",
        "Score": f"{correct}/{len(qs)}", "Accuracy": f"{accuracy}%",
        "Time": f"{em}m {es}s"
    })

    st.balloons()
    cfg = COMPANY_CONFIG[company]
    st.title(f"{cfg['emoji']} {company} Test Result — {rank_b}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score",    f"{correct}/{len(qs)}")
    c2.metric("Correct",  correct)
    c3.metric("Wrong",    wrong)
    c4.metric("Accuracy", f"{accuracy}%")

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=accuracy,
        title={"text": "Score %"},
        gauge={"axis": {"range":[0,100]}, "bar":{"color":"#2563EB"},
               "steps":[{"range":[0,60],"color":"#fee2e2"},
                        {"range":[60,80],"color":"#fef9c3"},
                        {"range":[80,100],"color":"#dcfce7"}]}))
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🔄 Try Another Company", type="primary"):
        for k in ["ct_started","ct_finished","ct_company","ct_questions",
                  "ct_answers","ct_marked","ct_idx","ct_start_time","ct_time_limit"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
