---
layout: section
heading: "Lab 3: benchmark the baseline"
time: "10:45"
minutes: 60
layer: runtime
question: "Where does more load stop helping, and what does it cost the user?"
---

---
layout: experiment
heading: "Predict the sweep before you run it"
step: prediction
experiment: concurrency
---

<Prediction>

Before the driver starts: at which concurrency does total tokens per second **stop growing**? What happens to TTFT and to the speed one user sees? Which resource will look saturated?

</Prediction>

| Concurrency | Aggregate tokens/s | TTFT p95 | Tokens/s per request |
| --- | --- | --- | --- |
| 1 | ? | ? | ? |
| 4 | ? | ? | ? |
| 8 | ? | ? | ? |
| 16 | ? | ? | ? |

A number or a direction in every cell. Write it into the report before anything runs.

<!--
**Key:** The prediction is the first step of the task, not an extra: a guess written down before the sweep is what turns a table of numbers into a test of our understanding of batching. **Example:** Give the groups five minutes. Typical guesses: throughput flattens at 8 or 16 users, TTFT stays flat, and the GPU is saturated. Ask each group for the one cell they are least sure about, and keep the answers on the shared screen for the debrief. **Transition:** Now the procedure: one driver per group, everybody else watches the dashboard. **Question:** "Do I need numbers?" Direction and rough size are enough; the point is to be able to say afterwards which part of the model was wrong. **Deeper:** The predictions from the morning table are still open: this lab tests the concurrency row.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 1 to 4: measure the sweep"
task: 03-benchmark
timebox: 45
artifact: workshop-artifacts/inference-report.md
---

**One benchmark at a time per group.** The *driver* runs it; everyone else watches.

- **1 Predict** first (previous slide).
- **2 Watch:** Grafana through a tunnel, dashboard *KI ohne Cloud: inference*.
- **3 Measure:** the driver runs the sweep.
- **4 Record:** copy the table into *Baseline* in your report.

<Terminal title="steps 2 and 3">

```bash
# everyone, on your laptop; then open http://127.0.0.1:3000
ssh -p <port> -L 3000:127.0.0.1:3000 <your-user>@<host>
# the driver, on the group's GPU host
./scripts/benchmark.sh --concurrency 1,4,8,16 --label baseline
```

</Terminal>

<!--
**Key:** One rule protects the data: only one benchmark runs at a time per group, because the server is shared; everything else is watching the right panels while it runs. **Example:** Watch Running requests, Waiting requests, KV cache usage, Tokens per second and GPU utilization. The command writes a table and JSON files to benchmark/results/mine with a new random seed each time, so nobody passes --seed. Record TTFT p50 and p95, latency p50 and p95, tokens/s per request, aggregate tokens/s, GPU utilization and VRAM. **Transition:** Two more steps wait after the first sweep. **Question:** "The prefix-cache warning appeared." An earlier run used the same prompts; run again without --seed, and ask the trainer if it stays. **Deeper:** Failures or timeouts usually mean another benchmark is still running: sudo wsctl status. If the room is behind, run 1, 8 and 16 only.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 5 and 6: contention, questions"
task: 03-benchmark
timebox: 45
artifact: workshop-artifacts/inference-report.md
---

**5. Contention round.** Two members run this at the same time, then compare each result with the concurrency-8 row of the first run.

<Terminal title="two members, two terminals, one server">

```bash
./scripts/benchmark.sh --concurrency 8 --label contention
```

</Terminal>

**6. Answer the four questions in the report:**

<div class="ki-grid ki-cols-2">
<div>

- When does throughput stop scaling?
- When does latency deteriorate?
- What resource looks saturated?

</div>
<div>

- Which configuration would you deploy, and why?

</div>
</div>

Stuck: `docs/TROUBLESHOOTING.md`, `./scripts/reset.sh lab-03`, or ask the trainer.

<!--
**Key:** The contention round makes the shared server visible: two people measuring at once are one load for the machine. The four questions are the deliverable; the numbers are the evidence. **Example:** Agree who runs the first round and who joins for contention. If the first run failed completely, ./scripts/reset.sh lab-03 copies the reference results; continue with those and say so in the report. Numbers more than 20 percent off the reference usually mean someone else is using the server or the run was too short: use --requests 64 per level. **Transition:** What should the table look like when you are done? **Question:** "Which configuration, which concurrency?" The one you would deploy for this morning's SLO; say what would break first above it. **Deeper:** Further exploration: --slo, an open-loop run with --request-rate, another workload, the cross-check script.
-->

