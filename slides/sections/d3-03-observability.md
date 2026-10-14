---
layout: section
heading: "Observability: metrics, dashboards, incident investigation"
time: "10:45"
minutes: 60
layer: infrastructure
question: "How do we know the service is healthy, and what do we look at when it is not?"
---

---
layout: default
heading: "Three questions an operator asks"
---

| Question | Signal | Example panel |
| --- | --- | --- |
| Is it up? | health, error rate | finished requests by reason |
| Is it fast enough for the SLO? | TTFT, inter-token latency, percentiles | TTFT p50 and p95 |
| Is it saturated, or wasted? | queue, KV usage, GPU work | waiting requests, KV usage, power |

**Metrics** say that something is wrong. **Logs** say which request. **Traces** say where on the path.

<!--
**Key:** Monitoring an inference service is three questions, alive, fast enough, saturated or idle, and each needs different signals; an average answers none of them well. **Example:** The course SLO is TTFT p95 of 800 ms, which is question two; a queue that stays above zero for minutes is question three. Both can be true while the process is perfectly alive. **Transition:** Here is the stack that produces these signals. **Question:** "Why not just look at nvidia-smi?" It answers the hardware question only, and its utilisation figure is the share of time any kernel ran, not efficiency; we measure that on a later slide. **Deeper:** Percentiles beat means because a user experiences their own request; METRICS section 6 has an illustrative example whose mean latency matches no request.
-->

---
layout: default
heading: "The observability stack"
---

<D14ObservabilityStack />

<!--
**Key:** Two exporters, one scraper, one dashboard: vLLM and a GPU exporter expose metrics, Prometheus pulls them every five seconds, Grafana queries Prometheus, and you reach it through your SSH tunnel. **Example:** Read left to right. Click once: the alert path, Prometheus rules into Alertmanager into a person, dashed because the workshop stack has dashboards and no alert rules. Click again: on the pods the boxes are plain processes started by wsmon, on your own server they are the compose containers. **Transition:** What does vLLM put on that metrics endpoint? **Question:** "Is the GPU exporter the same on both?" The pod exporter reads NVML and publishes the DCGM metric names the dashboard uses, so the dashboard cannot tell which one feeds it. **Deeper:** Profiling fields such as DRAM-active need SYS_ADMIN, which the pods lack; on your own hardware they are the best hardware-side view of decode.
-->

---
layout: default
heading: "What vLLM exposes at /metrics"
---

| Type | Metrics, as Prometheus scrapes them | You ask |
| --- | --- | --- |
| Gauges | `vllm:num_requests_running`, `vllm:num_requests_waiting`, `vllm:kv_cache_usage_perc` | what is true now? |
| Counters | `vllm:prompt_tokens_total`, `vllm:generation_tokens_total`, `vllm:request_success_total`, `vllm:num_preemptions_total`, `vllm:prefix_cache_queries_total`, `vllm:prefix_cache_hits_total` | how fast does it grow? |
| Histograms | `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:request_queue_time_seconds` | what is the distribution? |

<!--
**Key:** Three metric types, three questions: a gauge is a value now, a counter only grows so you take its rate, a histogram holds a distribution so you take a quantile. **Example:** `vllm:kv_cache_usage_perc` is a fraction from 0 to 1, not a percentage; `vllm:request_success_total` carries a finished_reason label with stop, length and abort. The list is a selection: the metrics endpoint carries many more, including per-phase times and request token counts. **Transition:** Raw series are not yet readings; four rules save hours. **Question:** "Is /metrics behind the API key?" No, it is open, which is why the server binds loopback. **Deeper:** MFU and MBU series, `vllm:estimated_flops_per_gpu_total` and the byte counters, appear only when the server starts with the MFU option; our base profile sets it.
-->

---
layout: default
heading: "Reading Prometheus data: four rules"
---

- Counters end in `_total`; take a **rate**.
- Histograms expose `_bucket`; percentiles come from **histogram_quantile**.
- There is **no hit-rate gauge**: divide two counters.
- **Old names** show "no data", not an error.

```text
histogram_quantile(0.95, sum by (le) (rate(vllm:time_to_first_token_seconds_bucket[5m])))
rate(vllm:prefix_cache_hits_total[5m]) / rate(vllm:prefix_cache_queries_total[5m])
```

