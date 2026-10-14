import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("sizing", Path(__file__).with_name("sizing.py"))
sizing = importlib.util.module_from_spec(spec)
sys.modules["sizing"] = sizing
spec.loader.exec_module(sizing)

QWEN3_8B = dict(params_b=8.2, layers=36, kv_heads=8, head_dim=128)


def test_kv_bytes_per_token_for_qwen3_8b():
    assert sizing.kv_bytes_per_token(36, 8, 128, "bf16") == 147_456
    assert sizing.kv_bytes_per_token(36, 8, 128, "fp8") == 73_728  # FP8 KV halves it


def test_kv_grows_linearly_with_context_and_with_concurrency():
    one = sizing.estimate(
        **QWEN3_8B,
        precision="bf16",
        kv_dtype="bf16",
        context=4096,
        concurrency=1,
        overhead_gib=0,
        gpu_gib=None,
        utilization=0.8,
    )
    both = sizing.estimate(
        **QWEN3_8B,
        precision="bf16",
        kv_dtype="bf16",
        context=8192,
        concurrency=4,
        overhead_gib=0,
        gpu_gib=None,
        utilization=0.8,
    )
    assert both["kv_gib"] == pytest.approx(8 * one["kv_gib"])


def test_weights_scale_with_precision():
    bf16 = sizing.weights_bytes(8.2, "bf16")
    assert sizing.weights_bytes(8.2, "fp8") == bf16 / 2
    assert sizing.weights_bytes(8.2, "int4") == bf16 / 4


def test_fits_and_capacity_on_the_workshop_gpu():
    r = sizing.estimate(
        **QWEN3_8B,
        precision="bf16",
        kv_dtype="bf16",
        context=8192,
        concurrency=16,
        overhead_gib=4,
        gpu_gib=96,
        utilization=0.8,
    )
    assert r["fits"] and r["kv_gib"] == pytest.approx(18.0, rel=1e-3)
    # 96 x 0.8 = 76.8 GiB budget, minus 15.3 GiB weights and 4 GiB overhead, divided by 147,456 B/token.
    assert 410_000 < r["kv_capacity_tokens"] < 430_000


def test_a_long_context_batch_does_not_fit_a_small_gpu():
    r = sizing.estimate(
        **QWEN3_8B,
        precision="bf16",
        kv_dtype="bf16",
        context=32768,
        concurrency=16,
        overhead_gib=4,
        gpu_gib=24,
        utilization=0.9,
    )
    assert not r["fits"] and r["max_concurrency_at_context"] < 1
