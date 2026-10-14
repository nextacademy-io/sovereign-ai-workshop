---
layout: section
heading: "Continuous batching"
time: "11:45"
minutes: 45
layer: runtime
question: "How does the engine keep the GPU busy when requests arrive at different times and have different lengths?"
---

---
layout: default
heading: "One request at a time wastes the weight read"
---

A decode step reads all 16.38 GB of weights **whatever the number of requests riding along**. Served one at a time, every step moves them for **one** token, and the eighth user waits for seven complete answers.

<div class="ki-grid ki-cols-4">
<MetricCard label="Aggregate, 1 request" source="measured:benchmark/results/reference/concurrency/baseline-c001/c001.json" metric="aggregate_tps" unit="tok/s" digits="1" />
<MetricCard label="Aggregate, 8 requests" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="aggregate_tps" unit="tok/s" digits="1" tone="good" />
<MetricCard label="ITL p50, 1 request" source="measured:benchmark/results/reference/concurrency/baseline-c001/c001.json" metric="itl_ms.p50" unit="ms" digits="1" />
<MetricCard label="ITL p50, 8 requests" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="itl_ms.p50" unit="ms" digits="1" />
</div>

<Provenance source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" />

<!--
**Key:** Your Lab 3 table already contains the argument: the step time barely moves from one request to eight while the tokens per step grow eightfold, so the engine's job is to keep as many requests in each step as the SLO allows. **Example:** Sequential serving means request two does not even start its prefill until request one has produced all 180 tokens, 180 times 11.6 ms, about two seconds; the eighth user waits for seven such answers. Batching shares one weight read, which is the whole gain. **Transition:** The question is how to form the batch; there are three answers. **Question:** "Why not just wait for eight requests and run them together?" That is static or dynamic batching, and it has a different price: see the next slide. **Deeper:** The cards are the concurrency 1 and concurrency 8 runs of the reference sweep from the lab.
-->

---
layout: default
heading: "Three ways to form a batch"
---

| Policy | A new request can start | A finished request frees its slot | What it costs |
| --- | --- | --- | --- |
| Static | when the whole batch is done | when the whole batch is done | everyone waits for the slowest request |
| Dynamic | when the next batch is formed, after waiting for a time limit or a size | when the whole batch is done | extra wait to fill the batch, and still the slowest request |
| Continuous | at the next step, if a slot and KV space are free | at the end of its own step | scheduler work at every step; the KV cache must fit |

<Takeaway>

Continuous batching decides at **every step**, not once per batch.

</Takeaway>

<!--
**Key:** The three policies differ in one thing, the moment at which the batch may change: after the whole batch (static), after a waiting window (dynamic), or at every step (continuous, also called iteration-level scheduling). **Example:** A chat answer of 20 tokens next to one of 500 tokens: under static batching the short request's slot idles for 480 steps, and a newcomer waits for the whole batch. Under continuous batching the slot is refilled at the next step. **Transition:** The next diagram draws exactly this, with four slots and the same requests. **Question:** "Is this the Orca idea?" Yes: iteration-level scheduling from the OSDI 2022 paper is the basis, and the references list has it; static, dynamic and continuous batching is also the framing of chapter 7.2 of the Inference Engineering book. **Deeper:** The table describes the policies in general, not a measurement of vLLM.
-->

---
layout: default
heading: "Same requests, two policies"
---

<D08ContinuousBatching />

<!--
**Key:** With the same four slots and requests, static batching leaves slots idle until the slowest request ends; continuous batching refills a slot in the step after its request finishes, so waiting requests start earlier and no slot idles. **Example:** The top panel: A, B and D finish early and idle until C ends at step 8; E to H wait for step 9. Click once: the same requests under continuous batching, with E taking A's slot at step 4. Click again: E starts at step 4 instead of 9, F at 6, H at 5. The lengths are made up. **Transition:** What does vLLM actually decide at each step? **Question:** "Does a late joiner slow the others?" Slightly: its prefill shares the step; chunked prefill is the lever. **Deeper:** Slot here means one running request; the cap on such requests is max-num-seqs.
-->

---
layout: default
heading: "What the vLLM scheduler decides at every step"
---

