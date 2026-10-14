"""End-to-end tests of the harness against a fake server with known timing."""

import asyncio
import json

import httpx
import pytest
from fake_server import FakeLLMServer
from infbench.cli import main
from infbench.client import RequestConfig, send_request
from infbench.report import build_result, markdown_summary, parse_slo
from infbench.runner import run_closed_loop, run_open_loop
from infbench.sampler import MetricsSampler, parse_prometheus
from infbench.workload import Prompt, Tokenizer, Workload, build_prompts

CFG = RequestConfig(model="fake-model", max_tokens=20)


def _prompts(n: int) -> list[Prompt]:
    return [Prompt(index=i, token_ids=[1, 2, 3]) for i in range(n)]


def test_single_request_timing_matches_the_server_configuration():
    with FakeLLMServer(ttft_s=0.10, itl_s=0.02) as srv:

        async def go():
            async with httpx.AsyncClient(base_url=srv.url) as client:
                return await send_request(client, CFG, _prompts(1)[0])

        r = asyncio.run(go())
    assert r.ok and r.completion_tokens == 20 and r.prompt_tokens == 3
    assert 0.09 < r.ttft_s < 0.25
    assert len(r.itl_s) == 19
    assert all(0.015 < x < 0.06 for x in r.itl_s)
    # 19 gaps of ~20 ms -> ~50 tokens per second after the first token.
    assert 35 < r.output_tps < 55
    assert r.latency_s > r.ttft_s


def test_chat_endpoint_is_parsed_too():
    cfg = RequestConfig(model="fake-model", endpoint_type="chat", max_tokens=5)
    with FakeLLMServer(ttft_s=0.01, itl_s=0.005) as srv:

        async def go():
            async with httpx.AsyncClient(base_url=srv.url) as client:
                return await send_request(client, cfg, Prompt(index=0, text="hello"))

        r = asyncio.run(go())
    assert r.ok and r.completion_tokens == 5 and len(r.itl_s) == 4


def test_closed_loop_respects_concurrency_and_counts_all_requests():
    with FakeLLMServer(ttft_s=0.02, itl_s=0.005) as srv:
        out = asyncio.run(
            run_closed_loop(srv.url, {}, CFG, _prompts(24), concurrency=4, quiet=True)
        )
        assert srv.max_inflight == 4
    assert len(out.results) == 24 and all(r.ok for r in out.results)


def test_queueing_shows_up_as_higher_ttft_but_aggregate_tps_saturates():
    """A server that handles 2 requests at a time: concurrency 8 cannot go faster than 2."""
    with FakeLLMServer(ttft_s=0.02, itl_s=0.01, capacity=2) as srv:
        low = asyncio.run(
            run_closed_loop(srv.url, {}, CFG, _prompts(16), concurrency=2, quiet=True)
        )
        high = asyncio.run(
            run_closed_loop(srv.url, {}, CFG, _prompts(16), concurrency=8, quiet=True)
        )
    cfg = {"hardware": {}, "workload": {}}
    r_low = build_result(configuration=cfg, outcome=low, gpu=None, server=None)
    r_high = build_result(configuration=cfg, outcome=high, gpu=None, server=None)
    assert r_high["ttft_ms"]["p50"] > 2 * r_low["ttft_ms"]["p50"]
    assert r_high["aggregate_tps"] < 1.3 * r_low["aggregate_tps"]


def test_aggregate_tps_math():
    with FakeLLMServer(ttft_s=0.05, itl_s=0.01) as srv:
        out = asyncio.run(run_closed_loop(srv.url, {}, CFG, _prompts(8), concurrency=8, quiet=True))
    res = build_result(configuration={}, outcome=out, gpu=None, server=None)
    assert res["requests"] == 8 and res["requests_failed"] == 0
    assert res["tokens"]["completion_total"] == 8 * 20
    assert res["aggregate_tps"] == pytest.approx(160 / res["duration_s"], rel=0.02)
    assert res["request_throughput_rps"] == pytest.approx(8 / res["duration_s"], rel=0.02)
    # Eight parallel streams: the whole server delivers about 8x one stream's rate.
    assert res["aggregate_tps"] > 4 * res["output_tps"]


def test_failures_are_counted_and_reported_not_hidden():
    with FakeLLMServer(ttft_s=0.01, itl_s=0.001, fail_every=4) as srv:
        out = asyncio.run(
            run_closed_loop(srv.url, {}, CFG, _prompts(16), concurrency=2, quiet=True)
        )
    res = build_result(configuration={}, outcome=out, gpu=None, server=None)
    assert res["requests_failed"] == 4 and res["requests"] == 12
    assert "injected failure" in res["errors"][0]["error"]


