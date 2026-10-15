# Experiment: baseline

## Question

Does the memory arithmetic of the sizing module predict what the server reports, and what does a single request cost?

## Hypothesis (a prediction to test, not a result)

The KV cache capacity the server reports is the available KV memory divided by the KV bytes per token (2 x layers x KV heads x head dim x bytes per element), to within about one percent. A single request decodes at a speed close to the memory-bandwidth bound: bytes of weights divided by bandwidth.

## What changes, what stays the same

Nothing changes: one server, default engine settings, one request at a time. The only comparison is arithmetic against the server's own log.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> baseline
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline`

## What is measured

Server startup time (first start and restart), weights memory, KV capacity in tokens, time to first token and inter-token latency of single requests, and the KV formula check (`kv-formula-check.json`).

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
