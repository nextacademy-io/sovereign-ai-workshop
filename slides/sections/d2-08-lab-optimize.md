---
layout: section
heading: "Lab 4: optimize the deployment"
time: "16:00"
minutes: 60
layer: runtime
question: "Which change fits your workload, and what does it cost you?"
---

---
layout: default
heading: "Rules of engagement: one variable, one trade-off"
---

<div class="ki-grid ki-cols-2">
<div>

One hypothesis per group. **Report the trade-off first.**

1. **One variable.** One profile, one change.
2. **Same workload and concurrency** before and after.
3. **Tell your group** before a restart: the model goes offline.
4. **A failed start is a result.** Record why.

</div>
<div class="ki-stack">

<MetricCard label="Restart of baseline, warm caches" source="measured:benchmark/results/reference/startup/restart.json" metric="wsctl_startup_seconds" unit="s" digits="1" />
<MetricCard label="Restart with FP8 weights, warm caches" source="measured:benchmark/results/reference/quantization/startup.json" metric="fp8.startup_seconds" unit="s" digits="1" />

</div>
</div>

<Provenance source="measured:benchmark/results/reference/startup/restart.json" />

<Warning title="The first start of the FP8 checkpoint is the slow one">

About two and a half minutes: a new checkpoint to load and compile.

</Warning>

<!--
**Key:** Lab 4 is a controlled experiment, not a tuning contest: each group changes one thing, measures it under identical conditions and says what it cost. The rules protect the data and the people sharing the machine. **Example:** Read the four rules aloud. A restart takes the model away from the whole group: 39.3 s for baseline and 41.3 s for FP8 with warm caches, but the first start of the FP8 checkpoint took 143 s in the reference session. That 143 s is in the task and in experiments/quantization/RESULTS.md, not in a result file, hence "about two and a half minutes". **Transition:** Which hypothesis does your group get? **Question:** "Can we change two things to save time?" No: nobody could then say which one moved the metric; combining two is Further Exploration. **Deeper:** Each group is alone on its machine, so a restart affects only its own members.
-->

---
layout: default
heading: "Your hypothesis: the trainer assigns one per group"
---

<div class="hyp">

| Group | Hypothesis | Profile(s) | Workload | What to look at |
| --- | --- | --- | --- | --- |
| **A** quantization | FP8 weights make decode faster and free memory for more KV cache, at some cost in quality | `fp8`; optionally `kv-fp8` | `workshop-baseline` | ITL, aggregate tokens/s, weights memory, KV capacity, quality |
| **B** prefix caching | A long prefix shared by many requests is prefilled only once | `baseline` vs `no-prefix-cache` | `shared-prefix` | TTFT, prefix-cache hit rate |
| **C** context length | Long prompts cost TTFT and KV memory; with a small KV budget they queue or get evicted | `baseline` vs `kv-constrained` | `--input-tokens 8192` | TTFT, waiting requests, preemptions, KV usage |
| **D** concurrency | Capping the batch limits throughput and creates queueing | `baseline` vs `max-seqs-8` | `workshop-baseline` | aggregate tokens/s, waiting requests, TTFT p95 |

</div>

<p class="small muted">Group E, tensor parallelism, is the trainer's demo in the last block of the day.</p>

<style>
.hyp :deep(code) {
  white-space: nowrap;
}
</style>

<!--
**Key:** Four hypotheses touch four different resources: quantization acts on bytes per decode step, prefix caching on prefill work, the small KV pool on memory capacity and queueing, the batch cap on the scheduler. Each is a prediction, not a result. **Example:** Assign A to D. Ask each group for one sentence: which of the morning's four resources does my change touch, and which metric should move first? Group C's profile simulates a small GPU with a 4 GiB KV pool, so the memory limit shows on a card that never reaches it. **Transition:** Steps one to four, on the next slide. **Question:** "Why is the baseline in every pair?" It is the control: one variable differs, everything else stays. **Deeper:** The letters belong to hypotheses; the machines are called alpha to delta in the agenda.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 1 to 4: hypothesis to measurement"
task: 04-optimization
timebox: 40
artifact: workshop-artifacts/inference-report.md
---

- **1 Hypothesis:** what improves, what gets worse, which resource is the bottleneck. Write it down first.
- **2 Baseline:** your Task 03 numbers; groups B and C first run `baseline` on their own workload.

<Terminal title="steps 3 and 4: change one variable, then measure the same way">