<Flow :items='[{ "label": "Waiting queue", "sub": "first come, first served" }, { "label": "Scheduler", "sub": "token budget per step", "layer": "runtime" }, { "label": "Running batch", "sub": "at most max-num-seqs", "layer": "runtime" }, { "label": "One engine step", "sub": "one token per running request" }, { "label": "Finished", "sub": "leave the batch" }]' />

| Limit | Setting | What happens at the limit |
| --- | --- | --- |
| Running requests | `max-num-seqs` | new requests wait in the queue |
| Tokens per step | `max-num-batched-tokens` | decodes first, one token per running request; the rest of the budget goes to prefill chunks |
| KV memory | cache size from the start-up log | requests wait; running ones can be preempted and recomputed |

<!--
**Key:** The scheduler is a loop with three budgets: how many requests may run, how many tokens one step may process, how much KV memory is free; whichever is hit first decides who waits. **Example:** At each step the decodes of all running requests go first, one token each; the rest of the token budget goes to prefill chunks of waiting requests, and a request only runs if there is KV space. Policy is first come, first served by default. Preemption frees a request's cache and recomputes it later: a cost, not an error. **Transition:** One of those budgets is why a long prompt does not freeze everyone else. **Question:** "Where do I see the queue?" In waiting requests, in the harness result and on the dashboard. **Deeper:** Source: docs/RESEARCH.md 3.9. The default max-num-seqs depends on the card and is unverified for this one: quote no number.
-->

---
layout: two-col
heading: "The benchmark is kind to batching"
---

### Our workload

- every request asks for **exactly 180 tokens**
- clients start together
- closed loop: N users who wait

::right::

### Real traffic

- answers end early and **vary in length**
- arrivals are spread out, not in waves
- users leave, requests are cancelled

<Warning title="The easy case">

Static batching pays for the spread of output lengths. Our pinned lengths hide that spread, so what we measure understates the benefit.

</Warning>

<!--
**Key:** The harness pins the output length so that runs compare, which is right for experiments and kind to batching: with equal lengths and a common start even a naive scheme loses little. In production the spread of lengths is where continuous batching earns its keep. **Example:** Every request here is 180 tokens, pinned with ignore_eos and min_tokens. Real answers end earlier and vary; we have not measured that variation, so this is an argument from the mechanism. **Transition:** Now the scheduler lever that matters for long prompts: chunked prefill. **Question:** "So are your numbers wrong?" No, they are right for this workload; they describe batching under uniform requests, so say so in the report. **Deeper:** The first wave also bunches arrivals: at concurrency N, N prompts arrive at the same moment, which inflates TTFT in small runs.
-->

---
layout: two-col
heading: "Chunked prefill: one long prompt shares the steps"
---

A long prompt is **cut into chunks**. Each step has a token budget: the decodes of the running requests go first, and the remaining budget goes to prefill chunks.

<Takeaway>

It trades **prefill interference with decode** (the ITL of running requests) against **TTFT**: a smaller budget favours the first, a larger one the second.

</Takeaway>

::right::

| Token budget per step | vLLM's documented advice |
| --- | --- |
| smaller, for example 2,048 | better ITL |
| larger | better TTFT |
| above 8,192, small models on large GPUs | best throughput |

<Warning title="Documented, not measured here">

We measure the cap on running requests today, not this lever.

</Warning>

<!--
**Key:** Without chunking, one long prompt could occupy whole steps and freeze every running decode; with chunking it shares the per-step budget, so the others slow slightly instead of stalling. **Example:** At concurrency 16, sixteen 1,200-token prompts arrive at once: 19,200 prompt tokens against a per-step budget, so later prompts wait for their chunks, consistent with the five waiting requests seen at that level. The table is the vLLM optimization guide's advice: smaller budgets favour ITL, larger ones TTFT, above 8,192 for throughput. **Transition:** Time to test the lever we can test: the cap on running requests. **Question:** "Is chunked prefill on?" By default for generative models; with it off, the token budget must cover the maximum model length. **Deeper:** That a long prompt then needs several steps to its first token is our reading of the mechanism; the documentation states the advice only.
-->

---
layout: experiment
heading: "Experiment: cap the batch at 8"
step: experiment
experiment: concurrency
---

<ExperimentCard
  name="concurrency"
  variable="--max-num-seqs: the engine default against 8"
  :profiles='["baseline", "max-seqs-8"]'
  workload="1,200 input tokens, 180 output tokens, closed loop, 4 to 32 clients"
  :metrics='["aggregate tokens/s", "TTFT p50", "tokens/s per request", "waiting requests"]'
  hypothesis="Capping the running batch adds queueing: waiting requests appear and time to first token rises."
