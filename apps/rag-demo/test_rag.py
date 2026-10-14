"""RAG pipeline tests with a deterministic stand-in for the embedding server."""

import hashlib
import re
from pathlib import Path

import numpy as np
import pytest
import rag

HANDBOOK = Path(__file__).resolve().parent / "handbook"


def fake_embed(texts: list[str], dim: int = 1024) -> np.ndarray:
    """Hashed bag of words: enough lexical signal to test the plumbing without a model."""
    out = np.zeros((len(texts), dim), dtype=np.float32)
    for row, text in enumerate(texts):
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            out[row, h % dim] += 1.0
    return rag.normalize(out)


def test_chunks_respect_size_and_cover_the_text():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 40 for i in range(10))
    chunks = rag.chunk_text(text, size=300, overlap=50)
    assert all(len(c) <= 300 + 60 for c in chunks)  # size plus the carried-over overlap
    joined = " ".join(chunks)
    for i in range(10):
        assert f"Paragraph {i}." in joined


def test_chunk_overlap_repeats_the_tail_of_the_previous_chunk():
    paras = [f"Alpha{i} " + "x" * 120 for i in range(6)]
    chunks = rag.chunk_text("\n\n".join(paras), size=300, overlap=40)
    assert len(chunks) >= 2
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        assert prev[-40:] in nxt


def test_oversized_paragraph_is_split_and_terminates():
    chunks = rag.chunk_text("a " * 2000, size=200, overlap=30)
    assert len(chunks) > 10 and all(len(c) <= 200 for c in chunks)


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        rag.chunk_text("text", size=100, overlap=100)


def test_top_k_orders_by_cosine_similarity():
    index = rag.normalize(np.array([[1, 0], [0.8, 0.6], [0, 1]], dtype=np.float32))
    query = rag.normalize(np.array([[1, 0.1]], dtype=np.float32))[0]
    hits = rag.top_k(index, query, 2)
    assert [i for i, _ in hits] == [0, 1]
    assert hits[0][1] > hits[1][1]


@pytest.mark.parametrize(
    ("question", "expected_file"),
    [
        ("How many vacation days do I get per year?", "01-vacation-and-leave.md"),
        ("What internet allowance does the company pay for remote work?", "02-remote-work-v2.md"),
        ("How long are call recordings stored?", "06-data-retention.md"),
        ("Who must approve expenses above 1,000 euros?", "04-expenses.md"),
        (
            "Within how many minutes must a critical incident be acknowledged?",
            "05-incident-response.md",
        ),
    ],
)
def test_retrieval_finds_the_right_document(monkeypatch, question, expected_file):
    monkeypatch.setattr(rag, "embed", fake_embed)
    chunks = rag.load_chunks(HANDBOOK, 600, 100)
    index = rag.embed([c.text for c in chunks])
    hits = rag.top_k(index, rag.embed([question])[0], 3)
    assert expected_file in {chunks[i].source for i, _ in hits}


def test_handbook_contains_the_facts_the_lab_questions_rely_on():
    text = " ".join(p.read_text() for p in HANDBOOK.glob("*.md"))
    for fact in ("28 days", "3 days per week", "90 days", "15 minutes", "72 hours"):
        assert fact in text


def test_prompt_numbers_passages_and_grounds_the_answer():
    chunks = [rag.Chunk("a.md", 0, "Alpha text"), rag.Chunk("b.md", 0, "Beta text")]
    msgs = rag.build_prompt("What?", chunks)
    assert msgs[0]["role"] == "system" and "only the numbered passages" in msgs[0]["content"]
    user = msgs[1]["content"]
    assert "[1] (a.md)" in user and "[2] (b.md)" in user and user.endswith("Question: What?")