```bash
./scripts/start-vllm.sh <profile>                   # step 3, for example: fp8
sudo wsctl info | python3 -m json.tool | head -30   # weights memory, KV tokens, time to ready
# step 4, groups A and D
./scripts/benchmark.sh --concurrency 1,8,16 --label <profile>
# step 4, group B
./scripts/benchmark.sh --workload shared-prefix --concurrency 1,8 --label <profile>
# step 4, group C
./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 1,4,8 --label <profile>
```

</Terminal>

<!--
**Key:** The prediction is written before anything runs, and the baseline must come from the same workload as the "after", because a before and after only mean something when both sides ran the same thing. **Example:** For groups B and C the Task 03 numbers are the wrong baseline: B needs the shared-prefix workload, C 8,192-token prompts, so they measure baseline with their workload first. After the start, sudo wsctl info shows the arguments in force; weights memory, KV cache tokens and time to ready are the first results of the change. **Transition:** Group A has one more step before anyone explains anything. **Question:** "My after-numbers look too good." Check workload and concurrency, and for group B the hit-rate warning: a benchmark that repeats its prompts measures the cache. **Deeper:** Each run draws a new random seed; nobody passes --seed.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 5 to 8: quality, explain, report"
task: 04-optimization
timebox: 40
artifact: workshop-artifacts/inference-report.md
---

**5. Group A, quality:** run the probe on `baseline` first. At 120 items a few points are noise.

<Terminal title="step 5, group A">

```bash
python3 experiments/quality_probe.py run --label <profile> --items 120 --out /tmp/quality-<profile>.json
python3 experiments/quality_probe.py compare /tmp/quality-baseline.json /tmp/quality-<profile>.json
```

</Terminal>

**6. Explain** with the resource model: which bottleneck, and what did the change do to it?

**7. Fill the template** in *Experiments*: before, after, improved, degraded, quality, memory, operations, recommendation.

**8. Five-minute report, trade-off first.** At least one metric got worse or costs more to operate: if you found none, look again.

<!--
**Key:** A speed-up without a quality check is half a result, and the probe also tells you how large a difference it can resolve. Everybody then explains with the four-resource model, fills the template and leads with the trade-off; the recommendation names a condition under which the group would not use the change. **Example:** Only the arithmetic kind of item can discriminate. In the reference session, with 240 items, FP8 weights scored 2.5 points lower, inside the interval, and about 3 percent of open completions matched BF16 exactly: say this after the reports. Suggested pacing for the 40 minutes: 5 hypothesis, 5 baseline, 15 change and measure, 5 explain, 10 template and report. **Transition:** What if the second profile does not start or time runs out? **Question:** "Is 120 items enough?" Not for the 2 percent bound of the SLO: that needs more items, from your own traffic. **Deeper:** The task's validation: result files of both configurations in benchmark/results/mine.
-->

---
layout: default
heading: "Stuck: fall-backs, and where the reference results are"
---

| Symptom | Fix |
| --- | --- |
| The new profile does not start | The server rolls back and prints why: `sudo wsctl logs 60`. That is a result: record it. |
| After-numbers look too good | Same workload and concurrency? Read the prefix-cache hit-rate warning. |
| Out of time for the second profile | `./scripts/reset.sh lab-04` copies reference results; use them for the missing side and say so. |
| The server runs the wrong profile | `./scripts/reset.sh lab-04 --server` (restarts it for your group). |
| You want your own variant | `./scripts/start-vllm.sh baseline --set max-num-seqs=16`; allowed keys: `sudo wsctl profiles`. |

Reference results, one directory per hypothesis under `benchmark/results/reference/`:

| A | B | C | D |
| --- | --- | --- | --- |
| `quantization` | `prefix-cache` | `context-length` | `concurrency` |

<!--
**Key:** Every fall-back keeps the experiment honest: a failed start is a finding, reference results fill a gap only when the report says so, and a reset never deletes work. **Example:** If the group's profile fails, the server rolls back to the previous profile by itself and prints the cause; the group reads the last lines with sudo wsctl logs 60 and records them. If time is short, ./scripts/reset.sh lab-04 puts the reference results of all four hypotheses on the machine, and the missing side is marked as reference in the report. **Transition:** Groups report, five minutes each. **Question:** "Does reset.sh lab-04 overwrite my report?" No: replaced files are saved to ~/.workshop-backups first, and only --hard replaces files you changed. **Deeper:** The full numbers belong to the quantization, KV cache and batching blocks and to the debrief; the directories hold summary.md files next to each result.
-->

