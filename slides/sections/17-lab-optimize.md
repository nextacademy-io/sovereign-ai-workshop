---
layout: section
module: 17
heading: "Lab 4: optimize the deployment"
layer: runtime
question: "Which change fits your workload, and what does it cost you?"
can:
  - "Test one lever with one variable and a control"
  - "Predict a variation nobody has measured, in writing, before the run"
  - "Report the trade-off first, then what your prediction got wrong"
---

---
layout: default
heading: "Your lever and your variation"
---

<div class="hyp">

| Group | Lever | Your variation (no reference run) | What to look at |
| --- | --- | --- | --- |
| **A** quantization | FP8 weights and FP8 KV cache | FP8 KV cache on the 4 GiB pool at 16 clients, 8,192-token prompts (`kv-constrained-fp8kv`) | KV capacity, waiting requests, preemptions, TTFT, tokens/s |
| **B** prefix caching | prefix cache on or off | a shorter shared prefix: 500 tokens (`baseline` against `no-prefix-cache`) | TTFT, prefix-cache hit rate |
| **C** context length | KV pool size | a middle pool: 8 GiB instead of 4 GiB, 8,192-token prompts, 4, 8 and 16 clients | TTFT, waiting requests, preemptions, KV usage |
| **D** concurrency | cap on the running batch | other caps: 4 and 16 (`max-num-seqs`), at 8, 16 and 32 clients | aggregate tokens/s, waiting requests, TTFT p95 |

</div>

<p class="small muted">Reference results exist for what the lecture showed, not for your variation. An optional fifth lever, tensor parallelism, only if a two-GPU machine is available.</p>

<style>
.hyp :deep(code) {
  white-space: nowrap;
}
</style>

<!--
**Key:** Each group takes its lever one step beyond the lecture: the lecture has a measured result for its configuration, the variation has none, so the prediction is a hypothesis and nobody has the answer yet.

**Example:** Assign A to D. Reference results exist for the lecture configurations (FP8, FP8 KV on the small pool, the 2,000-token prefix, three pools, the cap of 8); none for A's 16 clients, B's 500 tokens, C's 8 GiB pool or D's caps of 4 and 16.

**Transition:** Predict in writing first, before anything runs.

**Question:** "Why not just measure?" A prediction written after the run only describes it.

**Deeper:** A restart takes the model away from the whole group: 39.3 s for baseline, 41.3 s for FP8 with warm caches, 143 s for the first FP8 start in the reference session.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 1 to 4: predict, then change"
task: 04-optimization
artifact: workshop-artifacts/inference-report.md
---

- **1 Restate** the lecture result for your lever: what improved, what got worse, which resource limited.
- **2 Predict your variation in writing, before anything runs.** A number or a direction per metric, with the reason from the resource model. Hand it to the trainer.
- **3 Baseline** for your workload: Task 03 numbers where it matches; groups A, B and C first run `baseline` on their own workload.
- **4 Change one variable.** Tell your group first: the restart takes the model offline. A failed start is a result: record why.

<Terminal title="step 4">

```bash
./scripts/start-vllm.sh <profile> [--set key=value]   # for example: kv-constrained-fp8kv
sudo wsctl info | python3 -m json.tool | head -30     # weights memory, KV tokens, time to ready
```

</Terminal>

<!--
**Key:** The prediction is a document, written before the first restart and handed in, because only then can a wrong cell later be a finding about our model instead of a story told afterwards.

**Example:** The trainer collects the predictions before anything runs and reads two aloud, without comment. For groups A, B and C the Task 03 numbers are the wrong baseline: B needs the shared-prefix workload, A and C 8,192-token prompts, so they measure the baseline side with their workload first.

**Transition:** Now measure, then compare with what you wrote.

**Question:** "What if the pool is too small to start?" An over-small pool or a context longer than the pool fails at start-up and the server rolls back: record why, that is a result.

**Deeper:** The prediction names a metric, a direction or number, and one sentence on which resource limits: compute, bandwidth, KV capacity or queueing.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 5 to 9: measure, compare, report"
task: 04-optimization
artifact: workshop-artifacts/inference-report.md
---

<Terminal title="step 5, measure with the same harness and workload: your group's command">

```bash
./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 16 --label <profile>   # A
./scripts/benchmark.sh --workload shared-prefix --shared-prefix-tokens 500 \
  --concurrency 1,8 --label <profile>                                                                # B
./scripts/benchmark.sh --input-tokens 8192 --output-tokens 128 --concurrency 4,8,16 --label <profile>  # C
./scripts/benchmark.sh --concurrency 8,16,32 --label <profile>                                       # D
```

</Terminal>

