# Call Brief accuracy

Generated 2026-10-15 by `python -m src.eval_call_brief`. Model: `gpt-4o-mini`, prompt `v3` (temperature 0, strict function calling). Input: faster-whisper `base` transcripts (no speaker labels). Ground truth: `docs/eval/call_brief_ground_truth.csv` (9 calls).

| Metric | Result | Target (85%) |
|---|---|---|
| Disposition accuracy | 78% | ❌ |
| Sentiment accuracy | 78% | ❌ |
| Both correct | 67% | ❌ |

Cost: $0.00186 total, $0.00021 per call (avg 938 input / 110 output tokens). Average latency: 1.5s per call.

| Call | Disposition (truth → predicted) | Sentiment (truth → predicted) | Key topics |
|---|---|---|---|
| call_01 | teklif_kabul | pozitif | pricing, growth package, consulting services |
| call_02 | vazgecti | notr | growth package, refund policy, cancellation |
| call_03 | **bilgi_talebi → dusunecek** | notr | consulting process, discovery call, pricing, scheduling |
| call_04 | **sikayet_cozuldu → teklif_kabul** | **notr → pozitif** | action plan, extra session, email address correction |
| call_05 | dusunecek | notr | growth package, monthly retainer, staff hiring, pricing strategy |
| call_06 | teklif_kabul | pozitif | monthly retainer, payment details, session scheduling |
| call_07 | dusunecek | **negatif → notr** | pricing, member retention, consulting package |
| call_08 | vazgecti | negatif | cancellation policy, refund, client dissatisfaction |
| call_09 | bilgi_talebi | pozitif | session rescheduling, invoice due dates, email support |

## Summaries

- **call_01:** Sarah Mitchell, a small bakery owner, called Elena Ward to inquire about consulting prices. After discussing the options, Sarah decided to sign up for the growth package and pay upfront. The call ended with Elena confirming the details and expressing her eagerness to work with Sarah.
- **call_02:** David Chen called to cancel his growth package due to his company being acquired by a larger firm. The call ended with Elena confirming the cancellation and processing a pro-rata refund for the unused sessions.
- **call_03:** Mark Daniels called to inquire about the consulting process for his landscaping company. He received detailed information about the steps involved and requested an overview of the process and pricing to be emailed to him. The call ended with Mark expressing appreciation for the clarity of the information provided.
- **call_04:** Priya Sharma called Elena Ward to express her frustration about not receiving an action plan that was promised within five business days after their kickoff session. Elena acknowledged the mistake, apologized, and offered to send the plan to the correct email address while also providing an extra session at no cost to help Priya and her business partner. The call ended positively with Priya agreeing to the extra session and thanking Elena for addressing the issue.
- **call_05:** Tom Becker called Elena Ward to discuss options for his accounting practice, specifically between a growth package and a monthly retainer. He decided to consult with his wife about the budget and requested a comparison email to help with his decision. The call ended with Tom indicating he would likely get back to Elena by the end of the next week.
- **call_06:** Laura Kim called Elena Ward to request more regular support after a successful strategy session. They agreed on a monthly retainer for $600, which includes two sessions per month and email support. The call ended with Laura excited about starting the retainer and scheduling their first session.
- **call_07:** James Porter called to discuss the pricing of a consulting package for his fitness studio, expressing concern that the cost was higher than expected. The call ended with James deciding to think about the options presented and not committing to any service at that moment.
- **call_08:** Rachel Green called to inquire about a $79 invoice for a late cancellation fee. After discussing the policy and expressing her dissatisfaction, she decided to cancel her remaining sessions and requested a refund. The call ended with the consultant agreeing to send the refund details via email.
- **call_09:** Michael Torres called Elena Ward to reschedule a session planned for the day of his vacation and to ask about invoice due dates and email support while he is away. The call ended with Michael confirming the new session time and expressing gratitude for the flexibility offered.

<!-- manual analysis below: kept when the report is regenerated -->

## Prompt iterations

All runs: same 9 STT transcripts, `gpt-4o-mini`, temperature 0. Briefs per version are cached in
`data/synthetic_calls/briefs/<version>/`.

| Prompt | Change | Disposition | Sentiment | Both | Cost / call |
|---|---|---|---|---|---|
| v1 | Label definitions only | 78% | 56% | 44% | $0.00017 |
| v2 | "Politeness is not sentiment"; rescheduling / free make-up session is not a purchase | 78% | 78% | 67% | $0.00019 |
| v3 | `outcome_evidence` sentence before the label; disposition rules applied in a fixed order | 78% | 78% | 67% | $0.00021 |

v1 failure pattern: every sentiment error was a shift towards `pozitif`. The customers in the scripts
are polite, and the model read polite closings ("thank you, good luck") as satisfaction. v2 fixed 3 of the 4.

## Remaining errors (v3)

| Call | Truth → predicted | Analysis |
|---|---|---|
| call_04 | sikayet_cozuldu → teklif_kabul | Model error. Its own evidence says "agreed to an extra session at no cost", yet it still picks the purchase label. The pattern service + calendar slot + "yes" outweighs the written rule. |
| call_03 | bilgi_talebi → dusunecek | Label ambiguity. The prospect says he wants to "collect more information" before deciding, which fits both definitions. Fixed in v3's rule order for call_09, broken here. |
| call_04 | notr → pozitif | Debatable. The customer ends with "Thank you for owning the mistake, I appreciate it." |
| call_07 | negatif → notr | Model error. A price objection that is not resolved is rated neutral. |

## Status against the Definition of Done

Target ≥ 85% is **not met** (78% disposition, 78% sentiment). With 9 calls, each error is 11 points, so
85% means at most one error per field. Tuning the prompt further on the same 9 calls would overfit the
test set, so iteration stopped at v3. Next options:

1. Clarify the label definitions (e.g. is "wants more information before deciding" `bilgi_talebi` or `dusunecek`?) and relabel the ground truth if needed.
2. Grow the eval set (more scripts, or a CallCenterEN subset) and keep a separate dev split for prompt tuning.
3. Quality comparison with a larger model (`gpt-4o`) on the same 9 calls, as allowed by CLAUDE.md Bölüm 9 (~$0.03).
