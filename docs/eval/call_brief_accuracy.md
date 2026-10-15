# Call Brief accuracy

Generated 2026-10-15 by `python -m src.eval_call_brief`. Model: `gpt-4o-mini`, prompt `v5` (temperature 0, strict function calling). Input: faster-whisper `base` transcripts (no speaker labels). Ground truth: `docs/eval/call_brief_ground_truth.csv` (21 calls).

**dev** calls were used to tune the prompt. **test** calls were never used for tuning, so the test score is the one that counts against the target.

| Split | Calls | Disposition | Sentiment | Both correct |
|---|---|---|---|---|
| dev | 9 | 100% ✅ | 78% ❌ | 78% |
| test | 12 | 75% ❌ | 67% ❌ | 50% |

Target: ≥ 85% (CLAUDE.md 11.3). Cost: $0.00434 total, $0.00021 per call (avg 938 input / 110 output tokens). Average latency: 1.6s per call.

| Call | Split | Disposition (truth → predicted) | Sentiment (truth → predicted) | Key topics |
|---|---|---|---|---|
| call_01 | dev | teklif_kabul | pozitif | pricing, growth package, consulting sessions |
| call_02 | dev | vazgecti | notr | growth package, refund process, cancellation, action plan |
| call_03 | dev | dusunecek | notr | consulting process, discovery call, pricing, session format |
| call_04 | dev | sikayet_cozuldu | **notr → pozitif** | action plan, email address, extra session |
| call_05 | dev | dusunecek | notr | growth package, monthly retainer, budget consultation |
| call_06 | dev | teklif_kabul | pozitif | monthly retainer, pricing, session scheduling |
| call_07 | dev | dusunecek | **negatif → notr** | pricing, member retention, consulting package |
| call_08 | dev | vazgecti | negatif | cancellation policy, refund, client dissatisfaction |
| call_09 | dev | bilgi_talebi | pozitif | session rescheduling, invoice due dates, payment methods, email support |
| call_10 | test | teklif_kabul | **notr → pozitif** | strategy session, quoting process, payment method |
| call_11 | test | teklif_kabul | pozitif | growth package, scheduling, pricing, monthly payments |
| call_12 | test | dusunecek | pozitif | growth package, business partner approval, service plans |
| call_13 | test | dusunecek | notr | growth package, monthly retainer, consultant comparison |
| call_14 | test | **red → dusunecek** | **negatif → notr** | consulting package, business growth, customer skepticism |
| call_15 | test | vazgecti | negatif | cancellation process, service dissatisfaction, pricing |
| call_16 | test | **red → vazgecti** | notr | growth package, office manager, consulting services |
| call_17 | test | bilgi_talebi | **notr → pozitif** | growth package, invoice details, payment method |
| call_18 | test | bilgi_talebi | pozitif | sales performance, next session preparation, email support |
| call_19 | test | **bilgi_talebi → dusunecek** | negatif | rescheduling policy, session options, client meeting |
| call_20 | test | sikayet_cozuldu | pozitif | written summary, follow-up call, strategy session |
| call_21 | test | sikayet_cozuldu | **notr → pozitif** | double charge, refund, payment confirmation |

## Summaries

