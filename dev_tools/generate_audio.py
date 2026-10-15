"""turn the approved call scripts into audio with gTTS.

Each turn is synthesized separately: the consultant with a US English accent,
the customer with a British one, so the call sounds like two speakers. Turns
are joined with pydub and a short pause. Next to every call_NN.mp3 a
call_NN.segments.json records when each turn starts and ends — ground truth
for diarization (planned as Phase 1b).

Usage:  python -m dev_tools.generate_audio [--force]
Needs internet (gTTS) and ffmpeg on PATH (pydub mp3 export).
"""
import argparse
import io
import json
import time

from gtts import gTTS
from pydub import AudioSegment

from src.call_scripts import AUDIO_DIR, load_scripts

VOICES = {"consultant": "com", "customer": "co.uk"}  # gTTS tld -> accent
PAUSE_MS = 400
RETRIES = 3


def synthesize(text: str, tld: str) -> AudioSegment:
    for attempt in range(1, RETRIES + 1):
        try:
            buf = io.BytesIO()
            gTTS(text=text, lang="en", tld=tld).write_to_fp(buf)
            buf.seek(0)
            return AudioSegment.from_file(buf, format="mp3")
        except Exception as exc:  # gTTS raises on HTTP errors / rate limits
            if attempt == RETRIES:
                raise
            wait = 2 ** attempt
            print(f"  gTTS error ({exc}); retrying in {wait}s")
            time.sleep(wait)
    raise AssertionError("unreachable")


def build_call(script) -> tuple[AudioSegment, list[dict]]:
    audio = AudioSegment.silent(duration=0)
    pause = AudioSegment.silent(duration=PAUSE_MS)
    segments = []
    for turn in script.turns:
        clip = synthesize(turn.text, VOICES[turn.speaker])
        start = len(audio)
        audio += clip
        segments.append({"speaker": turn.speaker, "start": start / 1000,
                         "end": len(audio) / 1000, "text": turn.text})
        audio += pause
    return audio, segments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="regenerate existing files")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    total_s = 0.0
    produced = 0
    for script in load_scripts():
        mp3_path = AUDIO_DIR / f"{script.call_id}.mp3"
        if mp3_path.exists() and not args.force:
            duration = len(AudioSegment.from_file(mp3_path)) / 1000
            print(f"{script.call_id}: exists, skipped ({duration:.0f}s)")
            total_s += duration
            continue
        audio, segments = build_call(script)
        audio.export(mp3_path, format="mp3", bitrate="64k")
        (AUDIO_DIR / f"{script.call_id}.segments.json").write_text(
            json.dumps(segments, indent=2, ensure_ascii=False), encoding="utf-8")
        duration = len(audio) / 1000
        total_s += duration
        produced += 1
        print(f"{script.call_id}: {duration:.0f}s, {mp3_path.stat().st_size / 1024:.0f} KB")

    print(f"\n{produced} files generated; total audio {total_s / 60:.1f} min")


if __name__ == "__main__":
    main()
