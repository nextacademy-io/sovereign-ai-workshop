#!/usr/bin/env python3
"""GPU memory sizing, with the arithmetic shown.

    WEIGHTS + KV CACHE + RUNTIME OVERHEAD = VRAM REQUIREMENT

    python3 scripts/sizing.py --model primary --precision bf16 --context 8192 --concurrency 16
    python3 scripts/sizing.py --model primary --precision fp8 --kv-dtype fp8 --context 32768 --concurrency 8
    python3 scripts/sizing.py --params-b 70 --layers 80 --kv-heads 8 --head-dim 128 \\
        --precision int4 --context 8192 --concurrency 4 --gpu-gib 48

Weights use parameters x bytes per parameter. The KV cache stores one key and one value vector
per layer, per KV head, per token: 2 x layers x kv_heads x head_dim x bytes per element.
The overhead term (activations, CUDA graphs, framework workspaces) is an ASSUMPTION you can
change; the first thing to do with the real server is to compare this estimate with its startup
log (`GPU KV cache size: N tokens`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BYTES_PER_PARAM = {
    "fp32": 4.0,
    "bf16": 2.0,
    "fp16": 2.0,
    "fp8": 1.0,
    "int8": 1.0,
    "int4": 0.5,
    "fp4": 0.5,
}
KV_BYTES = {"bf16": 2.0, "fp16": 2.0, "fp8": 1.0}
GIB = 2**30
GB = 10**9
DEFAULT_OVERHEAD_GIB = 4.0  # assumption, see module docstring
MODELS_YAML = Path(__file__).resolve().parents[1] / "config" / "models.yaml"


def kv_bytes_per_token(layers: int, kv_heads: int, head_dim: int, kv_dtype: str = "bf16") -> int:
    """Bytes of KV cache one token occupies (K and V, every layer)."""
    return int(2 * layers * kv_heads * head_dim * KV_BYTES[kv_dtype])


def weights_bytes(params_b: float, precision: str) -> float:
    return params_b * 1e9 * BYTES_PER_PARAM[precision]


def estimate(
    *,
    params_b: float,
    layers: int,
    kv_heads: int,
    head_dim: int,
    precision: str,
    kv_dtype: str,
    context: int,
    concurrency: int,
    overhead_gib: float,
    gpu_gib: float | None,
    utilization: float,
) -> dict:
    per_token = kv_bytes_per_token(layers, kv_heads, head_dim, kv_dtype)
    w = weights_bytes(params_b, precision)
    kv_tokens = context * concurrency
    kv = per_token * kv_tokens
    total = w + kv + overhead_gib * GIB
    out = {
        "weights_gib": w / GIB,
        "kv_bytes_per_token": per_token,
        "kv_tokens": kv_tokens,
        "kv_gib": kv / GIB,
        "overhead_gib": overhead_gib,
        "total_gib": total / GIB,
    }
    if gpu_gib:
        budget = gpu_gib * utilization * GIB
        free_for_kv = budget - w - overhead_gib * GIB
        out["gpu_gib"] = gpu_gib
        out["budget_gib"] = budget / GIB
        out["fits"] = total <= budget
        out["kv_capacity_tokens"] = max(0, int(free_for_kv // per_token))
        out["max_concurrency_at_context"] = out["kv_capacity_tokens"] / context
    return out


def load_architecture(role: str) -> tuple[dict, dict]:
    try:
        import yaml
    except ImportError:
        sys.exit(
            "PyYAML is needed for --model; install it or pass --params-b/--layers/--kv-heads/--head-dim"
        )
    models = yaml.safe_load(MODELS_YAML.read_text())["models"]
    if role not in models:
        sys.exit(f"unknown model role '{role}'. Known: {', '.join(models)}")
    return models[role], models[role]["architecture"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", help="role from config/models.yaml (primary, quantized, small, ...)")
    ap.add_argument(
        "--params-b",
        type=float,
        help="parameters in billions (all stored parameters, also for MoE)",
    )
    ap.add_argument("--layers", type=int)
    ap.add_argument("--kv-heads", type=int)
    ap.add_argument("--head-dim", type=int)
    ap.add_argument("--precision", choices=sorted(BYTES_PER_PARAM), default="bf16")
    ap.add_argument("--kv-dtype", choices=sorted(KV_BYTES), default="bf16")
    ap.add_argument(
        "--context", type=int, default=8192, help="tokens per request (prompt + output)"
    )
    ap.add_argument(
        "--concurrency", type=int, default=8, help="requests in flight at the same time"
    )
    ap.add_argument("--overhead-gib", type=float, default=DEFAULT_OVERHEAD_GIB)
    ap.add_argument(
        "--gpu-gib", type=float, default=96.0, help="GPU memory (96 for the workshop GPU)"
    )
    ap.add_argument("--utilization", type=float, default=0.80, help="vLLM --gpu-memory-utilization")
    a = ap.parse_args()

    meta: dict = {}
    if a.model:
        meta, arch = load_architecture(a.model)
        params_b, layers, kv_heads, head_dim = (
            arch["parameters_b"],
            arch["layers"],
            arch["kv_heads"],
            arch["head_dim"],
        )
    else:
        params_b, layers, kv_heads, head_dim = a.params_b, a.layers, a.kv_heads, a.head_dim
        if None in (params_b, layers, kv_heads, head_dim):
            ap.error("give --model, or all of --params-b --layers --kv-heads --head-dim")

    r = estimate(
        params_b=params_b,
        layers=layers,
        kv_heads=kv_heads,
        head_dim=head_dim,
        precision=a.precision,
        kv_dtype=a.kv_dtype,
        context=a.context,
        concurrency=a.concurrency,
        overhead_gib=a.overhead_gib,
        gpu_gib=a.gpu_gib,
        utilization=a.utilization,
    )
    print(
        f"model: {meta.get('repo', 'custom')}   weights: {a.precision}   KV cache: {a.kv_dtype}\n"
    )
    print(
        f"WEIGHTS   {params_b:g} B params x {BYTES_PER_PARAM[a.precision]:g} bytes = {r['weights_gib']:7.2f} GiB"
    )
    disk_gib = meta.get("weights_gb", 0) * GB / GIB
    if (
        disk_gib
        and meta.get("precision") == a.precision
        and abs(disk_gib - r["weights_gib"]) / r["weights_gib"] > 0.05
    ):
        print(
            f"          note: the checkpoint on disk is {disk_gib:.2f} GiB, not {r['weights_gib']:.2f}: "
            "some tensors (embeddings, the output head) stay in higher precision"
        )
    print(
        f"KV CACHE  2 x {layers} layers x {kv_heads} kv heads x {head_dim} head_dim x {KV_BYTES[a.kv_dtype]:g} bytes"
        f" = {r['kv_bytes_per_token']:,} bytes/token"
    )
    print(
        f"          x {a.context:,} tokens x {a.concurrency} requests = {r['kv_tokens']:,} tokens"
        f" = {r['kv_gib']:7.2f} GiB"
    )
    print(f"OVERHEAD  assumed                                       = {r['overhead_gib']:7.2f} GiB")
    print(f"TOTAL                                                   = {r['total_gib']:7.2f} GiB\n")
    if "fits" in r:
        print(
            f"GPU: {r['gpu_gib']:g} GiB x {a.utilization:g} utilization = {r['budget_gib']:.1f} GiB budget  ->  "
            f"{'FITS' if r['fits'] else 'DOES NOT FIT'}"
        )
        print(
            f"The KV cache can hold about {r['kv_capacity_tokens']:,} tokens, i.e. "
            f"{r['max_concurrency_at_context']:.1f} requests of {a.context:,} tokens at the same time."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
