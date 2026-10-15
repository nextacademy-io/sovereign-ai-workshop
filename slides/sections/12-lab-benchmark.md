---
layout: section
module: 12
heading: "Lab 3: benchmark the baseline"
layer: runtime
question: "Where does more load stop helping, and what does it cost the user?"
can:
  - "Run a concurrency sweep and keep the results with their provenance"
  - "Locate where aggregate throughput stops growing and latency turns"
  - "Read the user's view and the hardware's view of the same run"
---

---
layout: lab
class: ki-code-sm
heading: "Steps 1 to 4: predict and measure"
task: 03-benchmark
artifact: workshop-artifacts/inference-report.md
---

<div class="ki-grid ki-cols-2">
<div>

**1 Predict** before anything runs: where does aggregate tokens/s **stop growing**, and which resource looks saturated?

| Clients | Aggregate tokens/s | TTFT p95 | Tokens/s per request |
| --- | --- | --- | --- |
| 1 | ? | ? | ? |
| 4 | ? | ? | ? |
| 8 | ? | ? | ? |
| 16 | ? | ? | ? |

</div>
<div>

- **2 Watch.** The *dashboard reader* opens Grafana through the tunnel of the task: GPU utilization, running and waiting requests.
- **3 Measure.** The *driver* runs the sweep, one benchmark at a time per group.
- **4 Record.** The *recorder* fills *Baseline*. The *skeptic* asks which number would change the group's mind.

<Terminal title="step 3, the driver, on the group's GPU host">

```bash
./scripts/benchmark.sh --concurrency 1,4,8,16 \
  --label baseline
```

</Terminal>

</div>
</div>

<!--
**Key:** The prediction is the first step of the task: a guess written down before the sweep turns a table of numbers into a test of our understanding. The roles keep everyone busy while one person drives.

**Example:** Typical guesses: throughput flattens at 8 or 16 users, TTFT stays flat, the GPU is saturated. Keep each group's least certain cell for the debrief. Every run draws a new random seed, so nobody passes --seed.

**Transition:** Two more steps wait after the first sweep: contention and the four questions.

**Question:** "The prefix-cache warning appeared." An earlier run used the same prompts: run again without --seed, and ask the trainer if it stays.

**Deeper:** Failures or timeouts usually mean another benchmark is still running: sudo wsctl status. To save effort, run 1, 8 and 16 only.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 5 and 6: contention and questions"
task: 03-benchmark
artifact: workshop-artifacts/inference-report.md
---

<div class="ki-grid ki-cols-2">
<div>

**5. Contention round.** The roles rotate. Two members run this at the same time, then compare each result with the concurrency-8 row of the first run.

<Terminal title="two members, two terminals, one server">

```bash
./scripts/benchmark.sh --concurrency 8 \
  --label contention
```

</Terminal>

</div>
<div>

**6. Answer the four questions in the report:**

- When does throughput stop scaling?
- When does latency deteriorate?
- What resource looks saturated?
- Which configuration would you deploy, and why?

</div>
</div>

**Done when** four result files exist, *Baseline* is filled in and the four questions have answers. Stuck: `docs/TROUBLESHOOTING.md`, or ask the trainer.

<!--
**Key:** The contention round makes the shared server visible: two people measuring at once are one load for the machine. The four questions are the deliverable; the numbers are the evidence.

**Example:** Agree who runs the first round and who joins for contention. If the first run failed completely, ./scripts/reset.sh lab-03 copies the reference results; continue with those and say so in the report. Numbers more than 20 percent off the reference usually mean someone else is using the server or the run was too short: use --requests 64 per level.

**Transition:** What should the table look like when you are done?

**Question:** "Which configuration, which concurrency?" The one you would deploy for the course SLO; say what would break first above it.

**Deeper:** Further exploration: --slo, an open-loop run with --request-rate, another workload, the cross-check script.
-->

---
layout: experiment
heading: "A good result: the sweep, read three ways"
step: measurement
experiment: concurrency
---

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  :match='["baseline-c001", "baseline-c008", "baseline-c016", "baseline-c032", "baseline-c064"]'
  :columns='["concurrency", "ttft_ms.p95", "output_tps_per_request.p50", "aggregate_tps", "gpu.utilization_pct.mean", "gpu.power_w.mean"]'
  :headers='["Clients (Lab 3: up to 16)", "User: TTFT p95 (ms)", "User: tokens/s per request", "System: aggregate tokens/s", "Hardware: GPU util (%)", "Hardware: power (W)"]'
  :digits='{ "output_tps_per_request.p50": 1 }'
/>

<Takeaway>

Every doubling adds less throughput, and utilization stays at 100 % while power rises. The knee is in the user's numbers: at 16 clients TTFT p95 misses 800 ms by 21 ms. Your numbers differ by a few percent; the shape should match.

</Takeaway>

<!--
**Key:** One sweep answers three questions that must agree with each other: what the user felt, what the server did, what the hardware reported. The reference is for comparison, not the answer.

