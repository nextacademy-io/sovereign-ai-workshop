import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("runner", Path(__file__).with_name("runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def result(tps: float, rps: float, ttft: float):
    return {
        "configuration": {"model": "m", "server_profile": "baseline"},
        "requests": 24,
        "requests_failed": 0,
        "aggregate_tps": tps,
        "request_throughput_rps": rps,
        "ttft_ms": {"p50": ttft},
        "itl_ms": {"p50": 12.0},
        "output_tps_per_request": {"p50": 80.0},
    }


def test_two_replicas_add_throughput_and_keep_latencies_apart():
    combined = runner.combine_replica_results(
        [result(500.0, 2.5, 100.0), result(520.0, 2.6, 110.0)], 16
    )
    assert combined["aggregate_tps"] == 1020.0
    assert combined["request_throughput_rps"] == 5.1
    assert combined["requests"] == 48 and combined["concurrency"] == 16
    assert combined["per_replica_ttft_ms_p50"] == [100.0, 110.0]
    assert "ttft_ms" not in combined  # percentiles cannot be pooled from summaries
    assert combined["configuration"]["server_profile"].startswith("baseline x2")