<!--
**Key:** Four rules decide whether a panel tells the truth: rates for counters, quantiles over buckets, a division for the hit rate, and current names. **Example:** A dashboard copied from an older tutorial that reads `vllm:gpu_cache_usage_perc` shows empty panels on v0.31.0, because the metric is now `vllm:kv_cache_usage_perc`; nothing errors, it is simply blank. The two expressions on the slide are the TTFT p95 and the prefix hit rate. **Transition:** Now the dashboard itself, which is built from these rules. **Question:** "Why does vllm:iteration_tokens_total break rule one?" It is a histogram despite the name, so use its count, sum or bucket series. **Deeper:** Request-phase histograms such as queue and prefill time start at 0.3 s, so on a fast server a quantile of them returns the first bucket whatever the truth is.
-->

---
layout: default
heading: "One dashboard, three rows"
---

| Row | Panels | The question it answers |
| --- | --- | --- |
| What the user feels | request rate, TTFT, inter-token latency, end-to-end latency | Are users waiting, and for what? |
| What the server is doing | running, waiting, tokens per second, KV cache usage, prefix hit rate, preemptions, queue time, prefill vs decode time, finish reasons | Is the scheduler saturated, is memory the limit? |
| What the hardware is doing | GPU utilisation, VRAM, power, estimated MFU, estimated MBU | What resource is busy? |

<div class="small muted">

18 panels. `monitoring/grafana/build_dashboard.py` generates the JSON and `monitoring/grafana/test_dashboard.py` checks every metric name against v0.31.0.

</div>

<!--
**Key:** The dashboard is organised by who asks: the user's row, the scheduler's row and the hardware's row, and a diagnosis reads top to bottom, from symptom to resource. **Example:** Open it through your tunnel now and find the three row headers. Everyone should see the same dashboard, titled KI ohne Cloud: inference, with the last 15 minutes and a five-second refresh. **Transition:** We walk the rows panel by panel and say what a problem looks like on each. **Question:** "Can I change a panel?" Edit the generator script, run it and commit both, because the JSON is generated; the test then checks that every metric name still exists. **Deeper:** The peak TFLOPS and bandwidth used by the MFU and MBU panels are dashboard variables, so you can change them without editing the JSON.
-->

---
layout: default
heading: "Row 1: what the user feels"
---

| Panel | Read it as | Read with care |
| --- | --- | --- |
| Request rate | completed requests per second; flat while load rises means saturation | counts every finish reason |
| TTFT, p50 and p95 | queueing plus prefill plus the first step | server-side: no network, no client |
| Inter-token latency | smoothness of the stream; 1 ÷ ITL is the per-user tokens per second | one sample per streamed event |
| End-to-end latency | arrival to last token, queueing included | bucket floor 0.3 s: coarse on a fast server |

<!--
**Key:** The first row is the user's experience as the server sees it: whether requests complete, how long until the first token, how smooth the stream is and how long the whole answer takes. **Example:** If request rate stays flat while you add clients, the server is saturated; if TTFT p95 climbs while p50 stays calm, a minority of requests wait behind something, which is the pattern the incident exercise will produce. **Transition:** The second row says why, starting with the scheduler. **Question:** "Why do these differ from my benchmark client?" The panels are server-side histograms; the harness measures from the client, including the tunnel, and its percentiles are exact over a run, not windowed estimates. **Deeper:** A p95 over a few seconds with a handful of requests is noisy; read trends, not single points.
-->

---
layout: default
heading: "Row 2: scheduler and memory"
---

| Panel | Read it as | A problem looks like |
| --- | --- | --- |
| Running requests | the batch; capped by `max-num-seqs` and by KV capacity | pinned at the cap |
| Waiting requests | the queue | above zero for minutes |
| KV cache usage | share of cache blocks in use | near 100 % |
| Preemptions | requests evicted and recomputed: a cost, not an error | a rate above zero while KV is full |
| Queue time | wait before first scheduling | rising, but floored at 0.3 s |

