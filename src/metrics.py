"""Headline quality metrics shared between the eval scripts and the dashboard.

Each eval script (eval_stt, eval_call_brief, eval_rag) saves its headline
numbers under its own key in docs/eval/metrics.json; the dashboard reads
them, so it never has to parse the Markdown reports. Spend, tokens and
latency come from SQLite instead (src/db.py).
"""
import json
from datetime import date
from pathlib import Path

from src.db import PROJECT_ROOT

METRICS_PATH = PROJECT_ROOT / "docs" / "eval" / "metrics.json"


def load(path: Path | str = METRICS_PATH) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save(name: str, values: dict, path: Path | str = METRICS_PATH) -> None:
    """Replace the metrics of one eval (`name`) and keep the others."""
    data = load(path)
    data[name] = {**values, "updated": date.today().isoformat()}
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
