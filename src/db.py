"""SQLite log of every pipeline step (STT, Call Brief, RAG).

One row per step execution. Feeds BudgetGuard (persistent spend) and the
Phase 4 dashboard. Schema follows the task plan, plus a `model`
column.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "clientpulse.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id       TEXT,
    timestamp     TEXT NOT NULL,
    step          TEXT NOT NULL,
    model         TEXT,
    input_tokens  INTEGER,
    output_tokens INTEGER,
    cost          REAL NOT NULL DEFAULT 0,
    latency       REAL,
    status        TEXT NOT NULL
)
"""


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def log_step(
    step: str,
    status: str,
    *,
    call_id: str | None = None,
    model: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cost: float = 0.0,
    latency: float | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO calls (call_id, timestamp, step, model, input_tokens,"
            " output_tokens, cost, latency, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                call_id,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                step,
                model,
                input_tokens,
                output_tokens,
                cost,
                latency,
                status,
            ),
        )
    conn.close()


def total_cost(db_path: Path | str = DEFAULT_DB_PATH) -> float:
    with connect(db_path) as conn:
        (total,) = conn.execute("SELECT COALESCE(SUM(cost), 0) FROM calls").fetchone()
    conn.close()
    return float(total)


def cost_by_step(db_path: Path | str = DEFAULT_DB_PATH) -> dict[str, float]:
    with connect(db_path) as conn:
        rows = conn.execute("SELECT step, SUM(cost) FROM calls GROUP BY step ORDER BY step").fetchall()
    conn.close()
    return {step: float(cost) for step, cost in rows}


def step_stats(db_path: Path | str = DEFAULT_DB_PATH) -> list[dict]:
    """One row per (step, model): run counts by status, spend, and averages over successful runs.

    Averages use status 'ok' only, so retries and errors do not distort cost or latency per run.
    """
    with connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT step, model,
                   COUNT(*)                                        AS runs,
                   SUM(status = 'ok')                              AS ok,
                   SUM(status = 'error')                           AS errors,
                   SUM(status = 'retry')                           AS retries,
                   SUM(status = 'invalid')                         AS invalid,
                   COALESCE(SUM(cost), 0)                          AS cost,
                   AVG(CASE WHEN status = 'ok' THEN cost END)      AS avg_cost,
                   AVG(CASE WHEN status = 'ok' THEN latency END)   AS avg_latency,
                   AVG(CASE WHEN status = 'ok' THEN input_tokens END)  AS avg_input_tokens,
                   AVG(CASE WHEN status = 'ok' THEN output_tokens END) AS avg_output_tokens
            FROM calls GROUP BY step, model ORDER BY step, model
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def daily_cost(db_path: Path | str = DEFAULT_DB_PATH) -> list[dict]:
    """Spend per UTC day and step, oldest first."""
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT substr(timestamp, 1, 10) AS day, step, SUM(cost) FROM calls"
            " GROUP BY day, step ORDER BY day, step").fetchall()
    conn.close()
    return [{"day": day, "step": step, "cost": float(cost)} for day, step, cost in rows]
