# Call Brief accuracy

Generated 2026-10-15 by `python -m src.eval_call_brief`. Model: `gpt-4o-mini`, prompt `v4` (temperature 0, strict function calling). Input: faster-whisper `base` transcripts (no speaker labels). Ground truth: `docs/eval/call_brief_ground_truth.csv` (9 calls).

| Metric | Result | Target (85%) |
|---|---|---|
| Disposition accuracy | 89% | ✅ |
| Sentiment accuracy | 78% | ❌ |
| Both correct | 67% | ❌ |

Cost: $0.00192 total, $0.00021 per call (avg 976 input / 112 output tokens). Average latency: 1.7s per call.

| Call | Disposition (truth → predicted) | Sentiment (truth → predicted) | Key topics |
|---|---|---|---|
| call_01 | teklif_kabul | pozitif | pricing, growth package, consulting sessions |
| call_02 | vazgecti | notr | growth package, refund policy, cancellation |
| call_03 | dusunecek | notr | consulting process, discovery call, pricing, session format |
| call_04 | sikayet_cozuldu | **notr → pozitif** | action plan, extra session, email address correction |
| call_05 | dusunecek | notr | growth package, monthly retainer, staff hiring, pricing strategy |
| call_06 | teklif_kabul | pozitif | monthly retainer, pricing, session scheduling |
| call_07 | dusunecek | **negatif → notr** | pricing, member retention, consulting package |
| call_08 | vazgecti | negatif | cancellation policy, refund, client dissatisfaction |
| call_09 | **bilgi_talebi → sikayet_cozuldu** | pozitif | session rescheduling, invoice due dates, email support |

## Summaries

- **call_01:** Sarah Mitchell, a small bakery owner, called Elena Ward to inquire about consulting prices. After discussing the options, Sarah decided to sign up for the growth package and pay upfront. The call ended with Elena confirming the details and expressing her eagerness to work with Sarah.
- **call_02:** David Chen called to cancel his growth package due to his company being acquired by a larger firm. The call ended with Elena confirming the cancellation and processing a pro-rata refund for the unused sessions.
- **call_03:** Mark Daniels called to inquire about the consulting process for his landscaping company. He learned about the steps involved, including a free discovery call and the subsequent sessions, but decided to collect more information before making a decision. The call ended with Mark requesting an overview of the process and pricing to be sent to his email.
- **call_04:** Priya Sharma called Elena Ward to express her frustration about not receiving an action plan that was promised within five business days after their kickoff session. Elena acknowledged the mistake, apologized, and offered to send the plan to the correct email address while also providing an extra session at no cost to help Priya and her business partner. The call ended positively with Priya agreeing to the extra session and thanking Elena for addressing the issue.
- **call_05:** Tom Becker called Elena Ward to discuss options for his accounting practice, specifically between a growth package and a monthly retainer. He decided to consult with his wife about the budget and requested a comparison email to help with his decision. The call ended with Tom indicating he would likely get back to Elena by the end of the next week.
- **call_06:** Laura Kim called Elena Ward to request more regular support after a successful strategy session. They agreed on a monthly retainer for $600, which includes two sessions per month and email support. The call ended with Laura excited about starting the retainer and scheduling their first session.
- **call_07:** James Porter called to discuss the pricing of a consulting package for his fitness studio, expressing concern that the cost was higher than expected. The call ended with James deciding to think about the options presented and not committing to any service at this time.
- **call_08:** Rachel Green called to inquire about a $79 invoice for a late cancellation fee. After discussing the policy and expressing her dissatisfaction, Rachel decided to cancel her remaining sessions and requested a refund. The call ended with the consultant agreeing to send the refund details via email.
- **call_09:** Michael Torres called Elena Ward to reschedule a session due to an upcoming vacation and to ask about invoice due dates and email support while away. The call ended with the session successfully rescheduled and Michael satisfied with the information provided.

<!-- manual analysis below: kept when the report is regenerated -->

## Label decision (2026-10-15)

call_03 was relabelled from `bilgi_talebi` to `dusunecek`: a prospect who wants more information before
deciding still needs a follow-up, so it is a pending sale. `bilgi_talebi` is now reserved for calls where
no purchase decision is pending (e.g. an existing client's questions about invoices or scheduling).
Prompt v4 adds this definition. v1–v3 below are re-scored against the corrected label.

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

## Remaining errors (v4, gpt-4o-mini)

| Call | Truth → predicted | Analysis |
|---|---|---|
| call_09 | bilgi_talebi → sikayet_cozuldu | Model error. No complaint in the call; rescheduling a session is read as a resolved problem. |
| call_04 | notr → pozitif | Debatable. The customer ends with "Thank you for owning the mistake, I appreciate it." |
| call_07 | negatif → notr | Missed by both models. A polite, unresolved price objection is rated neutral. |

## Status against the Definition of Done

Disposition 89% meets the ≥ 85% target; sentiment 78% does not. With 9 calls each error is 11 points and
results flip between prompt versions, so the numbers are not yet reliable. Next step: a larger, held-out
test set (new scripts never used for prompt tuning); the 9 original calls become the dev set.
