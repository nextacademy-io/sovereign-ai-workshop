# Results: tensor-parallel

**Not measured.** This experiment needs a pod with two RTX PRO 6000 GPUs, and none could be created during the validation: the first attempt returned "There are no longer any instances available with the requested specifications" and a later capacity read showed two-GPU stock as *Out* on both CUDA versions (it had been *Low*, and only on CUDA 13.2 hosts, earlier the same day). The raw files do not exist, so this document makes no claim about speed.

## What exists

- The runner (`experiments/runner.py`, experiment `tensor-parallel`) and the profiles `baseline`, `tp2` and `baseline-replica` are written. It compares one GPU, tensor parallelism across both GPUs (the same `gpu-memory-utilization` of 0.80 as the baseline) and two independent servers, one per GPU, each driven by its own harness process with half of the concurrency.
- The workload is 1,200 input and 180 output tokens at 1, 8 and 32 clients in total. The replica run starts two servers on ports 8000 and 8001; their throughputs add and their latency percentiles are kept per replica. The runner also saves `nvidia-smi topo -m`, so nobody has to argue about the link.
- `combine_replica_results` is unit-tested (`experiments/test_runner_tp.py`). **The process handling for the two replicas and the `tp2` start have never run on hardware.** Expect to debug them on the first real run, and budget that time: shared memory for NCCL (`/dev/shm`) and the start order of the two servers are the likely first problems.
- The arithmetic of the hypothesis is in [`README.md`](README.md).

## What to expect, as hypotheses, from the single-GPU measurements

- One RTX PRO 6000 delivers about 900 output tokens/s at concurrency 16 and 1,294 at 32 (see [`../concurrency/RESULTS.md`](../concurrency/RESULTS.md)). Two independent replicas at 16 clients each should come close to twice the aggregate throughput of one at 16, because they share nothing: that is arithmetic from a measurement, not a measurement.
- Tensor parallelism halves the weight bytes each GPU reads per decode step (8.2 GB instead of 16.4 GB, 5.1 ms instead of 10.3 ms at the datasheet bandwidth), and adds an all-reduce after each attention and each MLP block of all 36 layers: 72 per decode step. This GPU has no NVLink (RESEARCH 6.3 and 6.6), so the all-reduce travels over PCIe. Whether the saved 5 ms exceeds the communication time is the question the experiment answers; the prediction in the README is that it does not by much.
- The break-even is 5.1 ms ÷ 72, about 71 µs per all-reduce, assuming an ideal split and no overlap. No source in this repository measures the cost of one all-reduce over PCIe.

## Predictions to write down before the first run

A factor against one GPU for every row, and the reason. The floor arithmetic allows tensor parallelism at most twice the speed at one client, and two replicas at most twice the aggregate.

| Setup, against one GPU | Metric |
| --- | --- |
| TP = 2, 1 client | ITL p50 |
| TP = 2, 32 clients | aggregate tokens/s |
| Two replicas, 32 clients in total | aggregate tokens/s |
| Two replicas, 32 clients in total | tokens/s per request |

## What would change our mind

| If the measurement shows | Our reading |
| --- | --- |
| TP ITL near 5 to 6 ms | the link is not the bottleneck: the hypothesis is wrong |
| TP ITL near the one-GPU step or above | the all-reduces eat the saving, as predicted |
| replicas below twice the one-GPU aggregate at 16 clients each | something is shared that we missed |
| `nvidia-smi topo -m` shows an NV entry | the link assumption is wrong; the research notes expect only PIX, PXB, PHB, NODE or SYS paths on this card |

## Before you present this as a result

Run it once on a two-GPU machine and write the results here. Until then present tensor parallelism as a hypothesis with its design and its break-even arithmetic, as the slides of `16-parallelism` do, and say plainly that it was not measured. The demos module lists it among the optional demos for a trainer with more hardware; any number shown there is the trainer's own.
