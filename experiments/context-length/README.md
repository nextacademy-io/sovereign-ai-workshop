# Experiment: context-length

## Question

How do prompt length and a limited KV cache change time to first token, inter-token latency and the number of requests the server can hold?

## Hypothesis (a prediction to test, not a result)

Time to first token grows with prompt length (prefill does more work). Inter-token latency grows slowly with context (each step reads more KV). With a KV cache too small for the load, requests queue or are preempted and recomputed: the capacity formula predicts where.

## What changes, what stays the same

Prompt length 256 to 28,672 tokens at concurrency 1 and 4 on the default server; then 8,192-token prompts at rising concurrency with the KV cache capped at 4 GiB to simulate a small GPU.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> context-length
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline`, `kv-constrained`

## What is measured

Time to first token and inter-token latency by prompt length, KV cache usage, waiting requests and preemptions per run.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
