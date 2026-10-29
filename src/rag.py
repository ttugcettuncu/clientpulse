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
"""
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"
COLLECTION = "corpus"
CORPUS_VERSION = "v1"
MAX_CHUNK_WORDS = 180  # ~250 tokens, the MiniLM input limit
TOP_K = 4


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


if __name__ == "__main__":
    n = index_documents()
    print(f"Indexed {n} chunks from {CORPUS_DIR} into {CHROMA_DIR}")
