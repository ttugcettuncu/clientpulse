"""Ask My Docs: RAG over the consultant's own documents (data/corpus/*.md).

Indexing (task 3.2): each Markdown file is split along its `##` sections;
a section longer than MAX_CHUNK_WORDS is split further at paragraph or
line boundaries. Every chunk starts with "<document title> > <section>",
so a chunk is understandable on its own. Chunks are embedded locally with
Chroma's built-in all-MiniLM-L6-v2 (ONNX, same model as the
sentence-transformers default, no torch needed, free) and stored in a
persistent Chroma collection with metadata: source file and corpus version.

MiniLM truncates input after 256 word pieces, so chunks stay at about
180 words (~250 tokens) instead of the planned 400 tokens; longer chunks
would be embedded only partly.

Answering (task 3.3): the top-k chunks go to gpt-4o-mini with an
"answer only from the context" instruction and a strict JSON schema
{answer, answerable, sources}. With use_rag=False the whole corpus is sent
instead of the top-k chunks (baseline for the RAG vs no-RAG experiment).
BudgetGuard, retries and logging follow src/call_brief.py.
"""
import json
import re
import time
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from openai import OpenAI

from src import db
from src.budget_guard import PRICE, BudgetGuard
from src.call_brief import BACKOFF_SECONDS, MAX_RETRIES, RETRYABLE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"
COLLECTION = "corpus"
CORPUS_VERSION = "v1"
MAX_CHUNK_WORDS = 180  # ~250 tokens, the MiniLM input limit
TOP_K = 4

MODEL = "gpt-4o-mini"
PROMPT_VERSION = "v1"  # bump on every prompt change
MAX_OUTPUT_TOKENS = 300
NOT_FOUND = "The documents do not contain this information."

SYSTEM_PROMPT = f"""You answer questions from customers of Ward Advisory, a small-business consulting practice.
Use ONLY the documents in the user message. Do not use outside knowledge and do not guess.
- answer: 1-3 sentences in English. Include the exact figures, deadlines and conditions from the documents.
  If the question needs a calculation (e.g. a refund), show it briefly.
- answerable: false if the documents do not contain the answer; then answer exactly "{NOT_FOUND}"
- sources: the file names of the documents you used (empty if not answerable)
"""

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "docs_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "answerable": {"type": "boolean"},
                "sources": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["answer", "answerable", "sources"],
            "additionalProperties": False,
        },
    },
}


class InvalidAnswerError(ValueError):
    pass


def _split_long(text: str, max_words: int) -> list[str]:
    """Greedily pack paragraphs (then lines) into pieces of at most max_words."""
    if len(text.split()) <= max_words:
        return [text]
    units = [u for u in re.split(r"\n\s*\n", text) if u.strip()]
    if len(units) == 1:
        units = [u for u in text.splitlines() if u.strip()]
    if len(units) == 1:  # one huge line: hard split by words
        words = text.split()
        return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

    pieces, current = [], []
    for unit in units:
        for part in _split_long(unit, max_words):
            if current and len(" ".join(current + [part]).split()) > max_words:
                pieces.append("\n\n".join(current))
                current = []
            current.append(part)
    if current:
        pieces.append("\n\n".join(current))
    return pieces


def chunk_markdown(text: str, max_words: int = MAX_CHUNK_WORDS) -> list[dict]:
    """Split one Markdown document into chunks: [{"section", "text"}]."""
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""
    body = text[title_match.end():] if title_match else text

    sections = re.split(r"^## (.+)$", body, flags=re.MULTILINE)
    named = [("Introduction", sections[0])] + list(zip(sections[1::2], sections[2::2]))

    chunks = []
    for name, content in named:
        content = content.strip()
        if not content:
            continue
        header = f"{title} > {name.strip()}" if title else name.strip()
        for piece in _split_long(content, max_words - len(header.split())):
            chunks.append({"section": name.strip(), "text": f"{header}\n\n{piece}"})
    return chunks


def get_collection(chroma_dir: Path | str = CHROMA_DIR):
    client = chromadb.PersistentClient(path=str(chroma_dir))
    return client.get_or_create_collection(
        COLLECTION, embedding_function=DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )


def index_documents(corpus_dir: Path | str = CORPUS_DIR, chroma_dir: Path | str = CHROMA_DIR,
                    version: str = CORPUS_VERSION) -> int:
    """(Re)build the vector index from corpus_dir. Returns the number of chunks stored.

    The collection is emptied first, so re-running never leaves stale chunks.
    """
    ids, documents, metadatas = [], [], []
    for path in sorted(Path(corpus_dir).glob("*.md")):
        for i, chunk in enumerate(chunk_markdown(path.read_text(encoding="utf-8"))):
            ids.append(f"{path.stem}#{i}")
            documents.append(chunk["text"])
            metadatas.append({"source": path.name, "section": chunk["section"],
                              "chunk": i, "version": version})
    if not ids:
        raise ValueError(f"no Markdown documents in {corpus_dir}")

    collection = get_collection(chroma_dir)
    existing = collection.get(include=[])["ids"]
    if existing:
        collection.delete(ids=existing)
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)


