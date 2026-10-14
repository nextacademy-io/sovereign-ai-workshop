import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "compare_results", Path(__file__).resolve().parents[1] / "scripts" / "compare_results.py"
)
cr = importlib.util.module_from_spec(spec)
sys.modules["compare_results"] = cr
spec.loader.exec_module(cr)

# Structure-only fixtures to exercise the comparison logic; they are not benchmark results.
OURS = {
    "requests": 64,
    "duration_s": 10.0,
    "aggregate_tps": 1000.0,
    "request_throughput_rps": 6.4,
    "ttft_ms": {"mean": 100.0, "p50": 90.0, "p99": 300.0},
    "tpot_ms": {"mean": 20.0},
    "itl_ms": {"mean": 20.0, "p99": 40.0},
    "latency_ms": {"mean": 4000.0, "p99": 5000.0},
}
THEIRS = {
    "completed": 64,
    "duration": 10.2,
    "output_throughput": 980.0,
    "request_throughput": 6.3,
    "mean_ttft_ms": 105.0,
    "median_ttft_ms": 92.0,
    "p99_ttft_ms": 310.0,
    "mean_tpot_ms": 20.5,
    "mean_itl_ms": 20.5,
    "p99_itl_ms": 41.0,
    "mean_e2el_ms": 4100.0,
    "p99_e2el_ms": 5100.0,
}


def test_close_results_are_all_within_tolerance():
    rows = cr.compare(OURS, THEIRS, 10.0)
    assert len(rows) == len(cr.PAIRS) and all(r["flag"] == "ok" for r in rows)


def test_a_real_discrepancy_is_flagged_not_averaged_away():
    bad = dict(THEIRS, output_throughput=500.0)  # we would be reporting twice the throughput
    flagged = [r["metric"] for r in cr.compare(OURS, bad, 10.0) if r["flag"] == "DIFFERS"]
    assert flagged == ["output tokens/s (aggregate)"]


def test_missing_metrics_are_reported_as_missing():
    theirs = {k: v for k, v in THEIRS.items() if k != "p99_e2el_ms"}
    rows = {r["metric"]: r for r in cr.compare(OURS, theirs, 10.0)}
    assert rows["E2E latency p99 (ms)"]["flag"] == "missing"


def test_render_is_a_markdown_table():
    text = cr.render(cr.compare(OURS, THEIRS, 10.0), 10.0)
    assert text.startswith("| Metric |") and "output tokens/s (aggregate)" in text
