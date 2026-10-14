# Experiment: tensor-parallel

## Question

When do two GPUs help: tensor parallelism across both, or one replica per GPU?

## Hypothesis (a prediction to test, not a result)

Tensor parallelism splits every layer across the GPUs and pays an all-reduce per layer. On a GPU without NVLink that traffic goes over PCIe, so the latency gain is smaller than the memory-bandwidth arithmetic suggests, and two independent replicas give more total throughput. Which wins depends on whether the goal is single-request latency or capacity.

## What changes, what stays the same

One GPU, TP=2 across two GPUs, and two replicas (one server per GPU). Same workload; total concurrency held equal.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> tensor-parallel
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline` (one GPU), `tp2`, and two baseline servers on separate GPUs. Requires a two-GPU pod.

## What is measured

Per-request speed, aggregate throughput, time to first token, GPU power, and `nvidia-smi topo -m` to show how the GPUs are connected.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
