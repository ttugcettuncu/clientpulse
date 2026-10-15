"""STT layer: audio file -> transcript, with local faster-whisper.

Runs on CPU with int8 quantization (no CUDA runtime on the dev machine);
it switches to the GPU automatically if one becomes available. Every run
is logged to SQLite as step='stt' with cost 0 (local model).

Diarization (who said what) is deferred to Phase 1b; the transcript has
no speaker labels.
"""
import time
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from src import db

DEFAULT_MODEL = "base"
_models: dict[str, WhisperModel] = {}


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    text: str
    segments: list[Segment]
    audio_seconds: float
    latency: float  # wall-clock processing time, seconds
    model: str

    @property
    def rtf(self) -> float:
        """Real-Time Factor: processing time / audio duration (lower is faster)."""
        return self.latency / self.audio_seconds if self.audio_seconds else 0.0


def get_model(size: str = DEFAULT_MODEL) -> WhisperModel:
    """Load a model once per process; loading takes seconds, transcribing reuses it."""
    if size not in _models:
        _models[size] = WhisperModel(size, device="auto", compute_type="int8")
    return _models[size]


def transcribe(
    audio_path: Path | str,
    model_size: str = DEFAULT_MODEL,
    call_id: str | None = None,
    db_path: Path | str = db.DEFAULT_DB_PATH,
) -> Transcript:
    audio_path = Path(audio_path)
    call_id = call_id or audio_path.stem
    model_name = f"faster-whisper-{model_size}"
    model = get_model(model_size)

    start = time.perf_counter()
    try:
        raw_segments, info = model.transcribe(str(audio_path), language="en", beam_size=5)
        segments = [Segment(s.start, s.end, s.text.strip()) for s in raw_segments]  # generator: runs here
    except Exception:
        db.log_step("stt", "error", call_id=call_id, model=model_name,
                    latency=time.perf_counter() - start, db_path=db_path)
        raise
    latency = time.perf_counter() - start

    db.log_step("stt", "ok", call_id=call_id, model=model_name, latency=latency, db_path=db_path)
    return Transcript(
        text=" ".join(s.text for s in segments),
        segments=segments,
        audio_seconds=info.duration,
        latency=latency,
        model=model_name,
    )
