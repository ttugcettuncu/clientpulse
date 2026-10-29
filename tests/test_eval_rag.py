from src.eval_rag import is_correct, normalize


def test_normalize_ignores_case_and_hyphens():
    assert normalize("In-person  meetings") == "in person meetings"


def test_answerable_needs_every_key_fact():
    row = {"type": "single_fact", "key_facts": "$180;90"}
    assert is_correct(row, {"answerable": True, "answer": "It costs $180 for 90 minutes."})
    assert not is_correct(row, {"answerable": True, "answer": "It costs $180."})
    assert not is_correct(row, {"answerable": False, "answer": "$180 90"})


def test_unanswerable_needs_a_refusal():
    row = {"type": "unanswerable", "key_facts": ""}
    assert is_correct(row, {"answerable": False, "answer": "The documents do not contain this information."})
    assert not is_correct(row, {"answerable": True, "answer": "Ten years."})
