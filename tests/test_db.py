import pytest

from src import db, metrics


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    db.log_step("call_brief", "ok", model="gpt-4o-mini", cost=0.0002, latency=2.0,
                input_tokens=800, output_tokens=80, db_path=path)
    db.log_step("call_brief", "ok", model="gpt-4o-mini", cost=0.0004, latency=4.0,
                input_tokens=1000, output_tokens=100, db_path=path)
    db.log_step("call_brief", "retry", model="gpt-4o-mini", latency=30.0, db_path=path)
    db.log_step("call_brief", "invalid", model="gpt-4o-mini", cost=0.0001, db_path=path)
    db.log_step("stt", "ok", model="faster-whisper-base", latency=16.0, db_path=path)
    return path


def test_step_stats_counts_statuses_and_averages_ok_runs_only(db_path):
    stats = {(r["step"], r["model"]): r for r in db.step_stats(db_path)}
    brief = stats[("call_brief", "gpt-4o-mini")]

    assert (brief["runs"], brief["ok"], brief["retries"], brief["invalid"], brief["errors"]) == (4, 2, 1, 1, 0)
    assert brief["cost"] == pytest.approx(0.0007)  # the billed invalid run counts towards spend
    assert brief["avg_cost"] == pytest.approx(0.0003)
    assert brief["avg_latency"] == pytest.approx(3.0)  # the 30s retry is left out
    assert brief["avg_input_tokens"] == pytest.approx(900)
    assert stats[("stt", "faster-whisper-base")]["cost"] == 0


def test_daily_cost_groups_by_day_and_step(db_path):
    days = db.daily_cost(db_path)
    assert {d["step"] for d in days} == {"call_brief", "stt"}
    assert sum(d["cost"] for d in days) == pytest.approx(db.total_cost(db_path))


def test_metrics_save_keeps_other_evals(tmp_path):
    path = tmp_path / "metrics.json"
    metrics.save("stt", {"wer": 0.01}, path=path)
    metrics.save("rag", {"accuracy": 0.9}, path=path)
    metrics.save("stt", {"wer": 0.02}, path=path)

    data = metrics.load(path)
    assert data["stt"]["wer"] == 0.02 and data["rag"]["accuracy"] == 0.9
    assert "updated" in data["stt"]
    assert metrics.load(tmp_path / "missing.json") == {}
