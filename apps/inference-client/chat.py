#!/usr/bin/env python3
"""Streaming chat against the workshop server, with the numbers that matter.

    python apps/inference-client/chat.py "Explain continuous batching in two sentences."
    python apps/inference-client/chat.py --max-tokens 400 --temperature 0.7 "Write a haiku about GPUs."

After the answer it prints one line connecting the request to what the server did:

    prompt_tokens -> TTFT -> completion_tokens -> tokens/s -> total time

This is Lab 2's "REQUEST -> MODEL -> GPU -> TOKENS -> METRICS" chain from the user's side.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import make_client, model_name  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("prompt", nargs="?", help="user message (reads stdin when omitted)")
    ap.add_argument("--system", default="You are a concise, accurate assistant.")
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--model", default=model_name())
    ap.add_argument("--think", action="store_true", help="enable the model's thinking mode (Qwen3)")
    args = ap.parse_args()

    prompt = args.prompt or sys.stdin.read().strip()
    if not prompt:
        ap.error("no prompt given")

    client = make_client()
    start = time.perf_counter()
    first = last = None
    chunks = 0
    usage = None

    stream = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "system", "content": args.system}, {"role": "user", "content": prompt}],
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        stream=True,
        stream_options={"include_usage": True},
        extra_body={"chat_template_kwargs": {"enable_thinking": args.think}},
    )
    for event in stream:
        if event.usage:
            usage = event.usage
        if not event.choices:
            continue
        delta = event.choices[0].delta
        # vLLM 0.31 streams thinking as `reasoning`; older versions used `reasoning_content`.
        reasoning = (
            getattr(delta, "reasoning", None) or getattr(delta, "reasoning_content", None) or ""
        )
        text = (delta.content or "") + reasoning
        if text:
            now = time.perf_counter()
            first = first or now
            last = now
            chunks += 1
            print(text, end="", flush=True)
    end = time.perf_counter()
    print("\n")

    if first is None or usage is None:
        print("no tokens received", file=sys.stderr)
        return 1
    completion = usage.completion_tokens
    decode_s = max(last - first, 1e-9)
    print(
        f"prompt_tokens={usage.prompt_tokens}  ttft={1000 * (first - start):.0f} ms  "
        f"completion_tokens={completion}  decode={((completion - 1) / decode_s):.1f} tok/s  "
        f"total={end - start:.2f} s",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