<!--
**Key:** Running, waiting, KV usage and preemptions describe the scheduler's decisions: how many requests are in the batch, how many are queued, how full memory is and whether it had to evict work. **Example:** Running pinned at the cap with the queue growing and KV low says admission is the limit; KV near 100 % with preemptions and a queue says memory is the limit. They look alike in the waiting panel and differ everywhere else. **Transition:** Next, the work the server does and how caching changes it. **Question:** "Is a preemption an error?" No: v1 vLLM frees the request's KV blocks, puts it at the front of the queue and recomputes later; it costs time, not correctness. **Deeper:** The legacy warning text still says to raise gpu-memory-utilization or tensor parallelism, or to lower max-num-seqs; the first two add memory, the last reduces demand.
-->

---
layout: default
heading: "Row 2: work done and caching"
---

| Panel | Read it as | Read with care |
| --- | --- | --- |
| Tokens per second | decode tokens are what users read; prompt tokens are work on prompts | two lines, two kinds of work |
| Prefix cache hit rate | share of prompt tokens served from cache | high with shared prompts; also exposes flattered benchmarks |
| Prefill vs decode time | where a running request spends its time | same 0.3 s bucket floor |
| Finished by reason | `stop` model ended, `length` cut at the token limit, `abort` client left | `abort` is a user giving up |

<!--
**Key:** This part of the second row shows what kind of work arrives: prompt tokens against generated tokens, how much prefill the cache saved, and how requests end. **Example:** A burst of long prompts shows as a tall prompt-tokens line with little generation; a rising abort share means clients are giving up before the answer arrives, which is the user-side sign of a queue. **Transition:** The third row is the hardware, and it contains the panel that misleads most. **Question:** "Why is the hit rate near zero in our benchmarks?" The harness puts a random nonce in every prompt on purpose, so the hit rate stays near one percent unless a workload declares a shared prefix. **Deeper:** A benchmark that repeats prompts measures the cache, not the server; the hit-rate panel is the check.
-->

---
layout: default
heading: "Row 3: busy is not efficient"
---

<div class="ki-grid ki-cols-4">
<MetricCard label="GPU utilisation, mean" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="gpu.utilization_pct.mean" unit="%" note="one request at a time" />
<MetricCard label="Requests running, mean" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="server.gauges.num_requests_running.mean" digits="2" note="the batch" />
<MetricCard label="KV cache usage, max" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="server.gauges.kv_cache_usage_perc.max" digits="4" note="fraction of 1" />
<MetricCard label="Power, mean" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="gpu.power_w.mean" unit="W" note="follows real work" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

<Warning title="GPU utilisation is not efficiency">

It is the share of time any kernel ran. VRAM is flat too: vLLM reserves its budget at start.

</Warning>

<!--
**Key:** With one request at a time the card reads almost fully utilised while the batch holds less than one request on average and the cache is nearly empty: busy is not efficient. **Example:** Read the four cards: utilisation near 100 percent, 0.94 requests running, KV usage a third of one percent, power about 362 watts. Day 2 measures how different the work is when the batch is larger. **Transition:** The estimated MFU and MBU panels try to say how hard the silicon works. **Question:** "So which hardware panel do I trust?" Read power, running requests and the MFU and MBU estimates next to utilisation; none is a hardware counter. **Deeper:** VRAM used is flat after start-up because the budget is reserved at launch, so the KV usage panel, not VRAM, shows load.
-->

---
layout: two-col
heading: "Estimated MFU and MBU: relative signals"
ratio: "1:1"
---

**MFU** = FLOP/s achieved ÷ peak FLOP/s.

**MBU** = bytes/s moved ÷ peak bandwidth.

Peaks in the dashboard: **504 TFLOPS** BF16 dense, **1,597 GB/s**. They are variables.

::right::

<Warning title="Estimates, not hardware counters">

- computed from the scheduled work, with `--enable-mfu-metrics`
- 504 is uncertain by several percent for this card
- tied to BF16 and to the averaging window

</Warning>

Compare runs on the same card and window. Do not grade a deployment.

