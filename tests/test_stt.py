import sqlite3

import pytest

from src import stt
from src.call_scripts import AUDIO_DIR, SCRIPTS_DIR, parse_script
from src.eval_stt import wer

SAMPLE = AUDIO_DIR / "call_09.mp3"


@pytest.mark.skipif(not SAMPLE.exists(), reason="audio not generated")
def test_transcribe_sample_call_and_log(tmp_path):
    db_path = tmp_path / "test.db"
    t = stt.transcribe(SAMPLE, model_size="tiny", db_path=db_path)

    assert t.segments and t.text
    assert t.audio_seconds > 60
    reference = parse_script(SCRIPTS_DIR / "call_09.txt").reference_text
    assert wer(reference, t.text) < 0.15  # CLAUDE.md 11.3 target

    rows = sqlite3.connect(db_path).execute("SELECT step, status, model, cost, latency FROM calls").fetchall()
    assert rows == [("stt", "ok", "faster-whisper-tiny", 0.0, pytest.approx(t.latency))]


def test_failed_transcription_is_logged_as_error(tmp_path):
    db_path = tmp_path / "test.db"
    bad = tmp_path / "not_audio.mp3"
    bad.write_text("this is not audio")
    with pytest.raises(Exception):
        stt.transcribe(bad, model_size="tiny", db_path=db_path)
    rows = sqlite3.connect(db_path).execute("SELECT step, status, cost FROM calls").fetchall()
    assert rows == [("stt", "error", 0.0)]
