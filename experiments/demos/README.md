# Experiment: demos

## Question

Trainer demonstrations: what happens when a configuration cannot work, and when does speculative decoding help?

## Hypothesis (a prediction to test, not a result)

A context length that cannot fit into the KV budget fails at startup with a message that names the numbers, and the supervisor restores the previous profile. N-gram speculative decoding speeds up generation when the output repeats the input at low load, and stops helping, or hurts, at high load and on ordinary prompts.

## What changes, what stays the same

Intentional failures: the model's full context with a 4 GiB KV budget (`oom-demo`), and a context beyond the model's own limit (`oom-demo` with `--set max-model-len=1048576`). Speculation: a copy-the-text workload and, as the control, ordinary prompts, each at concurrency 1 and 16 with and without n-gram drafting.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> demos
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `oom-demo`, `baseline`, `spec-ngram`. For a live speculative-decoding demo the copy workload is ready as `benchmark/workloads/copy-text.jsonl` (`./scripts/benchmark.sh --prompts-file benchmark/workloads/copy-text.jsonl --output-tokens 350 --no-engine-extensions --concurrency 1,16`; the last flag stops the harness from forcing the output length, so the model ends the copy when the text ends).

## What is measured

The startup error, the rollback, inter-token latency and throughput with and without speculation, and the speculative-decoding counters (drafted and accepted tokens).

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
