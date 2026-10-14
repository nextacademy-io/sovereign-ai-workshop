#!/usr/bin/env python3
"""Compare one infbench result with one `vllm bench serve --save-result` JSON.

    python3 benchmark/scripts/compare_results.py infbench/c008.json vllm/vllm.json [--tolerance 10]

Two independent load generators measuring the same server should tell the same story. Differences
are expected where the tools define things differently (see docs/METRICS.md): prompts differ, chunk
boundaries differ, warm-up differs. This script shows every pair and flags those that differ by more
than the tolerance, so a harness bug cannot hide behind "close enough".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# (label, path into the infbench result, key in the vLLM bench result). Tail percentiles (p99) rest on a
# few dozen samples and swing from run to run, so they get three times the tolerance of means and medians.
PAIRS = [
    ("requests completed", ("requests",), "completed"),
    ("duration (s)", ("duration_s",), "duration"),
    ("output tokens/s (aggregate)", ("aggregate_tps",), "output_throughput"),
    ("requests/s", ("request_throughput_rps",), "request_throughput"),
    ("TTFT mean (ms)", ("ttft_ms", "mean"), "mean_ttft_ms"),
    ("TTFT median (ms)", ("ttft_ms", "p50"), "median_ttft_ms"),
    ("TTFT p99 (ms)", ("ttft_ms", "p99"), "p99_ttft_ms", True),
    ("TPOT mean (ms)", ("tpot_ms", "mean"), "mean_tpot_ms"),
    ("ITL mean (ms)", ("itl_ms", "mean"), "mean_itl_ms"),
    ("ITL p99 (ms)", ("itl_ms", "p99"), "p99_itl_ms", True),
    ("E2E latency mean (ms)", ("latency_ms", "mean"), "mean_e2el_ms"),
    ("E2E latency p99 (ms)", ("latency_ms", "p99"), "p99_e2el_ms", True),
]


def dig(doc: dict, path: tuple[str, ...]):
    for key in path:
        if not isinstance(doc, dict) or key not in doc or doc[key] is None:
            return None
        doc = doc[key]
    return doc


def compare(ours: dict, theirs: dict, tolerance_pct: float) -> list[dict]:
    rows = []
    for label, path, key, *tail in PAIRS:
        limit = tolerance_pct * (3 if tail else 1)
        a, b = dig(ours, path), theirs.get(key)
        if a is None or b is None:
            rows.append(
                {
                    "metric": label,
                    "infbench": a,
                    "vllm_bench": b,
                    "diff_pct": None,
                    "flag": "missing",
                }
            )
            continue
        diff = 100.0 * (a - b) / b if b else float("inf")
        flag = "ok" if abs(diff) <= limit else "DIFFERS"
        rows.append(
            {"metric": label, "infbench": a, "vllm_bench": b, "diff_pct": diff, "flag": flag}
        )
    return rows


def render(rows: list[dict], tolerance_pct: float) -> str:
    lines = [
        f"| Metric | infbench | vllm bench | difference | within {tolerance_pct:g} % |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for r in rows:
        fmt = lambda v: "n/a" if v is None else f"{v:,.2f}"  # noqa: E731
        diff = "n/a" if r["diff_pct"] is None else f"{r['diff_pct']:+.1f} %"
        lines.append(
            f"| {r['metric']} | {fmt(r['infbench'])} | {fmt(r['vllm_bench'])} | {diff} | {r['flag']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("infbench_json", type=Path)
    ap.add_argument("vllm_bench_json", type=Path)
    ap.add_argument("--tolerance", type=float, default=10.0, help="percent")
    ap.add_argument("--markdown-out", type=Path)
    a = ap.parse_args()
    rows = compare(
        json.loads(a.infbench_json.read_text()),
        json.loads(a.vllm_bench_json.read_text()),
        a.tolerance,
    )
    text = render(rows, a.tolerance)
    print(text)
    if a.markdown_out:
        a.markdown_out.write_text(text)
    return 1 if any(r["flag"] == "DIFFERS" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
