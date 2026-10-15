# STT WER Report

Generated 2026-10-15 by `python -m src.eval_stt`. Engine: faster-whisper, CPU, int8, English, beam size 5. Audio: 21 synthetic calls generated with gTTS (two accents).

Target (CLAUDE.md 11.3): **WER < 15%**. *Normalized WER* spells out digits before scoring ("$950" → "nine hundred and fifty dollars"); *raw WER* only lowercases and strips punctuation.

## Model comparison

| Model | Normalized WER | Raw WER | Avg latency / call | RTF | Target |
|---|---|---|---|---|---|
| tiny | 1.5% | 5.4% | 12.1s | 0.10 | ✅ met |
| base | 1.2% | 5.1% | 16.8s | 0.14 | ✅ met |
| small | 0.9% | 4.8% | 33.3s | 0.28 | ✅ met |

RTF = processing time / audio duration (below 1 = faster than real time).

## Per call — tiny

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 3.1% | 9.2% | 177s | 18.4s | ∅ → up; upfront → front; ∅ → dollars; card → cod; invoice is → invoices do; due → ∅ |
| call_02 | 1.6% | 6.8% | 151s | 16.3s | dollar → dollars; four → full; ∅ → up; upfront four → front for |
| call_03 | 2.9% | 7.6% | 144s | 15.1s | ∅ → question; questionnaire → i; makes → make; mark → mockdannialsatexamplecom; dot daniels at example dot com → ∅ |
| call_04 | 3.5% | 3.5% | 131s | 14.3s | ∅ → kick; kickoff → off; old → oldstudiocom; studio dot com → ∅; at → a; ∅ → and |
| call_05 | 2.1% | 4.6% | 138s | 15.1s | and → an; ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars |
| call_06 | 2.3% | 7.4% | 136s | 14.2s | it is → at his; ∅ → thousand; ∅ → hundred; one nine → and nineteen; and → in |
| call_07 | 0.9% | 8.3% | 146s | 16.0s | hoped → hope; ∅ → up; upfront → front |
| call_08 | 1.4% | 5.7% | 153s | 15.8s | are → a; dimed → dime; dollar → dollars; ∅ → all; alright → right |
| call_09 | 2.2% | 6.3% | 122s | 13.6s | hi → high; ∅ → may i; my accountant asked → count and test |
| call_10 | 0.5% | 6.8% | 89s | 9.4s | elena → alina |
| call_11 | 0.9% | 6.0% | 107s | 11.2s | and → in; calmer → karma |
| call_12 | 3.3% | 5.4% | 103s | 10.4s | jun → john; elena → alaina; and → in |
| call_13 | 0.0% | 5.1% | 96s | 8.9s | — |
| call_14 | 0.0% | 5.8% | 113s | 9.8s | — |
| call_15 | 2.3% | 4.3% | 108s | 11.1s | elena → alaina; cancel → council; and → in; would → with; hoped → hope |
| call_16 | 1.9% | 4.9% | 88s | 8.6s | sofia → sophia; call → called |
| call_17 | 0.5% | 3.6% | 89s | 8.3s | kowalski → kovolsky |
| call_18 | 2.0% | 2.0% | 92s | 9.8s | okafor → ocaffall; café → cafe; any → anytime; time → ∅ |
| call_19 | 0.0% | 4.4% | 97s | 10.1s | — |
| call_20 | 0.0% | 1.4% | 94s | 10.9s | — |
| call_21 | 0.0% | 3.7% | 83s | 7.4s | — |

