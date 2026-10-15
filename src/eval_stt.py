"""WER of the STT output against the original scripts.

Two scores per call:
- raw WER: lowercase + punctuation removed only.
- normalized WER: additionally spells out digits ("$950" -> "nine hundred and
  fifty dollars"), so that writing a number differently is not counted as a
  recognition error. This mirrors the normalizers used in published Whisper
  benchmarks.

Usage:  python -m src.eval_stt [--models tiny base small]
Writes transcripts to data/synthetic_calls/transcripts/<model>/ and the report
to docs/eval/wer_report.md.
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

import jiwer
from num2words import num2words

from src import stt
from src.call_scripts import AUDIO_DIR, PROJECT_ROOT, load_scripts

TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "synthetic_calls" / "transcripts"
REPORT_PATH = PROJECT_ROOT / "docs" / "eval" / "wer_report.md"
WER_TARGET = 0.15  # project success metric
MANUAL_MARKER = "<!-- manual analysis below: kept when the report is regenerated -->"

_basic = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.SubstituteRegexes({r"[-–—]": " "}),
    jiwer.RemovePunctuation(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
])


def _spell_number(match: re.Match) -> str:
    currency, number, suffix = match.group(1), match.group(2).replace(",", ""), match.group(3)
    if re.fullmatch(r"0\d*", number) and len(number) > 1:  # "0142" -> digit by digit
        words = " ".join(num2words(int(d)) for d in number)
    elif suffix in ("st", "nd", "rd", "th"):
        words = num2words(int(number), to="ordinal")
    else:
        words = num2words(float(number) if "." in number else int(number))
    if suffix == "%":
        words += " percent"
    if currency:
        words += " dollars"
    return f" {words} "


def spell_out_numbers(text: str) -> str:
    return re.sub(r"(\$)?(\d[\d,]*(?:\.\d+)?)(%|st|nd|rd|th)?", _spell_number, text)


def raw_text(text: str) -> str:
    return _basic(text)


def normalized_text(text: str) -> str:
    # phone numbers are read digit by digit: "555-0142" -> "5 5 5 0 1 4 2"
    text = re.sub(r"\b\d{3}-\d{4}\b", lambda m: " ".join(m.group().replace("-", "")), text)
    text = re.sub(r"(\d)\s*(am|pm|a\.m\.|p\.m\.)", r"\1 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d+):00\b", r"\1", text)  # "11:00" -> "11"
    return _basic(spell_out_numbers(text))


def wer(reference: str, hypothesis: str, normalize=normalized_text) -> float:
    return jiwer.wer(normalize(reference), normalize(hypothesis))


def top_errors(reference: str, hypothesis: str, n: int = 6) -> list[str]:
    """Most frequent substitutions/deletions/insertions after normalization."""
    out = jiwer.process_words(normalized_text(reference), normalized_text(hypothesis))
    counts: dict[str, int] = {}
    ref_words, hyp_words = out.references[0], out.hypotheses[0]
    for chunk in out.alignments[0]:
        if chunk.type == "equal":
            continue
        ref = " ".join(ref_words[chunk.ref_start_idx:chunk.ref_end_idx]) or "∅"
        hyp = " ".join(hyp_words[chunk.hyp_start_idx:chunk.hyp_end_idx]) or "∅"
        key = f"{ref} → {hyp}"
        counts[key] = counts.get(key, 0) + 1
    return [k for k, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:n]]


def run(models: list[str]) -> list[dict]:
    rows = []
    scripts = load_scripts()
    for size in models:
        out_dir = TRANSCRIPTS_DIR / size
        out_dir.mkdir(parents=True, exist_ok=True)
        for script in scripts:
            t = stt.transcribe(AUDIO_DIR / f"{script.call_id}.mp3", model_size=size)
            (out_dir / f"{script.call_id}.json").write_text(json.dumps({
                "call_id": script.call_id, "model": t.model, "text": t.text,
                "audio_seconds": t.audio_seconds, "latency": t.latency,
                "segments": [s.__dict__ for s in t.segments],
            }, indent=2, ensure_ascii=False), encoding="utf-8")
            row = {
                "model": size, "call_id": script.call_id,
                "raw_wer": wer(script.reference_text, t.text, raw_text),
                "wer": wer(script.reference_text, t.text),
                "audio_s": t.audio_seconds, "latency_s": t.latency, "rtf": t.rtf,
                "errors": top_errors(script.reference_text, t.text),
            }
            rows.append(row)
            print(f"{size:6} {script.call_id}  WER {row['wer']:.1%}  (raw {row['raw_wer']:.1%})  "
                  f"{t.latency:.1f}s / {t.audio_seconds:.0f}s ses")
    return rows


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def write_report(rows: list[dict], path: Path = REPORT_PATH) -> None:
    models = list(dict.fromkeys(r["model"] for r in rows))
    lines = [
        "# STT WER Report",
        "",
        f"Generated {date.today().isoformat()} by `python -m src.eval_stt`. "
        "Engine: faster-whisper, CPU, int8, English, beam size 5. "
        f"Audio: {len({r['call_id'] for r in rows})} synthetic calls generated with gTTS (two accents).",
        "",
        f"Target (CLAUDE.md 11.3): **WER < {WER_TARGET:.0%}**. "
        "*Normalized WER* spells out digits before scoring (\"$950\" → \"nine hundred and fifty dollars\"); "
        "*raw WER* only lowercases and strips punctuation.",
        "",
        "## Model comparison",
        "",
        "| Model | Normalized WER | Raw WER | Avg latency / call | RTF | Target |",
        "|---|---|---|---|---|---|",
    ]
    for m in models:
        mr = [r for r in rows if r["model"] == m]
        avg_wer = _mean(r["wer"] for r in mr)
        rtf = sum(r["latency_s"] for r in mr) / sum(r["audio_s"] for r in mr)
        lines.append(
            f"| {m} | {avg_wer:.1%} | {_mean(r['raw_wer'] for r in mr):.1%} | "
            f"{_mean(r['latency_s'] for r in mr):.1f}s | {rtf:.2f} | "
            f"{'✅ met' if avg_wer < WER_TARGET else '❌ missed'} |")
    lines += ["", "RTF = processing time / audio duration (below 1 = faster than real time).", ""]
    for m in models:
        lines += [f"## Per call — {m}", "",
                  "| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |",
                  "|---|---|---|---|---|---|"]
        for r in (r for r in rows if r["model"] == m):
            errs = "; ".join(r["errors"]).replace("|", "/") or "—"
            lines.append(f"| {r['call_id']} | {r['wer']:.1%} | {r['raw_wer']:.1%} | "
                         f"{r['audio_s']:.0f}s | {r['latency_s']:.1f}s | {errs} |")
        lines.append("")
    # keep the hand-written analysis below the marker across regenerations
    manual = ""
    if path.exists() and MANUAL_MARKER in (old := path.read_text(encoding="utf-8")):
        manual = old[old.index(MANUAL_MARKER):]
    path.write_text("\n".join(lines) + "\n" + manual, encoding="utf-8")
    print(f"\nReport written: {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["tiny", "base", "small"])
    args = parser.parse_args()
    write_report(run(args.models))


if __name__ == "__main__":
    main()
