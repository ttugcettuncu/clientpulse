"""Reads the synthetic call scripts in data/synthetic_calls/scripts/.

Script format: one turn per line, prefixed with a speaker label
(CONSULTANT: or CUSTOMER:). Lines starting with '#' are metadata, e.g.
'# disposition: offer_accepted'.
"""
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "data" / "synthetic_calls" / "scripts"
AUDIO_DIR = PROJECT_ROOT / "data" / "synthetic_calls" / "audio"

SPEAKERS = {"CONSULTANT": "consultant", "CUSTOMER": "customer"}


@dataclass
class Turn:
    speaker: str  # "consultant" or "customer"
    text: str


@dataclass
class CallScript:
    call_id: str
    turns: list[Turn]
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def reference_text(self) -> str:
        """Full spoken text, without speaker labels — the WER ground truth."""
        return " ".join(turn.text for turn in self.turns)


def parse_script(path: Path) -> CallScript:
    turns: list[Turn] = []
    metadata: dict[str, str] = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            key, _, value = line.lstrip("#").partition(":")
            metadata[key.strip()] = value.strip()
            continue
        label, sep, text = line.partition(":")
        if not sep or label not in SPEAKERS:
            raise ValueError(f"{path.name}:{line_no}: unknown speaker label in {line!r}")
        turns.append(Turn(speaker=SPEAKERS[label], text=text.strip()))
    if not turns:
        raise ValueError(f"{path.name}: no turns found")
    return CallScript(call_id=path.stem, turns=turns, metadata=metadata)


def load_scripts(scripts_dir: Path = SCRIPTS_DIR) -> list[CallScript]:
    return [parse_script(p) for p in sorted(scripts_dir.glob("call_*.txt"))]
