# Experiment: tensor-parallel

## Question

When do two GPUs help: tensor parallelism across both, or one replica per GPU?

## Hypothesis (a prediction to test, not a result)

Tensor parallelism splits every layer across the GPUs and pays an all-reduce per layer. On a GPU without NVLink that traffic goes over PCIe, so the latency gain is smaller than the memory-bandwidth arithmetic suggests, and two independent replicas give more total throughput. Which wins depends on whether the goal is single-request latency or capacity.

## The arithmetic behind the hypothesis

All of it is arithmetic from the datasheet and the layer structure, not a measurement.

- One decode step of Qwen3-8B reads 16.38 GB of BF16 weights. At 1,597 GB/s that is a floor of 10.3 ms.
- An ideal TP=2 split halves the weights each GPU reads, 8.19 GB, a floor of 5.1 ms. The saving is at most 5.1 ms per step.
- Each of the 36 layers needs two all-reduces, one after the attention part and one after the MLP part: 72 per decode step.
- The saving is used up when one all-reduce costs 5.1 ms ÷ 72, about 71 µs. Above that the step on two GPUs is slower than on one; below it tensor parallelism lowers the latency of one request.
- The payload of one all-reduce is the tokens in the step × 4,096 (hidden size) × 2 B: 8 KiB for one decode token, 9.4 MiB for a 1,200-token prompt. At 64 GB/s per direction (PCIe Gen 5 x16, derived in RESEARCH 6.6) the transfer alone takes 0.13 µs and 154 µs. The fixed latency of one all-reduce is not known from any source here.

The 71 µs assumes an ideal split and no overlap of communication with compute. Read it as a scale, not a threshold.

## What changes, what stays the same

One GPU, TP=2 across two GPUs, and two replicas (one server per GPU). Same workload; total concurrency held equal.

## Run it

```bash
# on the trainer's laptop: runs on the pod, copies results to benchmark/results/<date>-rtxpro6000-<label>/
experiments/run-session.sh --host <ip> --port <port> --label <label> tensor-parallel
```

`experiments/runner.py` restarts the shared server with the profiles below, runs the benchmark harness with fresh prompts
at every level, and stores each result with its hardware, model revision, engine version, server arguments and date.

Profiles: `baseline` (one GPU), `tp2` (it inherits the baseline's `gpu-memory-utilization` of 0.80, so the comparison is fair), and `baseline` plus `baseline-replica` on separate GPUs (ports 8000 and 8001, each driven by its own harness process with half of the total concurrency). The embedding server is stopped for the experiment. Requires a two-GPU pod.

## What is measured

Per-request speed, aggregate throughput, time to first token, GPU power, and `nvidia-smi topo -m` to show how the GPUs are connected.

## Results

See [`RESULTS.md`](RESULTS.md) for what was measured, on which hardware and date, and what surprised. Raw JSON lives under `benchmark/results/`.