---
layout: default
heading: "Debrief: four changes, four trade-offs"
---

| Group | Improved | Got worse | Operational cost |
| --- | --- | --- | --- |
| **A** FP8 weights | decode speed, aggregate tokens/s, TTFT, weights memory | arithmetic accuracy (within the probe's noise); outputs differ from BF16 | other checkpoint, slow first start, own quality check, BF16 kept as rollback |
| **B** prefix cache | TTFT and aggregate tokens/s on a shared prefix | nothing in these runs | the identical part must come first; watch the hit rate; a repeated benchmark measures the cache |
| **C** small KV pool | speed of each running request, GPU memory in use | TTFT, aggregate tokens/s, requests running at once | the pool must hold one maximum-length request, or the start is refused |
| **D** batch cap of 8 | speed of each running request (a little) | aggregate tokens/s, TTFT through queueing | choose the cap from the SLO; alert on waiting requests |

<Takeaway>

No row is free. The price is a metric, a condition, or something to operate.

</Takeaway>

<!--
**Key:** After the five-minute reports this table is the common answer: every change improves a metric and costs something, and the cost is a worse metric, a condition on the workload or an operating task. Reveal it only after the groups reported, then ask where each group's own report differed. **Example:** A and C trade a measured metric; B and D trade a condition: caching gives nothing without an identical shared prefix, and a cap only makes sense against an SLO. In group C the small pool is faster per request and slower to the first token. **Transition:** The numbers behind the table. **Question:** "Group B has nothing worse." Correct in these runs: the control with nothing shared behaved like cache-off, so the price is the condition and the pitfall of repeated benchmarks. **Deeper:** Decode speed with the cache was equal at one client.
-->

---
layout: default
heading: "The numbers behind the table"
---

<ResultTable
  source="measured:benchmark/results/reference"
  :match='["concurrency/baseline-c016/c016.json", "concurrency/max-seqs-8-c016/c016.json", "context-length/baseline-c008-in08192/c008.json", "context-length/kv-constrained-c008-in08192/c008.json", "prefix-cache/baseline-shared-c008/c008.json", "prefix-cache/no-prefix-cache-shared-c008/c008.json", "quantization/baseline-c016/c016.json", "quantization/fp8-c016/c016.json"]'
  :labels='["D baseline", "D max-seqs-8", "C baseline, 8k prompts", "C kv-constrained, 8k prompts", "B baseline, cache on", "B no-prefix-cache", "A baseline, BF16", "A fp8"]'
  label-header="Group and profile"
  :columns='["concurrency", "ttft_ms.p50", "output_tps_per_request.p50", "aggregate_tps"]'
  :headers='["Clients", "TTFT p50 (ms)", "Tokens/s per request", "Aggregate tokens/s"]'
/>

<p class="small muted">Pairs share a workload and a load. Compare within a pair, never across.</p>

<!--
**Key:** Read each pair as one group's before and after: same workload and load, one variable different. Compare the shape with your own numbers, not the digits; a few percent is normal for one session. **Example:** D: TTFT p50 0.59 s to 2.96 s, aggregate 900 to 553 tokens/s, speed per request 68.7 to 79.8. C: 1.6 s to 5.1 s, aggregate 189 to 129, speed 33.6 to 58.4. B: TTFT 106 against 588 ms, aggregate 620 against 444. A: TTFT 616 to 360 ms, speed 69.4 to 97.0, aggregate 897 to 1,323. The table is sorted by experiment name, so the groups run D to A. **Transition:** One question to end on. **Question:** "Why p50 and not p95?" The p50 has more samples behind it; the p95 tells the same story. **Deeper:** One session, one run per row, four experiments on the same card and engine version.
-->

---
layout: statement
---

# Under which condition would you NOT use your change?

<!--
**Key:** Every report ends with the exit condition, because a recommendation without one is a verdict. **Example:** Collect one answer per group on the shared screen. Typical ones: A, when the quality bar is tighter than a spot check can resolve, or on a GPU without native FP8; B, when requests share no byte-identical prefix; C and D, when the TTFT target cannot tolerate the queue. Ask the room which answer they would defend to a decision maker. **Transition:** Next: trainer demonstrations, then the morning's predictions get their answers. **Question:** "What if we would always use it?" Then say what you would watch to notice the day it stops being true: hit rate, waiting requests, an eval on your own items. **Deeper:** This sentence is also the last field of the report template: Recommendation names the condition.
-->