- **call_01:** Sarah Mitchell, a small bakery owner, called to inquire about consulting prices. She decided to sign up for the growth package, agreeing to pay $950 upfront. The call ended positively with Sarah expressing her satisfaction and looking forward to working together.
- **call_02:** David Chen called to cancel his growth package due to his company being acquired by a larger firm. The call ended with David understanding the refund process and confirming the cancellation of his package.
- **call_03:** Mark Daniels called to inquire about the consulting process for his landscaping company. He learned about the steps involved, including a free discovery call and the subsequent sessions, but decided he was not ready to sign up yet. The call ended with Mark requesting an email overview of the process and pricing.
- **call_04:** Priya Sharma called Elena Ward to express her frustration about not receiving an action plan that was promised within five business days after their kickoff session. Elena acknowledged the mistake, explained the situation, and offered to send the plan to the correct email address while also providing an extra session at no cost. The call ended positively with Priya agreeing to the extra session and thanking Elena for addressing the issue.
- **call_05:** Tom Becker called Elena Ward to discuss options for his accounting practice, specifically between a growth package and a monthly retainer. He decided to consult with his wife about the budget and requested a comparison email to help with his decision. The call ended with Tom indicating he would likely get back to Elena by the end of next week.
- **call_06:** Laura Kim called Elena Ward to request more regular support after a successful strategy session. Laura decided to start a monthly retainer for $600, which includes two sessions per month and email support. The call ended with Laura expressing excitement about the new arrangement.
- **call_07:** James Porter called to discuss the pricing of a consulting package for his fitness studio, expressing concern that the cost was higher than expected. The call ended with James deciding to think about the options presented and not committing to any service at this time.
- **call_08:** Rachel Green called to inquire about a $79 invoice for a late cancellation fee. After discussing the policy and expressing her dissatisfaction, Rachel decided to cancel her remaining sessions and requested a refund. The call ended with the consultant agreeing to send the refund details via email.
- **call_09:** Michael Torres called Elena Ward to reschedule a session planned for the day of his vacation and to ask about invoice due dates and payment methods. The call ended with Michael confirming the new session time and expressing gratitude for the flexibility offered.
- **call_10:** Greg Holloway from Holloway Plumbing called to book a strategy session focused on improving his quoting process. The call ended with Greg confirming the session for Wednesday at 10 and agreeing to pay via bank transfer.
- **call_11:** Nadia Flores called Elena Ward seeking help for her fast-growing catering company, which is experiencing chaos in scheduling and pricing. By the end of the call, Nadia decided to purchase the growth package, opting for monthly payments due to tight cash flow.
- **call_12:** Owen Price called Elena Ward to discuss the growth package for his bicycle repair shop after their previous discovery call. He expressed enthusiasm about the service plans but mentioned needing his business partner's approval before proceeding. The call ended with Elena agreeing to send a summary of their discussion to help Owen's partner make a decision.
- **call_13:** Hannah Brooks, a small bookshop owner, called to inquire about the differences between the consultant's growth package and monthly retainer. The call ended with Hannah requesting an email overview of both options to compare before making a decision, and a follow-up call was scheduled for Friday.
- **call_14:** Victor Lane called Elena Ward seeking help for his two car washes, which have been experiencing flat revenue for two years. Despite discussing a consulting package, Victor expressed skepticism and decided to think about it without wanting further contact. The call ended amicably with well-wishes.
- **call_15:** Patrick Doyle called to cancel his retina service due to dissatisfaction with the results after eight sessions. The call ended with the consultant confirming the cancellation process and agreeing to send written confirmation.
- **call_16:** Sophia Marin called Alaina Ward to inform her that they will not proceed with the growth package for her dental practice, as they have decided to hire a full-time office manager instead. The call ended with Alaina offering a single session for process setup, but Sophia indicated they are not planning to work with a consultant at this time.
- **call_17:** Martin Kowalski called Elena Ward to ask administrative questions about his growth package, including the number of sessions left and invoice details. The call ended with Elena confirming the payment method for the upcoming invoice and Martin expressing satisfaction with the information provided.
- **call_18:** Grace Okafour called Elena Ward to share the news of her cafe's best month ever and to ask two questions regarding their next session. The call ended on a positive note with Grace expressing gratitude and confirming her next appointment.
- **call_19:** Ben Carter called to inquire about moving his session scheduled for Thursday due to a client meeting. The consultant explained the rescheduling fee and offered alternative options, but Ben expressed dissatisfaction with the policy and decided to check his calendar before making a decision. The call ended with Ben agreeing to inform the consultant of his choice by the next day.
- **call_20:** Chloe Bennett called Elena Ward regarding a written summary from a strategy session that she had not received on time. Elena apologized for the oversight, sent the summary during the call, and offered a free follow-up call to discuss it further. The call ended positively with Chloe confirming the follow-up appointment.
- **call_21:** Robert Hayes called to report being charged twice for his monthly retainer payment of $600. The consultant, Elena Ward, confirmed the error and assured him that a refund would be processed and a confirmation email sent. The call ended with Robert satisfied that the issue was resolved and no further problems were expected for the next payment.

<!-- manual analysis below: kept when the report is regenerated -->

## Label decision (2026-10-15)