<!--
**Key:** MFU and MBU turn counters into a fraction of a datasheet peak, which makes them good for comparing two runs and poor for grading a single one. **Example:** Decode is usually limited by memory bandwidth, so estimated MBU should rise toward its ceiling long before MFU does; a small batch shows low MFU and a modest MBU. The peaks are variables, so you can overwrite them with your own measured numbers. **Transition:** Metrics tell us the numbers; logs and traces tell us which request. **Question:** "Why is the TFLOPS peak uncertain?" NVIDIA does not publish a dense BF16 peak for the Server Edition; 504 is the Workstation-clock figure and the plausible range runs from about 468 to 504. **Deeper:** The 1,597 GB/s bandwidth is published, so MBU has the firmer denominator.
-->

---
layout: two-col
heading: "Logs and traces, briefly"
ratio: "1:1"
---

### Logs

- a stats line every 10 s: throughput, running, waiting, KV usage, hit rate
- `sudo wsctl logs`, or `./scripts/gpu-status.sh --watch`
- request logging is **off**; switched on at debug level, it logs prompts

::right::

### Traces

- one request across gateway, balancer, replica
- vLLM ships an OpenTelemetry example
- not in the workshop stack

<Consequence>

Log metadata. A prompt in a log is personal data.

</Consequence>

<!--
**Key:** Metrics are aggregates, so to find the one request that went wrong you need logs with request ids, and across several hops you need traces; for inference, logging prompts is a privacy decision, not a default. **Example:** The stats line in the vLLM log carries the same fields as the dashboard every ten seconds, so on a pod you can read the queue without Grafana. **Transition:** Dashboards need someone looking; alerts do not. **Question:** "Should I turn on request logging?" Only with a purpose, an access list and a retention period; log request id, token counts, latency and status instead of text. **Deeper:** Whether a vLLM engine hang shows in the log is not established here; the safe design watches queue depth and latency rather than waiting for a log line.
-->

---
layout: default
heading: "Alerts that matter"
---

| Alert | Signal | Why this one |
| --- | --- | --- |
| Latency SLO | TTFT p95 above target for several minutes | the objective the user feels (course SLO: p95 800 ms) |
| Error rate | failed or aborted requests, gateway 5xx | the availability target |
| Queueing | waiting requests above zero for minutes | arrivals exceed capacity |
| KV pressure | KV usage near full with preemptions | memory is limiting concurrency |
| Idle GPU | running and waiting at zero, power near idle, during expected traffic | an idle card still bills per second |

The workshop stack has dashboards and **no alert rules**.

<!--
**Key:** Page a person on what the user feels, latency and errors, and use queueing, KV pressure and idle as the causes that explain the page, or as early warnings. **Example:** An alert on GPU utilisation would almost never fire usefully, since we just saw a nearly idle batch at full utilisation; waiting requests plus TTFT p95 is the natural alert for the incident we are about to run. **Transition:** Now you diagnose one, from the dashboard alone. **Question:** "What thresholds do I use?" The repository sets none; derive them from the SLO and calibrate on your baseline run, and use durations of minutes so a single burst does not page. **Deeper:** The vLLM example dashboards contain no alerts either, and an engine can hang while the health endpoint stays green, so alert on latency and queue, not only on up.
-->

---
layout: default
heading: "Incident investigation: how it runs"
---

- **1** Open the dashboard through your tunnel.
- **2** The trainer starts a load on your group's server. You do not see it.
- **3** Watch, then fill in the worksheet for your ticket.
- **4** Name the panel that moved first, the resource that is full and one change.

<Terminal title="your laptop, then on the GPU host">

```bash
ssh -p <port> -L 3000:127.0.0.1:3000 <your-user>@<host>
# browser: http://127.0.0.1:3000
./scripts/gpu-status.sh --watch    # on the GPU host
```

</Terminal>

<!--
**Key:** You get no description of the load, only a ticket from a user and the dashboard, which is exactly what an on-call engineer gets. **Example:** Trainer procedure for each ticket: switch the group's server to the right profile with sudo wsctl start, which restarts it for the group and takes one to three minutes, then run ./scripts/benchmark.sh on the pod. No dedicated incident script exists; the tools are the profiles max-seqs-8 and kv-constrained, and the harness options for request rate, concurrency, workload and input length. **Transition:** Here are the three tickets. **Question:** "How long do groups get?" Plan roughly five minutes of watching per ticket; the block length, not a task file, sets the budget. **Deeper:** Dry-run all three on a pod first: no measured result file for these conditions exists yet, so the expected readings in the answer key are hypotheses until you have seen them.
-->

