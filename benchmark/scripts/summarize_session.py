#!/usr/bin/env python3
"""One line per result file of a session, to read the whole picture before writing anything about it.

    python3 benchmark/scripts/summarize_session.py benchmark/results/<session> [experiment ...]

Shows profile, load, request shape, latency, throughput, GPU and server gauges. It prints facts only;
interpretation belongs in experiments/<name>/RESULTS.md after the surprises have been investigated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def line(path: Path, root: Path) -> str | None:
    try:
        d = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or "ttft_ms" not in d:
        return None
    cfg, wl = d["configuration"], d["configuration"]["workload"]
    ttft, itl, lat = d["ttft_ms"] or {}, d["itl_ms"] or {}, d["latency_ms"] or {}
    tps = d["output_tps_per_request"] or {}
    srv, gpu = d.get("server") or {}, d.get("gpu") or {}
    g = srv.get("gauges", {})
    util = (gpu.get("utilization_pct") or {}).get("mean")
    mem = (gpu.get("memory_used_mib") or {}).get("max")
    power = (gpu.get("power_w") or {}).get("mean")
    c = d["concurrency"] if d["concurrency"] is not None else f"{d['request_rate_target']}/s"
    shape = f"{wl['input_tokens']}/{wl['output_tokens']}" + (
        f"+p{wl['shared_prefix_tokens']}" if wl.get("shared_prefix_tokens") else ""
    )
    return (
        f"{str(path.relative_to(root)):<52} {cfg.get('server_profile') or '-':<16} c={c!s:<4} {shape:<12} "
        f"n={d['requests']:<4} fail={d['requests_failed']:<2} "
        f"ttft50={ttft.get('p50', 0):>7.0f} p95={ttft.get('p95', 0):>7.0f}  itl50={itl.get('p50', 0):>5.1f} p95={itl.get('p95', 0):>5.1f}  "
        f"lat50={lat.get('p50', 0):>7.0f}  tps/req={tps.get('p50', 0):>6.1f}  agg={d['aggregate_tps']:>7.1f}  rps={d['request_throughput_rps']:>5.2f}  "
        f"gpu%={util or 0:>3.0f} vram={((mem or 0) / 1024):>5.1f}G pw={power or 0:>4.0f}W  "
        f"run={g.get('num_requests_running', {}).get('max', 0):>3.0f} wait={g.get('num_requests_waiting', {}).get('max', 0):>3.0f} "
        f"kv={g.get('kv_cache_usage_perc', {}).get('max', 0) * 100:>4.1f}% pfx={((srv.get('prefix_cache_hit_rate') or 0) * 100):>4.1f}% "
        f"preempt={(srv.get('counters_delta') or {}).get('preemptions', 0):.0f}"
    )


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    root = Path(argv[0])
    names = argv[1:]
    for path in sorted(root.rglob("*.json")):
        if names and path.relative_to(root).parts[0] not in names:
            continue
        out = line(path, root)
        if out:
            print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
