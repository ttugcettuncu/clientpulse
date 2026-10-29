# RAG vs no-RAG Cost Experiment

Generated 2026-10-30 by `python -m src.eval_rag`. Model: `gpt-4o-mini`, answer prompt `v1` (temperature 0, strict JSON schema). Golden set: `docs/eval/golden_qa.csv` (20 questions).

- **no_rag:** all 6 corpus documents are sent with every question.
- **rag:** only the top-6 chunks are sent (embedding `text-embedding-3-small`, ~180-word chunks split by section).

Scoring is automatic: an answer is correct when every key fact of the question appears in it; an unanswerable question is correct when the model says the documents do not contain the answer.

| | no_rag | rag |
|---|---|---|
| Accuracy | 16/20 (80%) | 15/20 (75%) |
| &nbsp;&nbsp;single_fact | 8/11 | 8/11 |
| &nbsp;&nbsp;multi_fact | 5/6 | 4/6 |
| &nbsp;&nbsp;unanswerable | 3/3 | 3/3 |
| Input tokens / question | 4320 | 929 |
| Output tokens / question | 51 | 47 |
| Cost / question | $0.000678 | $0.000168 |
| Cost / 1,000 questions per month | $0.68 | $0.17 |
| Average latency | 1.29s | 1.18s |

Context recall (rag): all key facts were in the retrieved chunks for 16/16 answerable questions. Calculated answers (q12) are excluded because the result is not in any document. The rag cost does not include the query embedding (~20 tokens, about $0.0000004) or the one-off corpus embedding (about $0.0001).

**RAG reduced the cost per question by 75%; accuracy fell to 75% (no-RAG: 80%).**

| Question | Type | no_rag | rag | rag answer |
|---|---|---|---|---|
| q01 | single_fact | ✅ | ✅ | One Single Strategy Session costs $180 and lasts for 90 minutes. |
| q02 | single_fact | ✅ | ✅ | Yes, since you are cancelling less than 48 hours before the session, you will be charged 50% of the session fee, which is $79 for the Growth Package. Therefore, you will incur a late cancellation fee of $79. |
| q03 | single_fact | ✅ | ✅ | You will receive the written action plan within 5 business days after the kickoff session. |
| q04 | single_fact | ✅ | ✅ | No, card details are never taken over the phone or by email. Please use the secure payment link provided in every invoice. |
| q05 | single_fact | ✅ | ❌ | If you pay an invoice five weeks late (which is 35 days overdue), new sessions will be paused until the invoice is paid. However, sessions that were already paid for are not affected. |
| q06 | single_fact | ✅ | ✅ | Session notes and documents are kept for 2 years after the last session, then they are deleted. |
| q07 | single_fact | ✅ | ✅ | Yes, you can bring up to two other people from your business to the session at no extra cost. |
| q08 | single_fact | ❌ | ✅ | No, your unused session can be carried over to the next month. However, it cannot be carried over a second time and it is not refunded. |
| q09 | single_fact | ✅ | ✅ | You can stop being contacted by informing Ward Advisory by phone or email, and you will be removed from the follow-up list on the same day. |
| q10 | single_fact | ❌ | ❌ | The documents do not contain this information. |
| q11 | single_fact | ❌ | ❌ | The documents do not contain this information. |
| q12 | multi_fact | ❌ | ❌ | Since you have used 3 out of 6 sessions, you have 3 unused sessions remaining. The refund calculation is 3 × $158 − $50 = $474. Therefore, you will receive $474 back after cancellation. |
| q13 | multi_fact | ✅ | ✅ | If you pay the Growth Package in instalments, each payment is $330. The invoices are sent at signing and then on the 1st of the next two months. Each invoice is due within 14 days of the invoice date. |
| q14 | multi_fact | ✅ | ✅ | No, you cannot cancel the retainer now as it has a minimum term of 3 months. You can cancel after the minimum term with 30 days notice by phone or email. |
| q15 | multi_fact | ✅ | ❌ | From the Discovery Call, it takes up to 10 days to have the kickoff session, and then an additional 5 business days to receive the written action plan. Therefore, it can take up to 15 business days from the Discovery Call until you have your action plan. |
| q16 | multi_fact | ✅ | ✅ | If you were charged twice for your retainer, you should contact Elena. The extra amount will be refunded in full on the same day it is confirmed, and you will receive a written refund confirmation. Refunds are processed within 2 business days, and a card refund usually appears on your statement within 3 to 7 business days. |
| q17 | multi_fact | ✅ | ✅ | If you email a question on Saturday, you will hear back on Monday. Yes, in-person meetings are possible for clients in the local area at no extra cost. |
| q18 | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| q19 | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| q20 | unanswerable | ✅ | ✅ | The documents do not contain this information. |

<!-- manual analysis below: kept when the report is regenerated -->

## Manual analysis (prompt v1, 2026-10-30)

**Keyword scoring is noisy.** Two misses are correct answers in other words: q05 (rag) says "35 days
overdue" instead of "more than 30 days", and q08 (no_rag) says "not refundable" instead of "not refunded".
Judged by meaning, **no_rag answers 17/20 (85%) and rag 16/20 (80%)** correctly. The one real gap is q15
(rag): the retrieved chunks contained every fact, but the answer left out the 24-hour questionnaire step.

**The other misses are the same in both modes, so they come from the prompt, not from retrieval:**
- q10 (tax advice) and q11 (discounts): the documents say these are *not* offered, but the model treats a
  documented "no" as missing information and refuses. The prompt should say that a documented "no" is an answer.
- q12 (refund calculation): the model writes the right formula, 3 × $158 − $50, but gives $474 (it drops the
  − $50); the correct amount is $424. Calculations should be written step by step with intermediate results.

**Cost.** RAG sends 929 instead of 4,320 input tokens per question (−78%), which lowers the total cost per
question by 75% (output tokens are about the same in both modes). Before the experiment we expected only about
60%, because the corpus is small (6 documents, ~3,200 words); with top-6 chunks it was still 75%. The saving grows
with the corpus: the no-RAG prompt grows with every new document, while the RAG prompt stays at about 6 chunks.
At this scale both are cheap ($0.68 vs $0.17 per 1,000 questions). Latency is about the same (1.3s vs 1.2s),
because output generation takes most of the time.

**Embedding choice.** Local MiniLM was tried first (free, no API). With the same chunks, all key facts were in
the top-6 context for 15/16 questions with MiniLM and 16/16 with `text-embedding-3-small` (top-4: 14/16 for
both). MiniLM missed the "Discounts" section for "Is there a discount if I pay a year in advance?". The OpenAI
embedding was chosen; embedding the whole corpus cost $0.0001. The set is small, so this is a one-question
difference.

**Caveat.** The golden set (20 questions) has now been seen. Prompt changes made because of these results must be
checked on new held-out questions, as in Phase 2.