---
layout: default
heading: "Three tickets"
---

<div class="ki-grid ki-cols-3">
<div class="ki-card">

### Ticket A

"Everything is slow right now. Mine and everyone's."

</div>
<div class="ki-card">

### Ticket B

"Some requests take seconds before the first word. Others are fine."

</div>
<div class="ki-card">

### Ticket C

"Answers stall and stutter. Adding more clients made it worse."

</div>
</div>

<Prediction>

Before the load starts: which panel do you expect to move first for each ticket?

</Prediction>

<!--
**Key:** Each ticket is a user's words for one of three different mechanisms: a burst that meets a capped batch, long prompts, and a KV cache that is too small. **Example:** For A run profile max-seqs-8 and open-loop load above capacity, using the request-rate option of ./scripts/benchmark.sh. For B keep the baseline profile and use the rag-long-context workload or a long input-tokens value. For C use the kv-constrained profile, which caps the cache at 4 GiB, and several concurrent long contexts. **Transition:** Each group takes one ticket and the worksheet. **Question:** "Can groups see each other's tickets?" Give each pod one ticket at a time, or rotate; the point is the reasoning, so a shared answer after the attempt is fine. **Deeper:** Open-loop load matters for A: a closed loop backs off when the server slows, which hides the queue (METRICS section 7).
-->

---
layout: default
heading: "Diagnosis worksheet"
---

| Ticket | First panel that moved | Panels that stayed flat | What is full? | One change | Metric that would warn |
| --- | --- | --- | --- | --- | --- |
| A | | | | | |
| B | | | | | |
| C | | | | | |

What is full: batch slots, prefill compute or KV memory?

<!--
**Key:** The worksheet forces the order of a real diagnosis: what moved first, what did not, which resource is full, what changes it, what would have warned you. **Example:** Answer key, an expectation to verify in your dry run. A: running pinned at the cap, waiting and queue time rising, KV low; batch slots are full; raise max-num-seqs or add a replica; alert on waiting and TTFT p95. B: prompt tokens dominate, prefill time and TTFT p95 up, waiting near zero, estimated MFU up; prefill compute is full; limit context, use prefix caching. C: KV near 100 percent, running below any cap, waiting and preemptions above zero; KV memory is full; more cache or shorter contexts; alert on KV with preemptions. **Transition:** Compare with the reading table. **Question:** "A and C both queue; how to tell them apart?" KV usage and preemptions. **Deeper:** None of this is a measured result yet; correct the key after your dry run.
-->

---
layout: default
heading: "Debrief: reading the panels together"
---

| What you see | Likely reading |
| --- | --- |
| Waiting above zero, TTFT and queue time rising, KV usage low | too few sequences allowed, or a burst of prefill work |
| Waiting above zero, KV near 100 %, preemptions above zero | KV pressure: more KV, shorter contexts or fewer sequences; more clients do not help |
| Inter-token latency rising while running requests rise | heavier decode batches, or long contexts adding KV reads |
| Request rate flat while offered load rises | saturation: find which resource |
| GPU utilisation 100 %, few running, estimated MBU low | a small batch: busy but under-used |
| Running and waiting at zero, tokens per second zero, power near idle | idle: no load, or clients gave up |

<div class="small muted">An inference from what each metric measures, not a rule. Check it on your own system.</div>

<!--
**Key:** A reading guide is a list of hypotheses that tell you which panel to check next, not a decision rule; two different causes can raise the same panel. **Example:** Walk the three tickets against the table: A matches the first row, C the second, and B is the new case, where waiting stays low and the prompt-token line and prefill time carry the story. **Transition:** All three were one server under pressure; scaling asks what happens when we add servers, after a measured look at how long a new one takes. **Question:** "What do I do first in a real incident?" Look at user-facing panels, then the scheduler row, then the hardware row, and change one thing at a time. **Deeper:** The Day 2 context-length experiment produces measured evidence for rows two and three; replace these hypotheses with your own measurements when you have them.
-->
