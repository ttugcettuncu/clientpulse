import pytest

from src.call_scripts import load_scripts, parse_script


def test_all_scripts_parse_with_metadata():
    scripts = load_scripts()
    assert len(scripts) >= 8
    for s in scripts:
        assert 15 <= len(s.turns) <= 30, s.call_id
        assert {t.speaker for t in s.turns} == {"consultant", "customer"}
        assert s.metadata["disposition"]
        assert s.metadata["sentiment"] in {"positive", "neutral", "negative"}


def test_reference_text_has_no_labels(tmp_path):
    path = tmp_path / "call_99.txt"
    path.write_text("CONSULTANT: Hello there.\nCUSTOMER: Hi.\n# disposition: customer_inquiry\n",
                    encoding="utf-8")
    script = parse_script(path)
    assert script.reference_text == "Hello there. Hi."
    assert script.metadata == {"disposition": "customer_inquiry"}


def test_unknown_label_is_rejected(tmp_path):
    path = tmp_path / "call_98.txt"
    path.write_text("AGENT: Hello.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown speaker label"):
        parse_script(path)
