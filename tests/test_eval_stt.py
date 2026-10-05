import pytest

from src.eval_stt import normalized_text, raw_text, wer


def test_identical_text_has_zero_wer():
    assert wer("Hello, Elena Ward speaking.", "hello elena ward speaking") == 0


@pytest.mark.parametrize("written, spoken", [
    ("$950 upfront", "nine hundred and fifty dollars upfront"),
    ("up 20%", "up twenty percent"),
    ("call 555-0142", "call five five five, zero one four two"),
    ("Friday the 13th", "Friday the thirteenth"),
    ("48-hour notice", "forty-eight hour notice"),
])
def test_normalization_treats_digits_and_words_alike(written, spoken):
    assert normalized_text(written) == normalized_text(spoken)


def test_raw_wer_counts_number_formatting_as_errors():
    ref, hyp = "nine hundred and fifty dollars", "$950"
    assert wer(ref, hyp, raw_text) > 0
    assert wer(ref, hyp) == 0
