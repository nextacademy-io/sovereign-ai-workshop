# Task 04 — Optimize the deployment

## Goal

Test one optimization lever on your group's server with a controlled experiment, **predict a variation the lecture modules did not show**, and report honestly what improved, what got worse and what it costs.

## Context

There is no universally fastest configuration; there is only one that fits a workload and its constraints. The lecture modules on batching, the KV cache and quantization already showed one measured result for each lever. This lab is not a repeat of them: each group takes the same lever one step further, writes its prediction down before anything runs, and then finds out whether the explanation from the lecture still holds. The trainer will ask for the trade-off, not for the speed-up.

## Scope

Done means one lever is tested with a before and an after measurement on the same workload, **with a written prediction made before the run**, explained with the resource model, and written into the *Experiments* section of your report with its trade-off. Out of scope: combining several changes in one run, and changes beyond the profiles and `--set` values the launcher offers.

## Starting Point

- The baseline measurements of Task 03 are in your report (or in `benchmark/results/reference/` after `./scripts/reset.sh lab-04`).
- Your group's server runs `baseline`. **You are the only group on your machine**, so you may restart the server, but tell your group first: a restart takes from about 40 seconds (`baseline`) to about two and a half minutes (the first `fp8` start: 143 s in the reference session), and the model is offline meanwhile. If a profile fails to start, the previous one is restored automatically.

## Instructions

Your lever and your variation (the trainer assigns one lever per group):

| Group | Lever | What the lecture showed (reference exists) | Your variation (no reference exists) | What to look at |
| --- | --- | --- | --- | --- |
| A: quantization | FP8 weights and FP8 KV cache | Weights and KV cache in FP8 at 1 and 16 clients on `workshop-baseline`; FP8 KV on a small pool at 4 and 8 clients | FP8 KV cache on the small pool at **16 clients**: `kv-constrained` against `kv-constrained-fp8kv`, `--input-tokens 8192 --output-tokens 128` | KV capacity, waiting requests, preemptions, TTFT, tokens/s |
| B: prefix caching | Prefix cache on or off | A 2,000-token shared prefix of a 2,200-token prompt, 1 and 8 clients | A **shorter shared prefix**: `--workload shared-prefix --shared-prefix-tokens 500`, `baseline` against `no-prefix-cache` | TTFT, prefix-cache hit rate |
| C: context length | KV pool size | 8,192-token prompts, 8 clients, three pools (full, 4 GiB, 4 GiB with FP8 KV) | A **middle pool**: `kv-constrained` with `--set kv-cache-memory-bytes=8G`, 8,192-token prompts, 4, 8 and 16 clients | TTFT, waiting requests, preemptions, KV usage |
| D: concurrency / batching | Cap on the running batch | Cap of 8 against the default, 16 and 32 clients | **Other caps**: `baseline --set max-num-seqs=4` and `--set max-num-seqs=16`, 8, 16 and 32 clients | aggregate tokens/s, waiting requests, TTFT p95 |
| E: tensor parallelism | An optional fifth lever, only if a two-GPU machine is available. No reference run exists (`experiments/tensor-parallel/RESULTS.md`) | | | |

Reference results exist for what the lecture showed, not for your variation. They are in `benchmark/results/reference/` (after `./scripts/reset.sh lab-04`) and explained in `experiments/quantization/RESULTS.md`, `experiments/prefix-cache/RESULTS.md`, `experiments/context-length/RESULTS.md` and `experiments/concurrency/RESULTS.md`. Your variation is a new data point: nobody has its answer yet, so read the references only **after** your own measurement.

1. **Restate the lecture result** for your lever in two sentences of your own: what improved, what got worse, which resource was the bottleneck.
2. **Predict your variation, in writing, before anything runs.** For every metric in the last column: a number or a direction (up, down, flat), and the reason in terms of the resource model. Hand the prediction in to the trainer.
3. **Baseline for your workload.** Use your Task 03 numbers where the workload is the same. Groups A, B and C run the baseline side with *their* workload first; the numbers of Task 03 are for another workload.
4. **Change one variable.**

   ```bash
   ./scripts/start-vllm.sh <profile> [--set key=value]    # for example: kv-constrained-fp8kv
   sudo wsctl info | python3 -m json.tool | head -30
   ```

   Read the new startup numbers: weights memory, KV cache tokens, time to ready.
5. **Measure** with the same harness and the same workload:

   ```bash
   ./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 16 --label <profile>             # group A
   ./scripts/benchmark.sh --workload shared-prefix --shared-prefix-tokens 500 --concurrency 1,8 --label <profile>   # group B
   ./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 4,8,16 --label <profile>          # group C
   ./scripts/benchmark.sh --concurrency 8,16,32 --label <profile>                                                 # group D
   ```

6. **Check quality** if your change can affect it (group A, when you also changed the weights):

   ```bash
   python3 experiments/quality_probe.py run --label <profile> --items 120 --out /tmp/quality-<profile>.json
   python3 experiments/quality_probe.py compare /tmp/quality-baseline.json /tmp/quality-<profile>.json
   ```

   Run it first on the baseline profile if you have not. The probe is a spot check: with 120 items a difference of a few points is noise.
7. **Compare prediction and result.** Where were you wrong, and which part of your resource model does that correct? Only now read the lecture's reference results and put them next to yours.
8. **Fill the template** from `workshop-artifacts/inference-report.md` (*Experiments*): prediction, before, after, metric improved, metric degraded, quality impact, memory impact, operational impact, recommendation.
9. **Prepare a short report** for the other groups. Lead with the trade-off and with what your prediction got wrong.

## Expected Result

A completed experiment block with your written prediction, numbers from your own result files, an explanation in terms of memory bandwidth, compute, KV cache or queueing, and a recommendation that names a condition under which you would **not** use the change. At least one metric got worse or became more expensive to operate: if you found none, look again. A wrong prediction is a good result if the report says which assumption failed.

## Validation

- The result files of both configurations are in `benchmark/results/mine/` and carry their server arguments, so the difference between them is visible in the data.
- Your prediction was written down before the run and is in the report next to the result.
- Your *before* and *after* numbers use the same workload and the same concurrency.
- Your report states the **operational** cost of the change (a restart, a different checkpoint, a quality check, a new failure mode).
- You can say what you would measure next.

## If You Get Stuck

| Symptom | Fix |
| --- | --- |
| The new profile does not start | The server rolls back to the previous profile and prints why. Read the last log lines: `sudo wsctl logs 60`. That is also a result: record it. |
| After-numbers look too good | Check the hit rate warning (prefix cache) and that you compared the same workload and concurrency. |
| You cannot finish the second profile | `./scripts/reset.sh lab-04` copies measured reference results for what the lecture showed (not for your variation); use them for the missing side where they match your workload, and say so. |
| A variation does not start | An over-small pool or a context longer than the pool fails at start-up and the server rolls back (`sudo wsctl logs 60`). Record why: that is a result. |
| You want another variant | `./scripts/start-vllm.sh baseline --set max-num-seqs=16`. Allowed keys: `sudo wsctl profiles`. |

## Further Exploration

- Combine two of the hypotheses (for example FP8 weights with an FP8 KV cache) and measure whether the effects add up.
- Try a value between the two profiles (`--set max-num-seqs=...`, `--set max-model-len=...`) and draw the curve.
- Watch the same experiment on the Grafana dashboard and find the panel that explains the result best.
