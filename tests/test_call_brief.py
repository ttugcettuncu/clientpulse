import json
import sqlite3
from types import SimpleNamespace

import httpx
import openai
import pytest

from src import db
from src.budget_guard import BudgetExceededError, BudgetGuard
from src.call_brief import TOOL, InvalidBriefError, generate_call_brief, mask_pii

BRIEF = {"summary": "A bakery owner asked about prices and booked the Growth Package.",
         "sentiment": "pozitif",
         "outcome_evidence": "She paid for the Growth Package.", "disposition": "teklif_kabul", "key_topics": ["pricing"]}


def response(arguments: dict | str):
    args = arguments if isinstance(arguments, str) else json.dumps(arguments)
    tool_call = SimpleNamespace(function=SimpleNamespace(name="record_call_brief", arguments=args))
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[tool_call]))],
        usage=SimpleNamespace(prompt_tokens=1000, completion_tokens=100),
    )


class FakeClient:
    """Mimics client.chat.completions.create; returns or raises the queued outcomes in order."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def rate_limit_error():
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    return openai.RateLimitError("429", response=httpx.Response(429, request=request), body=None)


def statuses(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT step, status, cost FROM calls ORDER BY id").fetchall()


def test_returns_brief_and_records_cost(tmp_path):
    db_path = tmp_path / "test.db"
    client = FakeClient(response(BRIEF))
    brief = generate_call_brief("transcript", call_id="c1", client=client, db_path=db_path)

    assert brief["disposition"] == "teklif_kabul"
    assert brief["cost"] == pytest.approx(1000 * 0.15e-6 + 100 * 0.60e-6)
    assert statuses(db_path) == [("call_brief", "ok", pytest.approx(brief["cost"]))]
    # one forced function call, strict schema
    request = client.requests[0]
    assert request["tool_choice"]["function"]["name"] == "record_call_brief"
    assert TOOL["function"]["strict"] is True


def test_retries_transient_errors_without_charging(tmp_path):
    db_path = tmp_path / "test.db"
    waits = []
    client = FakeClient(rate_limit_error(), rate_limit_error(), response(BRIEF))
    generate_call_brief("t", client=client, db_path=db_path, sleep=waits.append)

    assert waits == [1.0, 2.0]  # exponential backoff
    assert [(s, c) for _, s, c in statuses(db_path)] == [("retry", 0), ("retry", 0), ("ok", pytest.approx(0.00021))]


def test_gives_up_after_two_retries(tmp_path):
    db_path = tmp_path / "test.db"
    client = FakeClient(rate_limit_error(), rate_limit_error(), rate_limit_error())
    with pytest.raises(openai.RateLimitError):
        generate_call_brief("t", client=client, db_path=db_path, sleep=lambda s: None)
    assert [s for _, s, _ in statuses(db_path)] == ["retry", "retry", "error"]
    assert db.total_cost(db_path) == 0


def test_invalid_output_is_billed_but_rejected(tmp_path):
    db_path = tmp_path / "test.db"
    client = FakeClient(response({**BRIEF, "disposition": "maybe"}))
    with pytest.raises(InvalidBriefError):
        generate_call_brief("t", client=client, db_path=db_path)
    assert [s for _, s, _ in statuses(db_path)] == ["invalid"]
    assert db.total_cost(db_path) > 0


def test_budget_guard_blocks_before_calling(tmp_path):
    db_path = tmp_path / "test.db"
    client = FakeClient(response(BRIEF))
    with pytest.raises(BudgetExceededError):
        generate_call_brief("t", client=client, guard=BudgetGuard(limit=0.0, db_path=db_path), db_path=db_path)
    assert client.requests == []


def test_pii_is_masked_before_sending(tmp_path):
    client = FakeClient(response(BRIEF))
    generate_call_brief("my card is 4111 1111 1111 1111, mail me at sarah@example.com",
                        client=client, db_path=tmp_path / "test.db")
    sent = client.requests[0]["messages"][1]["content"]
    assert "4111" not in sent and "sarah@example.com" not in sent


def test_mask_pii_keeps_prices_and_dates():
    text = "The session costs $180, invoice 0142 is due on the 15th. ID 12345678901."
    assert mask_pii(text) == "The session costs $180, invoice 0142 is due on the 15th. ID [NATIONAL_ID]."


def test_cost_by_step(tmp_path):
    db_path = tmp_path / "test.db"
    db.log_step("stt", "ok", cost=0.01, db_path=db_path)
    db.log_step("call_brief", "ok", cost=0.002, db_path=db_path)
    db.log_step("call_brief", "ok", cost=0.003, db_path=db_path)
    assert db.cost_by_step(db_path) == {"call_brief": pytest.approx(0.005), "stt": pytest.approx(0.01)}
