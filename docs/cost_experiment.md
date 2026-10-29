# RAG vs no-RAG Cost Experiment

Generated 2026-10-30 by `python -m src.eval_rag`. Model: `gpt-4o-mini`, answer prompt `v3` (temperature 0, strict JSON schema). Golden set: `docs/eval/golden_qa.csv` (32 questions).

**dev** questions were seen while analysing and changing the answer prompt; **test** questions were written before the first prompt change (see the prompt history below for how clean the test score is).

- **no_rag:** all 6 corpus documents are sent with every question.
- **rag:** only the top-6 chunks are sent (embedding `text-embedding-3-small`, ~180-word chunks split by section).

Scoring is automatic: an answer is correct when every key fact of the question appears in it; an unanswerable question is correct when the model says the documents do not contain the answer.

| | no_rag | rag |
|---|---|---|
| Accuracy, all questions | 29/32 (91%) | 30/32 (94%) |
| &nbsp;&nbsp;dev | 19/20 | 19/20 |
| &nbsp;&nbsp;test | 10/12 | 11/12 |
| &nbsp;&nbsp;single_fact | 18/18 | 17/18 |
| &nbsp;&nbsp;multi_fact | 7/9 | 9/9 |
| &nbsp;&nbsp;unanswerable | 4/5 | 4/5 |
| Input tokens / question | 4441 | 1074 |
| Output tokens / question | 59 | 55 |
| Cost / question | $0.000701 | $0.000194 |
| Cost / 1,000 questions per month | $0.70 | $0.19 |
| Average latency | 1.27s | 2.23s |

Context recall (rag): all key facts were in the retrieved chunks for 24/25 answerable questions (missed: t05). Calculated answers (q12, t04) are excluded because the result is not in any document. The rag cost does not include the query embedding (~20 tokens, about $0.0000004) or the one-off corpus embedding (about $0.0001).

**RAG reduced the cost per question by 72%; accuracy rose to 94% (no-RAG: 91%).**

