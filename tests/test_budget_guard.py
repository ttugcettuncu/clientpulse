from types import SimpleNamespace

import pytest

from src import db
from src.budget_guard import BudgetExceededError, BudgetGuard


def test_audio_cost_is_recorded_and_persisted(tmp_path):
    db_path = tmp_path / "test.db"
    guard = BudgetGuard(limit=1.0, db_path=db_path)
    cost = guard.record_audio(2.0, model="whisper-1", step="stt", call_id="c1")
    assert cost == pytest.approx(0.012)
    # a new guard (e.g. after restart) sees the same spend
    assert BudgetGuard(limit=1.0, db_path=db_path).spent == pytest.approx(0.012)


def test_chat_cost_uses_token_prices(tmp_path):
    guard = BudgetGuard(db_path=tmp_path / "test.db")
    usage = SimpleNamespace(prompt_tokens=1_000_000, completion_tokens=1_000_000)
    assert guard.record_chat(usage, step="call_brief") == pytest.approx(0.75)


def test_check_blocks_when_limit_reached(tmp_path):
    db_path = tmp_path / "test.db"
    guard = BudgetGuard(limit=0.01, db_path=db_path)
    guard.check(upcoming_cost=0.005)  # still fine
    db.log_step("stt", "ok", cost=0.01, db_path=db_path)
    with pytest.raises(BudgetExceededError):
        guard.check()


def test_check_blocks_when_upcoming_call_would_exceed(tmp_path):
    guard = BudgetGuard(limit=0.01, db_path=tmp_path / "test.db")
    with pytest.raises(BudgetExceededError):
        guard.check(upcoming_cost=0.02)


def test_failed_calls_do_not_count(tmp_path):
    db_path = tmp_path / "test.db"
    db.log_step("stt", "error", db_path=db_path)
    assert BudgetGuard(db_path=db_path).spent == 0
