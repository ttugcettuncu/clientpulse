# STT WER Report

Generated 2026-10-05 by `python -m src.eval_stt`. Engine: faster-whisper, CPU, int8, English, beam size 5. Audio: 9 synthetic calls generated with gTTS (two accents).

Target (CLAUDE.md 11.3): **WER < 15%**. *Normalized WER* spells out digits before scoring ("$950" → "nine hundred and fifty dollars"); *raw WER* only lowercases and strips punctuation.

## Model comparison

| Model | Normalized WER | Raw WER | Avg latency / call | RTF | Target |
|---|---|---|---|---|---|
| tiny | 2.2% | 6.6% | 9.8s | 0.07 | ✅ met |
| base | 1.7% | 6.1% | 14.8s | 0.10 | ✅ met |
| small | 1.4% | 5.8% | 73.8s | 0.51 | ✅ met |

RTF = processing time / audio duration (below 1 = faster than real time).

## Per call — tiny

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 3.1% | 9.2% | 177s | 10.3s | ∅ → up; upfront → front; ∅ → dollars; card → cod; invoice is → invoices do; due → ∅ |
| call_02 | 1.6% | 6.8% | 151s | 9.3s | dollar → dollars; four → full; ∅ → up; upfront four → front for |
| call_03 | 2.9% | 7.6% | 144s | 9.2s | ∅ → question; questionnaire → i; makes → make; mark → mockdannialsatexamplecom; dot daniels at example dot com → ∅ |
| call_04 | 3.5% | 3.5% | 131s | 7.9s | ∅ → kick; kickoff → off; old → oldstudiocom; studio dot com → ∅; at → a; ∅ → and |
| call_05 | 2.1% | 4.6% | 138s | 8.6s | and → an; ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars |
| call_06 | 2.3% | 7.4% | 136s | 9.0s | it is → at his; ∅ → thousand; ∅ → hundred; one nine → and nineteen; and → in |
| call_07 | 0.9% | 8.3% | 146s | 14.3s | hoped → hope; ∅ → up; upfront → front |
| call_08 | 1.4% | 5.7% | 153s | 11.5s | are → a; dimed → dime; dollar → dollars; ∅ → all; alright → right |
| call_09 | 2.2% | 6.3% | 122s | 8.2s | hi → high; ∅ → may i; my accountant asked → count and test |

## Per call — base

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 1.7% | 7.5% | 177s | 18.0s | ∅ → up; upfront → front; ∅ → dollars; mitchell → mitchellbakerycom; bakery dot com → ∅ |
| call_02 | 1.1% | 6.3% | 151s | 15.9s | dollar → dollars; ∅ → up; upfront → front |
| call_03 | 2.0% | 7.0% | 144s | 15.2s | makes → make; mark → markdannials; dot daniels → ∅; example → examplecom; dot com → ∅ |
| call_04 | 1.9% | 1.9% | 131s | 14.8s | old → oldstudiocom; studio dot com → ∅; ∅ → all; alright → right |
| call_05 | 2.4% | 4.9% | 138s | 14.8s | ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars; will do → well done |
| call_06 | 1.7% | 6.7% | 136s | 13.6s | ∅ → thousand; ∅ → hundred; one nine → and nineteen; and → in |
| call_07 | 2.0% | 9.1% | 146s | 14.3s | ∅ → a; elena ward → lane award; hoped → hope; ∅ → dollars; ∅ → all; alright → right |
| call_08 | 2.2% | 6.5% | 153s | 14.8s | cancelled → canceled; are → were; dimed → dime; dollar → dollars; ∅ → all; alright → right |
| call_09 | 0.7% | 4.9% | 122s | 11.5s | okay → ok; to → ∅ |

## Per call — small

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 1.2% | 7.1% | 177s | 79.8s | ∅ → dollars; mitchell → mitchellbakerycom; bakery dot com → ∅ |
| call_02 | 1.1% | 6.3% | 151s | 91.1s | dollar → dollars; ∅ → up; upfront → front |
| call_03 | 2.3% | 7.3% | 144s | 88.1s | elena → alayna; makes → make; mark → markdaniels; dot daniels → ∅; example → examplecom; dot com → ∅ |
| call_04 | 2.5% | 3.1% | 131s | 81.5s | elena → alayna; old → oldstudiocom; studio dot com → ∅; ∅ → all; alright → right |
| call_05 | 1.8% | 4.3% | 138s | 73.3s | ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars |
| call_06 | 2.0% | 7.0% | 136s | 73.3s | elena → alayna; ∅ → thousand; ∅ → hundred; one nine → and nineteen |
| call_07 | 1.1% | 8.3% | 146s | 83.9s | price → pricelist; list → ∅; hoped → hope; ∅ → dollars |
| call_08 | 0.3% | 4.6% | 153s | 52.9s | dollar → dollars |
| call_09 | 0.0% | 4.1% | 122s | 40.8s | — |

<!-- manual analysis below: kept when the report is regenerated -->
## Analysis (2026-10-05)

**Result:** every model is far below the 15% target (normalized WER 1.4–2.2%). **Default model: `base`**: it is only 0.3 points behind `small` but 5× faster (RTF 0.10, about 15 s per call on CPU).

**What the remaining "errors" are.** Most of them are about how a word is *written*, not what was *heard*:
- Formatting variants: "upfront" → "up front", "alright" → "all right", "okay" → "ok", "cancelled" → "canceled".
- Numbers said as words that the normalizer cannot match back: "eighteen hundred" → "1,800", "fifty dollar fee" → "$50 fee", card digits "four four one nine" → "4419".
- E-mail addresses: the model writes `sarah@mitchellbakery.com` while the script says "sarah at mitchell bakery dot com".

**Actual recognition errors** are rare and mostly about **names**: "Elena" → "Alayna" (small), "Elena Ward" → "lane award" (base). `tiny` adds a few acoustic mistakes ("my accountant asked" → "count and test", "hi" → "high").

**Raw vs normalized WER:** the gap (about 4.4 points) comes almost entirely from numbers and money amounts. This is why the ground truth needs a normalization step before scoring.

**Caveat (important):** this audio is clean text-to-speech: no background noise, no overlapping speech, full bandwidth. Real calls (8 kHz phone audio, noise, accents, people interrupting each other) give much higher WER. The numbers above are a **best case**. Next steps:
1. Add a degraded-audio test (8 kHz resampling + noise) to see how WER changes. Could be done in Faz 1b.
2. For Call Brief and PII masking (Faz 2), names, amounts and e-mails are exactly the error-prone fields. Masking must work on the STT format (`sarah@mitchellbakery.com`, `555-0142`), not on the spoken form.

**Hosted API** (see `stt_api_vs_local.md`): on this clean audio `whisper-1` and `gpt-4o-mini-transcribe` reach the same WER as local `base` (1.7% on call_01) and are faster (5–9 s vs 18 s on CPU), but cost $0.003–0.006/min. The local model stays the default; the API is the fallback when there is no GPU and latency matters.
