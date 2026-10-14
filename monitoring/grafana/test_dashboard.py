import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("build_dashboard", HERE / "build_dashboard.py")
bd = importlib.util.module_from_spec(spec)
sys.modules["build_dashboard"] = bd
spec.loader.exec_module(bd)

# Scraped metric names of vLLM v0.31.0 (docs/RESEARCH.md section 9, source: vllm/v1/metrics/loggers.py).
HIST = [
    "time_to_first_token_seconds",
    "inter_token_latency_seconds",
    "request_time_per_output_token_seconds",
    "e2e_request_latency_seconds",
    "request_queue_time_seconds",
    "request_inference_time_seconds",
    "request_prefill_time_seconds",
    "request_decode_time_seconds",
    "request_prompt_tokens",
    "request_generation_tokens",
    "iteration_tokens_total",
]
KNOWN = {
    "vllm:num_requests_running",
    "vllm:num_requests_waiting",
    "vllm:num_requests_waiting_by_reason",
    "vllm:kv_cache_usage_perc",
    "vllm:prefix_cache_queries_total",
    "vllm:prefix_cache_hits_total",
    "vllm:num_preemptions_total",
    "vllm:prompt_tokens_total",
    "vllm:generation_tokens_total",
    "vllm:prompt_tokens_cached_total",
    "vllm:request_success_total",
    "vllm:estimated_flops_per_gpu_total",
    "vllm:estimated_read_bytes_per_gpu_total",
    "vllm:estimated_write_bytes_per_gpu_total",
} | {f"vllm:{h}{s}" for h in HIST for s in ("_bucket", "_sum", "_count")}
DCGM = {
    "DCGM_FI_DEV_GPU_UTIL",
    "DCGM_FI_DEV_FB_USED",
    "DCGM_FI_DEV_FB_FREE",
    "DCGM_FI_DEV_POWER_USAGE",
}
REMOVED = (
    "vllm:gpu_cache_usage_perc",
    "vllm:cpu_cache_usage_perc",
    "vllm:num_requests_swapped",
    "vllm:time_per_output_token_seconds",
)


def exprs(doc):
    return [t["expr"] for p in doc["panels"] for t in p.get("targets", [])]


def test_committed_dashboard_matches_the_generator():
    committed = json.loads((HERE / "dashboards" / "workshop-inference.json").read_text())
    assert committed == bd.build(), "run: python3 monitoring/grafana/build_dashboard.py"


def test_every_vllm_metric_is_a_real_vllm_031_metric():
    for e in exprs(bd.build()):
        for name in re.findall(r"vllm:[a-z0-9_]+", e):
            assert name in KNOWN, f"{name} is not exported by vLLM v0.31.0 ({e})"
            assert name not in REMOVED


def test_gpu_panels_use_dcgm_metric_names():
    used = {m for e in exprs(bd.build()) for m in re.findall(r"DCGM_FI_[A-Z_]+", e)}
    assert used and used <= DCGM


def test_the_eight_panels_the_workshop_promises_exist():
    titles = " | ".join(p["title"] for p in bd.build()["panels"])
    for needed in (
        "Request rate",
        "TTFT",
        "End-to-end latency",
        "Tokens per second",
        "Running requests",
        "Waiting requests",
        "GPU utilization",
        "VRAM",
    ):
        assert needed in titles


def test_panels_do_not_overlap_and_ids_are_unique():
    panels = [p for p in bd.build()["panels"] if p["type"] != "row"]
    assert len({p["id"] for p in bd.build()["panels"]}) == len(bd.build()["panels"])
    for i, a in enumerate(panels):
        for b in panels[i + 1 :]:
            ga, gb = a["gridPos"], b["gridPos"]
            overlap = (
                ga["x"] < gb["x"] + gb["w"]
                and gb["x"] < ga["x"] + ga["w"]
                and ga["y"] < gb["y"] + gb["h"]
                and gb["y"] < ga["y"] + ga["h"]
            )
            assert not overlap, f"{a['title']} overlaps {b['title']}"
