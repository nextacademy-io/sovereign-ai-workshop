#!/usr/bin/env python3
"""Print a Markdown table from result files, so RESULTS.md tables are copied from data and never typed.

    python3 benchmark/scripts/results_table.py benchmark/results/reference/concurrency --match baseline-c \\
        --columns concurrency ttft_ms.p50 ttft_ms.p95 output_tps_per_request.p50 aggregate_tps

Columns are dotted paths into the result JSON; `server.gauges.num_requests_waiting.max` and the other
nested fields work too. Rows are sorted by path (natural order).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LABEL = {
    "concurrency": "Concurrency",
    "requests": "Requests",
    "ttft_ms.p50": "TTFT p50 (ms)",
    "ttft_ms.p95": "TTFT p95 (ms)",
    "itl_ms.p50": "ITL p50 (ms)",
    "itl_ms.p95": "ITL p95 (ms)",
    "latency_ms.p50": "Latency p50 (ms)",
    "latency_ms.p95": "Latency p95 (ms)",
    "output_tps_per_request.p50": "Tokens/s per request",
    "aggregate_tps": "Aggregate tokens/s",
    "request_throughput_rps": "Requests/s",
    "gpu.utilization_pct.mean": "GPU util (%)",
    "gpu.power_w.mean": "Power (W)",
    "gpu.memory_used_mib.max": "VRAM max (MiB)",
    "server.gauges.num_requests_running.max": "Running max",
    "server.gauges.num_requests_waiting.max": "Waiting max",
    "server.gauges.kv_cache_usage_perc.max": "KV usage max",
    "server.prefix_cache_hit_rate": "Prefix hit rate",
    "server.counters_delta.preemptions": "Preemptions",
    "configuration.server_profile": "Profile",
}


def natural(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def dig(doc, path: str):
    for part in path.split("."):
        if not isinstance(doc, dict) or part not in doc:
            return None
        doc = doc[part]
    return doc


def fmt(path: str, v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, str):
        return v
    if path.endswith("kv_cache_usage_perc.max") or path.endswith("prefix_cache_hit_rate"):
        return f"{v * 100:.1f} %"
    if "memory_used" in path:
        return f"{v / 1024:.1f} GiB"
    if path.endswith("rps"):
        return f"{v:,.2f}"
    if "tps" in path or "power" in path or "itl" in path:
        return f"{v:,.1f}"
    return f"{v:,.0f}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("root", type=Path)
    ap.add_argument("--match", default="")
    ap.add_argument("--columns", nargs="+", required=True)
    ap.add_argument(
        "--label-column", action="store_true", help="first column: the result directory name"
    )
    a = ap.parse_args(argv)
    files = sorted(
        (p for p in a.root.rglob("*.json") if a.match in str(p)), key=lambda p: natural(str(p))
    )
    rows = []
    for p in files:
        d = json.loads(p.read_text())
        if not isinstance(d, dict) or "ttft_ms" not in d:
            continue
        cells = [p.parent.name] if a.label_column else []
        cells += [fmt(c, dig(d, c)) for c in a.columns]
        rows.append(cells)
    head = (["Run"] if a.label_column else []) + [LABEL.get(c, c) for c in a.columns]
    print("| " + " | ".join(head) + " |")
    print("| " + " | ".join(["---"] * len(head)) + " |")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