def test_open_loop_sends_all_requests_with_approximately_the_target_rate():
    with FakeLLMServer(ttft_s=0.005, itl_s=0.001) as srv:
        out = asyncio.run(
            run_open_loop(srv.url, {}, CFG, _prompts(40), request_rate=100.0, quiet=True)
        )
    assert len(out.results) == 40 and all(r.ok for r in out.results)
    # 40 arrivals at 100/s take about 0.4 s (Poisson, so allow generous slack).
    assert 0.2 < out.duration_s < 1.2


def test_slo_attainment_and_goodput():
    with FakeLLMServer(ttft_s=0.05, itl_s=0.01) as srv:
        out = asyncio.run(run_closed_loop(srv.url, {}, CFG, _prompts(8), concurrency=2, quiet=True))
    strict = build_result(
        configuration={},
        outcome=out,
        gpu=None,
        server=None,
        slo=parse_slo("ttft_ms=1,output_tps=25"),
    )
    lenient = build_result(
        configuration={},
        outcome=out,
        gpu=None,
        server=None,
        slo=parse_slo("ttft_ms=5000,output_tps=5"),
    )
    assert strict["slo"]["attainment"] == 0.0
    assert lenient["slo"]["attainment"] == 1.0
    assert lenient["slo"]["goodput_rps"] > 0
    with pytest.raises(ValueError):
        parse_slo("bogus=1")


def test_prompts_are_unique_exact_length_and_deterministic():
    with FakeLLMServer() as srv:
        tok = Tokenizer(srv.url, "fake-model", {})
        assert tok.available()
        wl = Workload(input_tokens=120, output_tokens=10, seed=7)
        a = build_prompts(wl, 5, tok)
        b = build_prompts(wl, 5, tok)
        tok.close()
    assert [p.token_ids for p in a] == [p.token_ids for p in b]
    assert all(len(p.token_ids) == 120 for p in a)
    assert len({tuple(p.token_ids) for p in a}) == 5


def test_shared_prefix_is_identical_and_suffix_differs():
    with FakeLLMServer() as srv:
        tok = Tokenizer(srv.url, "fake-model", {})
        wl = Workload(input_tokens=200, output_tokens=10, shared_prefix_tokens=80, seed=3)
        prompts = build_prompts(wl, 4, tok)
        tok.close()
    heads = {tuple(p.token_ids[:80]) for p in prompts}
    tails = {tuple(p.token_ids[80:]) for p in prompts}
    assert len(heads) == 1 and len(tails) == 4
    assert all(len(p.token_ids) == 200 for p in prompts)


def test_text_mode_without_tokenize_endpoint():
    wl = Workload(input_tokens=100, output_tokens=5)
    prompts = build_prompts(wl, 3, None)
    assert all(p.text and p.token_ids is None for p in prompts)
    assert len({p.text for p in prompts}) == 3


def test_parse_prometheus_sums_labels_and_skips_buckets():
    text = (
        "# HELP x y\n"
        'vllm:num_requests_running{engine="0",model_name="m"} 3\n'
        'vllm:num_requests_running{engine="1",model_name="m"} 2\n'
        'vllm:time_to_first_token_seconds_bucket{le="0.1"} 9\n'
        "vllm:kv_cache_usage_perc 0.5\n"
    )
    parsed = parse_prometheus(text)
    assert parsed["vllm:num_requests_running"] == 5
    assert parsed["vllm:kv_cache_usage_perc"] == 0.5
    assert not any(k.endswith("_bucket") for k in parsed)


def test_metrics_sampler_reports_gauges_and_prefix_cache_hit_rate():
    import time

    with FakeLLMServer() as srv:
        sampler = MetricsSampler(srv.url, {}, interval_s=0.05)
        sampler.start()
        asyncio.run(run_closed_loop(srv.url, {}, CFG, _prompts(8), concurrency=2, quiet=True))
        time.sleep(0.12)
        summary = sampler.stop()
    assert summary and summary["gauges"]["kv_cache_usage_perc"]["max"] == 0.25
    assert summary["prefix_cache_hit_rate"] == pytest.approx(0.25)


def test_cli_end_to_end_writes_schema_compliant_results(tmp_path, capsys):
    with FakeLLMServer(ttft_s=0.01, itl_s=0.002, api_key="secret") as srv:
        code = main(
            [
                "--endpoint",
                srv.url,
                "--model",
                "fake-model",
                "--api-key",
                "secret",
                "--concurrency",
                "1,2",
                "--requests",
                "6",
                "--warmup",
                "1",
                "--input-tokens",
                "64",
                "--output-tokens",
                "10",
                "--no-gpu",
                "--quiet",
                "--out",
                str(tmp_path),
                "--server-args=--fake",
                "--gpu-name",
                "Fake GPU",
                "--gpu-count",
                "1",
                "--vram-gb",
                "1",
                "--model-revision",
                "abc",
                "--runtime-cuda",
                "13.0",
            ]
        )
    assert code == 0
    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["c001.json", "c002.json", "summary.md"]
    doc = json.loads((tmp_path / "c002.json").read_text())
    cfg = doc["configuration"]
    for key in (
        "hardware",
        "model",
        "model_revision",
        "engine",
        "engine_version",
        "cuda_version",
        "server_args",
        "workload",
        "date",
    ):
        assert cfg.get(key), key
    assert cfg["load"] == {"mode": "closed", "concurrency": 2, "request_rate": None}
    assert doc["requests"] == 6 and doc["ttft_ms"]["p95"] >= doc["ttft_ms"]["p50"]
    assert "aggregate_tps" in doc and "output_tps" in doc
    assert "| 2 |" in (tmp_path / "summary.md").read_text()
    # The API key must never be written to results.
    assert "secret" not in (tmp_path / "c002.json").read_text()


