"""Smoke test for Görev 1.2: every script has a non-empty audio file."""
import json

import pytest
from pydub import AudioSegment

from src.call_scripts import AUDIO_DIR, load_scripts

SCRIPTS = load_scripts()


@pytest.mark.parametrize("script", SCRIPTS, ids=[s.call_id for s in SCRIPTS])
def test_audio_exists_and_matches_script(script):
    mp3 = AUDIO_DIR / f"{script.call_id}.mp3"
    if not mp3.exists():
        pytest.skip("audio not generated — run: python -m dev_tools.generate_audio")
    assert len(AudioSegment.from_file(mp3)) > 0

    segments = json.loads((AUDIO_DIR / f"{script.call_id}.segments.json").read_text(encoding="utf-8"))
    assert [s["text"] for s in segments] == [t.text for t in script.turns]
    assert all(s["end"] > s["start"] for s in segments)
