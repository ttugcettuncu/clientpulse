"""one call through OpenAI's hosted STT vs local faster-whisper.

Approved spend for this experiment: $0.05 (checked before every call, on top
of the global BudgetGuard limit). Cost is recorded only for successful calls.

Usage:  python -m dev_tools.stt_api_compare [--call call_01]
Run `python -m src.eval_stt` first so the local transcripts exist.
"""
import argparse
import json
import time
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

from src import db
from src.budget_guard import PRICE, BudgetGuard
from src.call_scripts import AUDIO_DIR, PROJECT_ROOT, SCRIPTS_DIR, parse_script
from src.eval_stt import TRANSCRIPTS_DIR, raw_text, wer

API_MODELS = ["whisper-1", "gpt-4o-mini-transcribe"]
LOCAL_MODELS = ["tiny", "base", "small"]
EXPERIMENT_CAP = 0.05  # USD, approved by the user on 2026-10-05
REPORT_PATH = PROJECT_ROOT / "docs" / "eval" / "stt_api_vs_local.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--call", default="call_01")
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    client = OpenAI()
    guard = BudgetGuard()
    script = parse_script(SCRIPTS_DIR / f"{args.call}.txt")
    audio_path = AUDIO_DIR / f"{args.call}.mp3"
    minutes = len(AudioSegment.from_file(audio_path)) / 60_000

    rows = []
    for size in LOCAL_MODELS:
        local = json.loads((TRANSCRIPTS_DIR / size / f"{args.call}.json").read_text(encoding="utf-8"))
        rows.append({"engine": f"faster-whisper {size} (local, CPU)", "text": local["text"],
                     "latency": local["latency"], "cost": 0.0})

    experiment_spent = 0.0
    for model in API_MODELS:
        estimated = minutes * PRICE[model]["per_minute"]
        if experiment_spent + estimated > EXPERIMENT_CAP:
            print(f"{model}: skipped — would exceed the approved experiment cap ${EXPERIMENT_CAP}")
            continue
        guard.check(upcoming_cost=estimated)
        start = time.perf_counter()
        try:
            with audio_path.open("rb") as f:
                result = client.audio.transcriptions.create(model=model, file=f, language="en")
        except Exception as exc:
            db.log_step("stt", "error", call_id=args.call, model=model,
                        latency=time.perf_counter() - start)
            print(f"{model}: error — {exc}")
            continue
        latency = time.perf_counter() - start
        cost = guard.record_audio(minutes, model=model, step="stt", call_id=args.call, latency=latency)
        experiment_spent += cost
        rows.append({"engine": f"OpenAI {model} (API)", "text": result.text,
                     "latency": latency, "cost": cost})
        print(f"{model}: {latency:.1f}s, ${cost:.4f}")

    for r in rows:
        r["wer"] = wer(script.reference_text, r["text"])
        r["raw_wer"] = wer(script.reference_text, r["text"], raw_text)
        print(f"{r['engine']:40} WER {r['wer']:.1%} (raw {r['raw_wer']:.1%})")

    lines = [
        "# STT: OpenAI API vs local faster-whisper",
        "",
        f"Generated {date.today().isoformat()} by `python -m dev_tools.stt_api_compare`. "
        f"Audio: `{args.call}.mp3` ({minutes:.2f} min, synthetic gTTS speech). "
        f"Experiment spend: ${experiment_spent:.4f} (approved cap ${EXPERIMENT_CAP}).",
        "",
        "| Engine | Normalized WER | Raw WER | Processing time | Cost | Cost / 1,000 min |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        per_1000 = r["cost"] / minutes * 1000
        lines.append(f"| {r['engine']} | {r['wer']:.1%} | {r['raw_wer']:.1%} | "
                     f"{r['latency']:.1f}s | ${r['cost']:.4f} | ${per_1000:.2f} |")
    lines += [
        "",
        "Local latency is CPU time on the dev laptop (no GPU); API latency includes upload and network.",
        "Local cost excludes hardware and electricity.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport written: {REPORT_PATH.relative_to(PROJECT_ROOT)}  |  total spend: ${guard.spent:.4f}")


if __name__ == "__main__":
    main()
