"""Call Brief accuracy against the hand-labelled ground truth.

Input is the STT output (faster-whisper base, the production default), not
the original scripts, so recognition errors are part of the measurement.
Briefs are cached in data/synthetic_calls/briefs/<prompt version>/; a call that already has a
brief is not sent again (no double spend for the same call_id) unless
--force is given.

Usage:  python -m src.eval_call_brief [--stt-model base] [--model gpt-4o] [--force]
Run `python -m src.eval_stt` first so the transcripts exist.
"""
import argparse
import csv
import json
from datetime import date

from dotenv import load_dotenv

from src import db
from src.budget_guard import BudgetGuard
from src.call_brief import MODEL, PROMPT_VERSION, generate_call_brief
from src.call_scripts import PROJECT_ROOT
from src.eval_stt import TRANSCRIPTS_DIR

GROUND_TRUTH_PATH = PROJECT_ROOT / "docs" / "eval" / "call_brief_ground_truth.csv"
BRIEFS_DIR = PROJECT_ROOT / "data" / "synthetic_calls" / "briefs"
REPORT_PATH = PROJECT_ROOT / "docs" / "eval" / "call_brief_accuracy.md"
SPLITS = ["dev", "test"]  # dev = used for prompt tuning, test = held out
ACCURACY_TARGET = 0.85  # project success metric
MANUAL_MARKER = "<!-- manual analysis below: kept when the report is regenerated -->"


def load_ground_truth() -> list[dict]:
    with GROUND_TRUTH_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def accuracy(rows: list[dict], field: str) -> float:
    return sum(r[field] == r[f"pred_{field}"] for r in rows) / len(rows)


def score(rows: list[dict]) -> dict[str, float]:
    both = sum(r["disposition"] == r["pred_disposition"] and r["sentiment"] == r["pred_sentiment"]
               for r in rows) / len(rows)
    return {"disposition": accuracy(rows, "disposition"), "sentiment": accuracy(rows, "sentiment"),
            "both": both}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stt-model", default="base")
    parser.add_argument("--force", action="store_true", help="regenerate cached briefs")
    parser.add_argument("--model", default=MODEL, help="e.g. gpt-4o for a quality comparison")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    guard = BudgetGuard()
    variant = PROMPT_VERSION if args.model == MODEL else f"{PROMPT_VERSION}-{args.model}"
    out_dir = BRIEFS_DIR / variant / args.stt_model
    report_path = REPORT_PATH if args.model == MODEL else REPORT_PATH.with_stem(f"{REPORT_PATH.stem}_{args.model}")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for truth in load_ground_truth():
        call_id = truth["call_id"]
        brief_path = out_dir / f"{call_id}.json"
        if brief_path.exists() and not args.force:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
        else:
            transcript = json.loads(
                (TRANSCRIPTS_DIR / args.stt_model / f"{call_id}.json").read_text(encoding="utf-8"))
            brief = generate_call_brief(transcript["text"], call_id=call_id, guard=guard, model=args.model)
            brief_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append({**truth, "pred_disposition": brief["disposition"],
                     "pred_sentiment": brief["sentiment"], "brief": brief})
        print(f"{call_id}: {brief['disposition']:16} {brief['sentiment']:8} ${brief['cost']:.5f}")

    splits = {name: [r for r in rows if r["split"] == name] for name in SPLITS}
    scores = {name: score(split_rows) for name, split_rows in splits.items() if split_rows}
    total_cost = sum(r["brief"]["cost"] for r in rows)
    avg_latency = sum(r["brief"]["latency"] for r in rows) / len(rows)
    avg_in = sum(r["brief"]["input_tokens"] for r in rows) / len(rows)
    avg_out = sum(r["brief"]["output_tokens"] for r in rows) / len(rows)

    def verdict(value: float) -> str:
        return "✅" if value >= ACCURACY_TARGET else "❌"

    lines = [
        "# Call Brief accuracy",
        "",
        f"Generated {date.today().isoformat()} by `python -m src.eval_call_brief`. "
        f"Model: `{args.model}`, prompt `{PROMPT_VERSION}` (temperature 0, strict function calling). "
        f"Input: faster-whisper `{args.stt_model}` transcripts (no speaker labels). "
        f"Ground truth: `docs/eval/call_brief_ground_truth.csv` ({len(rows)} calls).",
        "",
        "**dev** calls were used to tune the prompt. **test** calls were never used for tuning, "
        "so the test score is the one that counts against the target.",
        "",
        f"| Split | Calls | Disposition | Sentiment | Both correct |",
        "|---|---|---|---|---|",
    ]
    for name, sc in scores.items():
        lines.append(f"| {name} | {len(splits[name])} | {sc['disposition']:.0%} {verdict(sc['disposition'])} | "
                     f"{sc['sentiment']:.0%} {verdict(sc['sentiment'])} | {sc['both']:.0%} |")
    lines += [
        "",
        f"Target: ≥ {ACCURACY_TARGET:.0%} (CLAUDE.md 11.3). "
        f"Cost: ${total_cost:.5f} total, ${total_cost / len(rows):.5f} per call "
        f"(avg {avg_in:.0f} input / {avg_out:.0f} output tokens). "
        f"Average latency: {avg_latency:.1f}s per call.",
        "",
        "| Call | Split | Disposition (truth → predicted) | Sentiment (truth → predicted) | Key topics |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        d = r["disposition"] if r["disposition"] == r["pred_disposition"] \
            else f"**{r['disposition']} → {r['pred_disposition']}**"
        s = r["sentiment"] if r["sentiment"] == r["pred_sentiment"] \
            else f"**{r['sentiment']} → {r['pred_sentiment']}**"
        lines.append(f"| {r['call_id']} | {r['split']} | {d} | {s} | {', '.join(r['brief']['key_topics'])} |")
    lines += ["", "## Summaries", ""]
    lines += [f"- **{r['call_id']}:** {r['brief']['summary']}" for r in rows]

    manual = ""
    if report_path.exists():
        old = report_path.read_text(encoding="utf-8")
        if MANUAL_MARKER in old:
            manual = old[old.index(MANUAL_MARKER):]
    report_path.write_text("\n".join(lines) + "\n\n" + (manual or MANUAL_MARKER + "\n"), encoding="utf-8")

    for name, sc in scores.items():
        print(f"{name:5} Disposition {sc['disposition']:.0%} | Sentiment {sc['sentiment']:.0%} | Both {sc['both']:.0%}")
    print(f"Report written: {report_path.relative_to(PROJECT_ROOT)}  |  "
          f"cost by step: {db.cost_by_step()}  |  total: ${guard.spent:.4f}")


if __name__ == "__main__":
    main()
