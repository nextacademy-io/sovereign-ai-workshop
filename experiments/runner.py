#!/usr/bin/env python3
"""Run the workshop experiments on a GPU pod and write results with full provenance.

Runs ON THE POD as root (it restarts the shared vLLM server between configurations), normally through
`experiments/run-session.sh`, which copies the results back to the trainer's laptop.

    python3 experiments/runner.py list
    python3 experiments/runner.py run baseline concurrency --out /var/lib/workshop/results/s2

Every experiment follows the workshop's method: one question, one variable changed, measurements with
hardware / model revision / engine version / server arguments / date attached (infbench does that),
then a RESULTS.md written by a human from these numbers. Nothing here interprets the results.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "benchmark"))

from infbench.cli import main as bench_main  # noqa: E402

BASE = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1").removesuffix("/v1")
KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or ""
MODEL = os.environ.get("WORKSHOP_MODEL", "Qwen/Qwen3-8B")
STATE = Path("/var/lib/workshop")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------------------- server control
def wsctl(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["wsctl", *args], capture_output=True, text=True, check=check)


def start_profile(profile: str, *sets: str, fresh: bool = False) -> dict:
    """Make `profile` the running configuration and return the server's provenance file.

    A server that already runs exactly this profile is reused (a restart costs about 70 s of GPU time),
    unless `fresh` is set: experiments that need an empty prefix cache or a measured startup ask for it.
    A failed start raises RuntimeError with the output of wsctl; wsctl rolls back to the previous profile.
    """
    active = STATE / "active-profile"
    info_path = STATE / "server.json"
    if (
        not fresh
        and not sets
        and active.exists()
        and info_path.exists()
        and active.read_text().strip() == profile
    ):
        info = json.loads(info_path.read_text())
        if not info.get("overrides"):
            try:
                if urllib.request.urlopen(f"{BASE}/health", timeout=5).status == 200:
                    log(f"profile '{profile}' is already running; reusing it")
                    return info
            except OSError:
                pass
    argv = ["start", profile] + [x for s in sets for x in ("--set", s)]
    t0 = time.time()
    log(f"starting profile '{profile}' {' '.join(sets)}")
    r = wsctl(*argv, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"wsctl start {profile} failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    info = json.loads(info_path.read_text())
    log(
        f"  ready in {time.time() - t0:.0f}s; KV cache {info['startup_log'].get('kv_cache_tokens')} tokens"
    )
    return info


def metrics() -> dict[str, float]:
    req = urllib.request.Request(f"{BASE}/metrics")
    text = urllib.request.urlopen(req, timeout=10).read().decode()
    out: dict[str, float] = {}
    for line in text.splitlines():
        m = re.match(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+([-+0-9.eE]+)$", line)
        if m and not m.group(1).endswith("_bucket"):
            out[m.group(1)] = out.get(m.group(1), 0.0) + float(m.group(3))
    return out


# --------------------------------------------------------------------------------------- benchmarking
def bench(
    out: Path, label: str, *, concurrency: list[int] | int, requests: int | None = None, **opts
) -> list[dict]:
    """One infbench invocation (a sweep when concurrency is a list). Returns the per-level result dicts."""
    levels = concurrency if isinstance(concurrency, list) else [concurrency]
    argv = [
        "--endpoint", BASE, "--model", MODEL, "--concurrency", ",".join(map(str, levels)),
        "--out", str(out / label), "--label", label, "--quiet",
    ]  # fmt: skip
    if requests:
        argv += ["--requests", str(requests)]
    for key, value in opts.items():
        flag = "--" + key.replace("_", "-")
        if value is True:
            argv.append(flag)
        elif value not in (False, None):
            argv += [flag, str(value)]
    log(f"benchmark {label}: concurrency {levels} {opts}")
    code = bench_main(argv)
    if code != 0:
        raise RuntimeError(f"benchmark {label} reported failed requests")
    return [json.loads(p.read_text()) for p in sorted((out / label).glob("c*.json"))]


def summary_line(r: dict) -> str:
    t = r["ttft_ms"]["p50"]
    return (
        f"c={r['concurrency']:<3} ttft_p50={t:>7.1f}ms itl_p50={r['itl_ms']['p50']:>5.1f}ms "
        f"out_tps/req={r['output_tps']:>6.1f} aggregate={r['aggregate_tps']:>7.1f} tok/s"
    )


# --------------------------------------------------------------------------------------- experiments
WORKLOAD = {"input_tokens": 1200, "output_tokens": 180}  # the SLO example of the course material


def exp_baseline(out: Path) -> dict:
    """Does the KV-cache arithmetic predict the server? What does one request cost?"""
    sizing = _load("sizing", ROOT / "scripts" / "sizing.py")
    info = start_profile("baseline", fresh=True)
    kv_gib = info["startup_log"]["kv_cache_memory_gib"]
    bytes_per_token = sizing.kv_bytes_per_token(36, 8, 128, "bf16")
    predicted = kv_gib * 2**30 / bytes_per_token
    reported = info["startup_log"]["kv_cache_tokens"]
    check = {
        "kv_bytes_per_token": bytes_per_token, "available_kv_gib": kv_gib,
        "predicted_tokens": round(predicted), "reported_tokens": reported,
        "ratio": reported / predicted, "model_memory_gib": info["startup_log"]["model_memory_gib"],
        "weights_on_disk_gib": 16.38e9 / 2**30,
    }  # fmt: skip
    (out / "baseline").mkdir(parents=True, exist_ok=True)
    (out / "baseline" / "kv-formula-check.json").write_text(json.dumps(check, indent=2) + "\n")
    log(
        f"KV formula: predicted {predicted:,.0f} vs reported {reported:,} tokens (ratio {check['ratio']:.4f})"
    )
    results = bench(out, "baseline/single-stream", concurrency=1, requests=24, **WORKLOAD)
    log("  " + summary_line(results[0]))
    cold = info["startup_seconds"]
    wsctl("restart")
    warm = json.loads((STATE / "server.json").read_text())["startup_seconds"]
    (out / "baseline" / "startup.json").write_text(
        json.dumps({"first_start_s": cold, "restart_s": warm}, indent=2) + "\n"
    )
    return {"kv_check": check, "startup_s": {"first": cold, "restart": warm}}


def exp_concurrency(out: Path) -> dict:
    """Where does aggregate throughput stop scaling? What does a capped batch do to queueing?"""
    start_profile("baseline")
    levels = [1, 2, 4, 8, 16, 32, 64]
    for c in levels:  # one invocation per level so the request count can grow with the level
        for r in bench(
            out,
            f"concurrency/baseline-c{c:03d}",
            concurrency=c,
            requests=max(48, 6 * c),
            **WORKLOAD,
        ):
            log("  " + summary_line(r))
    start_profile("max-seqs-8")
    for c in [4, 8, 16, 32]:
        for r in bench(
            out,
            f"concurrency/max-seqs-8-c{c:03d}",
            concurrency=c,
            requests=max(48, 6 * c),
            **WORKLOAD,
        ):
            log("  " + summary_line(r))
    return {"levels": levels}


def exp_context_length(out: Path) -> dict:
    """How do prompt length and KV capacity change TTFT, ITL and concurrency?"""
    start_profile("baseline")
    for n in [256, 1024, 4096, 8192, 16384, 28672]:
        for r in bench(
            out,
            f"context-length/baseline-in{n:05d}",
            concurrency=1,
            requests=8,
            input_tokens=n,
            output_tokens=128,
        ):
            log(f"  in={n:<6}" + summary_line(r))
    for n in [4096, 16384]:
        for r in bench(
            out,
            f"context-length/baseline-c4-in{n:05d}",
            concurrency=4,
            requests=16,
            input_tokens=n,
            output_tokens=128,
        ):
            log(f"  in={n:<6}" + summary_line(r))
    # The same load as the KV-limited runs below, on the full KV cache: the control for them.
    for c in [2, 4, 8, 16]:
        for r in bench(
            out,
            f"context-length/baseline-c{c:03d}-in08192",
            concurrency=c,
            requests=max(16, 3 * c),
            input_tokens=8192,
            output_tokens=128,
        ):
            log("  in=8192  " + summary_line(r))
    start_profile("kv-constrained")
    for c in [1, 2, 4, 8, 16]:
        before = metrics()
        for r in bench(
            out,
            f"context-length/kv-constrained-c{c:03d}-in08192",
            concurrency=c,
            requests=max(16, 3 * c),
            input_tokens=8192,
            output_tokens=128,
        ):
            after = metrics()
            preempt = after.get("vllm:num_preemptions_total", 0) - before.get(
                "vllm:num_preemptions_total", 0
            )
            log(f"  KV-limited c={c}: " + summary_line(r) + f" preemptions={preempt:.0f}")
            (
                out / f"context-length/kv-constrained-c{c:03d}-in08192" / "preemptions.json"
            ).write_text(json.dumps({"preemptions": preempt}))
    # The same 4 GiB with an FP8 KV cache: twice the tokens fit in the same bytes.
    start_profile("kv-constrained-fp8kv")
    for c in [4, 8]:
        before = metrics()
        for r in bench(
            out,
            f"context-length/kv-constrained-fp8kv-c{c:03d}-in08192",
            concurrency=c,
            requests=max(16, 3 * c),
            input_tokens=8192,
            output_tokens=128,
        ):
            after = metrics()
            preempt = after.get("vllm:num_preemptions_total", 0) - before.get(
                "vllm:num_preemptions_total", 0
            )
            log(f"  KV-limited, FP8 KV c={c}: " + summary_line(r) + f" preemptions={preempt:.0f}")
            (
                out / f"context-length/kv-constrained-fp8kv-c{c:03d}-in08192" / "preemptions.json"
            ).write_text(json.dumps({"preemptions": preempt}))
    start_profile("baseline")
    return {}


def exp_quantization(out: Path) -> dict:
    """What does FP8 change in memory, speed and quality?"""
    probe = _load("quality_probe", HERE / "quality_probe.py")
    runs: dict[str, dict] = {}
    (out / "quantization").mkdir(parents=True, exist_ok=True)
    for profile in ["baseline", "fp8", "kv-fp8"]:
        try:
            info = start_profile(profile)
        except RuntimeError as exc:
            # A profile that cannot start on this GPU is a result, not a crash.
            runs[profile] = {"failed_to_start": str(exc)[:1500]}
            log(f"  {profile} did not start: {str(exc)[-300:]}")
            continue
        runs[profile] = {"startup": info["startup_log"], "startup_seconds": info["startup_seconds"]}
        for c, reqs in [(1, 24), (16, 96)]:
            for r in bench(
                out, f"quantization/{profile}-c{c:03d}", concurrency=c, requests=reqs, **WORKLOAD
            ):
                log("  " + summary_line(r))
        res = probe.run(profile, 240, f"{BASE}/v1", KEY, MODEL)
        (out / "quantization" / f"quality-{profile}.json").write_text(
            json.dumps(res, indent=2) + "\n"
        )
        log(f"  quality {profile}: accuracy {res['accuracy']:.3f} {res['accuracy_by_kind']}")
    (out / "quantization" / "startup.json").write_text(json.dumps(runs, indent=2) + "\n")
    ref = json.loads((out / "quantization" / "quality-baseline.json").read_text())
    comparisons = {}
    for profile in ["fp8", "kv-fp8"]:
        path = out / "quantization" / f"quality-{profile}.json"
        if path.exists():
            comparisons[profile] = probe.compare(ref, json.loads(path.read_text()))
    (out / "quantization" / "quality-comparison.json").write_text(
        json.dumps(comparisons, indent=2) + "\n"
    )
    start_profile("baseline")
    return {
        "comparisons": comparisons,
        "failed": [k for k, v in runs.items() if "failed_to_start" in v],
    }


def exp_prefix_cache(out: Path) -> dict:
    """How much prefill does a shared prefix save?"""
    stats = {}
    for profile in ["baseline", "no-prefix-cache"]:
        start_profile(profile, fresh=True)  # a fresh server: the prefix cache starts empty
        before = metrics()
        for c, reqs in [(1, 32), (8, 64)]:
            for r in bench(
                out,
                f"prefix-cache/{profile}-shared-c{c:03d}",
                concurrency=c,
                requests=reqs,
                workload="shared-prefix",
            ):
                log("  shared prefix: " + summary_line(r))
        after = metrics()
        stats[profile] = {
            k: after.get(k, 0) - before.get(k, 0)
            for k in (
                "vllm:prefix_cache_queries_total",
                "vllm:prefix_cache_hits_total",
                "vllm:prompt_tokens_total",
                "vllm:prompt_tokens_cached_total",
            )
        }
        if profile == "baseline":  # the control: the same length, but nothing shared
            for r in bench(
                out,
                "prefix-cache/baseline-unique-c008",
                concurrency=8,
                requests=64,
                input_tokens=2200,
                output_tokens=150,
            ):
                log("  unique prompts: " + summary_line(r))
    (out / "prefix-cache").mkdir(parents=True, exist_ok=True)
    (out / "prefix-cache" / "counters.json").write_text(json.dumps(stats, indent=2) + "\n")
    # The pitfall: the same prompts twice (same seed) are answered from the cache the second time. A benchmark
    # that repeats its own prompts measures the cache, not the deployment.
    start_profile("baseline", fresh=True)
    for label, seed in [("first", 4711), ("again", 4711), ("new-seed", 4712)]:
        for r in bench(
            out,
            f"prefix-cache/pitfall-{label}-c008",
            concurrency=8,
            requests=64,
            seed=seed,
            **WORKLOAD,
        ):
            log(f"  same prompts? {label}: " + summary_line(r))
    return stats


def exp_demos(out: Path) -> dict:
    """Trainer demonstrations: the intentional failure, then speculative decoding."""
    demo = out / "demos"
    demo.mkdir(parents=True, exist_ok=True)
    # 1. Configurations that cannot work: read the error, then see the automatic rollback. Two different checks fire,
    #    depending on what is asked for: the KV budget (oom-demo as it is), or the model's own context limit.
    start_profile("baseline")
    for label, sets in [("kv", []), ("model-limit", ["--set", "max-model-len=1048576"])]:
        r = wsctl("start", "oom-demo", *sets, check=False)
        text = r.stdout + "\n" + r.stderr
        errors = [
            ln
            for ln in text.splitlines()
            if "KV cache" in ln
            or "max seq len" in ln
            or "max_model_len" in ln
            or "estimated maximum model length" in ln
            or "rolling back" in ln
        ]
        (demo / f"oom-demo-{label}.txt").write_text(text[-6000:])
        healthy = urllib.request.urlopen(BASE + "/health", timeout=10).status == 200
        log(
            f"oom-demo ({label}) exit={r.returncode}; {len(errors)} relevant lines; healthy afterwards: {healthy}"
        )
    # 2. Speculative decoding with n-gram drafting: helps when output repeats the input.
    passage = " ".join(
        f"Section {i}: invoices above {1000 + 250 * i} euros need a second approval, and approved invoices are paid within {7 + i} days."
        for i in range(1, 17)
    )
    prompts = [
        f"Repeat the following text exactly, without any changes or comments.\n\n{passage} (copy {k})"
        for k in range(8)
    ]
    pf = demo / "copy-prompts.jsonl"
    pf.write_text("\n".join(json.dumps({"prompt": p}) for p in prompts) + "\n")
    for profile in ["baseline", "spec-ngram"]:
        try:
            start_profile(profile)
        except RuntimeError as exc:
            (demo / f"spec-{profile}-FAILED.txt").write_text(str(exc)[:3000])
            log(f"  {profile} did not start: {str(exc)[-300:]}")
            continue
        for c in [1, 16]:
            for r in bench(
                out,
                f"demos/spec-{profile}-c{c:03d}",
                concurrency=c,
                requests=max(16, 2 * c),
                prompts_file=str(pf),
                output_tokens=350,
                no_engine_extensions=True,
            ):
                log(f"  {profile}: " + summary_line(r))
        # The control: open questions whose answers are new text. Drafts taken from the prompt rarely match. (The
        # harness's own synthetic prompts are NOT a control: the model copies them, 146 of 157 four-word
        # sequences of one answer came from the prompt, so they behave almost like the copy task.)
        for c in [1, 16]:
            for r in bench(
                out,
                f"demos/spec-{profile}-open-questions-c{c:03d}",
                concurrency=c,
                requests=max(32, 2 * c),
                prompts_file=str(ROOT / "benchmark" / "workloads" / "open-questions.jsonl"),
                output_tokens=200,
                no_engine_extensions=True,
            ):
                log(f"  {profile}, open questions: " + summary_line(r))
        m = metrics()
        (demo / f"spec-{profile}-metrics.json").write_text(
            json.dumps({k: v for k, v in m.items() if "spec_decode" in k}, indent=2) + "\n"
        )
    start_profile("baseline")
    return {}


# ----------------------------------------------------------------------------- tensor parallelism and replicas
def gpu_count() -> int:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True
    ).stdout
    return len([ln for ln in out.splitlines() if ln.strip()])


def combine_replica_results(results: list[dict], concurrency: int) -> dict:
    """What two servers deliver together under one client load that was split between them.

    Throughputs add. Latency percentiles cannot be pooled from summaries, so they are not combined:
    the per-replica result files keep them.
    """
    first = results[0]
    cfg = dict(first["configuration"])
    cfg["server_profile"] = "baseline x2 (one server per GPU)"
    cfg["note"] = "two servers, each on its own GPU, each driven by its own harness process"
    return {
        "configuration": cfg,
        "concurrency": concurrency,
        "replicas": len(results),
        "requests": sum(r["requests"] for r in results),
        "requests_failed": sum(r["requests_failed"] for r in results),
        "aggregate_tps": round(sum(r["aggregate_tps"] for r in results), 2),
        "request_throughput_rps": round(sum(r["request_throughput_rps"] for r in results), 4),
        "per_replica_ttft_ms_p50": [r["ttft_ms"]["p50"] for r in results],
        "per_replica_itl_ms_p50": [r["itl_ms"]["p50"] for r in results],
        "per_replica_output_tps_p50": [r["output_tps_per_request"]["p50"] for r in results],
    }


@contextlib.contextmanager
def replica_servers(out: Path):
    """Two independent baseline servers, one per GPU (ports 8000 and 8001), started like wsctl does."""
    lib = ROOT / "infra" / "pod"
    procs: list[subprocess.Popen] = []
    infos: list[Path] = []
    try:
        for gpu, profile in enumerate(["baseline", "baseline-replica"]):
            cfg = STATE / f"active-replica{gpu}.yaml"
            summary = subprocess.run(
                [sys.executable, str(lib / "render-profile.py"), profile, "--dir",
                 str(ROOT / "config" / "vllm-profiles"), "--out", str(cfg)],
                capture_output=True, text=True, check=True,
            ).stdout  # fmt: skip
            logfile = Path("/var/log/workshop") / f"vllm-replica{gpu}.log"
            env = {
                **os.environ, "CUDA_VISIBLE_DEVICES": str(gpu), "HOME": "/root",
                "HF_HOME": "/opt/workshop/hf", "HF_HUB_OFFLINE": "1", "VLLM_NO_USAGE_STATS": "1",
                "VLLM_CACHE_ROOT": "/var/cache/workshop/vllm", "VLLM_API_KEY": KEY, "PYTHONUNBUFFERED": "1",
            }  # fmt: skip
            t0 = time.time()
            proc = subprocess.Popen(
                ["vllm", "serve", "--config", str(cfg)],
                stdout=open(logfile, "w"),  # noqa: SIM115 - the server writes to it until it is stopped
                stderr=subprocess.STDOUT, env=env, start_new_session=True,
            )  # fmt: skip
            procs.append(proc)
            port = 8000 + gpu
            log(f"replica {gpu}: vllm serve on GPU {gpu}, port {port} (pid {proc.pid})")
            deadline = time.time() + 600
            while time.time() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(f"replica {gpu} exited early; see {logfile}")
                try:
                    if (
                        urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3).status
                        == 200
                    ):
                        break
                except OSError:
                    time.sleep(3)
            else:
                raise RuntimeError(f"replica {gpu} not healthy after 600 s; see {logfile}")
            info = out / "tensor-parallel" / f"replica{gpu}-server.json"
            subprocess.run(
                [sys.executable, str(lib / "server-info.py"), "--log", str(logfile), "--summary", summary,
                 "--out", str(info), "--started-epoch", str(t0), "--ready-epoch", str(time.time()),
                 "--engine-version", _engine_version(), "--gpu", f"GPU {gpu}"],
                capture_output=True, text=True, check=True,
            )  # fmt: skip
            infos.append(info)
            log(f"  replica {gpu} ready in {time.time() - t0:.0f}s")
        yield infos
    finally:
        for proc in procs:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGTERM)
        for proc in procs:
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)


def _engine_version() -> str:
    return subprocess.run(
        [sys.executable, "-c", "import vllm; print(vllm.__version__)"],
        capture_output=True,
        text=True,
    ).stdout.strip()


NOTE_ONE = "pod with two GPUs; this server uses one of them"
NOTE_TP = "pod with two GPUs; this server uses both (tensor parallel size 2)"
NOTE_REPLICAS = (
    "pod with two GPUs; two servers, one per GPU, each driven by its own harness process"
)


def exp_tensor_parallel(out: Path) -> dict:
    """When do two GPUs help: tensor parallelism across both, or one replica per GPU? Needs two GPUs."""
    if gpu_count() < 2:
        raise RuntimeError("tensor-parallel needs a pod with two GPUs")
    tp = out / "tensor-parallel"
    tp.mkdir(parents=True, exist_ok=True)
    topo = subprocess.run(["nvidia-smi", "topo", "-m"], capture_output=True, text=True)
    (tp / "topology.txt").write_text(topo.stdout)
    wsctl("embed", "stop", check=False)  # the RAG embedding server is not part of this comparison
    levels = [1, 8, 32]

    def reqs(c: int) -> int:
        return max(48, 6 * c)

    start_profile("baseline", fresh=True)
    for c in levels:
        for r in bench(
            out, f"tensor-parallel/single-gpu-c{c:03d}", concurrency=c, requests=reqs(c), **WORKLOAD
        ):
            log("  one GPU: " + summary_line(r))
    start_profile("tp2", fresh=True)
    for c in levels:
        for r in bench(
            out, f"tensor-parallel/tp2-c{c:03d}", concurrency=c, requests=reqs(c), **WORKLOAD
        ):
            log("  TP=2: " + summary_line(r))
    wsctl("stop", check=False)
    time.sleep(10)  # let the GPU memory come back
    combined = {}
    with replica_servers(out) as infos:
        for c in [8, 32]:  # the same total load as above, split between the two servers
            procs = []
            for i, info in enumerate(infos):
                label = f"tensor-parallel/replicas-c{c:03d}/server{i}"
                argv = [
                    sys.executable, "-m", "infbench", "--endpoint", f"http://127.0.0.1:{8000 + i}",
                    "--model", MODEL, "--concurrency", str(c // 2), "--requests", str(reqs(c) // 2),
                    "--out", str(out / label), "--label", label, "--quiet", "--note", NOTE_REPLICAS,
                    "--server-info", str(info),
                    "--input-tokens", str(WORKLOAD["input_tokens"]), "--output-tokens", str(WORKLOAD["output_tokens"]),
                ]  # fmt: skip
                procs.append(
                    subprocess.Popen(
                        argv, cwd=ROOT / "benchmark", env={**os.environ, "OPENAI_API_KEY": KEY}
                    )
                )
            codes = [p.wait() for p in procs]
            if any(codes):
                raise RuntimeError(f"replica benchmark at c={c} failed (exit codes {codes})")
            docs = [
                json.loads(
                    next(
                        (out / f"tensor-parallel/replicas-c{c:03d}/server{i}").glob("c*.json")
                    ).read_text()
                )
                for i in range(2)
            ]
            combined[c] = combine_replica_results(docs, c)
            (tp / f"replicas-c{c:03d}").mkdir(exist_ok=True)
            (tp / f"replicas-c{c:03d}" / "combined.json").write_text(
                json.dumps(combined[c], indent=2) + "\n"
            )
            log(
                f"  two replicas, total concurrency {c}: aggregate {combined[c]['aggregate_tps']} tok/s"
            )
    start_profile("baseline", fresh=True)
    wsctl("embed", "start", check=False)
    return {
        "gpus": gpu_count(),
        "replicas": {str(k): v["aggregate_tps"] for k, v in combined.items()},
    }


EXPERIMENTS = {
    "baseline": exp_baseline,
    "concurrency": exp_concurrency,
    "context-length": exp_context_length,
    "quantization": exp_quantization,
    "prefix-cache": exp_prefix_cache,
    "demos": exp_demos,
    "tensor-parallel": exp_tensor_parallel,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    r = sub.add_parser("run")
    r.add_argument("names", nargs="+", choices=sorted(EXPERIMENTS))
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.cmd == "list":
        for name, fn in EXPERIMENTS.items():
            print(f"{name:16s} {fn.__doc__}")
        return 0
    if not KEY:
        sys.exit(
            "OPENAI_API_KEY is not set: log in again or export it (cat /var/lib/workshop/api-key)"
        )
    a.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    summary = {}
    for name in a.names:
        log(f"===== experiment: {name}")
        try:
            summary[name] = {
                "ok": True,
                "details": EXPERIMENTS[name](a.out),
                "seconds": round(time.time() - t0),
            }
        except Exception as exc:  # noqa: BLE001 - record the failure and continue with the next experiment
            log(f"experiment {name} FAILED: {exc}")
            summary[name] = {"ok": False, "error": str(exc)[:2000]}
        (a.out / "session-summary.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n"
        )
    log(f"done in {(time.time() - t0) / 60:.1f} min; results in {a.out}")
    return 0 if all(v["ok"] for v in summary.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
