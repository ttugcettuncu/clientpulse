"""Call Brief layer: transcript -> {summary, sentiment, disposition, key_topics}.

The schema also has an `outcome_evidence` sentence placed before `disposition`:
writing the evidence first makes the label more reliable (prompt v3, see
docs/eval/call_brief_accuracy.md).

PII (card numbers, national ID numbers, e-mail addresses) is masked before
the transcript leaves the machine (CLAUDE.md Bölüm 15, risk #5).

One gpt-4o-mini call with a forced, strict function call (CLAUDE.md 6.2), so
the output always matches the schema below. BudgetGuard is checked before
every attempt; transient API errors are retried with exponential backoff
(2 retries). Failed attempts are logged with cost 0; a billed response that
is still unusable is logged with its cost and status 'invalid'.
"""
import json
import re
import time
from pathlib import Path

import openai
from openai import OpenAI

from src import db
from src.budget_guard import PRICE, BudgetGuard

MODEL = "gpt-4o-mini"
PROMPT_VERSION = "v3"  # bump on every prompt change; eval results are kept per version
STEP = "call_brief"
MAX_OUTPUT_TOKENS = 400
MAX_RETRIES = 2
BACKOFF_SECONDS = 1.0  # 1s, then 2s

DISPOSITIONS = ["teklif_kabul", "dusunecek", "vazgecti", "bilgi_talebi", "sikayet_cozuldu"]
SENTIMENTS = ["pozitif", "notr", "negatif"]

SYSTEM_PROMPT = f"""You analyse phone calls between an independent business consultant and a customer.
The transcript comes from speech-to-text, has no speaker labels and may contain small recognition errors.
Call the record_call_brief function exactly once.

summary: 2-3 sentences in English: who called, what they wanted, how the call ended.

sentiment: the customer's attitude across the whole call (not the consultant's).
Politeness is not sentiment: thanks, greetings and well-wishes at the end of a call are neutral.
- pozitif: the customer is clearly pleased, e.g. enthusiastic about a service or happy with how a request was handled
- notr: matter-of-fact; or the call starts with a problem or bad news and ends calmly
- negatif: the customer stays frustrated, dissatisfied or unconvinced (e.g. finds the price too high) at the end

outcome_evidence: one sentence stating what the customer decided or received by the end of the call,
and whether money changed hands for a new or upgraded service. Write it before choosing the disposition.

disposition: the outcome of the call. Go through the rules in order and pick the first that applies.
1. sikayet_cozuldu: the customer raised a complaint and it was resolved during the call, even if the fix
   includes a free extra session or other compensation
2. vazgecti: the customer cancels, declines or decides not to continue (including after an unresolved complaint)
3. teklif_kabul: the customer agrees to pay for a new or upgraded service during the call
4. dusunecek: the customer is interested in buying but postpones the decision
5. bilgi_talebi: anything else, e.g. questions about process, invoices or support, or moving an existing appointment

key_topics: 2-5 short noun phrases, e.g. "pricing", "refund policy".
"""

TOOL = {
    "type": "function",
    "function": {
        "name": "record_call_brief",
        "description": "Record the structured brief of one customer call.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "2-3 sentence summary in English."},
                "sentiment": {"type": "string", "enum": SENTIMENTS},
                "outcome_evidence": {"type": "string", "description": "One sentence, written before the disposition."},
                "disposition": {"type": "string", "enum": DISPOSITIONS},
                "key_topics": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary", "sentiment", "outcome_evidence", "disposition", "key_topics"],
            "additionalProperties": False,
        },
    },
}

RETRYABLE = (
    openai.APIConnectionError,  # includes APITimeoutError
    openai.RateLimitError,
    openai.InternalServerError,
)


PII_PATTERNS = [
    (re.compile(r"\b(?:\d[ -]?){12,18}\d\b"), "[CARD]"),  # 13-19 digits, spaces/dashes allowed
    (re.compile(r"\b\d{11}\b"), "[NATIONAL_ID]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
]


class InvalidBriefError(ValueError):
    pass


def mask_pii(text: str) -> str:
    for pattern, placeholder in PII_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text


def _estimate_cost(transcript: str) -> float:
    """Upper-bound guess for guard.check(): ~4 chars per token, plus prompt and max output."""
    input_tokens = (len(SYSTEM_PROMPT) + len(transcript)) / 4 + 200
    price = PRICE[MODEL]
    return input_tokens * price["input"] + MAX_OUTPUT_TOKENS * price["output"]


def _parse(response) -> dict:
    message = response.choices[0].message
    if not message.tool_calls:
        raise InvalidBriefError("model returned no function call")
    try:
        brief = json.loads(message.tool_calls[0].function.arguments)
    except json.JSONDecodeError as exc:
        raise InvalidBriefError(f"function arguments are not valid JSON: {exc}") from exc
    if brief.get("sentiment") not in SENTIMENTS or brief.get("disposition") not in DISPOSITIONS:
        raise InvalidBriefError(f"label outside the allowed set: {brief}")
    return brief


def generate_call_brief(
    transcript: str,
    call_id: str | None = None,
    client: OpenAI | None = None,
    guard: BudgetGuard | None = None,
    db_path: Path | str = db.DEFAULT_DB_PATH,
    sleep=time.sleep,
) -> dict:
    client = client or OpenAI(max_retries=0)  # retries are handled here, so they are logged
    guard = guard or BudgetGuard(db_path=db_path)
    log = {"step": STEP, "call_id": call_id, "model": MODEL}
    transcript = mask_pii(transcript)

    for attempt in range(MAX_RETRIES + 1):
        guard.check(upcoming_cost=_estimate_cost(transcript))
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Transcript:\n{transcript}"},
                ],
                tools=[TOOL],
                tool_choice={"type": "function", "function": {"name": TOOL["function"]["name"]}},
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0,
            )
        except RETRYABLE:
            latency = time.perf_counter() - start
            if attempt == MAX_RETRIES:
                db.log_step(STEP, "error", call_id=call_id, model=MODEL, latency=latency, db_path=db_path)
                raise
            db.log_step(STEP, "retry", call_id=call_id, model=MODEL, latency=latency, db_path=db_path)
            sleep(BACKOFF_SECONDS * 2 ** attempt)
            continue
        except Exception:
            db.log_step(STEP, "error", call_id=call_id, model=MODEL,
                        latency=time.perf_counter() - start, db_path=db_path)
            raise
        latency = time.perf_counter() - start

        try:
            brief = _parse(response)
        except InvalidBriefError:
            guard.record_chat(response.usage, status="invalid", latency=latency, **log)  # billed anyway
            raise
        cost = guard.record_chat(response.usage, latency=latency, **log)
        return {**brief, "cost": cost, "latency": latency,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens}
