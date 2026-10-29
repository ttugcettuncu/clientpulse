from pathlib import Path

import pytest

from src import rag

CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus"


def test_chunk_markdown_splits_on_sections_and_prefixes_header():
    text = "# Doc\n\nIntro line.\n\n## Prices\n\nA costs $1.\n\n## Refunds\n\nNo refunds.\n"
    chunks = rag.chunk_markdown(text)
    assert [c["section"] for c in chunks] == ["Introduction", "Prices", "Refunds"]
    assert chunks[1]["text"] == "Doc > Prices\n\nA costs $1."


def test_long_section_is_split_under_the_word_limit():
    paragraphs = "\n\n".join(" ".join(["word"] * 40) for _ in range(6))  # 240 words
    chunks = rag.chunk_markdown(f"# Doc\n\n## Long\n\n{paragraphs}", max_words=100)
    assert len(chunks) == 3
    assert all(len(c["text"].split()) <= 100 for c in chunks)
    assert all(c["text"].startswith("Doc > Long") for c in chunks)


def test_corpus_chunks_fit_the_embedding_model():
    for path in CORPUS.glob("*.md"):
        for chunk in rag.chunk_markdown(path.read_text(encoding="utf-8")):
            assert len(chunk["text"].split()) <= rag.MAX_CHUNK_WORDS, (path.name, chunk["section"])


@pytest.fixture(scope="module")
def index_dir(tmp_path_factory):
    chroma_dir = tmp_path_factory.mktemp("chroma")
    count = rag.index_documents(chroma_dir=chroma_dir)
    return chroma_dir, count


def test_index_documents_stores_every_chunk_with_metadata(index_dir):
    chroma_dir, count = index_dir
    expected = sum(len(rag.chunk_markdown(p.read_text(encoding="utf-8"))) for p in CORPUS.glob("*.md"))
    assert count == expected

    stored = rag.get_collection(chroma_dir).get(include=["metadatas"])
    assert len(stored["ids"]) == count
    assert {m["source"] for m in stored["metadatas"]} == {p.name for p in CORPUS.glob("*.md")}
    assert {m["version"] for m in stored["metadatas"]} == {"v1"}


def test_reindexing_does_not_duplicate_chunks(index_dir):
    chroma_dir, count = index_dir
    assert rag.index_documents(chroma_dir=chroma_dir) == count
    assert rag.get_collection(chroma_dir).count() == count


def test_retrieve_finds_the_cancellation_policy(index_dir):
    chroma_dir, _ = index_dir
    hits = rag.retrieve("Will I be charged if I cancel a session less than 48 hours before?",
                        chroma_dir=chroma_dir)
    assert len(hits) == rag.TOP_K
    assert "cancellation_and_refund_policy.md" in {h["source"] for h in hits}


def test_index_documents_rejects_an_empty_corpus(tmp_path):
    with pytest.raises(ValueError):
        rag.index_documents(corpus_dir=tmp_path, chroma_dir=tmp_path / "chroma")


# --- answer_question (fake OpenAI client, no cost) ---

import json
import sqlite3
from types import SimpleNamespace

import httpx
import openai

from src.budget_guard import BudgetExceededError, BudgetGuard


def chat_response(answer: dict | str):
    content = answer if isinstance(answer, str) else json.dumps(answer)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(prompt_tokens=1000, completion_tokens=50),
    )


class FakeClient:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def logged(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT step, status, call_id FROM calls ORDER BY id").fetchall()


POLICY_ANSWER = {"answer": "Yes, 50% of the session fee.", "answerable": True,
                 "sources": ["cancellation_and_refund_policy.md"]}


def test_answer_question_sends_top_k_chunks_and_logs_cost(index_dir, tmp_path):
    chroma_dir, _ = index_dir
    db_path = tmp_path / "test.db"
    client = FakeClient(chat_response(POLICY_ANSWER))
    result = rag.answer_question("Will I be charged if I cancel a session at short notice?",
                                 question_id="q02", client=client, db_path=db_path, chroma_dir=chroma_dir)

    assert result["answer"] == POLICY_ANSWER["answer"]
    assert result["cost"] == pytest.approx(1000 * 0.15e-6 + 50 * 0.60e-6)
    assert "cancellation_and_refund_policy.md" in result["context_sources"]
    assert logged(db_path) == [("rag", "ok", "q02")]
    request = client.requests[0]
    assert request["response_format"]["json_schema"]["strict"] is True
    assert request["messages"][1]["content"].count("<document ") == rag.TOP_K


def test_without_rag_the_whole_corpus_is_sent(tmp_path):
    db_path = tmp_path / "test.db"
    client = FakeClient(chat_response(POLICY_ANSWER))
    result = rag.answer_question("q", use_rag=False, client=client, db_path=db_path)

    assert set(result["context_sources"]) == {p.name for p in CORPUS.glob("*.md")}
    assert logged(db_path) == [("no_rag", "ok", None)]


def test_citing_a_document_outside_the_context_is_invalid_but_billed(index_dir, tmp_path):
    chroma_dir, _ = index_dir
    db_path = tmp_path / "test.db"
    bad = {"answer": "x", "answerable": True, "sources": ["made_up.md"]}
    with pytest.raises(rag.InvalidAnswerError):
        rag.answer_question("q", client=FakeClient(chat_response(bad)), db_path=db_path, chroma_dir=chroma_dir)
    assert logged(db_path) == [("rag", "invalid", None)]


def test_transient_error_is_retried(index_dir, tmp_path):
    chroma_dir, _ = index_dir
    db_path = tmp_path / "test.db"
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    error = openai.RateLimitError("429", response=httpx.Response(429, request=request), body=None)
    not_found = {"answer": rag.NOT_FOUND, "answerable": False, "sources": []}
    client = FakeClient(error, chat_response(not_found))
    rag.answer_question("q", client=client, db_path=db_path, chroma_dir=chroma_dir, sleep=lambda s: None)
    assert [row[1] for row in logged(db_path)] == ["retry", "ok"]


def test_budget_guard_blocks_before_the_api_call(index_dir, tmp_path):
    chroma_dir, _ = index_dir
    db_path = tmp_path / "test.db"
    client = FakeClient()
    with pytest.raises(BudgetExceededError):
        rag.answer_question("q", client=client, guard=BudgetGuard(limit=0, db_path=db_path),
                            db_path=db_path, chroma_dir=chroma_dir)
    assert client.requests == []