| Question | Split | Type | no_rag | rag | rag answer |
|---|---|---|---|---|---|
| q01 | dev | single_fact | ✅ | ✅ | One Single Strategy Session costs $180 and takes 90 minutes. |
| q02 | dev | single_fact | ✅ | ✅ | Yes, you will be charged a late cancellation fee of 50% of the session fee, which is $79 for the Growth Package. Since you are cancelling less than 48 hours before the session, the fee applies. |
| q03 | dev | single_fact | ✅ | ✅ | You will receive the written action plan within 5 business days after the kickoff session. |
| q04 | dev | single_fact | ✅ | ✅ | No, card details are never taken over the phone or by email; please use the secure payment link provided in the invoice. |
| q05 | dev | single_fact | ✅ | ✅ | If you pay an invoice five weeks late, which is more than 30 days overdue, new sessions will be paused until the invoice is paid. However, sessions that were already paid for are not affected. |
| q06 | dev | single_fact | ✅ | ✅ | Session notes and documents are kept for 2 years after the last session, then deleted. |
| q07 | dev | single_fact | ✅ | ✅ | Yes, up to two other people from your business can join at no extra cost. |
| q08 | dev | single_fact | ✅ | ✅ | No, the session that is not used in a month can be carried over to the next month only. However, it cannot be carried over a second time and it is not refunded. |
| q09 | dev | single_fact | ✅ | ✅ | You can stop being contacted by informing Ward Advisory by phone or email, and you will be removed from the follow-up list on the same day. |
| q10 | dev | single_fact | ✅ | ✅ | No. Elena does not provide legal, tax or accounting advice, but she can tell you which questions to ask a specialist. |
| q11 | dev | single_fact | ✅ | ✅ | No. Ward Advisory does not offer discounts, coupon codes or special prices. |
| q12 | dev | multi_fact | ✅ | ✅ | You have used 3 out of 6 sessions, so you have 3 unused sessions. The refund calculation is as follows: 3 × $158 (value of unused sessions) = $474; then subtract the $50 admin fee: $474 - $50 = $424. Therefore, you will get back $424. |
| q13 | dev | multi_fact | ✅ | ✅ | If you pay the Growth Package in instalments, each payment is $330. The invoices are sent in three installments: the first invoice is sent at signing, and the next two invoices are sent on the 1st of the following two months. Each invoice is due within 14 days of the invoice date. |
| q14 | dev | multi_fact | ✅ | ✅ | No, you cannot cancel it now. The retainer has a minimum term of 3 months, and you can only cancel after that with 30 days notice. |
| q15 | dev | multi_fact | ✅ | ✅ | From the Discovery Call to receiving your written action plan, it takes a total of 15 business days. This includes: 1) The Discovery Call (0 days), 2) Receiving the intake questionnaire within 24 hours (1 day), 3) Completing and returning the questionnaire at least 2 business days before the first session (3 days), 4) The kickoff session within 10 days of signing the agreement (10 days), and 5) Receiving the written action plan within 5 business days after the kickoff session (5 days). Total: 1 + 3 + 10 + 5 = 19 days, but since the kickoff session is counted as part of the 10 days, the total is 15 business days. |
| q16 | dev | multi_fact | ✅ | ✅ | If you were charged twice for your retainer, you should contact Elena. The extra amount will be refunded in full on the same day it is confirmed, and you will receive a written refund confirmation. Elena processes refunds within 2 business days, and a card refund usually appears on your statement within 3 to 7 business days. |
| q17 | dev | multi_fact | ✅ | ✅ | If you email a question on Saturday, you will receive a reply on Monday, as retainer clients get email support with a reply within 1 business day, Monday to Friday. Yes, in-person meetings are possible for clients in the local area, at no extra cost. |
| q18 | dev | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| q19 | dev | unanswerable | ❌ | ❌ | No, the documents state that "Elena does not work with large corporations or with start-ups that have no customers yet," and there is no mention of group workshops for several business owners together. |
| q20 | dev | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| t01 | test | single_fact | ✅ | ✅ | No, cash is not accepted. "Cash and cheques are not accepted." |
| t02 | test | single_fact | ✅ | ✅ | Since you are cancelling less than 48 hours before the session, you will incur a late cancellation fee of 50% of the session fee. The Monthly Retainer session is valued at $300, so the late cancellation fee will be: 50% of $300 = $150. |
| t03 | test | single_fact | ✅ | ✅ | Yes, you can get a full refund of the amount paid since you are within 14 days of purchase and have not used any session. |
| t04 | test | multi_fact | ❌ | ✅ | You have used 5 out of 6 sessions, so you have 1 unused session. The refund calculation is as follows: 1 × $158 (value of the unused session) - $50 (admin fee) - $79 (unpaid late-cancellation fee) = $158 - $50 - $79 = $29. Therefore, you will get back $29. |
| t05 | test | single_fact | ✅ | ❌ | No, Elena does not provide legal, tax or accounting advice, but she can tell you which questions to ask a specialist. |
| t06 | test | single_fact | ✅ | ✅ | No, Ward Advisory does not send newsletters. |
| t07 | test | single_fact | ✅ | ✅ | If your tax number on an invoice is wrong, you can contact Elena, and she will issue a corrected invoice. |
| t08 | test | multi_fact | ❌ | ✅ | If you do not show up to a session on the Monthly Retainer and did not inform Ward Advisory, you will be charged 100% of the session fee, which is $300. However, the missed session is not lost; it can still be rescheduled. |
| t09 | test | multi_fact | ✅ | ✅ | If your written action plan is late, you should contact Elena. If the delay is on Ward Advisory's side, she may offer a free 30-minute follow-up call to go through the document together. Complaints are answered within 1 business day. |
| t10 | test | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| t11 | test | unanswerable | ✅ | ✅ | The documents do not contain this information. |
| t12 | test | single_fact | ✅ | ✅ | No, Elena does not work with start-ups that have no customers yet. |

