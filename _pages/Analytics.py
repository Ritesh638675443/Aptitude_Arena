import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_questions, clean_question, clean_text, get_rank

data = load_questions()

st.title("📊 Analytics")
st.caption("Deep-dive into your performance across all topics.")

ts      = st.session_state.get("topic_stats", {})
solved  = st.session_state.get("questions_solved", 0)
correct = st.session_state.get("correct_answers", 0)
tests   = st.session_state.get("tests_taken", 0)
xp      = st.session_state.get("xp", 0)

if not ts:
    st.info("📭 No data yet. Start practising to see your analytics here!")
    st.stop()

# ── Summary metrics ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Questions Solved",  solved)
c2.metric("Correct Answers",   correct)
c3.metric("Tests Taken",       tests)
c4.metric("Overall Accuracy",  f"{round(correct/solved*100,1) if solved else 0}%")

st.divider()

# ── Per-topic data ─────────────────────────────────────────────────────────────
rows = []
for topic, s in ts.items():
    acc = round(s["correct"]/s["solved"]*100, 1) if s["solved"] else 0
    rows.append({"Topic": topic, "Solved": s["solved"],
                 "Correct": s["correct"], "Accuracy": acc})
df = pd.DataFrame(rows).sort_values("Accuracy", ascending=False)

if df.empty:
    st.info("Practice more questions to see analytics.")
    st.stop()

# ── Strong & Weak ──────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("💪 Strong Areas (Top 5)")
    strong = df.head(5)
    for _, row in strong.iterrows():
        st.progress(int(row["Accuracy"]) / 100,
                    text=f"{row['Topic']}: {row['Accuracy']}%")

with col_r:
    st.subheader("⚠️ Weak Areas (Bottom 5)")
    weak = df.tail(5)
    for _, row in weak.iterrows():
        st.progress(int(row["Accuracy"]) / 100,
                    text=f"{row['Topic']}: {row['Accuracy']}%")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Bar Chart", "Radar Chart", "Pie Chart", "Solved vs Correct"])

with tab1:
    fig = px.bar(df, x="Topic", y="Accuracy",
                 color="Accuracy", color_continuous_scale="Blues",
                 title="Accuracy by Topic")
    fig.update_layout(xaxis_tickangle=-45, margin=dict(b=120))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    top_topics = df.head(min(12, len(df)))
    fig_radar  = go.Figure(go.Scatterpolar(
        r=top_topics["Accuracy"].tolist(),
        theta=top_topics["Topic"].tolist(),
        fill="toself",
        line_color="#2563EB"
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                             title="Performance Radar")
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    fig_pie = px.pie(df, names="Topic", values="Solved",
                     title="Questions Solved per Topic", hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

with tab4:
    fig_bar2 = px.bar(df, x="Topic", y=["Solved","Correct"],
                      barmode="group", title="Solved vs Correct per Topic")
    fig_bar2.update_layout(xaxis_tickangle=-45, margin=dict(b=120))
    st.plotly_chart(fig_bar2, use_container_width=True)

st.divider()

# ── Recent tests table ─────────────────────────────────────────────────────────
st.subheader("Recent Test History")
recent = st.session_state.get("recent_tests", [])
if recent:
    st.dataframe(pd.DataFrame(recent[::-1]), use_container_width=True, hide_index=True)
else:
    st.info("No test history yet.")

# ── Full topic table ───────────────────────────────────────────────────────────
st.subheader("Full Topic Breakdown")
st.dataframe(df.reset_index(drop=True), use_container_width=True, hide_index=True)
