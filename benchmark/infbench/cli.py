"""Command line interface: ./benchmark/run.sh --endpoint URL --model M --concurrency 8 ..."""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

from . import __version__
from .client import RequestConfig
from .provenance import REPO_ROOT, collect_configuration
from .report import build_result, markdown_summary, parse_slo
from .runner import RunOutcome, run_closed_loop, run_open_loop
from .sampler import GpuSampler, MetricsSampler
from .workload import Tokenizer, Workload, build_prompts, load_workload


def _parse_levels(text: str) -> list[int]:
    try:
        levels = [int(x) for x in text.split(",") if x.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("concurrency must be an integer or a comma list") from exc
    if not levels or any(n < 1 for n in levels):
        raise argparse.ArgumentTypeError("concurrency levels must be >= 1")
    return levels


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="benchmark/run.sh",
        description="Load-test an OpenAI-compatible LLM endpoint and write machine-readable results.",
        epilog="Example: ./benchmark/run.sh --endpoint http://localhost:8000 --model Qwen/Qwen3-8B "
        "--concurrency 1,4,8,16 --input-tokens 1000 --output-tokens 200",
    )
    p.add_argument(
        "--endpoint",
        default=os.environ.get("OPENAI_BASE_URL", "http://localhost:8000"),
        help="server base URL (a trailing /v1 is accepted)",
    )
    p.add_argument(
        "--model",
        default=os.environ.get("WORKSHOP_MODEL"),
        help="served model name; defaults to the only model the server lists",
    )
    p.add_argument(
        "--api-key", default=None, help="bearer token (default: $VLLM_API_KEY or $OPENAI_API_KEY)"
    )
    p.add_argument(
        "--engine",
        default="vllm",
        help="engine label for the report (vllm, ollama, llama.cpp, ...)",
    )
    p.add_argument("--endpoint-type", choices=["completions", "chat"], default="completions")

    g = p.add_argument_group("workload")
    g.add_argument("--workload", help="name in benchmark/workloads/ or a YAML path")
    g.add_argument("--input-tokens", type=int, help="prompt tokens per request (default 1000)")
    g.add_argument("--output-tokens", type=int, help="generated tokens per request (default 200)")
    g.add_argument("--shared-prefix-tokens", type=int, help="tokens identical across all requests")
    g.add_argument(
        "--prompt-mode", choices=["auto", "ids", "text"], help="exact token ids or plain text"
    )
    g.add_argument("--seed", type=int, help="prompt seed (default 1234)")
    g.add_argument("--temperature", type=float, default=0.0)
    g.add_argument(
        "--no-engine-extensions",
        action="store_true",
        help="do not send vLLM-only fields (ignore_eos, min_tokens); needed for other engines",
    )

    g = p.add_argument_group("load")
    g.add_argument(
        "--concurrency",
        type=_parse_levels,
        default=[1],
        help="closed loop: parallel requests; a comma list runs a sweep (1,4,8,16)",
    )
    g.add_argument(
        "--request-rate", type=float, help="open loop: Poisson arrival rate in requests/s"
    )
    g.add_argument("--max-inflight", type=int, help="open loop: cap on simultaneous requests")
    g.add_argument(
        "--requests", type=int, help="requests per run (default max(32, 8 x concurrency))"
    )
    g.add_argument(
        "--duration", type=float, help="closed loop: stop starting requests after N seconds"
    )
    g.add_argument(
        "--warmup", type=int, help="warm-up requests, excluded from results (default min(8, c))"
    )
    g.add_argument("--slo", help="e.g. ttft_ms=800,output_tps=25: reports attainment and goodput")
    g.add_argument(
        "--reset-prefix-cache",
        action="store_true",
        help="POST /reset_prefix_cache before each run (needs VLLM_SERVER_DEV_MODE=1)",
    )
    g.add_argument(
        "--same-prompts",
        action="store_true",
        help="reuse identical prompts in every run of a sweep (prefix cache will make later runs faster)",
    )

    g = p.add_argument_group("output")
    g.add_argument(
        "--out",
        type=Path,
        help="output directory (default benchmark/results/_scratch/<time>-<label>)",
    )
    g.add_argument("--label", help="short label for the run directory")
    g.add_argument("--note", help="free text stored in the result")
    g.add_argument("--quiet", action="store_true")
    g.add_argument("--no-gpu", action="store_true", help="do not sample nvidia-smi")
    g.add_argument("--no-server-metrics", action="store_true", help="do not scrape /metrics")

    g = p.add_argument_group("provenance (override what cannot be detected)")
    g.add_argument(
        "--server-info",
        type=Path,
        help="JSON written by the supervisor (default /workspace/state/server.json)",
    )
    g.add_argument("--model-revision")
    g.add_argument(
        "--server-args",
        help="the engine arguments, if the supervisor file is unavailable; "
        'write --server-args="--max-model-len 8192" (with =) because the value starts with --',
    )
    g.add_argument("--gpu-name")
    g.add_argument("--gpu-count", type=int)
    g.add_argument("--vram-gb", type=float)
    g.add_argument("--runtime-cuda")
    g.add_argument("--engine-version")
    p.add_argument("--version", action="version", version=f"infbench {__version__}")
    return p