---
layout: default
heading: "A good result: the reference up to concurrency 16"
---

<div class="sweep-to-16">

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="baseline-c"
  :columns='["concurrency", "ttft_ms.p50", "ttft_ms.p95", "latency_ms.p50", "latency_ms.p95", "output_tps_per_request.p50", "aggregate_tps", "gpu.utilization_pct.mean", "gpu.memory_used_mib.max"]'
  :headers='["Concurrency", "TTFT p50 (ms)", "TTFT p95 (ms)", "Latency p50 (ms)", "Latency p95 (ms)", "Tokens/s per request", "Aggregate tokens/s", "GPU util (%)", "VRAM max (MiB)"]'
/>

</div>

- Aggregate tokens/s grows, and **every doubling adds less**.
- Per-request speed falls slowly at first; TTFT grows because prompts queue. GPU utilization stays near 100 %.
- Your numbers differ by a few percent. **The shape should be the same.**

<style>
.sweep-to-16 :deep(tbody tr:nth-child(n + 6)) {
  display: none;
}
</style>

<!--
**Key:** The reference run is for comparison, not the answer: the shape should match yours, and a few percent difference is normal for one session on one card. **Example:** The reference has levels 1, 2, 4, 8 and 16; you ran 1, 4, 8 and 16, so concurrency 2 has no counterpart. Compare ratios, for example the growth per doubling. Validation from the task: ls benchmark/results/mine/*/c*.json lists four files, each with hardware, model revision, engine version and server arguments, and your table agrees with summary.md. **Transition:** The trainer's longer sweep shows what happens beyond 16. **Question:** "Is 100 percent GPU utilization at one request a problem?" No, and it is the observation to keep: utilization is a poor measure of how well the GPU is used. **Deeper:** The reference results are read-only; reset.sh copies them to your machine.
-->

---
layout: experiment
heading: "Longer sweep: where is the knee?"
step: measurement
experiment: concurrency
---

<div class="ki-grid ki-cols-2">
<ResultChart source="measured:benchmark/results/reference/concurrency" match="baseline-c" x="concurrency" y="aggregate_tps" title="Aggregate output tokens/s" ylabel="tokens/s" />
<ResultChart source="measured:benchmark/results/reference/concurrency" match="baseline-c" x="concurrency" y="output_tps_per_request.p50" title="Tokens/s per request (p50)" ylabel="tokens/s" digits="1" />
</div>

<Observation>

No flat region up to 64. The knee is in the user's numbers, not in the throughput.

</Observation>

<!--
**Key:** Throughput does not stop growing in the tested range, so the honest answer to "when does it stop scaling" is "not before 64 on this workload"; what changes is the price each user pays. **Example:** The gain per doubling falls from about 1.9 at the start to about 1.3 between 32 and 64: 83.9, 160.5, 310.4, 550.8, 900.0, 1,294.3 and 1,692.2 tokens per second, while the per-request speed falls from 86 to 32. The SLO breaks long before the throughput saturates. **Transition:** Why can the aggregate grow so much while each request slows only a little? **Question:** "So where is the knee?" Define it by the SLO or the per-request speed, not by the throughput curve; here the user-facing knee sits between 8 and 32, with 16 at the limit. **Deeper:** One run per level, no confidence intervals; a flat region would only appear above 64.
-->

---
layout: experiment
heading: "Explanation: bytes moved per step"
step: explanation
experiment: concurrency
---

<Formula :terms='[{ "t": "WEIGHTS + N × KV OF ONE REQUEST", "sub": "16.38 GB + N × 1,290 tokens × 147,456 B" }, { "op": "÷" }, { "t": "BANDWIDTH", "sub": "1,597 GB/s" }, { "op": "=" }, { "t": "STEP TIME FLOOR", "hot": true }]' />

<div class="ki-grid ki-cols-2 skip-c2">
<div>

| N | GB read per step | Floor (ms) |
| --- | --- | --- |
| 1 | 16.57 | 10.4 |
| 4 | 17.14 | 10.7 |
| 8 | 17.90 | 11.2 |
| 16 | 19.42 | 12.2 |
| 32 | 22.47 | 14.1 |
| 64 | 28.55 | 17.9 |

<p class="small muted">The measured step sits a little above the floor at every level.</p>

</div>
<div>

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="baseline-c"
  :columns='["concurrency", "itl_ms.p50"]'
  :headers='["Concurrency", "Measured ITL p50 (ms)"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>
</div>

<style>
.skip-c2 :deep(.rt tbody tr:nth-child(2)) {
  display: none;
}
</style>

<!--
**Key:** One decode step reads all the weights once plus the KV cache of every running request, so the step time barely moves while tokens per step grow: that is why batching works. The model lands within 10 to 15 percent of the measured step at every level. **Example:** KV of one request: 1,290 tokens (1,200 prompt plus half of the 180 output) times 147,456 bytes is 0.19 GB. Eight requests add 1.5 GB to 16.38 GB: the floor moves from 10.4 to 11.2 ms while tokens per step grow eightfold. At 64 requests the cache is 43 percent of the bytes. **Transition:** What does this mean for the SLO and the price of a token? **Question:** "Why is the measured step above the floor?" Attention kernels below peak bandwidth, sampling, scheduling: named, not profiled. **Deeper:** A model, not a measurement: see experiments/concurrency/RESULTS.md.
-->

---
layout: experiment
heading: "The SLO and the price of a token"
step: consequence
experiment: concurrency
---

<div class="ki-grid ki-cols-2 skip-c2">
<div>

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="baseline-c"
  :columns='["concurrency", "ttft_ms.p95", "output_tps_per_request.p50", "output_tps_per_request.p5"]'
  :headers='["Concurrency", "TTFT p95 (ms)", "Speed p50 (tok/s)", "Speed p5 (tok/s)"]'
  :digits='{ "output_tps_per_request.p50": 1, "output_tps_per_request.p5": 1 }'
/>

</div>
<div>

**Arithmetic, not a measurement.** GPU time at USD 2.49 per hour, per million output tokens:

| Concurrency | Price ÷ (tokens/s × 3,600) × 10⁶ | USD |
| --- | --- | --- |
| 1 | 2.49 ÷ (83.88 × 3,600) | 8.25 |
| 16 | 2.49 ÷ (900.04 × 3,600) | 0.77 |
| 64 | 2.49 ÷ (1,692.20 × 3,600) | 0.41 |

TTFT p95 under 800 ms holds at 8, sits at the limit at 16 and fails clearly at 32. 20 users fall between 16 and 32: expect a miss, then measure it.

</div>
</div>

<Consequence>

Pick the concurrency from the SLO, not from the cost curve.

</Consequence>

<style>
.skip-c2 :deep(.rt tbody tr:nth-child(2)) {
  display: none;
}
</style>

<!--
**Key:** The SLO, not the price, picks the operating point: the cheapest token comes from the highest concurrency, exactly where the user waits longest. **Example:** The speed target of 25 tokens per second holds at every level, even for the slowest five percent of requests at 64. The TTFT p95 target of 800 ms holds at 8 with 416 ms, sits right at the limit at 16 with 821 ms, and clearly misses at 32 with 1,463 ms. A p95 from a few dozen requests is noisy: an independent run on another machine agreed within 1 percent on throughput, but its p95 at 16 differed. Twenty users fall between 16 and 32: expect a miss; options are a second GPU, FP8 weights or a looser SLO. **Transition:** Last: what two simultaneous runs did. **Question:** "Is 20 users measured?" No, it is an inference.
-->

---
layout: default
heading: "The contention round: one server, two benchmarks"
---

<Prediction title="Expected from the sweep (inference, not a result)">

Two runs of 8 clients are 16 clients for the server. Each run should look more like the concurrency-16 row than like its own concurrency-8 row.

</Prediction>

| Compare with your first concurrency-8 row | Expectation |
| --- | --- |
| TTFT p50 | closer to the concurrency-16 row |
| Tokens/s per request | closer to the concurrency-16 row |
| Aggregate tokens/s of one run | below it: the server's throughput is shared |
| GPU utilization | still about 100 %: it says nothing |

<Consequence>

A shared server has no isolation. One user's batch job is another user's TTFT.

</Consequence>

<!--
**Key:** Two benchmarks at once are one workload for the server, so each measures a busier machine than it asked for; production users cause the same effect for each other. **Example:** Ask each group which row of its first sweep its contention numbers resemble. We have no reference measurement of this round, so the slide is an expectation from the sweep and your own numbers decide. If a group sees the concurrency-8 row, ask whether the two runs really overlapped. **Transition:** Next block: how the engine produces this behaviour, continuous batching, using the same data. **Question:** "Can we isolate users?" Not on one server: separate replicas, per-tenant limits or a queue in front; Day 3 returns to scaling and routing. **Deeper:** Each run's aggregate counts only its own tokens over its own duration, so with full overlap each sees roughly half of the server's total.
-->
