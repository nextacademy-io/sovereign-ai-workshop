#!/usr/bin/env python3
"""Download the pinned workshop models into the Hugging Face cache on the pod.

    fetch-models.py --models workshop      # primary, quantized, small, embedding
    fetch-models.py --models demo          # the trainer-demo models (30B MoE, GGUF)
    fetch-models.py --models primary,small # explicit roles

Every model is downloaded at its pinned commit SHA from config/models.yaml, never `main`.
After the download the servers run with HF_HUB_OFFLINE=1, so a model that is not in the cache
fails fast instead of silently fetching something else.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

DEFAULT_PATTERNS = [
    "*.json",
    "*.safetensors",
    "*.txt",
    "*.model",
    "tokenizer*",
    "*.tiktoken",
    "LICENSE*",
]


def select(models: dict, which: str) -> dict:
    """Pick roles by group name ('workshop', 'demo', 'all') or by a comma list of role names."""
    if which in ("workshop", "demo"):
        return {
            k: v
            for k, v in models.items()
            if v.get("workshop") == (True if which == "workshop" else "demo")
        }
    if which == "all":
        return dict(models)
    wanted = [w.strip() for w in which.split(",") if w.strip()]
    missing = [w for w in wanted if w not in models]
    if missing:
        raise SystemExit(f"unknown model role(s): {', '.join(missing)}. Known: {', '.join(models)}")
    return {k: models[k] for k in wanted}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--models", default="workshop")
    ap.add_argument("--config", type=Path, default=Path("/opt/workshop/repo/config/models.yaml"))
    a = ap.parse_args()

    models = yaml.safe_load(a.config.read_text())["models"]
    chosen = select(models, a.models)
    if not chosen:
        print("nothing selected", file=sys.stderr)
        return 1

    from huggingface_hub import snapshot_download  # imported late so --help works anywhere

    for role, m in chosen.items():
        t0 = time.perf_counter()
        path = snapshot_download(
            repo_id=m["repo"],
            revision=m["revision"],
            allow_patterns=m.get("allow_patterns", DEFAULT_PATTERNS),
        )
        print(
            f"{role:10s} {m['repo']} @ {m['revision'][:12]}  {time.perf_counter() - t0:6.1f}s  {path}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
