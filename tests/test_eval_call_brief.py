import pytest

from src.call_brief import DISPOSITIONS, SENTIMENTS
from src.call_scripts import load_scripts
from src.eval_call_brief import SPLITS, load_ground_truth, score

GROUND_TRUTH = load_ground_truth()


def test_ground_truth_matches_script_labels():
    scripts = {s.call_id: s.metadata for s in load_scripts()}
    assert {r["call_id"] for r in GROUND_TRUTH} == set(scripts)
    for row in GROUND_TRUTH:
        meta = scripts[row["call_id"]]
        assert (row["disposition"], row["sentiment"]) == (meta["disposition"], meta["sentiment"]), row["call_id"]


def test_labels_and_splits_are_valid():
    for row in GROUND_TRUTH:
        assert row["disposition"] in DISPOSITIONS
        assert row["sentiment"] in SENTIMENTS
        assert row["split"] in SPLITS


def test_test_split_is_held_out_and_covers_every_label():
    test = [r for r in GROUND_TRUTH if r["split"] == "test"]
    assert len(test) >= 12
    assert {r["disposition"] for r in test} == set(DISPOSITIONS)
    assert {r["sentiment"] for r in test} == set(SENTIMENTS)


def test_score_counts_each_field_and_both():
    rows = [
        {"disposition": "vazgecti", "pred_disposition": "vazgecti", "sentiment": "notr", "pred_sentiment": "notr"},
        {"disposition": "vazgecti", "pred_disposition": "vazgecti", "sentiment": "notr", "pred_sentiment": "negatif"},
        {"disposition": "dusunecek", "pred_disposition": "bilgi_talebi", "sentiment": "notr", "pred_sentiment": "notr"},
        {"disposition": "dusunecek", "pred_disposition": "bilgi_talebi", "sentiment": "notr", "pred_sentiment": "pozitif"},
    ]
    assert score(rows) == {"disposition": 0.5, "sentiment": 0.5, "both": pytest.approx(0.25)}
