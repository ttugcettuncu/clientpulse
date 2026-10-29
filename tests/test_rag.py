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
