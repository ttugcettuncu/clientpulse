import pytest

from src import dashboard_data

STATS = [
    {"step": "stt", "model": "faster-whisper-base", "avg_cost": 0.0, "avg_latency": 16.0},
    {"step": "call_brief", "model": "gpt-4o-mini", "avg_cost": 0.0002, "avg_latency": 2.0},
    {"step": "call_brief", "model": "gpt-4o", "avg_cost": 0.0035, "avg_latency": 2.1},
    {"step": "rag", "model": "gpt-4o-mini", "avg_cost": 0.0002, "avg_latency": 1.5},
]
METRICS = {
    "stt": {"default_model": "base", "target": 0.15, "models": {"base": {"wer": 0.012}}},
    "call_brief": {"target": 0.85, "prompt": "v6",
                   "splits": {"test": {"disposition": 0.75, "sentiment": 0.67, "calls": 12}}},
    "rag": {"prompt": "v3", "top_k": 6, "context_recall": {"hit": 24, "total": 25},
            "modes": {"rag": {"splits": {"test": {"correct": 11, "total": 12}}}}},
}


def test_pipeline_uses_the_production_models():
    stages = {p["stage"]: p for p in dashboard_data.pipeline_per_call(STATS)}
    assert stages["Call Brief"]["cost"] == 0.0002  # gpt-4o comparison runs are ignored
    assert stages["STT"]["latency"] == 16.0
    assert sum(p["cost"] for p in stages.values()) == pytest.approx(0.0004)


def test_missing_stage_is_none():
    stages = dashboard_data.pipeline_per_call(STATS[:2])
    assert stages[2]["cost"] is None


def test_definition_of_done_statuses():
    rows = {r["metric"]: r for r in dashboard_data.definition_of_done(METRICS, STATS)}
    assert rows["WER (STT)"]["status"] == "met"
    assert rows["Call Brief accuracy"]["status"] == "missed"
    assert rows["RAG faithfulness"]["status"] == "not measured"
    assert "11/12" in rows["RAG faithfulness"]["actual"]
    assert rows["End-to-end latency"]["actual"].startswith("19.5s")


def test_definition_of_done_without_metrics_keeps_db_rows():
    rows = dashboard_data.definition_of_done({}, STATS)
    assert [r["metric"] for r in rows] == ["Cost / call", "End-to-end latency"]
