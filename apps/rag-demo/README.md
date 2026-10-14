# rag-demo

A RAG pipeline in one readable file, without a framework:

```text
DOCUMENTS → CHUNKING → EMBEDDINGS → INDEX → RETRIEVAL → CONTEXT → LLM
```

`rag.py` reads the Markdown files of `handbook/` (a small, fictional company handbook), splits them into overlapping chunks, embeds them through a **second vLLM instance** that serves `Qwen/Qwen3-Embedding-0.6B` (port 8001, started by `sudo wsctl embed start`), keeps the vectors in a NumPy array, retrieves by cosine similarity and answers with the main server. Every step prints what it costs, including how many extra prompt tokens the retrieved context adds.

```bash
python3 apps/rag-demo/rag.py ask "How many vacation days do I get?"
python3 apps/rag-demo/rag.py ask --no-rag "How many vacation days do I get?"        # the same question without retrieval
python3 apps/rag-demo/rag.py ask --top-k 6 --chunk-chars 400 "Can I work from Spain?"
```

Environment: `EMBEDDING_BASE_URL` (default `http://127.0.0.1:8001/v1`), `EMBEDDING_MODEL`, and the usual `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `WORKSHOP_MODEL`.

## What to look at

- With retrieval the answer cites the handbook (`[1]`); without it the model answers in general terms.
- The handbook contains a superseded policy on purpose (`03-remote-work-v1-archived.md` next to `02-remote-work-v2.md`): ask a question both versions answer and read which chunks come back. Whose job is it to keep stale documents out: the retriever's or the pipeline's?
- Change `--chunk-chars` and `--top-k` and watch retrieval quality and prompt tokens move in opposite directions.

`test_rag.py` tests the pipeline with a deterministic stand-in for the embedding server and needs no GPU.
