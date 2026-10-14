# Task 04 — Optimize the deployment

## Goal

Test one optimization hypothesis on your group's server with a controlled experiment, and report honestly what improved, what got worse and what it costs.

## Context

There is no universally fastest configuration; there is only one that fits a workload and its constraints. Each group gets one hypothesis, changes one variable, measures before and after, and explains the result. The trainer will ask for the trade-off, not for the speed-up.

## Timebox

40 minutes.

## Starting Point

- The baseline measurements of Task 03 are in your report (or in `benchmark/results/reference/` after `./scripts/reset.sh lab-04`).
- Your group's server runs `baseline`. **You are the only group on your machine**, so you may restart the server, but tell your group first: a restart takes from about 40 seconds (`baseline`) to about two and a half minutes (the first `fp8` start: 143 s in the reference session), and the model is offline meanwhile. If a profile fails to start, the previous one is restored automatically.

## Instructions

Your hypothesis (the trainer assigns one per group):

| Group | Hypothesis | Profile(s) | Workload | What to look at |
| --- | --- | --- | --- | --- |
| A: quantization | FP8 weights make decode faster and free memory for more KV cache, at some cost in quality | `fp8`; optionally `kv-fp8` | `workshop-baseline` | ITL, aggregate tokens/s, weights memory, KV capacity, quality |
| B: prefix caching | A long prompt prefix shared by many requests is prefilled only once | `baseline` vs `no-prefix-cache` | `shared-prefix` | TTFT, prefix-cache hit rate |
| C: context length | Long prompts cost time to first token and KV memory; with a small KV budget they queue or get evicted | `baseline` vs `kv-constrained` | `--input-tokens 8192` | TTFT, waiting requests, preemptions, KV usage |
| D: concurrency / batching | Capping the batch limits throughput and creates queueing | `baseline` vs `max-seqs-8` | `workshop-baseline` | aggregate tokens/s, waiting requests, TTFT p95 |
| E (optional): tensor parallelism | Trainer demo only: it needs a two-GPU machine, and the reference run could not be made (`experiments/tensor-parallel/RESULTS.md`) | | | |

The trainer's reference results for each hypothesis are in `benchmark/results/reference/` (after `./scripts/reset.sh lab-04`) and explained in `experiments/quantization/RESULTS.md`, `experiments/prefix-cache/RESULTS.md`, `experiments/context-length/RESULTS.md` and `experiments/concurrency/RESULTS.md`. Read them **after** your own measurement, not before.

1. **Write the hypothesis** in your report: what do you expect to improve, what do you expect to get worse, and why (which resource is the bottleneck)?
2. **Baseline.** Use your Task 03 numbers at the concurrency you will compare (for example 8 and 16). For group B and C run the baseline with *their* workload first; the numbers of Task 03 are for another workload.
3. **Change one variable.**

   ```bash
   ./scripts/start-vllm.sh <profile>            # for example: fp8
   sudo wsctl info | python3 -m json.tool | head -30
   ```

   Read the new startup numbers: weights memory, KV cache tokens, time to ready.
4. **Measure** with the same harness and the same workload:

   ```bash
   ./scripts/benchmark.sh --concurrency 1,8,16 --label <profile>            # groups A, D
   ./scripts/benchmark.sh --workload shared-prefix --concurrency 1,8 --label <profile>   # group B
   ./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 1,4,8 --label <profile>   # group C
   ```

5. **Check quality** if your change can affect it (group A):

   ```bash
   python3 experiments/quality_probe.py run --label <profile> --items 120 --out /tmp/quality-<profile>.json
   python3 experiments/quality_probe.py compare /tmp/quality-baseline.json /tmp/quality-<profile>.json
   ```

   Run it first on the baseline profile if you have not. The probe is a spot check: with 120 items a difference of a few points is noise.
6. **Explain** the result with the resource model: which resource was the bottleneck, and what did the change do to it?
7. **Fill the template** from `workshop-artifacts/inference-report.md` (*Experiments*): before, after, metric improved, metric degraded, quality impact, memory impact, operational impact, recommendation.
8. **Prepare a five-minute report** for the other groups. Lead with the trade-off.

## Expected Result

A completed experiment block with numbers from your own result files, an explanation in terms of memory bandwidth, compute, KV cache or queueing, and a recommendation that names a condition under which you would **not** use the change. At least one metric got worse or became more expensive to operate: if you found none, look again.

## Validation

- The result files of both configurations are in `benchmark/results/mine/` and carry their server arguments, so the difference between them is visible in the data.
- Your *before* and *after* numbers use the same workload and the same concurrency.
- Your report states the **operational** cost of the change (a restart, a different checkpoint, a quality check, a new failure mode).
- You can say what you would measure next.

## If You Get Stuck

| Symptom | Fix |
| --- | --- |
| The new profile does not start | The server rolls back to the previous profile and prints why. Read the last log lines: `sudo wsctl logs 60`. That is also a result: record it. |
| After-numbers look too good | Check the hit rate warning (prefix cache) and that you compared the same workload and concurrency. |
| You are out of time for the second profile | `./scripts/reset.sh lab-04` copies measured reference results for all four hypotheses; use them for the missing side and say so. |
| You want your own variant | `./scripts/start-vllm.sh baseline --set max-num-seqs=16`. Allowed keys: `sudo wsctl profiles`. |

## Further Exploration

- Combine two of the hypotheses (for example FP8 weights with an FP8 KV cache) and measure whether the effects add up.
- Try a value between the two profiles (`--set max-num-seqs=...`, `--set max-model-len=...`) and draw the curve.
- Watch the same experiment on the Grafana dashboard and find the panel that explains the result best.
