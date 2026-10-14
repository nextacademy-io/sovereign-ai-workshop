#!/usr/bin/env python3
"""Generate dashboards/workshop-inference.json.

The dashboard is generated, not hand-edited, so panel positions stay consistent and every
metric name can be checked against the list of metrics vLLM v0.31.0 really exports
(see test_dashboard.py). Run:  python3 monitoring/grafana/build_dashboard.py

Panels follow the workshop's question order: what does the user feel (request rate, TTFT, ITL,
latency), what is the server doing (running/waiting, KV cache, prefix cache, preemptions,
tokens/s), and what is the hardware doing (GPU utilization, VRAM, power, estimated MFU/MBU).
GPU metrics use DCGM's names so the same dashboard works with the pod exporter and dcgm-exporter.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("dashboards") / "workshop-inference.json"
DS = {"type": "prometheus", "uid": "workshop-prometheus"}
INTERVAL = "$__rate_interval"

# Datasheet peaks of the workshop GPU (RTX PRO 6000 Blackwell Server Edition), used only to
# scale the *estimated* utilisation panels. Dense BF16 is derived from the vendor's sparse
# figure at workstation clocks; see docs/RESEARCH.md. Edit the dashboard variables to change them.
PEAK_TFLOPS_BF16_DENSE = 504
PEAK_BANDWIDTH_GBS = 1597

_next_id = [0]


def _id() -> int:
    _next_id[0] += 1
    return _next_id[0]


def target(expr: str, legend: str, ref: str = "A") -> dict:
    return {"datasource": DS, "expr": expr, "legendFormat": legend, "refId": ref, "range": True}


def quantiles(metric: str, qs=(0.5, 0.95)) -> list[dict]:
    return [
        target(
            f"histogram_quantile({q}, sum by (le) (rate({metric}_bucket[{INTERVAL}])))",
            f"p{int(q * 100)}",
            chr(ord("A") + i),
        )
        for i, q in enumerate(qs)
    ]


def panel(
    title,
    targets,
    x,
    y,
    w=8,
    h=7,
    unit="short",
    description="",
    minimum=None,
    maximum=None,
    kind="timeseries",
):
    defaults: dict = {
        "unit": unit,
        "custom": {"lineWidth": 2, "fillOpacity": 12, "showPoints": "never"},
    }
    if minimum is not None:
        defaults["min"] = minimum
    if maximum is not None:
        defaults["max"] = maximum
    return {
        "id": _id(),
        "type": kind,
        "title": title,
        "description": description,
        "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "fieldConfig": {"defaults": defaults, "overrides": []},
        "options": {
            "legend": {"displayMode": "list", "placement": "bottom"},
            "tooltip": {"mode": "multi"},
        },
        "targets": targets,
    }


def row(title: str, y: int) -> dict:
    return {
        "id": _id(),
        "type": "row",
        "title": title,
        "collapsed": False,
        "gridPos": {"x": 0, "y": y, "w": 24, "h": 1},
        "panels": [],
    }


def build() -> dict:
    _next_id[0] = 0
    p = []
    # ---------------------------------------------------------------- user experience
    p.append(row("What the user feels", 0))
    p.append(
        panel(
            "Request rate",
            [target(f"sum(rate(vllm:request_success_total[{INTERVAL}]))", "requests/s")],
            0,
            1,
            6,
            unit="reqps",
            description="Completed requests per second. Compare with the load you generate: if the line is flat while load rises, the server is saturated.",
        )
    )
    p.append(
        panel(
            "TTFT (time to first token)",
            quantiles("vllm:time_to_first_token_seconds"),
            6,
            1,
            6,
            unit="s",
            description="Queueing + prefill. Grows with prompt length and with waiting requests.",
        )
    )
    p.append(
        panel(
            "Inter-token latency",
            quantiles("vllm:inter_token_latency_seconds"),
            12,
            1,
            6,
            unit="s",
            description="Gap between streamed tokens. 1 / ITL is the tokens per second one user sees.",
        )
    )
    p.append(
        panel(
            "End-to-end latency",
            quantiles("vllm:e2e_request_latency_seconds"),
            18,
            1,
            6,
            unit="s",
            description="Request arrival to last token, including queueing.",
        )
    )
    # ---------------------------------------------------------------- server state
    p.append(row("What the server is doing", 8))
    p.append(
        panel(
            "Running requests",
            [target("sum(vllm:num_requests_running)", "running")],
            0,
            9,
            4,
            unit="short",
            minimum=0,
            description="Requests in the current batch. Bounded by --max-num-seqs and by KV cache capacity.",
        )
    )
    p.append(
        panel(
            "Waiting requests",
            [target("sum(vllm:num_requests_waiting)", "waiting")],
            4,
            9,
            4,
            unit="short",
            minimum=0,
            description="Queue depth. Anything above zero for a sustained time means arrivals exceed capacity.",
        )
    )
    p.append(
        panel(
            "Tokens per second",
            [
                target(
                    f"sum(rate(vllm:generation_tokens_total[{INTERVAL}]))",
                    "generated (decode)",
                    "A",
                ),
                target(f"sum(rate(vllm:prompt_tokens_total[{INTERVAL}]))", "prompt (prefill)", "B"),
            ],
            8,
            9,
            6,
            unit="short",
            description="Aggregate throughput. Decode tokens are what users read; prefill tokens are the work done on prompts.",
        )
    )
    p.append(
        panel(
            "KV cache usage",
            [target("max(vllm:kv_cache_usage_perc) * 100", "KV cache used")],
            14,
            9,
            5,
            unit="percent",
            minimum=0,
            maximum=100,
            description="Share of KV cache blocks in use. Near 100 % the scheduler must queue or preempt requests.",
        )
    )
    p.append(
        panel(
            "Prefix cache hit rate",
            [
                target(
                    f"sum(rate(vllm:prefix_cache_hits_total[{INTERVAL}])) / sum(rate(vllm:prefix_cache_queries_total[{INTERVAL}]))",
                    "hit rate",
                )
            ],
            19,
            9,
            5,
            unit="percentunit",
            minimum=0,
            maximum=1,
            description="Cached prompt tokens / queried prompt tokens. High with shared system prompts or documents.",
        )
    )
    p.append(
        panel(
            "Preemptions",
            [target(f"sum(rate(vllm:num_preemptions_total[{INTERVAL}]))", "preemptions/s")],
            0,
            16,
            6,
            unit="ops",
            minimum=0,
            description="Requests evicted from the KV cache and recomputed later. Non-zero means memory pressure.",
        )
    )
    p.append(
        panel(
            "Queue time",
            quantiles("vllm:request_queue_time_seconds"),
            6,
            16,
            6,
            unit="s",
            description="Time spent waiting before the first scheduling. The bucket floor is 0.3 s, so small values read as ~0.3.",
        )
    )
    p.append(
        panel(
            "Prefill vs decode time",
            [
                target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vllm:request_prefill_time_seconds_bucket[{INTERVAL}])))",
                    "prefill p50",
                    "A",
                ),
                target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vllm:request_decode_time_seconds_bucket[{INTERVAL}])))",
                    "decode p50",
                    "B",
                ),
            ],
            12,
            16,
            6,
            unit="s",
            description="Where a request spends its time once it runs.",
        )
    )
    p.append(
        panel(
            "Finished requests by reason",
            [
                target(
                    f"sum by (finished_reason) (rate(vllm:request_success_total[{INTERVAL}]))",
                    "{{finished_reason}}",
                )
            ],
            18,
            16,
            6,
            unit="reqps",
            description="stop = model ended, length = hit max_tokens, abort = client left.",
        )
    )
    # ---------------------------------------------------------------- hardware
    p.append(row("What the hardware is doing", 23))
    p.append(
        panel(
            "GPU utilization",
            [target("avg(DCGM_FI_DEV_GPU_UTIL)", "GPU-Util")],
            0,
            24,
            6,
            unit="percent",
            minimum=0,
            maximum=100,
            description="Share of time any kernel ran. NOT efficiency: a GPU can read 100 % while moving little data.",
        )
    )
    p.append(
        panel(
            "VRAM used",
            [
                target("sum(DCGM_FI_DEV_FB_USED) / 1024", "used (GiB)", "A"),
                target("sum(DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE) / 1024", "total (GiB)", "B"),
            ],
            6,
            24,
            6,
            unit="short",
            minimum=0,
            description="vLLM reserves its memory budget at startup, so this is flat; the KV cache panel shows the real use.",
        )
    )
    p.append(
        panel(
            "Power",
            [target("sum(DCGM_FI_DEV_POWER_USAGE)", "watts")],
            12,
            24,
            4,
            unit="watt",
            minimum=0,
            description="Power draw rises with real compute, which is a better hint of work than GPU-Util.",
        )
    )
    p.append(
        panel(
            "Estimated compute use (MFU)",
            [
                target(
                    f"sum(rate(vllm:estimated_flops_per_gpu_total[{INTERVAL}])) / ($peak_tflops * 1e12)",
                    "estimated MFU",
                )
            ],
            16,
            24,
            4,
            unit="percentunit",
            minimum=0,
            maximum=1,
            description="vLLM's own FLOP estimate divided by the peak you set in the variable. Needs --enable-mfu-metrics. An estimate, not a hardware counter.",
        )
    )
    p.append(
        panel(
            "Estimated memory traffic (MBU)",
            [
                target(
                    f"(sum(rate(vllm:estimated_read_bytes_per_gpu_total[{INTERVAL}])) + sum(rate(vllm:estimated_write_bytes_per_gpu_total[{INTERVAL}]))) / ($peak_bw_gbs * 1e9)",
                    "estimated MBU",
                )
            ],
            20,
            24,
            4,
            unit="percentunit",
            minimum=0,
            maximum=1,
            description="Estimated bytes moved per second divided by peak bandwidth. Decode is usually limited here, prefill by compute.",
        )
    )

    def textbox(name, label, value):
        return {
            "name": name,
            "label": label,
            "type": "textbox",
            "query": str(value),
            "current": {"text": str(value), "value": str(value)},
            "options": [{"selected": True, "text": str(value), "value": str(value)}],
            "hide": 0,
        }

    return {
        "uid": "workshop-inference",
        "title": "KI ohne Cloud: inference",
        "tags": ["workshop", "vllm", "inference"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "5s",
        "time": {"from": "now-15m", "to": "now"},
        "editable": False,
        "graphTooltip": 1,
        "templating": {
            "list": [
                textbox("peak_tflops", "Peak dense BF16 TFLOPS", PEAK_TFLOPS_BF16_DENSE),
                textbox("peak_bw_gbs", "Peak memory bandwidth GB/s", PEAK_BANDWIDTH_GBS),
            ]
        },
        "annotations": {"list": []},
        "panels": p,
    }


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"wrote {OUT}")