def _resolve_model(base_url: str, headers: dict[str, str], requested: str | None) -> str:
    try:
        r = httpx.get(f"{base_url}/v1/models", headers=headers, timeout=10.0)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise SystemExit(f"cannot reach {base_url}/v1/models: {exc}") from exc
    served = [m["id"] for m in r.json().get("data", [])]
    if requested:
        if served and requested not in served:
            raise SystemExit(
                f"model '{requested}' is not served; server lists: {', '.join(served)}"
            )
        return requested
    if len(served) == 1:
        return served[0]
    raise SystemExit(f"--model is required; server lists: {', '.join(served) or '(nothing)'}")


def _workload_from_args(a: argparse.Namespace) -> Workload:
    wl = load_workload(a.workload) if a.workload else Workload()
    updates = {
        k: v
        for k, v in {
            "input_tokens": a.input_tokens,
            "output_tokens": a.output_tokens,
            "shared_prefix_tokens": a.shared_prefix_tokens,
            "prompt_mode": a.prompt_mode,
            "seed": a.seed,
        }.items()
        if v is not None
    }
    if updates and not a.workload:
        updates["name"] = "custom"
    return dataclasses.replace(wl, **updates)


async def _one_run(
    a, base_url, headers, cfg, workload, level, run_idx, tokenizer
) -> tuple[RunOutcome, dict | None, dict | None]:
    seed = workload.seed if a.same_prompts else workload.seed + run_idx * 1_000_003
    wl = dataclasses.replace(workload, seed=seed)
    open_loop = a.request_rate is not None
    n_requests = a.requests or (max(32, 8 * level) if not open_loop else 64)
    warmup = a.warmup if a.warmup is not None else max(2, min(8, level))

    if a.reset_prefix_cache:
        try:
            httpx.post(
                f"{base_url}/reset_prefix_cache", headers=headers, timeout=10.0
            ).raise_for_status()
        except httpx.HTTPError as exc:
            print(f"warning: could not reset the prefix cache: {exc}", file=sys.stderr)

    prompts = build_prompts(wl, n_requests + warmup, tokenizer)
    warm, measured = prompts[:warmup], prompts[warmup:]
    if warm:
        await run_closed_loop(base_url, headers, cfg, warm, min(level, len(warm)), quiet=True)

    gpu = GpuSampler() if (not a.no_gpu and GpuSampler.available()) else None
    metrics = MetricsSampler(base_url, headers) if not a.no_server_metrics else None
    for s in (gpu, metrics):
        if s:
            s.start()
    if open_loop:
        outcome = await run_open_loop(
            base_url,
            headers,
            cfg,
            measured,
            a.request_rate,
            max_inflight=a.max_inflight,
            seed=seed,
            quiet=a.quiet,
        )
    else:
        outcome = await run_closed_loop(
            base_url, headers, cfg, measured, level, duration_s=a.duration, quiet=a.quiet
        )
    gpu_summary = gpu.stop() if gpu else None
    server_summary = metrics.stop() if metrics else None
    return outcome, gpu_summary, server_summary


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    base_url = a.endpoint.rstrip("/").removesuffix("/v1")
    api_key = a.api_key or os.environ.get("VLLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    model = _resolve_model(base_url, headers, a.model)
    workload = _workload_from_args(a)
    tokenizer = Tokenizer(base_url, model, headers)
    if workload.prompt_mode == "ids" and not tokenizer.available():
        raise SystemExit("prompt_mode 'ids' requested but the server has no /tokenize endpoint")
    if not tokenizer.available():
        if workload.prompt_mode == "auto":
            print(
                "note: server has no /tokenize; sending text prompts, sizes are approximate",
                file=sys.stderr,
            )
        tokenizer.close()
        tokenizer = None  # type: ignore[assignment]

    cfg = RequestConfig(
        model=model,
        endpoint_type=a.endpoint_type,
        max_tokens=workload.output_tokens,
        temperature=a.temperature,
        engine_extensions=not a.no_engine_extensions,
    )
    configuration = collect_configuration(
        base_url=base_url,
        headers=headers,
        model=model,
        engine=a.engine,
        server_info_path=a.server_info,
        overrides={
            "model_revision": a.model_revision,
            "server_args": a.server_args,
            "gpu_name": a.gpu_name,
            "gpu_count": a.gpu_count,
            "vram_gb": a.vram_gb,
            "runtime_cuda": a.runtime_cuda,
            "engine_version": a.engine_version,
            "note": a.note,
        },
    )
    configuration["workload"] = workload.to_dict()
    configuration["harness_version"] = __version__
    configuration["endpoint_type"] = a.endpoint_type
    slo = parse_slo(a.slo)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out_dir = a.out or (
        REPO_ROOT / "benchmark" / "results" / "_scratch" / f"{stamp}-{a.label or workload.name}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    levels = [0] if a.request_rate is not None else a.concurrency
    results: list[dict] = []
    for run_idx, level in enumerate(levels):
        label = f"rate {a.request_rate}/s" if a.request_rate is not None else f"concurrency {level}"
        print(
            f"== {label}: {workload.input_tokens} in / {workload.output_tokens} out",
            file=sys.stderr,
        )
        outcome, gpu, server = asyncio.run(
            _one_run(a, base_url, headers, cfg, workload, max(level, 1), run_idx, tokenizer)
        )
        # Each result carries its own copy of the configuration with the concrete load.
        run_cfg = {
            **configuration,
            "load": {
                "mode": outcome.mode,
                "concurrency": outcome.concurrency,
                "request_rate": outcome.request_rate,
            },
        }
        result = build_result(
            configuration=run_cfg, outcome=outcome, gpu=gpu, server=server, slo=slo or None
        )
        results.append(result)
        name = f"rate-{a.request_rate}.json" if a.request_rate is not None else f"c{level:03d}.json"
        (out_dir / name).write_text(json.dumps(result, indent=2) + "\n")
        t = result["ttft_ms"] or {}
        print(
            f"   ok={result['requests']} failed={result['requests_failed']} "
            f"ttft_p50={t.get('p50')}ms aggregate_tps={result['aggregate_tps']} "
            f"output_tps/req={result['output_tps']} -> {out_dir / name}",
            file=sys.stderr,
        )

    summary = markdown_summary(results)
    (out_dir / "summary.md").write_text(summary)
    print(summary)
    missing = [
        k
        for k in ("model_revision", "engine_version", "cuda_version", "server_args")
        if not configuration.get(k)
    ] + (["hardware.gpu"] if not configuration["hardware"].get("gpu") else [])
    if missing:
        print(
            f"warning: provenance incomplete ({', '.join(missing)}); "
            "this result will not pass `pnpm check` if committed. Use the --model-revision, "
            "--server-args, --gpu-name overrides or run on the GPU host.",
            file=sys.stderr,
        )
    return 1 if any(r["requests"] == 0 for r in results) else 0
