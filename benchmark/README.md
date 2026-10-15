# Benchmark harness

`benchmark/run.sh` sends load to any OpenAI-compatible endpoint and writes machine-readable results plus a Markdown
summary. It measures what a user feels (time to first token, inter-token latency, end-to-end latency, tokens per
second per request) and what the operator sees (aggregate tokens per second, requests per second, GPU and server
metrics during the run).

```bash
./benchmark/run.sh --endpoint http://localhost:8000 --model Qwen/Qwen3-8B \
  --concurrency 8 --input-tokens 1000 --output-tokens 200
```

On the workshop machines `./scripts/benchmark.sh` fills in the endpoint, model and key from your environment:

```bash
./scripts/benchmark.sh --concurrency 1,4,8,16 --label baseline
```

Results go to `benchmark/results/mine/<time>-<label>/`: one `cNNN.json` per concurrency level and a `summary.md`.

## What a result contains

```json
{
  "configuration": { "hardware": {}, "model": "", "model_revision": "", "engine": "vllm",
                      "engine_version": "", "cuda_version": "", "server_args": "", "workload": {}, "date": "" },
  "requests": 100, "concurrency": 8,
  "ttft_ms": { "p50": 0, "p90": 0, "p95": 0, "p99": 0 },
  "itl_ms": {}, "tpot_ms": {}, "latency_ms": {},
  "output_tps": 0, "aggregate_tps": 0, "request_throughput_rps": 0,
  "gpu": {}, "server": {}
}
```

Hardware, model revision, engine version, server arguments and date are collected for you. A result without them is
rejected by `pnpm check` in this repository: a number without its provenance is an anecdote.

## Options that matter

| Option | Meaning |
| --- | --- |
| `--concurrency 1,4,8,16` | closed loop: this many requests in flight; a list runs a sweep |
| `--request-rate 5` | open loop: Poisson arrivals, 5 per second, regardless of how the server copes |
| `--requests N` | requests per run (default: 8 per worker, at least 32). Small runs inflate TTFT (the first wave arrives at once) |
| `--workload NAME` | `workshop-baseline` (1200 in / 180 out), `chat-short`, `rag-long-context`, `doc-processing`, `shared-prefix` |
| `--input-tokens`, `--output-tokens` | prompt and output length; prompts are sized exactly with the server's tokenizer |
| `--slo ttft_ms=800,output_tps=25` | also report which share of requests met the targets, and goodput |
| `--seed N` | repeat exactly the same prompts. **Default: random**, see below |
| `--prompts-file F` | use your own prompts (JSONL or one per line) |

## Pitfalls the harness guards against

- **Prefix caching flatters repeated runs.** vLLM caches the KV of prompts it has seen. Sending the same prompts
  twice makes the second run's time to first token look several times better (measured on the workshop GPU: p50
  359 ms, then 50 ms). Each run therefore uses a fresh random seed (stored in the result), and the harness warns if
  the server's cache hit rate during a run shows that earlier prompts were reused. Use `--seed` only on purpose.
- **GPU utilization is not efficiency.** The `gpu` block reports `nvidia-smi` utilization, memory and power. The
  utilization figure is the share of time any kernel ran; read power draw and the server's own numbers next to it.
- **Percentiles from few samples are noisy.** p99 of 48 requests is the slowest request. Run enough requests.
- **Closed-loop load hides overload.** When the server slows down, a closed loop sends less. Use `--request-rate`
  to see what happens when arrivals do not wait.

## Cross-check

Two independent load generators should agree. `benchmark/scripts/crosscheck.sh` runs the same shape through this
harness and through `vllm bench serve` on the GPU host and compares them (`compare_results.py`).

## Tests

`uv run --extra dev pytest benchmark` runs the harness against a fake streaming server with known timing, so the
metric arithmetic is checked without a GPU.