## Per call — base

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 1.7% | 7.5% | 177s | 34.2s | ∅ → up; upfront → front; ∅ → dollars; mitchell → mitchellbakerycom; bakery dot com → ∅ |
| call_02 | 1.1% | 6.3% | 151s | 29.3s | dollar → dollars; ∅ → up; upfront → front |
| call_03 | 2.0% | 7.0% | 144s | 28.6s | makes → make; mark → markdannials; dot daniels → ∅; example → examplecom; dot com → ∅ |
| call_04 | 1.9% | 1.9% | 131s | 28.5s | old → oldstudiocom; studio dot com → ∅; ∅ → all; alright → right |
| call_05 | 2.4% | 4.9% | 138s | 29.3s | ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars; will do → well done |
| call_06 | 1.7% | 6.7% | 136s | 26.1s | ∅ → thousand; ∅ → hundred; one nine → and nineteen; and → in |
| call_07 | 2.0% | 9.1% | 146s | 28.0s | ∅ → a; elena ward → lane award; hoped → hope; ∅ → dollars; ∅ → all; alright → right |
| call_08 | 2.2% | 6.5% | 153s | 16.4s | cancelled → canceled; are → were; dimed → dime; dollar → dollars; ∅ → all; alright → right |
| call_09 | 0.7% | 4.9% | 122s | 12.6s | okay → ok; to → ∅ |
| call_10 | 0.0% | 6.8% | 89s | 9.2s | — |
| call_11 | 0.9% | 6.0% | 107s | 10.4s | ∅ → up; upfront → front |
| call_12 | 2.5% | 4.5% | 103s | 11.7s | jun → john; call → called |
| call_13 | 0.0% | 5.1% | 96s | 10.3s | — |
| call_14 | 0.0% | 5.8% | 113s | 10.6s | — |
| call_15 | 1.2% | 3.1% | 108s | 11.4s | retainer → retina; and → in; hoped → hope |
| call_16 | 2.4% | 5.3% | 88s | 9.3s | sofia → sophia; elena → alaina |
| call_17 | 0.0% | 3.1% | 89s | 9.7s | — |
| call_18 | 2.0% | 2.0% | 92s | 9.0s | okafor → okafour; café → cafe; any → anytime; time → ∅ |
| call_19 | 0.0% | 4.4% | 97s | 9.6s | — |
| call_20 | 0.5% | 1.9% | 94s | 10.4s | sent → send |
| call_21 | 0.0% | 3.2% | 83s | 7.7s | — |

## Per call — small

| Call | Normalized WER | Raw WER | Audio | Latency | Most frequent errors (ref → hyp) |
|---|---|---|---|---|---|
| call_01 | 1.2% | 7.1% | 177s | 54.7s | ∅ → dollars; mitchell → mitchellbakerycom; bakery dot com → ∅ |
| call_02 | 1.1% | 6.3% | 151s | 43.4s | dollar → dollars; ∅ → up; upfront → front |
| call_03 | 2.3% | 7.3% | 144s | 43.5s | elena → alayna; makes → make; mark → markdaniels; dot daniels → ∅; example → examplecom; dot com → ∅ |
| call_04 | 2.5% | 3.1% | 131s | 43.4s | elena → alayna; old → oldstudiocom; studio dot com → ∅; ∅ → all; alright → right |
| call_05 | 1.8% | 4.3% | 138s | 42.5s | ∅ → one thousand; eighteen → eight; ∅ → hundred and; ∅ → dollars |
| call_06 | 2.0% | 7.0% | 136s | 38.1s | elena → alayna; ∅ → thousand; ∅ → hundred; one nine → and nineteen |
| call_07 | 1.1% | 8.3% | 146s | 43.6s | price → pricelist; list → ∅; hoped → hope; ∅ → dollars |
| call_08 | 0.3% | 4.6% | 153s | 43.2s | dollar → dollars |
| call_09 | 0.0% | 4.1% | 122s | 33.4s | — |
| call_10 | 0.0% | 6.8% | 89s | 24.1s | — |
| call_11 | 0.0% | 5.6% | 107s | 26.9s | — |
| call_12 | 2.1% | 4.1% | 103s | 27.3s | jun → john |
| call_13 | 0.0% | 5.1% | 96s | 24.9s | — |
| call_14 | 0.4% | 6.2% | 113s | 28.3s | elena → alayna |
| call_15 | 0.4% | 2.3% | 108s | 32.1s | hoped → hope |
| call_16 | 1.5% | 4.4% | 88s | 24.7s | sofia → sophia |
| call_17 | 0.0% | 3.1% | 89s | 25.7s | — |
| call_18 | 1.5% | 1.5% | 92s | 26.4s | café → cafe; any → anytime; time → ∅ |
| call_19 | 0.4% | 4.9% | 97s | 27.0s | elena → alayna |
| call_20 | 0.5% | 1.9% | 94s | 26.7s | sent → send |
| call_21 | 0.5% | 3.7% | 83s | 20.5s | elena → alayna |

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
