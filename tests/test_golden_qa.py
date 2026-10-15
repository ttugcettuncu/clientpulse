import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = list(csv.DictReader((ROOT / "docs/eval/golden_qa.csv").open(encoding="utf-8")))
CORPUS = ROOT / "data/corpus"


def test_ids_are_unique_and_types_valid():
    assert len({r["id"] for r in GOLDEN}) == len(GOLDEN) >= 15
    assert {r["type"] for r in GOLDEN} == {"single_fact", "multi_fact", "unanswerable"}


def test_source_docs_exist_and_unanswerable_has_none():
    for row in GOLDEN:
        docs = [d for d in row["source_docs"].split(";") if d]
        if row["type"] == "unanswerable":
            assert not docs and not row["key_facts"], row["id"]
        else:
            assert docs and row["key_facts"], row["id"]
            assert all((CORPUS / d).is_file() for d in docs), row["id"]