def test_cli_sweep_does_not_reuse_prompts_between_levels(tmp_path):
    """Identical prompts in a later run would be served from the prefix cache."""
    with FakeLLMServer(ttft_s=0.001, itl_s=0.001) as srv:
        main(
            [
                "--endpoint",
                srv.url,
                "--model",
                "fake-model",
                "--concurrency",
                "1,1",
                "--requests",
                "3",
                "--warmup",
                "0",
                "--input-tokens",
                "50",
                "--output-tokens",
                "3",
                "--no-gpu",
                "--quiet",
                "--out",
                str(tmp_path),
            ]
        )
        seen = [tuple(p) for p in srv.prompts_seen]
    assert len(seen) == len(set(seen))


def test_markdown_summary_contains_the_lab_columns():
    with FakeLLMServer(ttft_s=0.01, itl_s=0.002) as srv:
        out = asyncio.run(run_closed_loop(srv.url, {}, CFG, _prompts(4), concurrency=2, quiet=True))
    cfg = {
        "hardware": {"gpu": "G", "gpu_count": 1, "vram_gb": 1},
        "model": "m",
        "engine": "e",
        "workload": {"name": "w", "input_tokens": 3, "output_tokens": 20},
        "date": "d",
    }
    md = markdown_summary([build_result(configuration=cfg, outcome=out, gpu=None, server=None)])
    for column in ("TTFT p50", "TTFT p95", "Latency p50", "Latency p95", "Aggregate TPS", "VRAM"):
        assert column in md


def test_default_seed_is_random_per_invocation_so_a_rerun_is_not_served_from_the_prefix_cache(
    tmp_path,
):
    """Regression for a measured pitfall: the same prompts twice made TTFT 7x faster (391 ms, then 51 ms)."""

    def run(out):
        with FakeLLMServer(ttft_s=0.001, itl_s=0.001) as srv:
            main(
                [
                    "--endpoint",
                    srv.url,
                    "--model",
                    "fake-model",
                    "--requests",
                    "3",
                    "--warmup",
                    "0",
                    "--input-tokens",
                    "40",
                    "--output-tokens",
                    "2",
                    "--no-gpu",
                    "--quiet",
                    "--out",
                    str(out),
                ]
            )
            return [tuple(p) for p in srv.prompts_seen]

    first, second = run(tmp_path / "a"), run(tmp_path / "b")
    assert set(first).isdisjoint(second)
    seeds = {
        json.loads((d / "c001.json").read_text())["configuration"]["workload"]["seed"]
        for d in (tmp_path / "a", tmp_path / "b")
    }
    assert len(seeds) == 2 and None not in seeds


def test_explicit_seed_repeats_the_prompts(tmp_path):
    def run(out):
        with FakeLLMServer(ttft_s=0.001, itl_s=0.001) as srv:
            main(
                [
                    "--endpoint",
                    srv.url,
                    "--model",
                    "fake-model",
                    "--requests",
                    "3",
                    "--warmup",
                    "0",
                    "--seed",
                    "9",
                    "--input-tokens",
                    "40",
                    "--output-tokens",
                    "2",
                    "--no-gpu",
                    "--quiet",
                    "--out",
                    str(out),
                ]
            )
            return [tuple(p) for p in srv.prompts_seen]

    assert run(tmp_path / "a") == run(tmp_path / "b")


def test_cache_flattery_is_warned_about(tmp_path, capsys):
    # The fake server reports a 25 % prefix cache hit rate and the workload shares no prefix.
    with FakeLLMServer(ttft_s=0.001, itl_s=0.001) as srv:
        main(
            [
                "--endpoint",
                srv.url,
                "--model",
                "fake-model",
                "--requests",
                "4",
                "--warmup",
                "0",
                "--input-tokens",
                "40",
                "--output-tokens",
                "2",
                "--no-gpu",
                "--quiet",
                "--out",
                str(tmp_path),
            ]
        )
    assert "prefix cache answered" in capsys.readouterr().err
