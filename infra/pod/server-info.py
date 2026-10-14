#!/usr/bin/env python3
"""Write the server provenance file (/workspace/state/server.json) from a vLLM startup log.

The benchmark harness reads this file to attach engine version, CUDA version, server
arguments and KV-cache capacity to every result. Log formats are those of vLLM v0.31.0
(vllm/v1/worker/gpu_model_runner.py, gpu_worker.py, v1/core/kv_cache_utils.py).
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

PATTERNS = {
    "model_memory_gib": (
        re.compile(r"Model loading took ([\d.]+) GiB memory and ([\d.]+) seconds"),
        1,
    ),
    "model_load_seconds": (
        re.compile(r"Model loading took ([\d.]+) GiB memory and ([\d.]+) seconds"),
        2,
    ),
    "weights_seconds": (re.compile(r"Loading weights took ([\d.]+) seconds"), 1),
    "kv_cache_memory_gib": (re.compile(r"Available KV cache memory: ([\d.]+) GiB"), 1),
    "graph_capture_seconds": (
        re.compile(r"Graph capturing finished in ([\d.]+) secs, took ([\d.]+) GiB"),
        1,
    ),
    "graph_capture_gib": (
        re.compile(r"Graph capturing finished in ([\d.]+) secs, took ([\d.]+) GiB"),
        2,
    ),
    "engine_init_seconds": (
        re.compile(r"init engine \(profile, create kv cache, warmup model\) took ([\d.]+) s"),
        1,
    ),
}
KV_LINE = re.compile(
    r"KV cache size: ([\d,]+) tokens, Maximum concurrency for ([\d,]+) tokens per request: ([\d.]+)x"
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def parse_log(text: str) -> dict:
    """Pull startup facts out of a log. Missing facts are simply absent, never guessed."""
    text = ANSI.sub("", text)
    out: dict = {}
    for key, (pattern, group) in PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            value = matches[-1]  # the last start in an appended log wins
            raw = value if isinstance(value, str) else value[group - 1]
            out[key] = float(raw)
    kv = KV_LINE.findall(text)
    if kv:
        tokens, max_len, concurrency = kv[-1]
        out["kv_cache_tokens"] = int(tokens.replace(",", ""))
        out["kv_cache_max_model_len"] = int(max_len.replace(",", ""))
        out["kv_cache_max_concurrency"] = float(concurrency)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--summary", required=True, help="JSON from render-profile.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--started-epoch", type=float, required=True)
    ap.add_argument("--ready-epoch", type=float, required=True)
    ap.add_argument("--engine-version", default=None)
    ap.add_argument("--runtime-cuda", default=None)
    ap.add_argument("--gpu", default=None)
    ap.add_argument("--actor", default="root")
    a = ap.parse_args()

    summary = json.loads(a.summary)
    iso = lambda t: datetime.fromtimestamp(t, UTC).isoformat(timespec="seconds")  # noqa: E731
    info = {
        "engine": "vllm",
        "engine_version": a.engine_version,
        "runtime_cuda_version": a.runtime_cuda,
        "gpu": a.gpu,
        "profile": summary["profile"],
        "role": summary["role"],
        "model": summary["model"],
        "model_revision": summary["model_revision"],
        "args": summary["args"],
        "overrides": summary["overrides"],
        "started_by": a.actor,
        "started_at": iso(a.started_epoch),
        "ready_at": iso(a.ready_epoch),
        "startup_seconds": round(a.ready_epoch - a.started_epoch, 1),
        "startup_log": parse_log(a.log.read_text(errors="replace")),
    }
    a.out.write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps({k: info[k] for k in ("profile", "startup_seconds")} | info["startup_log"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
