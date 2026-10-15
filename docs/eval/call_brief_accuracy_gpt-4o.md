# Call Brief accuracy

Generated 2026-10-15 by `python -m src.eval_call_brief`. Model: `gpt-4o`, prompt `v3` (temperature 0, strict function calling). Input: faster-whisper `base` transcripts (no speaker labels). Ground truth: `docs/eval/call_brief_ground_truth.csv` (9 calls).

| Metric | Result | Target (85%) |
|---|---|---|
| Disposition accuracy | 89% | ✅ |
| Sentiment accuracy | 89% | ✅ |
| Both correct | 78% | ❌ |

Cost: $0.03195 total, $0.00355 per call (avg 938 input / 120 output tokens). Average latency: 2.1s per call.

| Call | Disposition (truth → predicted) | Sentiment (truth → predicted) | Key topics |
|---|---|---|---|
| call_01 | teklif_kabul | pozitif | pricing, growth package, payment options, consulting services |
| call_02 | vazgecti | notr | cancellation, refund policy, growth package, company acquisition |
| call_03 | **dusunecek → bilgi_talebi** | notr | consulting process, discovery call, intake questionnaire, scheduling, pricing |
| call_04 | sikayet_cozuldu | notr | action plan delay, email address error, compensation offer, scheduling extra session |
| call_05 | dusunecek | notr | growth package, monthly retainer, pricing, budget discussion |
| call_06 | teklif_kabul | pozitif | monthly retainer, online store growth, payment method, session scheduling |
| call_07 | dusunecek | **negatif → notr** | pricing, growth package, member retention, payment options |
| call_08 | vazgecti | negatif | cancellation fee, refund policy, client dissatisfaction, session cancellation |
| call_09 | bilgi_talebi | pozitif | session rescheduling, invoice payment terms, email support |

## Summaries

- **call_01:** Sarah Mitchell, who runs a small bakery, called to inquire about the consultant's pricing options. After discussing the available packages, Sarah decided to sign up for the growth package and agreed to pay upfront. The call ended with the consultant confirming the email address to send the invoice and questionnaire.
- **call_02:** David Chen called to cancel his growth package with Elena Ward because his company is being acquired by a larger firm with their own advisors. Elena explained the refund policy and processed a pro-rata refund for the unused sessions, minus an admin fee. The call ended with David accepting the terms and expressing appreciation for the action plan provided.
- **call_03:** Mark Daniels called Elena Ward to inquire about her consulting process, as he had never worked with a consultant before. Elena explained the steps involved, including a free discovery call, an intake questionnaire, and a kickoff session. The call ended with Mark requesting an email overview of the process and prices.
- **call_04:** Priya Sharma called Elena Ward, expressing frustration over not receiving an action plan within the promised timeframe. Elena apologized for the oversight, explained the mistake, and offered a free extra session as compensation. The call ended with Priya agreeing to the proposed solution and scheduling the additional session.
- **call_05:** Tom Becker called Elena Ward to discuss options for his accounting practice, specifically between a growth package and a monthly retainer. They discussed the differences and costs of each option, and Tom decided to consult with his wife about the budget before making a decision.
- **call_06:** Laura Kim called Elena Ward to discuss ongoing support for her online store after a successful strategy session. Laura was pleased with the previous results and decided to start a monthly retainer for regular support. The call ended with Elena agreeing to send a secure payment link and scheduling the first session.
- **call_07:** James Porter called to discuss the pricing of consulting services for his fitness studio, expressing concern over the cost of the growth package. The consultant offered alternatives, including a single strategy session and a free discovery call, but James decided to think about it due to budget constraints.
- **call_08:** Rachel Green called Elena Ward to inquire about a $79 invoice for a late cancellation fee. Despite Rachel's explanation that the cancellation was due to her daughter's illness, Elena explained her policy and offered to apply the fee as credit toward a future session. Rachel was dissatisfied with this resolution and decided to cancel her remaining sessions.
- **call_09:** Michael Torres called to reschedule a session due to an upcoming vacation and to inquire about invoice payment terms and email support during his absence. The call ended with the consultant accommodating the schedule change and clarifying the payment and support details.

<!-- manual analysis below: kept when the report is regenerated -->
