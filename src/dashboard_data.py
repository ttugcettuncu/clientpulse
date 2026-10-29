"""Numbers for the Phase 4 dashboard (dashboard.py), kept free of Streamlit so they can be tested.

Inputs: db.step_stats() (spend, runs, latency from SQLite) and
metrics.load() (headline quality metrics written by the eval scripts).
"""
from src import call_brief, rag, stt

# Pipeline order; also the fixed colour order of the charts
STEPS = ["stt", "call_brief", "embedding", "rag", "no_rag"]
STEP_LABELS = {"stt": "STT", "call_brief": "Call Brief", "embedding": "Embedding",
               "rag": "Ask My Docs (RAG)", "no_rag": "No-RAG baseline"}


def _find(stats: list[dict], step: str, model: str) -> dict | None:
    return next((s for s in stats if s["step"] == step and s["model"] == model), None)


def pipeline_per_call(stats: list[dict]) -> list[dict]:
    """Average cost and latency of one call with the production defaults, stage by stage.

    One call = local STT + one Call Brief + one Ask My Docs question.
    """
    stages = [("STT", "stt", f"faster-whisper-{stt.DEFAULT_MODEL}"),
              ("Call Brief", "call_brief", call_brief.MODEL),
              ("Ask My Docs", "rag", rag.MODEL)]
    rows = []
    for label, step, model in stages:
        s = _find(stats, step, model)
        rows.append({"stage": label, "model": model,
                     "cost": (s["avg_cost"] or 0.0) if s else None,
                     "latency": s["avg_latency"] if s else None})
    return rows


def _pct(value: float) -> str:
    return f"{value:.0%}" if value >= 0.1 else f"{value:.1%}"


def definition_of_done(metrics: dict, stats: list[dict]) -> list[dict]:
    """CLAUDE.md 11.3 targets next to the measured values. status: met / missed / reported / not measured."""
    rows = []
    s = metrics.get("stt")
    if s:
        wer = s["models"][s["default_model"]]["wer"]
        rows.append({"metric": "WER (STT)", "target": f"< {_pct(s['target'])}",
                     "actual": f"{_pct(wer)} (faster-whisper {s['default_model']}, normalized)",
                     "status": "met" if wer < s["target"] else "missed"})
    c = metrics.get("call_brief")
    if c:
        test = c["splits"]["test"]
        ok = test["disposition"] >= c["target"] and test["sentiment"] >= c["target"]
        rows.append({"metric": "Call Brief accuracy", "target": f">= {_pct(c['target'])}",
                     "actual": f"disposition {_pct(test['disposition'])}, sentiment {_pct(test['sentiment'])} "
                               f"(held-out, {test['calls']} calls, prompt {c['prompt']})",
                     "status": "met" if ok else "missed"})
    r = metrics.get("rag")
    if r:
        test = r["modes"]["rag"]["splits"]["test"]
        rows.append({"metric": "RAG faithfulness", "target": ">= 90%",
                     "actual": f"not judged yet; answer accuracy {test['correct']}/{test['total']} "
                               f"on held-out questions (prompt {r['prompt']})",
                     "status": "not measured"})
        recall = r["context_recall"]
        rows.append({"metric": "RAG context recall", "target": "reported",
                     "actual": f"{recall['hit']}/{recall['total']} questions with every key fact in the top-{r['top_k']}",
                     "status": "reported"})
    per_call = pipeline_per_call(stats)
    if all(p["cost"] is not None for p in per_call):
        rows.append({"metric": "Cost / call", "target": "reported",
                     "actual": f"${sum(p['cost'] for p in per_call):.5f} (local STT + Call Brief + 1 question)",
                     "status": "reported"})
    if all(p["latency"] is not None for p in per_call):
        parts = " + ".join(f"{p['stage']} {p['latency']:.1f}s" for p in per_call)
        rows.append({"metric": "End-to-end latency", "target": "reported",
                     "actual": f"{sum(p['latency'] for p in per_call):.1f}s ({parts})", "status": "reported"})
    return rows
