"""RAG vs no-RAG experiment on the golden Q&A set (CLAUDE.md section 10).

Every golden question is answered twice by gpt-4o-mini: with the top-k
retrieved chunks (rag) and with the whole corpus in the prompt (no_rag).
Scoring is automatic and objective:
- answerable questions: correct if the model answers and every key fact
  (docs/eval/golden_qa.csv) appears in the answer (case-insensitive,
  hyphens ignored)
- unanswerable questions: correct if the model says it cannot answer
Context recall (rag only): all key facts appear in the retrieved chunks.
Questions whose key fact is a calculated result are excluded, because the
result itself is not in any document.

Answers are cached in data/rag_answers/<prompt version>/<mode>/, so a
question is not sent again unless --force is given.

Usage:  python -m src.eval_rag [--force]
"""
import argparse
import csv
import json
import re
from datetime import date

from dotenv import load_dotenv

from src import db, metrics, rag
from src.budget_guard import BudgetGuard

PROJECT_ROOT = rag.PROJECT_ROOT
GOLDEN_PATH = PROJECT_ROOT / "docs" / "eval" / "golden_qa.csv"
ANSWERS_DIR = PROJECT_ROOT / "data" / "rag_answers"
REPORT_PATH = PROJECT_ROOT / "docs" / "cost_experiment.md"
MODES = ["no_rag", "rag"]
CALCULATED = {"q12", "t04"}  # key fact is a computed amount, not text in the documents
SPLITS = ["dev", "test"]  # dev = seen while tuning the answer prompt, test = held out
QUERIES_PER_MONTH = 1_000  # for the monthly cost projection
MANUAL_MARKER = "<!-- manual analysis below: kept when the report is regenerated -->"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[-\u2010-\u2013]", " ", text.lower()))


def key_facts(row: dict) -> list[str]:
    return [f for f in row["key_facts"].split(";") if f]


def is_correct(row: dict, result: dict) -> bool:
    if row["type"] == "unanswerable":
        return not result["answerable"]
    answer = normalize(result["answer"])
    return result["answerable"] and all(normalize(f) in answer for f in key_facts(row))


def load_golden() -> list[dict]:
    with GOLDEN_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def run_mode(rows: list[dict], mode: str, guard: BudgetGuard, force: bool) -> dict[str, dict]:
    out_dir = ANSWERS_DIR / rag.PROMPT_VERSION / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for row in rows:
        path = out_dir / f"{row['id']}.json"
        if path.exists() and not force:
            result = json.loads(path.read_text(encoding="utf-8"))
        else:
            result = rag.answer_question(row["question"], question_id=row["id"], use_rag=mode == "rag",
                                         guard=guard)
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        results[row["id"]] = result
        print(f"{mode:6} {row['id']} {'OK  ' if is_correct(row, result) else 'MISS'} "
              f"in={result['input_tokens']:5} ${result['cost']:.5f}")
    return results


def context_recall(rows: list[dict], guard: BudgetGuard) -> tuple[int, int, list[str]]:
    """Answerable, non-calculated questions whose key facts all appear in the top-k chunks."""
    checked = [r for r in rows if r["type"] != "unanswerable" and r["id"] not in CALCULATED]
    missed = []
    for row in checked:
        context = normalize(" ".join(h["text"] for h in rag.retrieve(row["question"], guard=guard)))
        if not all(normalize(f) in context for f in key_facts(row)):
            missed.append(row["id"])
    return len(checked) - len(missed), len(checked), missed