<!-- manual analysis below: kept when the report is regenerated -->

## Prompt history

| Prompt | Change | no_rag dev | no_rag test | rag dev | rag test |
|---|---|---|---|---|---|
| v1 | first version | 16/20 | 9/12 | 15/20 | 9/12 |
| v2 | a documented "no" is an answer; calculations step by step; process questions list every step | 18/20 | 8/12 | 18/20 | 12/12 |
| v3 | a "no" needs an explicit statement; silence stays unanswerable | 19/20 | 10/12 | 19/20 | 11/12 |

How clean is the test score? The test questions (t01-t12) were committed before v2 was written, so the
**v2 test score (rag 12/12) is a true held-out result**. v3 fixes a side effect of v2 that showed up on dev
questions (q18, q19: the model answered "no" to things the documents never mention), but v2's test results had
been seen by then, so the v3 test score is only partly held out. No further prompt changes were made, to avoid
tuning on the test questions.

## Manual analysis (2026-10-30)

**v1 problems** (both modes, so they came from the prompt and not from retrieval):
- A documented "no" was treated as missing information (q10 tax advice, q11 discounts; on test t01 cash, t05 ad
  campaigns, t12 start-ups). The model often wrote the right "No, ..." answer and still marked it unanswerable.
- Arithmetic: q12 had the right formula 3 x $158 - $50 but gave $474 instead of $424.
- Keyword scoring was noisy for v1 (q05 rag, q08 no_rag were correct answers in other words); judged by meaning,
  v1 was 17/20 (no_rag) vs 16/20 (rag) on dev.

**v2** fixed these, but over-corrected: for questions the documents do not cover, the model answered "No" and
even invented a rule (q19: "group workshops are not offered"). **v3** keeps the v2 fixes and puts the
unanswerable questions back.

**Remaining misses with v3:**
- t05 (rag): a retrieval miss. The "What is not included" section (no advertising campaigns) was not in the
  top-6 for "Can you run our Facebook ad campaigns?", so the model quoted the tax-advice rule instead.
  Context recall found the same gap (24/25).
- q19 (both): still answers "No" with an unrelated quote about group workshops, which the documents never mention.
- no_rag only: t04 drops the $50 admin fee from the refund, t08 invents a condition ("until the end of the notice
  period"). With the whole corpus in the prompt the model mixes up rules more often; with only the relevant chunks
  it did not. With v2 no_rag also charged 100% instead of 50% for a late cancellation (t02).
- q15 (rag) is scored correct because all key facts are present, but its total ("15 business days") is muddled.

**Cost.** RAG sends ~1,070 instead of ~4,440 input tokens per question (-76%), which lowers the cost per question
by 72% (output tokens are about the same). Before the experiment we expected only about 60%, because the corpus is
small (6 documents, ~3,200 words). The saving grows with the corpus: the no-RAG prompt grows with every new
document, while the RAG prompt stays at about 6 chunks. At this scale both are cheap ($0.70 vs $0.19 per 1,000
questions). Generation latency does not drop: output generation takes most of the time, and the v3 rag average is
pulled up by a few long step-by-step answers; RAG also adds a query-embedding call (not in the table).

**Embedding choice.** Local MiniLM was tried first (free, no API). With the same chunks, all key facts were in
the top-6 context for 15/16 dev questions with MiniLM and 16/16 with `text-embedding-3-small` (top-4: 14/16 for
both). MiniLM missed the "Discounts" section for "Is there a discount if I pay a year in advance?". The OpenAI
embedding was chosen; embedding the whole corpus costs $0.0001. The set is small, so this is a one-question
difference.

**Result:** with prompt v3, RAG answered 30/32 questions correctly vs 29/32 without RAG, at 72% lower cost per
question. On the held-out test questions RAG was at least as accurate as sending the whole corpus with every prompt
version (v1 9 vs 9, v2 12 vs 8, v3 11 vs 10).
