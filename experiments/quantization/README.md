# Experiment: quantization

## Question

What does quantization change in memory, speed and quality on this GPU?

## Hypothesis (a prediction to test, not a result)

FP8 weights roughly halve the bytes read per decoded token, so single-stream decode speeds up, and the freed memory holds more KV cache. Throughput under load also improves, less than the single-stream speed-up. Quality moves by an amount a small spot check cannot distinguish from noise, which is itself the finding: it can show that a change is not large, not that it is zero.

## What changes, what stays the same

Weights: BF16 against the publisher's FP8 checkpoint (same tokenizer and served name). KV cache: BF16 against FP8 with BF16 weights. Same workload and concurrency throughout.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> quantization
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline`, `fp8`, `kv-fp8`

## What is measured

Weights memory, KV capacity, inter-token latency, aggregate throughput, and a self-generated quality probe (accuracy with confidence intervals; agreement of greedy completions with the BF16 reference). A profile that cannot start on this GPU is recorded as a result.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
