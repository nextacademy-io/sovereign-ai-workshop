# Results: tensor-parallel

**Not measured.** This experiment needs a pod with two RTX PRO 6000 GPUs, and none could be created during the validation: the first attempt returned "There are no longer any instances available with the requested specifications" and a later capacity read showed two-GPU stock as *Out* on both CUDA versions (it had been *Low*, and only on CUDA 13.2 hosts, earlier the same day). The raw files do not exist, so this document makes no claim about speed.

## What exists

- The runner (`experiments/runner.py`, experiment `tensor-parallel`) and the profiles `baseline`, `tp2` and `baseline-replica` are written. It compares one GPU, tensor parallelism across both GPUs (the same `gpu-memory-utilization` of 0.80 as the baseline) and two independent servers, one per GPU, each driven by its own harness process with half of the concurrency.
- `combine_replica_results` is unit-tested (`experiments/test_runner_tp.py`). **The process handling for the two replicas and the `tp2` start have never run on hardware.** Expect to debug them on the first real run, and budget that time: shared memory for NCCL (`/dev/shm`) and the start order of the two servers are the likely first problems.
- The arithmetic of the hypothesis is in [`README.md`](README.md).

## What to expect, as hypotheses, from the single-GPU measurements

- One RTX PRO 6000 delivers about 900 output tokens/s at concurrency 16 and 1,294 at 32 (see [`../concurrency/RESULTS.md`](../concurrency/RESULTS.md)). Two independent replicas at 16 clients each should come close to twice the aggregate throughput of one at 16, because they share nothing: that is arithmetic from a measurement, not a measurement.
- Tensor parallelism halves the weight bytes each GPU reads per decode step (8.2 GB instead of 16.4 GB, 5.1 ms instead of 10.3 ms at the datasheet bandwidth), and adds an all-reduce after each attention and each MLP block of all 36 layers. This GPU has no NVLink (RESEARCH 5), so the all-reduce travels over PCIe. Whether the saved 5 ms exceeds the communication time is the question the experiment answers; the prediction in the README is that it does not by much.

## Before you teach this block

Run it once on a two-GPU machine and write the results here. Until then present tensor parallelism as a hypothesis with its design, as the slides of `d2-07-parallelism` do, and say plainly that it was not measured.