def retrieve(question: str, k: int = TOP_K, chroma_dir: Path | str = CHROMA_DIR) -> list[dict]:
    """Top-k chunks for a question: [{"id", "text", "source", "section", "distance"}]."""
    result = get_collection(chroma_dir).query(query_texts=[question], n_results=k)
    return [
        {"id": id_, "text": doc, "source": meta["source"], "section": meta["section"], "distance": dist}
        for id_, doc, meta, dist in zip(result["ids"][0], result["documents"][0],
                                        result["metadatas"][0], result["distances"][0])
    ]


def _format_context(chunks: list[dict]) -> str:
    return "\n\n".join(f'<document source="{c["source"]}">\n{c["text"]}\n</document>' for c in chunks)


def _full_corpus(corpus_dir: Path | str = CORPUS_DIR) -> list[dict]:
    return [{"source": p.name, "text": p.read_text(encoding="utf-8")}
            for p in sorted(Path(corpus_dir).glob("*.md"))]


def _estimate_cost(user_message: str, model: str = MODEL) -> float:
    """Upper-bound guess for guard.check(): ~4 chars per token, plus prompt and max output."""
    input_tokens = (len(SYSTEM_PROMPT) + len(user_message)) / 4 + 100
    price = PRICE[model]
    return input_tokens * price["input"] + MAX_OUTPUT_TOKENS * price["output"]


def _parse(response, allowed_sources: set[str]) -> dict:
    try:
        answer = json.loads(response.choices[0].message.content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise InvalidAnswerError(f"response is not valid JSON: {exc}") from exc
    unknown = set(answer["sources"]) - allowed_sources
    if unknown:
        raise InvalidAnswerError(f"cited documents that were not in the context: {unknown}")
    return answer


def answer_question(
    question: str,
    question_id: str | None = None,
    use_rag: bool = True,
    k: int = TOP_K,
    client: OpenAI | None = None,
    guard: BudgetGuard | None = None,
    db_path: Path | str = db.DEFAULT_DB_PATH,
    chroma_dir: Path | str = CHROMA_DIR,
    corpus_dir: Path | str = CORPUS_DIR,
    sleep=time.sleep,
    model: str = MODEL,
) -> dict:
    """Answer a question from the documents.

    Returns {answer, answerable, sources, context_sources, cost, latency,
    input_tokens, output_tokens}. `context_sources` lists the documents that
    were sent (top-k chunks with RAG, every document without).
    """
    client = client or OpenAI(max_retries=0)  # retries are handled here, so they are logged
    guard = guard or BudgetGuard(db_path=db_path)
    step = "rag" if use_rag else "no_rag"

    context = retrieve(question, k=k, chroma_dir=chroma_dir) if use_rag else _full_corpus(corpus_dir)
    context_sources = list(dict.fromkeys(c["source"] for c in context))
    user_message = f"Documents:\n{_format_context(context)}\n\nQuestion: {question}"

    for attempt in range(MAX_RETRIES + 1):
        guard.check(upcoming_cost=_estimate_cost(user_message, model))
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format=RESPONSE_FORMAT,
                max_tokens=MAX_OUTPUT_TOKENS,
                temperature=0,
            )
        except RETRYABLE:
            latency = time.perf_counter() - start
            if attempt == MAX_RETRIES:
                db.log_step(step, "error", call_id=question_id, model=model, latency=latency, db_path=db_path)
                raise
            db.log_step(step, "retry", call_id=question_id, model=model, latency=latency, db_path=db_path)
            sleep(BACKOFF_SECONDS * 2 ** attempt)
            continue
        except Exception:
            db.log_step(step, "error", call_id=question_id, model=model,
                        latency=time.perf_counter() - start, db_path=db_path)
            raise
        latency = time.perf_counter() - start

        log_fields = {"step": step, "call_id": question_id, "latency": latency}
        try:
            answer = _parse(response, set(context_sources))
        except InvalidAnswerError:
            guard.record_chat(response.usage, model=model, status="invalid", **log_fields)  # billed anyway
            raise
        cost = guard.record_chat(response.usage, model=model, **log_fields)
        return {**answer, "context_sources": context_sources, "cost": cost, "latency": latency,
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens}


if __name__ == "__main__":
    import sys

    if sys.argv[1:]:
        print(json.dumps(answer_question(" ".join(sys.argv[1:])), indent=2))
    else:
        n = index_documents()
        print(f"Indexed {n} chunks from {CORPUS_DIR} into {CHROMA_DIR}")