/>

Same weights, same card, same workload. One server setting differs.

<!--
**Key:** The cleanest test of what the scheduler does is to take away one of its budgets: the profile max-seqs-8 changes nothing except the cap on running requests, which makes queueing visible even on a card this large. **Example:** The baseline profile leaves the cap at the engine default, which the sweep never reached: even at 64 clients up to 64 requests ran at once. The capped profile limits the batch to 8, so at 16 clients eight run and eight wait. In Lab 4, a concurrency group can do the same with a profile override. **Transition:** Before you see the data, you predict. **Question:** "Why 8?" It is a level the lab sweep reaches: at 8 clients nothing changes, above it the cap bites. **Deeper:** The profile description in config/vllm-profiles says it caps the running batch at 8 requests so that queueing is visible even on a large GPU.
-->

---
layout: experiment
heading: "Predict: 16 and 32 clients, cap of 8"
step: prediction
experiment: concurrency
---

<Prediction>

Compared with the default server, what changes when the cap is 8? Answer more, same or less for each cell, and say why.

</Prediction>

| Capped at 8, compared with the default | 16 clients | 32 clients |
| --- | --- | --- |
| Aggregate tokens/s | ? | ? |
| Tokens/s per request | ? | ? |
| TTFT p50 | ? | ? |
| Waiting requests | ? | ? |
| GPU utilization | ? | ? |

<!--
**Key:** Five cells, two loads: a forecast that has to separate what the cap changes, the throughput and the queue, from what it does not, the speed of a running request and the utilization gauge. **Example:** Give two minutes. Common guesses: throughput lower, per-request speed higher because the batch is smaller, TTFT higher, and utilization lower. Listen for the group that says per-request speed stays the same because the step reads the same weights: that is the model that predicts the data. **Transition:** The measurements, first throughput. **Question:** "Doesn't a smaller batch make each request faster?" Only if the step got shorter; with eight in the batch it is the step we measured with eight. **Deeper:** Utilization is the cell most people get wrong in the direction they expect: the gauge reads about 100 percent in both profiles.
-->

---
layout: experiment
heading: "Measured: throughput under the cap"
step: measurement
experiment: concurrency
---

<div class="ki-grid ki-cols-2">
<ResultChart source="measured:benchmark/results/reference/concurrency" match="c016" kind="bar" x="configuration.server_profile" y="aggregate_tps" title="16 clients: aggregate tokens/s" xlabel="server profile" ylabel="tokens/s" />
<ResultChart source="measured:benchmark/results/reference/concurrency" match="c032" kind="bar" x="configuration.server_profile" y="aggregate_tps" title="32 clients: aggregate tokens/s" xlabel="server profile" ylabel="tokens/s" />
</div>

<Observation>

The default server keeps growing with the clients. The capped server stays where eight requests put it.

</Observation>

<!--
**Key:** With the batch capped at eight, throughput stops where eight requests per step put it, while the default server keeps adding requests to the batch and keeps growing. **Example:** At 16 clients the default server delivers 900 tokens per second and the capped one about 553; at 32 clients 1,294 against the same 553, and at 8 clients the two profiles are equal. The two charts have different vertical scales, so read the printed values. **Transition:** The extra clients do not make the server slower. Where did they go? **Question:** "Is the chart fair?" Each bar pair is one run per profile at the same load, one session, no repetition; the point is the pattern, not the second decimal. **Deeper:** In the capped profile the running batch peaked at 8 at both loads, so the throughput limit is the cap, not the GPU.
-->

---
layout: experiment
heading: "Measured: the queue shows in TTFT"
step: measurement
experiment: concurrency
---

<div class="ki-grid ki-cols-2">
<ResultChart source="measured:benchmark/results/reference/concurrency" match="c016" kind="bar" x="configuration.server_profile" y="ttft_ms.p50" title="16 clients: TTFT p50 (ms)" xlabel="server profile" ylabel="ms" />
<ResultChart source="measured:benchmark/results/reference/concurrency" match="c032" kind="bar" x="configuration.server_profile" y="ttft_ms.p50" title="32 clients: TTFT p50 (ms)" xlabel="server profile" ylabel="ms" />
</div>

<Observation>

