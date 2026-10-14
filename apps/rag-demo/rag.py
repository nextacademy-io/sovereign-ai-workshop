#!/usr/bin/env python3
"""A RAG pipeline in one readable file. No framework.

    DOCUMENTS -> CHUNKING -> EMBEDDINGS -> INDEX -> RETRIEVAL -> CONTEXT -> LLM

    python apps/rag-demo/rag.py ask "How many vacation days do I get?"
    python apps/rag-demo/rag.py ask --no-rag "How many vacation days do I get?"    # no retrieval
    python apps/rag-demo/rag.py ask --top-k 6 --chunk-chars 400 "Can I work from Spain?"

Embeddings come from a second vLLM instance (default http://127.0.0.1:8001/v1) serving an
embedding model; generation comes from the main server. Every step prints what it costs.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import make_client, model_name  # noqa: E402

HERE = Path(__file__).resolve().parent
EMBED_URL = os.environ.get("EMBEDDING_BASE_URL", "http://127.0.0.1:8001/v1")
EMBED_MODEL = os.environ.get("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")
# Qwen3-Embedding is instruction-aware: queries carry a task description, documents do not.
QUERY_INSTRUCTION = "Given a question, retrieve the passages that answer it"


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str


def chunk_text(text: str, size: int = 600, overlap: int = 100) -> list[str]:
    """Split on paragraph boundaries into chunks of about `size` characters.

    Paragraphs are never cut unless a single paragraph exceeds `size`; consecutive chunks
    share `overlap` trailing characters so a fact on a boundary is not lost.
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        while len(para) > size:  # an oversized paragraph is cut on a space near the limit
            cut = para.rfind(" ", 0, size)
            if cut <= 0:
                cut = size
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:cut])
            para = para[max(cut - overlap, 1) :]
        if current and len(current) + len(para) + 2 > size:
            chunks.append(current)
            current = (current[-overlap:] + "\n\n" if overlap else "") + para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


def load_chunks(folder: Path, size: int, overlap: int) -> list[Chunk]:
    out: list[Chunk] = []
    for path in sorted(folder.glob("*.md")):
        for i, text in enumerate(chunk_text(path.read_text(), size, overlap)):
            out.append(Chunk(path.name, i, text))
    return out


def embed(texts: list[str], batch: int = 32) -> np.ndarray:
    client = make_client(url=EMBED_URL)
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=EMBED_MODEL, input=texts[i : i + batch])
        vectors += [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
    return normalize(np.array(vectors, dtype=np.float32))


def normalize(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.maximum(norms, 1e-12)


def top_k(index: np.ndarray, query_vec: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Cosine similarity of unit vectors is a dot product. Brute force is fine up to ~100k chunks."""
    scores = index @ query_vec
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]


def build_prompt(question: str, passages: list[Chunk]) -> list[dict]:
    context = "\n\n".join(f"[{i + 1}] ({c.source})\n{c.text}" for i, c in enumerate(passages))
    system = (
        "Answer the question using only the numbered passages. Cite passage numbers like [1]. "
        "If the passages do not contain the answer, say you do not know. "
        "If passages disagree, prefer the one that is marked as the newer version."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"},
    ]


def cmd_ask(a: argparse.Namespace) -> int:
    llm = make_client()
    messages = [{"role": "user", "content": a.question}]
    t_retrieve = 0.0
    if not a.no_rag:
        chunks = load_chunks(a.docs, a.chunk_chars, a.overlap)
        t0 = time.perf_counter()
        vectors = embed([c.text for c in chunks])
        t_index = time.perf_counter() - t0
        t0 = time.perf_counter()
        qvec = embed([f"Instruct: {QUERY_INSTRUCTION}\nQuery: {a.question}"])[0]
        hits = top_k(vectors, qvec, a.top_k)
        t_retrieve = time.perf_counter() - t0
        print(
            f"indexed {len(chunks)} chunks in {t_index:.2f}s; retrieval took {t_retrieve * 1000:.0f} ms\n"
        )
        for rank, (i, score) in enumerate(hits, 1):
            preview = chunks[i].text.replace("\n", " ")[:90]
            print(f"  [{rank}] score={score:.3f} {chunks[i].source}: {preview}...")
        print()
        messages = build_prompt(a.question, [chunks[i] for i, _ in hits])

    t0 = time.perf_counter()
    resp = llm.chat.completions.create(
        model=a.model,
        messages=messages,
        temperature=0,
        max_tokens=a.max_tokens,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    elapsed = time.perf_counter() - t0
    print(resp.choices[0].message.content.strip())
    u = resp.usage
    print(
        f"\n{'no retrieval' if a.no_rag else f'top-{a.top_k}'}: prompt_tokens={u.prompt_tokens} "
        f"completion_tokens={u.completion_tokens} generation={elapsed:.2f}s "
        f"(retrieved context is the difference in prompt tokens)",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("ask", help="retrieve and answer")
    ask.add_argument("question")
    ask.add_argument("--docs", type=Path, default=HERE / "handbook")
    ask.add_argument("--chunk-chars", type=int, default=600)
    ask.add_argument("--overlap", type=int, default=100)
    ask.add_argument("--top-k", type=int, default=3)
    ask.add_argument("--max-tokens", type=int, default=300)
    ask.add_argument("--model", default=model_name())
    ask.add_argument(
        "--no-rag", action="store_true", help="skip retrieval to see the ungrounded answer"
    )
    ask.set_defaults(func=cmd_ask)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