def summarize(rows: list[dict], results: dict[str, dict]) -> dict:
    n = len(rows)
    by_split = {}
    for s in SPLITS:
        split_rows = [r for r in rows if r["split"] == s]
        by_split[s] = (sum(is_correct(r, results[r["id"]]) for r in split_rows), len(split_rows))
    by_type = {}
    for t in ["single_fact", "multi_fact", "unanswerable"]:
        typed = [r for r in rows if r["type"] == t]
        by_type[t] = (sum(is_correct(r, results[r["id"]]) for r in typed), len(typed))
    return {
        "correct": sum(is_correct(r, results[r["id"]]) for r in rows),
        "by_split": by_split,
        "by_type": by_type,
        "cost": sum(results[r["id"]]["cost"] for r in rows) / n,
        "input_tokens": sum(results[r["id"]]["input_tokens"] for r in rows) / n,
        "output_tokens": sum(results[r["id"]]["output_tokens"] for r in rows) / n,
        "latency": sum(results[r["id"]]["latency"] for r in rows) / n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="ask every question again")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env", override=True)
    guard = BudgetGuard()
    rows = load_golden()
    results = {mode: run_mode(rows, mode, guard, args.force) for mode in MODES}
    stats = {mode: summarize(rows, results[mode]) for mode in MODES}
    recall_hit, recall_n, recall_missed = context_recall(rows, guard)

    base, new = stats["no_rag"], stats["rag"]
    n = len(rows)
    saving = 1 - new["cost"] / base["cost"]
    acc_base, acc_new = base["correct"] / n, new["correct"] / n
    trend = "stayed the same at" if acc_new == acc_base else ("rose to" if acc_new > acc_base else "fell to")

    lines = [
        "# RAG vs no-RAG Cost Experiment",
        "",
        f"Generated {date.today().isoformat()} by `python -m src.eval_rag`. "
        f"Model: `{rag.MODEL}`, answer prompt `{rag.PROMPT_VERSION}` (temperature 0, strict JSON schema). "
        f"Golden set: `docs/eval/golden_qa.csv` ({n} questions).",
        "",
        "**dev** questions were seen while analysing and changing the answer prompt; **test** questions were "
        "written before the first prompt change (see the prompt history below for how clean the test score is).",
        "",
        f"- **no_rag:** all {len(rag._full_corpus())} corpus documents are sent with every question.",
        f"- **rag:** only the top-{rag.TOP_K} chunks are sent "
        f"(embedding `{rag.EMBEDDINGS[rag.EMBEDDING]}`, ~180-word chunks split by section).",
        "",
        "Scoring is automatic: an answer is correct when every key fact of the question appears in it; "
        "an unanswerable question is correct when the model says the documents do not contain the answer.",
        "",
        "| | no_rag | rag |",
        "|---|---|---|",
        f"| Accuracy, all questions | {base['correct']}/{n} ({acc_base:.0%}) | {new['correct']}/{n} ({acc_new:.0%}) |",
    ]
    for s in SPLITS:
        lines.append(f"| &nbsp;&nbsp;{s} | {base['by_split'][s][0]}/{base['by_split'][s][1]} | "
                     f"{new['by_split'][s][0]}/{new['by_split'][s][1]} |")
    for t in ["single_fact", "multi_fact", "unanswerable"]:
        lines.append(f"| &nbsp;&nbsp;{t} | {base['by_type'][t][0]}/{base['by_type'][t][1]} | "
                     f"{new['by_type'][t][0]}/{new['by_type'][t][1]} |")
    lines += [
        f"| Input tokens / question | {base['input_tokens']:.0f} | {new['input_tokens']:.0f} |",
        f"| Output tokens / question | {base['output_tokens']:.0f} | {new['output_tokens']:.0f} |",
        f"| Cost / question | ${base['cost']:.6f} | ${new['cost']:.6f} |",
        f"| Cost / {QUERIES_PER_MONTH:,} questions per month | ${base['cost'] * QUERIES_PER_MONTH:.2f} | "
        f"${new['cost'] * QUERIES_PER_MONTH:.2f} |",
        f"| Average latency | {base['latency']:.2f}s | {new['latency']:.2f}s |",
        "",
        f"Context recall (rag): all key facts were in the retrieved chunks for {recall_hit}/{recall_n} "
        f"answerable questions{' (missed: ' + ', '.join(recall_missed) + ')' if recall_missed else ''}. "
        f"Calculated answers ({', '.join(sorted(CALCULATED))}) are excluded because the result is not in any document. "
        "The rag cost does not include the query embedding (~20 tokens, about $0.0000004) "
        "or the one-off corpus embedding (about $0.0001).",
        "",
        f"**RAG reduced the cost per question by {saving:.0%}; accuracy {trend} {acc_new:.0%} "
        f"(no-RAG: {acc_base:.0%}).**",
        "",
        "| Question | Split | Type | no_rag | rag | rag answer |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        marks = ["✅" if is_correct(row, results[m][row["id"]]) else "❌" for m in MODES]
        answer = results["rag"][row["id"]]["answer"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {row['id']} | {row['split']} | {row['type']} | {marks[0]} | {marks[1]} | {answer} |")

    manual = ""
    if REPORT_PATH.exists():
        old = REPORT_PATH.read_text(encoding="utf-8")
        if MANUAL_MARKER in old:
            manual = old[old.index(MANUAL_MARKER):]
    REPORT_PATH.write_text("\n".join(lines) + "\n\n" + (manual or MANUAL_MARKER + "\n"), encoding="utf-8")

    metrics.save("rag", {
        "model": rag.MODEL, "prompt": rag.PROMPT_VERSION, "embedding": rag.EMBEDDINGS[rag.EMBEDDING],
        "top_k": rag.TOP_K, "questions": n, "cost_saving": saving,
        "context_recall": {"hit": recall_hit, "total": recall_n},
        "modes": {mode: {"correct": stats[mode]["correct"],
                         "splits": {s: {"correct": c, "total": t} for s, (c, t) in stats[mode]["by_split"].items()},
                         "cost_per_question": stats[mode]["cost"], "input_tokens": stats[mode]["input_tokens"],
                         "latency": stats[mode]["latency"]}
                  for mode in MODES},
    })

    for mode in MODES:
        splits = " | ".join(f"{s} {c}/{t}" for s, (c, t) in stats[mode]["by_split"].items())
        print(f"{mode:6} all {stats[mode]['correct']}/{n} | {splits} | ${stats[mode]['cost']:.6f}/q")
    print(f"saving {saving:.0%} | context recall {recall_hit}/{recall_n} {recall_missed}")
    print(f"Report written: {REPORT_PATH.relative_to(PROJECT_ROOT)}  |  cost by step: {db.cost_by_step()}  |  "
          f"total: ${guard.spent:.4f}")


if __name__ == "__main__":
    main()
