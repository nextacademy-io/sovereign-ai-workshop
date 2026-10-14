# Experiment: demos

## Question

Trainer demonstrations: what happens when a configuration cannot work, and when does speculative decoding help?

## Hypothesis (a prediction to test, not a result)

A context length that cannot fit into the KV budget fails at startup with a message that names the numbers, and the supervisor restores the previous profile. N-gram speculative decoding speeds up inter-token latency when the output repeats the input at low load, and stops helping, or hurts, at high load.

## What changes, what stays the same

Intentional failure: a 1,048,576-token context with a 4 GiB KV budget. Speculation: a copy-the-text workload at concurrency 1 and 16 with and without n-gram drafting.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> demos
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `oom-demo`, `baseline`, `spec-ngram`

## What is measured

The startup error, the rollback, inter-token latency and throughput with and without speculation, and the speculative-decoding counters (drafted and accepted tokens).

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
