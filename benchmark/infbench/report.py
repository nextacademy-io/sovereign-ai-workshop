"""Turn raw request results into the JSON result schema and Markdown tables."""

from __future__ import annotations

from collections import Counter

from .client import RequestResult
from .runner import RunOutcome
from .stats import summarize

SCHEMA_VERSION = 1


def parse_slo(spec: str | None) -> dict[str, float]:
    """'ttft_ms=800,output_tps=25,latency_ms=8000' -> {'ttft_ms': 800.0, ...}"""
    out: dict[str, float] = {}
    for part in filter(None, (spec or "").split(",")):
        key, _, value = part.partition("=")
        if key.strip() not in {"ttft_ms", "output_tps", "latency_ms"}:
            raise ValueError(f"unknown SLO key '{key}' (use ttft_ms, output_tps, latency_ms)")
        out[key.strip()] = float(value)
    return out


def _meets(r: RequestResult, slo: dict[str, float]) -> bool:
    """A request counts toward goodput only if it met every stated target."""
    violations = (
        "ttft_ms" in slo and (r.ttft_s is None or r.ttft_s * 1000 > slo["ttft_ms"]),
        "latency_ms" in slo and (r.latency_s is None or r.latency_s * 1000 > slo["latency_ms"]),
        "output_tps" in slo and (r.output_tps is None or r.output_tps < slo["output_tps"]),
    )
    return not any(violations)


def build_result(
    *,
    configuration: dict,
    outcome: RunOutcome,
    gpu: dict | None,
    server: dict | None,
    slo: dict[str, float] | None = None,
) -> dict:
    ok = [r for r in outcome.results if r.ok]
    failed = [r for r in outcome.results if not r.ok]
    duration = outcome.duration_s

    prompt_tokens = sum(r.prompt_tokens or 0 for r in ok)
    completion_tokens = sum(r.completion_tokens or 0 for r in ok)
    per_request_tps = [r.output_tps for r in ok if r.output_tps]

    result: dict = {
        "schema_version": SCHEMA_VERSION,
        "configuration": configuration,
        "requests": len(ok),
        "requests_failed": len(failed),
        "concurrency": outcome.concurrency,
        "request_rate_target": outcome.request_rate,
        "load_mode": outcome.mode,
        "duration_s": round(duration, 3),
        "ttft_ms": summarize((r.ttft_s for r in ok if r.ttft_s is not None), scale=1000),
        "itl_ms": summarize((x for r in ok for x in r.itl_s), scale=1000),
        "tpot_ms": summarize((r.tpot_s for r in ok if r.tpot_s), scale=1000),
        "latency_ms": summarize((r.latency_s for r in ok if r.latency_s is not None), scale=1000),
        # Tokens per second one user sees after the first token: 1 / TPOT.
        "output_tps": round(sum(per_request_tps) / len(per_request_tps), 2)
        if per_request_tps
        else None,
        "output_tps_per_request": summarize(per_request_tps, ndigits=2, low=(1, 5)),
        # Tokens per second the whole server delivered over the whole run.
        "aggregate_tps": round(completion_tokens / duration, 2),
        "input_tps": round(prompt_tokens / duration, 2),
        "total_tps": round((prompt_tokens + completion_tokens) / duration, 2),
        "request_throughput_rps": round(len(ok) / duration, 4),
        "tokens": {
            "prompt_total": prompt_tokens,
            "completion_total": completion_tokens,
            "prompt_mean": round(prompt_tokens / len(ok), 1) if ok else None,
            "completion_mean": round(completion_tokens / len(ok), 1) if ok else None,
        },
        "gpu": gpu,
        "server": server,
    }
    if failed:
        counts = Counter(r.error for r in failed)
        result["errors"] = [{"count": n, "error": e} for e, n in counts.most_common(5)]
    if slo:
        met = [r for r in ok if _meets(r, slo)]
        result["slo"] = {
            "targets": slo,
            "attainment": round(len(met) / len(outcome.results), 4) if outcome.results else None,
            "goodput_rps": round(len(met) / duration, 4),
        }
    return result


def _fmt(value: float | None, digits: int = 0) -> str:
    return "n/a" if value is None else f"{value:,.{digits}f}"


def result_row(result: dict) -> list[str]:
    ttft, lat, itl = result["ttft_ms"] or {}, result["latency_ms"] or {}, result["itl_ms"] or {}
    tps = result["output_tps_per_request"] or {}
    gpu = result.get("gpu") or {}
    util, mem = gpu.get("utilization_pct") or {}, gpu.get("memory_used_mib") or {}
    load = (
        result["concurrency"]
        if result["concurrency"] is not None
        else f"{result['request_rate_target']}/s"
    )
    return [
        str(load),
        str(result["requests"])
        + (f" (+{result['requests_failed']} failed)" if result["requests_failed"] else ""),
        _fmt(ttft.get("p50")),
        _fmt(ttft.get("p95")),
        _fmt(lat.get("p50")),
        _fmt(lat.get("p95")),
        _fmt(itl.get("p50"), 1),
        _fmt(tps.get("p50"), 1),
        _fmt(result["aggregate_tps"]),
        _fmt(result["request_throughput_rps"], 2),
        _fmt(util.get("mean"), 0),
        _fmt((mem.get("max") or 0) / 1024 if mem else None, 1),
    ]


HEADER = [
    "Load",
    "Requests",
    "TTFT p50 (ms)",
    "TTFT p95 (ms)",
    "Latency p50 (ms)",
    "Latency p95 (ms)",
    "ITL p50 (ms)",
    "Output TPS/req p50",
    "Aggregate TPS",
    "Req/s",
    "GPU util mean (%)",
    "VRAM max (GiB)",
]


def markdown_summary(results: list[dict]) -> str:
    if not results:
        return "No results.\n"
    cfg = results[0]["configuration"]
    hw = cfg["hardware"]
    wl = cfg["workload"]
    lines = [
        f"# Benchmark: {wl['name']}",
        "",
        f"- **Hardware:** {hw.get('gpu_count')}× {hw.get('gpu')} ({hw.get('vram_gb')} GB), driver {hw.get('driver_version')}",
        f"- **Model:** `{cfg['model']}` @ `{(cfg.get('model_revision') or 'unknown')[:12]}`",
        f"- **Engine:** {cfg['engine']} {cfg.get('engine_version')} · CUDA {cfg.get('cuda_version')}",
        f"- **Workload:** {wl['input_tokens']} input tokens, {wl['output_tokens']} output tokens"
        + (
            f", {wl['shared_prefix_tokens']} shared prefix tokens"
            if wl.get("shared_prefix_tokens")
            else ""
        ),
        f"- **Server arguments:** `{cfg.get('server_args')}`",
        f"- **Date:** {cfg['date']} · prompt seed {wl.get('seed')}",
        "",
        "| " + " | ".join(HEADER) + " |",
        "| " + " | ".join(["---"] * len(HEADER)) + " |",
    ]
    lines += ["| " + " | ".join(result_row(r)) + " |" for r in results]
    lines += [
        "",
        "TTFT = time to first token. ITL = inter-token latency. Output TPS/req = tokens per second one",
        "request sees after its first token (1 / TPOT). Aggregate TPS = output tokens per second",
        "delivered by the whole server over the run. GPU utilization is the share of time any kernel",
        "ran, not an efficiency measure.",
        "",
    ]
    return "\n".join(lines)
