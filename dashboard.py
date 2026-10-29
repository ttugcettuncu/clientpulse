"""ClientPulse cost & metrics dashboard (Phase 4).

Reads spend, tokens and latency from SQLite (data/clientpulse.db) and the
headline quality metrics from docs/eval/metrics.json. Read-only: it never
calls the OpenAI API.

Usage:  streamlit run dashboard.py
"""
import altair as alt
import pandas as pd
import streamlit as st

from src import dashboard_data as dd
from src import db, metrics
from src.budget_guard import BUDGET_LIMIT, WARN_RATIO

# Categorical palette (fixed order, one colour per pipeline step, never cycled)
STEP_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
STATUS_LABELS = {"met": "✅ Met", "missed": "❌ Missed", "reported": "ℹ️ Reported", "not measured": "⚪ Not measured"}

st.set_page_config(page_title="ClientPulse metrics", page_icon="📊", layout="wide")
st.title("ClientPulse — cost & metrics")
st.caption("Spend from the SQLite step log, quality from the eval reports (docs/eval/). "
           "Read-only: this page makes no API calls.")

stats = db.step_stats()
m = metrics.load()
spent = db.total_cost()
labels = [dd.STEP_LABELS[s] for s in dd.STEPS]
step_color = alt.Color("label:N", title="Step", scale=alt.Scale(domain=labels, range=STEP_COLORS))

# --- Budget -------------------------------------------------------------------------------
st.subheader("Budget")
st.progress(min(spent / BUDGET_LIMIT, 1.0),
            text=f"\\${spent:.4f} of \\${BUDGET_LIMIT:.2f} spent ({spent / BUDGET_LIMIT:.1%}); "
                 f"warning at {WARN_RATIO:.0%}, hard stop at 100% (BudgetGuard)")

per_call = dd.pipeline_per_call(stats)
cols = st.columns(4)
cols[0].metric("Total spend", f"${spent:.4f}")
cols[1].metric("Remaining budget", f"${BUDGET_LIMIT - spent:.2f}")
if all(p["cost"] is not None for p in per_call):
    cols[2].metric("Cost per call", f"${sum(p['cost'] for p in per_call):.5f}",
                   help="Local STT + one Call Brief + one Ask My Docs question (production defaults)")
if "rag" in m:
    cols[3].metric("RAG cost saving", f"{m['rag']['cost_saving']:.0%}",
                   help="Cost per question with top-k chunks vs the whole corpus in the prompt")

# --- Quality ------------------------------------------------------------------------------
st.subheader("Quality (CLAUDE.md 11.3 definition of done)")
cols = st.columns(3)
if "stt" in m:
    s = m["stt"]
    cols[0].metric(f"WER — {s['default_model']}", f"{s['models'][s['default_model']]['wer']:.1%}",
                   help=f"Normalized WER on 21 synthetic calls; target < {s['target']:.0%}")
if "call_brief" in m:
    t = m["call_brief"]["splits"]["test"]
    cols[1].metric("Call Brief disposition (held-out)", f"{t['disposition']:.0%}",
                   help=f"Sentiment {t['sentiment']:.0%}; target {m['call_brief']['target']:.0%}; {t['calls']} calls")
if "rag" in m:
    t = m["rag"]["modes"]["rag"]["splits"]["test"]
    cols[2].metric("Ask My Docs accuracy (held-out)", f"{t['correct']}/{t['total']}",
                   help=f"Key facts in the answer; prompt {m['rag']['prompt']}")

dod = pd.DataFrame(dd.definition_of_done(m, stats))
if not dod.empty:
    dod["status"] = dod["status"].map(STATUS_LABELS)
    st.dataframe(dod.rename(columns=str.capitalize), hide_index=True, width="stretch")

# --- Spend --------------------------------------------------------------------------------
st.subheader("Spend")
left, right = st.columns(2)

