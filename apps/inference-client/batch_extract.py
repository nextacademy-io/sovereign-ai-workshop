#!/usr/bin/env python3
"""Offline document processing: many documents, bounded concurrency, throughput report.

This is workshop scenario D in miniature. Offline pipelines care about total tokens per
second and cost, not about the latency of a single request, so they should keep the server
busy (a high --concurrency) instead of sending one document at a time.

    python apps/inference-client/batch_extract.py --docs 48 --concurrency 16

Documents are synthetic (generated from the benchmark corpus); the point is the shape of
the work, not the content.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "benchmark"))
import os  # noqa: E402

from common import base_url, model_name  # noqa: E402
from infbench.corpus import SENTENCES  # noqa: E402
from openai import AsyncOpenAI  # noqa: E402

PROMPT = (
    "Extract every deadline, monetary amount and responsible role from the document. "
    'Reply with JSON: {"deadlines": [...], "amounts": [...], "roles": [...]}.\n\nDocument:\n'
)


def make_docs(n: int, sentences: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    return [" ".join(rng.choice(SENTENCES) for _ in range(sentences)) for _ in range(n)]


async def run(docs: list[str], concurrency: int, model: str, max_tokens: int) -> dict:
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or "not-set"
    client = AsyncOpenAI(base_url=base_url(), api_key=key, timeout=600.0, max_retries=0)
    gate = asyncio.Semaphore(concurrency)
    totals = {"prompt": 0, "completion": 0, "ok": 0, "bad_json": 0, "failed": 0}

    async def one(doc: str) -> None:
        async with gate:
            try:
                r = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": PROMPT + doc}],
                    temperature=0,
                    max_tokens=max_tokens,
                    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                )
            except Exception as exc:  # noqa: BLE001 - report and continue; one failure must not stop a batch
                totals["failed"] += 1
                print(f"request failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                return
            totals["prompt"] += r.usage.prompt_tokens
            totals["completion"] += r.usage.completion_tokens
            totals["ok"] += 1
            text = r.choices[0].message.content or ""
            try:
                json.loads(text[text.index("{") : text.rindex("}") + 1])
            except ValueError:
                totals["bad_json"] += 1

    start = time.perf_counter()
    await asyncio.gather(*(one(d) for d in docs))
    totals["seconds"] = time.perf_counter() - start
    return totals


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--docs", type=int, default=32)
    ap.add_argument(
        "--sentences", type=int, default=60, help="sentences per document (about 1.3k tokens)"
    )
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--model", default=model_name())
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    t = asyncio.run(
        run(make_docs(a.docs, a.sentences, a.seed), a.concurrency, a.model, a.max_tokens)
    )
    sec = t["seconds"]
    print(
        f"docs ok={t['ok']} failed={t['failed']} bad_json={t['bad_json']}  "
        f"concurrency={a.concurrency}  wall={sec:.1f}s\n"
        f"input {t['prompt'] / sec:,.0f} tok/s  output {t['completion'] / sec:,.0f} tok/s  "
        f"{t['ok'] / sec:.2f} docs/s  ->  {3600 * t['ok'] / sec:,.0f} docs/hour on this GPU"
    )
    return 1 if t["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