**Example:** Throughput still grows at 64, so the SLO breaks first. Utilization reads about 100 percent at every level while power and throughput grow; VRAM is flat because vLLM reserves its budget at start-up. Little's law at 8 clients: 8 ÷ 3.06 requests/s = 2.61 s, and the measured median latency is 2,610 ms.

**Transition:** Why can the aggregate grow so much while each request slows only a little?

**Question:** "Where is the knee?" Define it by the SLO or the per-request speed, not the throughput curve: here between 8 and 32.

**Deeper:** One run per level, no confidence intervals. You ran 1, 4, 8 and 16: compare ratios.
-->

---
layout: experiment
heading: "Why batching works, and what it costs"
step: explanation
experiment: concurrency
---

<Formula :terms='[{ "t": "WEIGHTS + N × KV OF ONE REQUEST", "sub": "16.38 GB + N × 1,290 tokens × 147,456 B" }, { "op": "÷" }, { "t": "BANDWIDTH", "sub": "1,597 GB/s" }, { "op": "=" }, { "t": "STEP TIME FLOOR", "hot": true }]' />

<div class="ki-grid ki-cols-2">
<div>

| N | GB read per step | Floor (ms) |
| --- | --- | --- |
| 1 | 16.57 | 10.4 |
| 16 | 19.42 | 12.2 |
| 64 | 28.55 | 17.9 |

</div>
<div>

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  :match='["baseline-c001", "baseline-c016", "baseline-c064"]'
  :columns='["concurrency", "itl_ms.p50"]'
  :headers='["Clients", "Measured ITL p50 (ms)"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>
</div>

<Consequence>

Pick the concurrency from the SLO, not from the cost curve: the cheapest token (arithmetic: USD 8.25 per million at 1 client, 0.41 at 64) comes where users wait longest.

</Consequence>

<!--
**Key:** One decode step reads the weights once plus the KV cache of every running request, so step time barely moves while tokens per step grow: that is why batching works.

**Example:** One request holds 1,290 tokens times 147,456 bytes, 0.19 GB; sixteen add 3.0 GB, so the floor moves from 10.4 to 12.2 ms while tokens per step grow sixteenfold. Price: 2.49 ÷ (83.88 × 3,600) × 10⁶ is USD 8.25 at one client, 0.41 at 64 (1,692.20 tokens/s).

**Transition:** Last: what two simultaneous runs did.

**Question:** "What about the 20 users of the SLO?" They fall between the 16 and 32 rows: expect a TTFT miss, an inference to measure.

**Deeper:** A model, not a measurement: experiments/concurrency/RESULTS.md. The measured step sits 10 to 15 percent above the floor; the gap is named, not profiled.
-->

---
layout: default
heading: "One dry run: two benchmarks, one server"
---

Inference from the sweep: two runs of 8 clients (8 + 8) load the server like 16 clients.

<div class="dry-run">

<ResultTable
  source="measured:benchmark/results/"
  :match='["participant-anna/20261014T151221Z-baseline/c008.json", "participant-anna/20261014T151221Z-baseline/c016.json", "participant-anna/20261014T151513Z-contention-a/c008.json", "participant-anna/20261014T151513Z-contention-b/c008.json"]'
  :labels='["8 alone", "16 alone", "8 + 8 (A)", "8 + 8 (B)"]'
  label-header="Dry run"
  :columns='["ttft_ms.p50", "ttft_ms.p95", "output_tps_per_request.p50", "aggregate_tps", "server.gauges.num_requests_running.mean"]'
  :headers='["TTFT p50 (ms)", "TTFT p95 (ms)", "Tokens/s per request", "Aggregate tokens/s", "Running requests (mean)"]'
  :digits='{ "output_tps_per_request.p50": 1, "aggregate_tps": 0, "server.gauges.num_requests_running.mean": 1 }'
/>

</div>

<Warning title="One dry run, not the answer to expect">

Second pod of the reference GPU type; your numbers decide. A shared server has no isolation: one user's batch job is another user's TTFT.

</Warning>

<style>
.dry-run :deep(td.first) {
  white-space: nowrap;
}
</style>

<!--
**Key:** Two benchmarks at once are one workload for the server; production users do the same to each other. The table is one dry run, not a reference for your numbers.

**Example:** The two contention runs started together on the baseline server. It held 14.8 and 14.6 requests running on average, like the 14.5 of the 16-client row; each run delivered about 447 tokens/s, and 447 + 447 is close to the 893 of 16 clients alone. TTFT p50 differed, 405 and 743 ms.

**Transition:** Next module: how the engine produces this behavior, continuous batching.

**Question:** "Can we isolate users?" Not on one server: separate replicas, per-tenant limits or a queue in front; the scaling module returns to this.

**Deeper:** Each run's aggregate counts only its own tokens over its own duration, so with full overlap each sees about half.
-->