- **6 Quality** (group A, only if the weights changed): the probe in the task.
- **7 Compare prediction and result:** where were you wrong, and which assumption of the resource model does that correct? Only now read the lecture's reference results.
- **8 and 9 Template and short report:** the trade-off first, then what your prediction got wrong.

<!--
**Key:** The comparison is the point of the lab: a wrong prediction is a good result when the report names the assumption that failed, and the reference results are read only after your own measurement.

**Example:** Group A's probe matters only if the weights changed; at 120 items a few points are noise. At least one metric got worse or costs more to operate: if a group found none, look again. If a variation does not start, the server rolls back and prints why (sudo wsctl logs 60).

**Transition:** Then the debrief: what each group got wrong.

**Question:** "My after-numbers look too good." Check workload, concurrency and, for group B, the hit-rate warning.

**Deeper:** ./scripts/reset.sh lab-04 copies reference results for the lecture configurations, never for a variation. Done: result files of both configurations in benchmark/results/mine.
-->

---
layout: default
heading: "Debrief: the trade-off, and what you got wrong"
---

| Lecture configuration | Improved | Got worse | Operational cost |
| --- | --- | --- | --- |
| **A** FP8 weights | decode speed, aggregate tokens/s, weights memory | arithmetic accuracy, within the probe's noise | other checkpoint, slow first start, own quality check |
| **B** prefix cache | TTFT and aggregate tokens/s on a shared prefix | nothing in these runs | the identical part must come first; watch the hit rate |
| **C** small KV pool | speed of each running request | TTFT, aggregate tokens/s, requests at once | the pool must hold one maximum-length request |
| **D** batch cap of 8 | speed of each running request (a little) | aggregate tokens/s, TTFT through queueing | choose the cap from the SLO; alert on waiting requests |

<Takeaway title="Questions for every report">

What did your prediction get wrong, and which assumption of the resource model failed? When would you NOT use your change? What would you measure next?

</Takeaway>

<!--
**Key:** The table is the lecture's trade-off per lever; each group says how its variation moved it, then answers the questions. No exit condition, no recommendation. See FACILITATOR.md section 5.

**Example:** Expected readings are hypotheses reasoned from the lecture, with no reference run. A: an FP8 cache holds twice the tokens in the same bytes, so fewer waiting requests. B: 500 shared tokens save less prefill, so a smaller TTFT gain. C: 8 GiB holds about seven 8,320-token requests, so queueing starts above seven. D: cap 4 pins below the lecture's cap of 8, cap 16 acts like the default at 16 clients and pins below it at 32.

**Transition:** The lecture numbers, as the anchor.

**Question:** "Group B has nothing worse." Correct in these runs: the price is the condition.

**Deeper:** The trainer collected the predictions before the runs: read two wrong ones aloud first.
-->

---
layout: default
heading: "Anchor: the lecture configurations, measured"
---

<ResultTable
  source="measured:benchmark/results/reference"
  :match='["concurrency/baseline-c016/c016.json", "concurrency/max-seqs-8-c016/c016.json", "context-length/baseline-c008-in08192/c008.json", "context-length/kv-constrained-c008-in08192/c008.json", "prefix-cache/baseline-shared-c008/c008.json", "prefix-cache/no-prefix-cache-shared-c008/c008.json", "quantization/baseline-c016/c016.json", "quantization/fp8-c016/c016.json"]'
  :labels='["D baseline", "D max-seqs-8", "C baseline, 8k prompts", "C kv-constrained, 8k prompts", "B baseline, cache on", "B no-prefix-cache", "A baseline, BF16", "A fp8"]'
  label-header="Group and profile"
  :columns='["concurrency", "ttft_ms.p50", "output_tps_per_request.p50", "aggregate_tps"]'
  :headers='["Clients", "TTFT p50 (ms)", "Tokens/s per request", "Aggregate tokens/s"]'
/>

<p class="small muted">The lecture's configurations, not your variations. Pairs share a workload and a load: compare within a pair, and put your own result next to its pair.</p>

<!--
**Key:** These pairs are the anchor, not the answer: the lecture configuration of each lever. Your variation is a new data point to read against its pair; compare the shape, not the digits.

**Example:** D: TTFT p50 0.59 s to 2.96 s, aggregate 900 to 553 tokens/s, speed per request 68.7 to 79.8. C: 1.6 s to 5.1 s, aggregate 189 to 129, speed 33.6 to 58.4. B: TTFT 106 against 588 ms, aggregate 620 against 444. A: TTFT 616 to 360 ms, speed 69.4 to 97.0, aggregate 897 to 1,323.

**Transition:** Next: trainer demos, then the predictions from the checkpoint get scored.

**Question:** "Why p50 and not p95?" The p50 has more samples behind it; the p95 tells the same story.

**Deeper:** One session, one run per row, four experiments on the same card and engine version.
-->