by_step = pd.DataFrame([{"step": s, "cost": c} for s, c in db.cost_by_step().items()])
if not by_step.empty:
    by_step["label"] = by_step["step"].map(dd.STEP_LABELS)
    left.altair_chart(
        alt.Chart(by_step, title="Spend by step (all time)")
        .mark_bar(cornerRadiusEnd=4, size=18)
        .encode(x=alt.X("cost:Q", title="USD", axis=alt.Axis(format="$.3f", grid=True)),
                y=alt.Y("label:N", title=None, sort="-x"),
                color=alt.Color("label:N", scale=alt.Scale(domain=labels, range=STEP_COLORS), legend=None),
                tooltip=[alt.Tooltip("label:N", title="Step"), alt.Tooltip("cost:Q", title="USD", format="$.5f")]),
        width="stretch")

daily = pd.DataFrame(db.daily_cost())
if not daily.empty:
    daily["label"] = daily["step"].map(dd.STEP_LABELS)
    right.altair_chart(
        alt.Chart(daily, title="Spend per day")
        .mark_bar(size=18, stroke="white", strokeWidth=2)
        .encode(x=alt.X("day:O", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("sum(cost):Q", title="USD", axis=alt.Axis(format="$.3f")),
                color=step_color,
                order=alt.Order("step_order:Q"),
                tooltip=[alt.Tooltip("day:O", title="Day"), alt.Tooltip("label:N", title="Step"),
                         alt.Tooltip("cost:Q", title="USD", format="$.5f")])
        .transform_calculate(step_order=f"indexof({labels}, datum.label)"),
        width="stretch")

# --- Per call -----------------------------------------------------------------------------
st.subheader("One call, stage by stage")
st.caption("Averages over successful runs with the production models.")
pc = pd.DataFrame(per_call)
if not pc.empty:
    pc["cost"] = pc["cost"].map(lambda v: "—" if v is None or pd.isna(v) else f"${v:.5f}")
    pc["latency"] = pc["latency"].map(lambda v: "—" if v is None or pd.isna(v) else f"{v:.1f}s")
    st.dataframe(pc.rename(columns=str.capitalize), hide_index=True, width="stretch")

# --- RAG vs no-RAG ------------------------------------------------------------------------
if "rag" in m:
    r = m["rag"]
    st.subheader("Ask My Docs: RAG vs whole corpus in the prompt")
    st.caption(f"{r['questions']} golden questions, prompt {r['prompt']}, embedding {r['embedding']}, "
               f"top-{r['top_k']} chunks. Details: docs/cost_experiment.md")
    modes = pd.DataFrame([
        {"mode": dd.STEP_LABELS[k], "cost": v["cost_per_question"], "accuracy": v["correct"] / r["questions"],
         "tokens": v["input_tokens"]}
        for k, v in r["modes"].items()])
    mode_color = alt.Color("mode:N", legend=None,
                           scale=alt.Scale(domain=[dd.STEP_LABELS["rag"], dd.STEP_LABELS["no_rag"]],
                                           range=STEP_COLORS[3:5]))
    a, b = st.columns(2)
    for col, field, title, fmt in [(a, "cost", "Cost per question", "$.5f"),
                                   (b, "accuracy", "Accuracy (all questions)", ".0%")]:
        col.altair_chart(
            alt.Chart(modes, title=title).mark_bar(cornerRadiusEnd=4, size=18)
            .encode(x=alt.X(f"{field}:Q", title=None, axis=alt.Axis(format=fmt)),
                    y=alt.Y("mode:N", title=None), color=mode_color,
                    tooltip=[alt.Tooltip("mode:N", title="Mode"), alt.Tooltip(f"{field}:Q", format=fmt),
                             alt.Tooltip("tokens:Q", title="Input tokens", format=",.0f")]),
            width="stretch")

# --- Raw step log -------------------------------------------------------------------------
with st.expander("Step log by model (all runs, including eval and comparison runs)"):
    st.dataframe(pd.DataFrame(stats), hide_index=True, width="stretch")
