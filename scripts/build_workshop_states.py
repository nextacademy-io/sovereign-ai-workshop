#!/usr/bin/env python3
"""Generate the workshop states 02 to 05 from the measured reference results.

A workshop state is a known-good starting point for a lab (`./scripts/reset.sh lab-NN`): the inference report
filled in as far as the earlier labs would have, plus the reference results to fall back on. The numbers in
the filled sections are NEVER typed: they are read from `benchmark/results/reference/` by this script, so a
re-measurement and a rerun of this script update every state together.

    python3 scripts/build_workshop_states.py            write workshop-states/0[2-5]-*/
    python3 scripts/build_workshop_states.py --check    exit 1 if the checked-in states are stale

State 01 (the clean templates) is hand-written and not touched.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "benchmark" / "results" / "reference"
TEMPLATE = ROOT / "workshop-artifacts" / "inference-report.md"
STATES = ROOT / "workshop-states"
BANNER = (
    "**Reference version.** The sections filled in below come from the trainer's measured reference run "
    "(`benchmark/results/reference/`, workshop GPU). They are here so you can continue if you fell behind: "
    "replace every number with your own as soon as you have it, and keep the file next to each number.\n"
)


def load(rel: str) -> dict:
    return json.loads((REF / rel).read_text())


def dig(doc: dict, path: str):
    for part in path.split("."):
        doc = doc[part]
    return doc


def run(experiment: str, run_name: str) -> dict:
    """The single result file of one run directory."""
    files = sorted((REF / experiment / run_name).glob("c*.json"))
    if len(files) != 1:
        raise FileNotFoundError(
            f"{experiment}/{run_name}: expected one result file, found {len(files)}"
        )
    return json.loads(files[0].read_text())


def n(value: float, digits: int = 0) -> str:
    return f"{value:,.{digits}f}"


def hit_rate(result: dict) -> str:
    """Prefix-cache hit rate in percent; with caching off the server counts no queries at all, so the rate is 0."""
    rate = result["server"].get("prefix_cache_hit_rate")
    return "0.0" if rate is None else f"{rate * 100:.1f}"


# ------------------------------------------------------------------------------------------ section bodies
def section_selected_model() -> str:
    return """_Lab 1. Model, precision, why this one, which alternatives you rejected and why. Licence and commercial implications._