call_03 was relabelled from `bilgi_talebi` to `dusunecek`: a prospect who wants more information before
deciding still needs a follow-up, so it is a pending sale. `bilgi_talebi` is now reserved for calls where
no purchase decision is pending (e.g. an existing client's questions about invoices or scheduling).
Prompt v4 adds this definition. v1–v3 below are re-scored against the corrected label.

New label `red` (prompt v5): a prospect who has never bought anything declines the offer or asks not to be
followed up (call_14, call_16). `vazgecti` is now reserved for an existing client who cancels a service
they already bought. Both test labels were set before any model output on the test set was seen.

## Prompt iterations (gpt-4o-mini)

All runs: same 9 STT transcripts, temperature 0. Briefs per version are cached in
`data/synthetic_calls/briefs/<version>/`.

| Prompt | Change | Disposition | Sentiment | Both | Cost / call |
|---|---|---|---|---|---|
| v1 | Label definitions only | 67% | 56% | 44% | $0.00017 |
| v2 | "Politeness is not sentiment"; rescheduling / free make-up session is not a purchase | 67% | 78% | 56% | $0.00019 |
| v3 | `outcome_evidence` sentence before the label; disposition rules applied in a fixed order | 89% | 78% | 78% | $0.00021 |
| v4 | `dusunecek` / `bilgi_talebi` boundary from the label decision above | 89% | 78% | 67% | $0.00022 |

v1 failure pattern: every sentiment error was a shift towards `pozitif`. The customers in the scripts
are polite, and the model read polite closings ("thank you, good luck") as satisfaction. v2 fixed 3 of the 4.

v3 → v4 shows the instability: call_04 flipped to correct (`sikayet_cozuldu`) while call_09 flipped to
wrong (`bilgi_talebi` → `sikayet_cozuldu`). Same score, different errors. On 9 calls this is noise, not signal.

## Model comparison: gpt-4o-mini vs gpt-4o (prompt v3)

| Model | Disposition | Sentiment | Both | Cost / call | Cost / 1,000 calls |
|---|---|---|---|---|---|
| gpt-4o-mini | 89% | 78% | 78% | $0.00021 | $0.21 |
| gpt-4o | 89% | 89% | 78% | $0.0036 | $3.55 |

Full gpt-4o run: `call_brief_accuracy_gpt-4o.md`. gpt-4o was 17× more expensive for one more correct
sentiment label. Its only disposition miss was call_03 (`bilgi_talebi`), the label whose definition was
unclear before v4, so that miss reflects the prompt, not model capacity. Both models rate call_07
(price objection, "I will think about it") as `notr` instead of `negatif`.

Decision: keep **gpt-4o-mini** as the default. The quality gap is within the noise of a 9-call set and
does not justify a 17× cost.

## Held-out test set (prompt v5, gpt-4o-mini)

12 new calls (call_10–call_21), written and labelled after prompt tuning had finished and never used to
tune it. They deliberately include hard boundary cases: a matter-of-fact purchase, an enthusiastic
prospect who still postpones, polite but unconvinced prospects, a happy client with only questions, an
annoyed client who only asks about options.

| Split | Calls | Disposition | Sentiment | Both |
|---|---|---|---|---|
| dev (used for tuning) | 9 | 100% | 78% | 78% |
| **test (held out)** | 12 | **75%** | **67%** | **50%** |

The dev-vs-test gap is the expected sign of prompt overfitting: the prompt was tuned on the 9 dev calls,
so its dev score is optimistic. **The test score is the real performance.**

### Test errors

| Call | Truth → predicted | Analysis |
|---|---|---|
| call_14 | red → dusunecek | The model's own evidence ("decided to think about it and requested not to be contacted") matches the `red` definition, but it picks another label. |
| call_16 | red → vazgecti | Same: evidence says the prospect "decided not to proceed and asked to be removed from the follow-up list". The model does not separate a prospect's decline from a client's cancellation. |
| call_19 | bilgi_talebi → dusunecek | Client will tell which rescheduling option he picks tomorrow; the model reads the pending choice as a pending purchase. |
| call_10 | notr → pozitif | Matter-of-fact purchase rated positive. |
| call_17 | notr → pozitif | Routine admin questions rated positive. |
| call_21 | notr → pozitif | Calm, resolved double charge rated positive. |
| call_14 | negatif → notr | Polite but unconvinced prospect rated neutral (same pattern as call_07 in dev). |

Patterns:
1. **`red` was never predicted** (0 of 21 calls), although the evidence sentences fit it. Hypothesis: the
   prompt is in English, where "red" is a colour, so the enum name works against its definition. A
   self-describing value (e.g. `teklif_reddedildi`) is the first thing to try.
2. **Sentiment is biased in two directions:** neutral calls with a good outcome become `pozitif` (3 errors),
   and polite negativity becomes `notr` (call_14, and call_07 in dev). The model rates the outcome and
   the tone of voice rather than the customer's attitude.

## Status against the Definition of Done

On the held-out test set the target (≥ 85%) is **not met**: disposition 75%, sentiment 67%.
The test set has now been seen, so any prompt change made in response to these errors must be checked on
a new held-out set; re-scoring on call_10–call_21 would no longer be an honest test.

Backlog for a later iteration (each to be measured on fresh calls):
- Self-describing label value instead of `red` (pattern 1).
- An evidence sentence for sentiment as well, quoting what the customer said, before the label (pattern 2).
- gpt-4o on the test set for comparison (~$0.045 for 12 calls).
