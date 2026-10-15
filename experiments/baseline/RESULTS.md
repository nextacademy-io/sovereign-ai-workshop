# Results: baseline

What was measured, on what, and what it says. The raw files are in [`benchmark/results/reference/baseline/`](../../benchmark/results/reference/baseline/) and [`benchmark/results/reference/startup/`](../../benchmark/results/reference/startup/); each carries hardware, model revision, engine version, server arguments and date. Hypotheses are in [`README.md`](README.md).

## Setup

| | |
| --- | --- |
| GPU | 1× NVIDIA RTX PRO 6000 Blackwell Server Edition, driver 595.91.07, 94.97 GiB usable |
| Model | `Qwen/Qwen3-8B` at revision `b968826d9c46`, BF16 |
| Engine | vLLM 0.31.0 (image digest in `infra/versions.env`), CUDA 13.0 runtime, profile `baseline` (`--gpu-memory-utilization 0.80`, `--max-model-len 32768`) |
| Workload | 1,200 input tokens, 180 output tokens, one request at a time, 24 requests |
| Run | one session on a single pod; one start per measurement, no repetitions |

## 1. Does the arithmetic predict the server?

| | Value |
| --- | --- |
| KV cache bytes per token (2 × 36 layers × 8 KV heads × 128 × 2 B) | 147,456 |
| Available KV memory reported by vLLM | 58.14 GiB |
| Predicted KV capacity | 423,363 tokens |
| KV capacity reported by vLLM | 423,328 tokens |
| Reported ÷ predicted | 0.9999 |
| Maximum concurrency reported for 32,768-token requests | 12.92× |

**Yes, to within 0.01 %.** The check feeds the server's own *available KV memory* into the formula, so it validates the per-token arithmetic, not the budget. The budget is the part you have to estimate yourself, and vLLM's own accounting of it is in `memory-accounting.json` (verbatim log lines in `startup-log-excerpt.txt`):

| Part of the 94.97 GiB | GiB |
| --- | --- |
| Budget requested (`0.80 × 94.97`) | 75.98 |
| Weights plus memory outside PyTorch's allocator | 16.14 (weights alone: 15.27) |
| Peak activations during profiling | 1.70 |
| CUDA graphs | 0.21 |
| KV cache | 58.14 |
| Not claimed (about 20 %) | about 18.8 |

Capacity varies between starts of the same profile: the first start reported 423,328 tokens, later restarts 426,992 (a difference of about 1 %), because the profiled activation memory differs slightly. Treat the KV capacity as a number to read from the log, not a constant.

## 2. What one request costs

| Metric | Value |
| --- | --- |
| Time to first token, p50 / p95 | 70 ms / 71 ms |
| Inter-token latency, p50 / p95 | 11.6 ms / 11.8 ms |
| Tokens per second seen by the request | 86.2 |
| End-to-end latency, p50 | 2,147 ms |
| GPU power while generating | about 362 W |
| GPU utilization reported by `nvidia-smi` | 99 % (with one request) |

**Decode is close to the memory-bandwidth bound.** Every decode step reads all weights once: 16.38 GB at the datasheet bandwidth of 1,597 GB/s is 10.3 ms. The measured 11.6 ms is 1.13× that bound, so one request uses about 88 % of the memory bandwidth for its weight reads. Prefill of 1,200 tokens in 70 ms is about 17,000 tokens per second including scheduling and network overhead; this phase is compute-bound.

The `nvidia-smi` utilization of 99 % with a single request is not a sign of a busy GPU; it says a kernel was running almost all the time (see [`docs/METRICS.md`](../../docs/METRICS.md)).

## 3. Start-up

| Start | Seconds to ready | How it was measured |
| --- | --- | --- |
| First vLLM start in a freshly rebuilt container (no compile caches) | 176 in the log; about 198 by `wsctl` (188 to 198 were seen) | server log timestamps; `wsctl` wall time |
| Start with warm compile and kernel caches | 67.4 by `wsctl`, 55 in the log | `wsctl` wall time; log timestamps |
| Restart of the same profile (`wsctl restart`) | 39.3 by `wsctl`, 29 in the log | as above |

Where the time goes in the cold start (from the log): weights loaded after 25 s (the files were already on local disk), KV capacity sized after 83 s (compilation and profiling), CUDA graph capture 57 s, ready after 176 s. With warm caches, graph capture drops from 57 s to 6 s. A cold start is the number to plan for when a replica is added; a restart is what a lab group sees when it changes a profile.

## What surprised

- The per-token KV formula matched almost exactly, but the **budget** around it (16.14 GiB for weights and non-PyTorch memory, not 15.27) is not obvious from the model card. About 0.9 GiB is the CUDA context and similar allocations.
- The second vLLM instance (the embedding server) held about 7.8 GiB of the same GPU when the baseline server started, which the engine reports as lower free memory at start.
- The single-stream decode speed is a function of weights and bandwidth, so it is the number that quantization moves (see [`../quantization/RESULTS.md`](../quantization/RESULTS.md)).

## Caveats

- GPU memory used as `nvidia-smi` shows it (about 83 to 85 GiB in the result files) is the main server's 75.3 GiB plus the embedding server's 7.8 GiB, which ran on the same GPU. The server's own budget is the 75.98 GiB above.
- One session, one pod, no repetitions: restart variation is shown by the two KV capacities above, run-to-run variation of latency is under about 1 % in the repeated single-stream and concurrency-1 runs (`baseline/single-stream` and `concurrency/baseline-c001`).
- In this session every prompt began with the same instruction line, so vLLM's prefix cache reported a hit rate of 1.3 % (one 16-token block of 1,200). The effect on the time to first token is at most about 1 %. The harness has since been changed (a random line comes first), and the later runs report a hit rate of 0 %.
- The bandwidth bound uses the datasheet value; the achievable bandwidth of the memory system is lower, which would make the measured step closer to the true limit than 88 %.

## Production consequence

Capacity planning starts from arithmetic you can check against a log line: weights, KV bytes per token, a budget. Single-user decode speed is set by weight bytes divided by bandwidth, so halving the weight bytes is the first lever for latency; the cold start of minutes, not seconds, is the first constraint on how quickly you can scale out.