| | |
| --- | --- |
| Model and revision | `Qwen/Qwen3-8B` at `b968826d9c46dd6066d109eabc6255188de91218` (the workshop's primary model; replace with your own choice for your scenario) |
| Precision | BF16 (FP8 is the Day 2 experiment) |
| Licence (and what it means for commercial use) | Apache-2.0: commercial use permitted; keep the licence and attribution notices |
| Why it is the smallest model that does the task | Reference answer for the workshop workload only: a dense 8B model with tool calling and structured output that fits one GPU with room for a large KV cache. For your scenario, argue it from your own eval. |
| Rejected alternatives | `Qwen/Qwen3-1.7B` (smaller, would need an eval on your items); `Qwen/Qwen3-30B-A3B-FP8` (mixture of experts: all 30.5 B weights must be resident) |
"""


def section_hardware() -> str:
    check = load("baseline/kv-formula-check.json")
    mem = load("baseline/memory-accounting.json")["startup_log"]
    acc = mem["memory_accounting_gib"]
    cfg = load("baseline/kv-formula-check.json")["configuration"]["hardware"]
    return f"""_Lab 2. What is the GPU? How much memory, how much bandwidth? How much of the memory is weights, how much is KV cache, how many tokens fit?_

| | |
| --- | --- |
| GPU | {cfg["gpu"]}, driver {cfg["driver_version"]} |
| VRAM / memory bandwidth | {n(acc["device_total"], 2)} GiB usable of a 96 GB card / 1,597 GB/s (datasheet) |
| Weights (GiB) | {n(check["model_memory_gib"], 2)} measured in memory (BF16, 8.2 B parameters × 2 bytes) |
| KV cache capacity (tokens) and how you computed it | {n(check["reported_tokens"])} tokens reported by vLLM; {n(check["available_kv_gib"], 2)} GiB available ÷ {n(check["kv_bytes_per_token"])} B per token (2 × 36 layers × 8 KV heads × 128 × 2 B) = {n(check["predicted_tokens"])} |
| Maximum concurrency at the context length you need | {n(mem["kv_cache_max_concurrency"], 2)}× at 32,768 tokens per request (as reported by vLLM) |
"""


def baseline_table() -> tuple[str, dict]:
    rows = []
    data = {}
    for c in (1, 4, 8, 16):
        d = run("concurrency", f"baseline-c{c:03d}")
        data[c] = d
        gpu = d["gpu"]
        rows.append(
            f"| {c} | {n(d['ttft_ms']['p50'])} ms | {n(d['ttft_ms']['p95'])} ms | {n(d['latency_ms']['p50'])} ms "
            f"| {n(d['latency_ms']['p95'])} ms | {n(d['output_tps_per_request']['p50'], 1)} | {n(d['aggregate_tps'], 1)} "
            f"| {n(gpu['utilization_pct']['mean'])} % | {n(gpu['memory_used_mib']['max'] / 1024, 1)} GiB |"
        )
    return "\n".join(rows), data


def section_baseline() -> str:
    rows, d = baseline_table()
    return f"""_Lab 3. The same deployment at concurrency 1, 4, 8 and 16. Link the result files._

Reference results: `benchmark/results/reference/concurrency/baseline-c001` to `baseline-c016`.

| Concurrency | TTFT p50 | TTFT p95 | Latency p50 | Latency p95 | Output TPS / request | Aggregate TPS | GPU util | VRAM |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{rows}

1. When does throughput stop scaling? It keeps growing up to concurrency 16 ({n(d[8]["aggregate_tps"])} tokens/s at 8, {n(d[16]["aggregate_tps"])} at 16) but every doubling adds less; the reference sweep to 64 does not flatten either.
2. When does latency deteriorate? Time to first token p95 passes the 800 ms of the example SLO between concurrency 8 ({n(d[8]["ttft_ms"]["p95"])} ms) and 16 ({n(d[16]["ttft_ms"]["p95"])} ms); the speed per request falls from {n(d[1]["output_tps_per_request"]["p50"])} to {n(d[16]["output_tps_per_request"]["p50"])} tokens/s.
3. What resource looks saturated? GPU utilization reads about 100 % everywhere, so it tells you nothing; power draw rises from {n(d[1]["gpu"]["power_w"]["mean"])} W to {n(d[16]["gpu"]["power_w"]["mean"])} W and waiting requests appear at 16.
4. Which configuration would you deploy, and why? Concurrency 8 per GPU meets the example SLO (TTFT p95 under 800 ms, at least 25 tokens/s per request) with room; at 20 users you need FP8 weights or a second GPU.
"""


def section_experiments() -> str:
    # A: quantization
    qb, qf = run("quantization", "baseline-c016"), run("quantization", "fp8-c016")
    qb1, qf1 = run("quantization", "baseline-c001"), run("quantization", "fp8-c001")
    start = load("quantization/startup.json")
    qual = load("quantization/quality-comparison.json")["fp8"]
    # B: prefix caching
    pb = run("prefix-cache", "baseline-shared-c008")
    pn = run("prefix-cache", "no-prefix-cache-shared-c008")
    # C: context length
    cb = run("context-length", "baseline-c008-in08192")
    cc = run("context-length", "kv-constrained-c008-in08192")
    # D: batching
    db, dc = run("concurrency", "baseline-c016"), run("concurrency", "max-seqs-8-c016")
    return f"""_Lab 4. One hypothesis, one changed variable, measured before and after. Reference results for all four hypotheses (`benchmark/results/reference/`):_

**A. Quantization** (`quantization/`: `baseline-c*` against `fp8-c*`)

```text
Hypothesis: FP8 weights make decode faster and free memory for more KV cache, at some cost in quality
Change (one variable): profile fp8 (published FP8 checkpoint of the same model)
Before: concurrency 1: ITL p50 {n(qb1["itl_ms"]["p50"], 1)} ms, {n(qb1["output_tps_per_request"]["p50"], 1)} tokens/s per request; concurrency 16: {n(qb["aggregate_tps"])} tokens/s, TTFT p50 {n(qb["ttft_ms"]["p50"])} ms
After:  concurrency 1: ITL p50 {n(qf1["itl_ms"]["p50"], 1)} ms, {n(qf1["output_tps_per_request"]["p50"], 1)} tokens/s per request; concurrency 16: {n(qf["aggregate_tps"])} tokens/s, TTFT p50 {n(qf["ttft_ms"]["p50"])} ms
Metric improved: decode speed, throughput, time to first token
Metric degraded: the first start of a new checkpoint is slow (about 2.5 minutes in the reference session, {n(start["fp8"]["startup_seconds"])} s once its compile caches exist, against {n(start["baseline"]["startup_seconds"])} s for baseline)
Quality impact: {n(qual["other"]["accuracy"] * 100, 1)} % against {n(qual["reference"]["accuracy"] * 100, 1)} % on {qual["items"]} spot-check items (difference {n(qual["accuracy_difference_points"], 1)} points, within the noise of this probe); {n(qual["greedy_completions_identical"] * 100)} % of greedy completions are identical to BF16
Memory impact: weights {n(start["baseline"]["startup"]["model_memory_gib"], 2)} to {n(start["fp8"]["startup"]["model_memory_gib"], 2)} GiB; KV capacity {n(start["baseline"]["startup"]["kv_cache_tokens"])} to {n(start["fp8"]["startup"]["kv_cache_tokens"])} tokens
Operational impact: a second checkpoint to pin and store; a quality check before every model update
Recommendation: use FP8 for latency and cost when your own quality check passes; do not use it where outputs must stay identical to BF16
```

**B. Prefix caching** (`prefix-cache/`: `baseline-shared-c008` against `no-prefix-cache-shared-c008`)

```text
Hypothesis: a long prompt prefix shared by many requests is prefilled only once
Change (one variable): profile no-prefix-cache (prefix caching off)
Before (cache on):  TTFT p50 {n(pb["ttft_ms"]["p50"])} ms, aggregate {n(pb["aggregate_tps"])} tokens/s, prefix hit rate {hit_rate(pb)} %
After (cache off):  TTFT p50 {n(pn["ttft_ms"]["p50"])} ms, aggregate {n(pn["aggregate_tps"])} tokens/s, prefix hit rate {hit_rate(pn)} %
Metric improved: time to first token with the cache on
Metric degraded: nothing at the server; the cache uses KV memory that could hold other requests
Quality impact: none (same model, same outputs)
Memory impact: cached blocks occupy KV pool until evicted
Operational impact: none; but benchmarks that repeat their prompts measure the cache, not the deployment
Recommendation: leave it on; design prompts so the shared part comes first
```

**C. Context length** (`context-length/`: `baseline-c008-in08192` against `kv-constrained-c008-in08192`)

```text
Hypothesis: with a small KV budget, long prompts queue
Change (one variable): profile kv-constrained (4 GiB KV pool, 16,384-token context limit)
Before: concurrency 8, 8,192-token prompts: TTFT p50 {n(cb["ttft_ms"]["p50"])} ms, aggregate {n(cb["aggregate_tps"])} tokens/s, {n(cb["server"]["gauges"]["num_requests_running"]["max"])} requests running, KV usage up to {n(cb["server"]["gauges"]["kv_cache_usage_perc"]["max"] * 100)} %
After:  TTFT p50 {n(cc["ttft_ms"]["p50"])} ms, aggregate {n(cc["aggregate_tps"])} tokens/s, {n(cc["server"]["gauges"]["num_requests_running"]["max"])} requests running, {n(cc["server"]["gauges"]["num_requests_waiting"]["max"])} waiting, KV usage up to {n(cc["server"]["gauges"]["kv_cache_usage_perc"]["max"] * 100)} %
Metric improved: GPU memory in use (about 30 GiB instead of about 85 GiB)
Metric degraded: time to first token and throughput: requests wait for KV space
Quality impact: none
Memory impact: the pool holds 29,120 tokens, about three 8,192-token requests
Operational impact: the pool must be sized for context times concurrency
Recommendation: size the KV pool for the concurrency you promise, or cap the context per request
```

**D. Concurrency and batching** (`concurrency/`: `baseline-c016` against `max-seqs-8-c016`)

```text
Hypothesis: capping the batch limits throughput and creates queueing
Change (one variable): profile max-seqs-8 (--max-num-seqs 8)
Before: concurrency 16: aggregate {n(db["aggregate_tps"])} tokens/s, TTFT p50 {n(db["ttft_ms"]["p50"])} ms, {n(db["output_tps_per_request"]["p50"], 1)} tokens/s per request
After:  aggregate {n(dc["aggregate_tps"])} tokens/s, TTFT p50 {n(dc["ttft_ms"]["p50"])} ms, {n(dc["output_tps_per_request"]["p50"], 1)} tokens/s per request, {n(dc["server"]["gauges"]["num_requests_waiting"]["max"])} waiting
Metric improved: nothing measured here (a cap protects a shared server from overload)
Metric degraded: throughput and time to first token; the speed of each running request is unchanged
Quality impact: none
Memory impact: none
Operational impact: overload becomes queueing; alert on waiting requests
Recommendation: set the cap from the SLO, not from the throughput curve
```
"""


def section_optimized() -> str:
    return """_The configuration you would run now, as a vLLM profile or flag list, with the evidence for every non-default setting._

Reference example (replace with your own):

```yaml
extends: baseline
description: "FP8 weights for the example SLO at 20 concurrent users"
# evidence: benchmark/results/reference/quantization/ (speed, memory), quality-comparison.json (spot check)
```
"""


# ------------------------------------------------------------------------------------------ assembly
def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(preamble, [(heading, body)]) for the `## ` sections of the template."""
    parts = re.split(r"(?m)^## ", text)
    pre, rest = parts[0], parts[1:]
    out = []
    for part in rest:
        head, _, body = part.partition("\n")
        out.append((head.strip(), body))
    return pre, out


def assemble(filled: dict[str, str]) -> str:
    pre, sections = split_sections(TEMPLATE.read_text())
    pieces = [pre.rstrip("\n") + "\n\n" + BANNER]
    for head, body in sections:
        new = filled.get(head)
        pieces.append(
            f"## {head}\n\n{new.strip()}\n" if new else f"## {head}\n{body.rstrip(chr(10))}\n"
        )
    return "\n".join(pieces) + ""


def build() -> dict[str, dict[str, str]]:
    """state directory name -> {relative file: content}"""
    selected = {"Selected Model": section_selected_model()}
    hardware = {**selected, "Hardware": section_hardware()}
    baseline = {**hardware, "Baseline": section_baseline()}
    full = {
        **baseline,
        "Experiments": section_experiments(),
        "Optimized Configuration": section_optimized(),
    }
    states = {
        "02-first-server": ("lab-02", "Lab 2: a first inference server", selected, ["baseline"], ["Selected Model filled in (reference answer for the workshop workload)"]),
        "03-benchmark": ("lab-03", "Lab 3: benchmark the baseline", hardware, ["baseline", "concurrency", "startup"], ["Hardware filled in from the reference server log"]),
        "04-optimization": ("lab-04", "Lab 4: optimize the deployment", baseline, ["baseline", "concurrency", "quantization", "prefix-cache", "context-length", "startup"], ["Baseline filled in from the reference sweep"]),
        "05-production": ("lab-05", "Lab 5: production architecture", full, ["baseline", "concurrency", "quantization", "prefix-cache", "context-length", "startup", "demos"], ["Experiments and an optimized configuration filled in from the reference results"]),
    }  # fmt: skip
    out: dict[str, dict[str, str]] = {}
    for name, (lab, title, filled, refs, notes) in states.items():
        state = {
            "id": name,
            "lab": lab,
            "title": title,
            "server": {"profile": "baseline"},
            "files": ["workshop-artifacts/inference-report.md"],
            "references": [f"benchmark/results/reference/{r}" for r in refs],
            "note": "Generated by scripts/build_workshop_states.py from the reference results. "
            + "; ".join(notes)
            + ". Your own work is kept unless you use --hard (your version is saved first).\n",
        }
        if name == "05-production":
            state["restore"] = ["workshop-artifacts/production-architecture.md"]
        out[name] = {
            "state.yaml": yaml.safe_dump(state, sort_keys=False, width=100, allow_unicode=True),
            "files/workshop-artifacts/inference-report.md": assemble(filled),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for name, files in build().items():
        for rel, content in files.items():
            path = STATES / name / rel
            if a.check:
                if not path.exists() or path.read_text() != content:
                    stale.append(str(path.relative_to(ROOT)))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    if a.check:
        if stale:
            print(
                "stale workshop states (run python3 scripts/build_workshop_states.py):\n  "
                + "\n  ".join(stale)
            )
            return 1
        print("workshop states are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
