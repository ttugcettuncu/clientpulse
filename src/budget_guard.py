"""Code-level hard stop for OpenAI spend (CLAUDE.md Bölüm 12).

The OpenAI account budget only sends e-mail alerts, so this is the real
limit. Spend is persisted in SQLite (the `calls` table), so the limit
survives restarts. Usage: guard.check() before every paid call, record_*()
after a successful one. Failed calls are never recorded.
"""
from pathlib import Path

from src import db

# Prices as of Sep 2026 — verify at platform.openai.com/docs/pricing
PRICE = {
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "whisper-1": {"per_minute": 0.006},
    "gpt-4o-mini-transcribe": {"per_minute": 0.003},
    "text-embedding-3-small": {"input": 0.02 / 1_000_000},
}
BUDGET_LIMIT = 5.00
WARN_RATIO = 0.8


class BudgetExceededError(RuntimeError):
    pass


class BudgetGuard:
    def __init__(self, limit: float = BUDGET_LIMIT, db_path: Path | str = db.DEFAULT_DB_PATH):
        self.limit = limit
        self.db_path = db_path

    @property
    def spent(self) -> float:
        return db.total_cost(self.db_path)

    def check(self, upcoming_cost: float = 0.0) -> None:
        """Raise if the budget is used up, or would be by `upcoming_cost`."""
        spent = self.spent
        if spent + upcoming_cost >= self.limit:
            raise BudgetExceededError(
                f"Bütçe doldu: ${spent:.4f} harcandı (+${upcoming_cost:.4f} planlanan) / ${self.limit}"
            )

    def record_chat(self, usage, model: str = "gpt-4o-mini", **log_fields) -> float:
        cost = (usage.prompt_tokens * PRICE[model]["input"]
                + usage.completion_tokens * PRICE[model]["output"])
        self._record(cost, model=model, input_tokens=usage.prompt_tokens,
                     output_tokens=usage.completion_tokens, **log_fields)
        return cost

    def record_audio(self, minutes: float, model: str = "whisper-1", **log_fields) -> float:
        cost = minutes * PRICE[model]["per_minute"]
        self._record(cost, model=model, **log_fields)
        return cost

    def _record(self, cost: float, *, step: str, **log_fields) -> None:
        db.log_step(step, "ok", cost=cost, db_path=self.db_path, **log_fields)
        spent = self.spent
        if spent >= self.limit * WARN_RATIO:
            print(f"⚠️ Bütçenin %{WARN_RATIO * 100:.0f}'i harcandı: ${spent:.4f} / ${self.limit}")