The queue shows up in the first token: seconds instead of a fraction of a second.

</Observation>

<!--
**Key:** Users who do not fit into the batch wait in the queue, and the wait is added to their time to first token, so the cost of the cap is paid in TTFT, not in the speed of the text. **Example:** At 16 clients the median TTFT is about 3 seconds with the cap against about 0.6 without; at 32 clients about 8 seconds against about 1. Once the first word arrives, the stream runs at the speed of eight users. Read the printed values on the bars. **Transition:** Put the pieces together in one table: speed per request, running and waiting. **Question:** "Why p50 and not p95?" The p50 is the typical wait, with more samples behind it; the p95 values tell the same story. **Deeper:** The default server also queues at high load, but its batch keeps all requests running, so its TTFT grows more slowly.
-->

---
layout: experiment
heading: "Eight run, the rest wait"
step: explanation
experiment: concurrency
---

<div class="ki-grid ki-cols-2 nowrap-first">
<div>

### 16 clients

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="c016"
  :columns='["configuration.server_profile", "output_tps_per_request.p50", "server.gauges.num_requests_running.max", "server.gauges.num_requests_waiting.max", "gpu.utilization_pct.mean"]'
  :headers='["Profile", "Tokens/s each", "Running max", "Waiting max", "GPU util %"]'
  :digits='{ "output_tps_per_request.p50": 1 }'
/>

</div>
<div>

### 32 clients

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="c032"
  :columns='["configuration.server_profile", "output_tps_per_request.p50", "server.gauges.num_requests_running.max", "server.gauges.num_requests_waiting.max", "gpu.utilization_pct.mean"]'
  :headers='["Profile", "Tokens/s each", "Running max", "Waiting max", "GPU util %"]'
  :digits='{ "output_tps_per_request.p50": 1 }'
/>

</div>
</div>

<Takeaway>

The batch is full, the step is as long as before, the extra users wait. Overload becomes queueing, and GPU utilization still reads 100 %.

</Takeaway>

<style>
.nowrap-first :deep(td.first) {
  white-space: nowrap;
}
</style>

<!--
**Key:** The capped server behaves like a server of eight users with a queue in front: the step is the step of eight requests, so each running request keeps its speed, throughput is fixed by the batch, and everything else turns into waiting. **Example:** Capped rows: running peaks at 8 at both loads, waiting at 8 and 24, and the speed per request stays near what we saw at 8 clients in the lab. The default rows show the other cost of a big batch: the speed per request falls, because each step reads more cache. **Transition:** What would you alert on in production? **Question:** "Should I set max-num-seqs below the default?" Only if the SLO needs it: a cap protects running requests and moves the cost into a queue. **Deeper:** The lost throughput bought no speed: ITL is about 12 ms for eight running requests in both profiles.
-->

---
layout: experiment
heading: "Overload becomes queueing"
step: consequence
experiment: concurrency
---

| Signal | What it says |
| --- | --- |
| `vllm:num_requests_waiting` above zero for long, TTFT p95 rising | arrivals exceed capacity: the queue is the symptom |
| `vllm:num_requests_running` at the cap, KV usage low | the cap is the limit, not memory: `max-num-seqs` |
| `vllm:kv_cache_usage_perc` near 100 %, `vllm:num_preemptions_total` rising | memory pressure: more KV, shorter contexts or fewer sequences |
| GPU utilization at 100 % | says nothing: it read 100 % at every level |

<Consequence>

Alert on **waiting requests and TTFT p95**, not on GPU utilization. Choose the cap from the SLO: it protects the speed of running requests and moves the cost to the queue.

</Consequence>

<!--
**Key:** In a closed-loop lab overload is invisible in throughput; in production it appears as a queue, and the queue appears as time to first token. The alert belongs on waiting requests and on TTFT against the SLO, with the KV gauges to tell the causes apart. **Example:** Waiting requests with low KV usage point to the cap or a prefill burst; waiting requests with KV near 100 percent and preemptions point to memory. Both are queueing, and only the second is helped by fewer sequences. Utilization read 100 percent in every run of this block, so it cannot be an alert. **Transition:** After lunch: the KV cache itself, PagedAttention and prefix caching. **Question:** "Should the queue be bounded?" A design decision for Day 3: an unbounded queue turns overload into long waits for everybody. **Deeper:** The reading guide is docs/METRICS.md section 13.
-->
