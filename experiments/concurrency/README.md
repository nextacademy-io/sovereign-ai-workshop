# Experiment: concurrency

## Question

Where does aggregate throughput stop scaling with concurrency, and what does a capped batch do to queueing?

## Hypothesis (a prediction to test, not a result)

Aggregate tokens per second grows with concurrency, less than linearly, then flattens when another resource saturates. Each user's speed falls only slowly at first, because one read of the weights serves every request in the batch. Capping the running batch (`max-num-seqs`) adds queueing: waiting requests appear and time to first token rises.

## What changes, what stays the same

Concurrency 1 to 64 on the default server; then the same sweep with the batch capped at 8 requests. Workload: 1,200 input and 180 output tokens.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> concurrency
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline`, `max-seqs-8`

## What is measured

Aggregate tokens per second, time to first token (p50, p95), inter-token latency, tokens per second per request, running and waiting requests, KV cache usage, GPU utilization and power.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
