---
layout: section
heading: "Scaling strategies"
time: "11:45"
minutes: 45
layer: infrastructure
question: "When load grows, what do we add, and what does it cost to add it?"
---

---
layout: default
heading: "Three ways to add GPUs"
---

<TradeoffMatrix :rows='[
  { "name": "Vertical: a bigger or faster GPU", "note": "more VRAM and bandwidth", "effects": { "latency": "up", "throughput": "up", "concurrency": "up", "memory": "up", "cost": "down", "ops": "flat" } },
  { "name": "Horizontal: more replicas", "note": "full copies behind a balancer", "effects": { "latency": "flat", "throughput": "up", "concurrency": "up", "memory": "flat", "cost": "down", "ops": "down" } },
  { "name": "Model parallel: split one model", "note": "tensor parallel across GPUs", "effects": { "latency": "risk", "throughput": "risk", "concurrency": "up", "memory": "up", "cost": "down", "ops": "down" } }
]' />

<Takeaway>

More GPUs do not automatically mean lower latency. Say which metric you want to move.

</Takeaway>

<!--
**Key:** There are three levers and each trades something different: a bigger GPU raises everything and the price, replicas raise throughput and concurrency but leave one request exactly as fast, and splitting a model buys memory with communication. **Example:** Read the latency column: replicas do nothing for a single request, a faster GPU helps because decode is limited by memory bandwidth, and tensor parallelism depends on the link between the GPUs. The matrix shows direction only; sizes come from measurements. **Transition:** The next diagram contrasts the last two. **Question:** "Where is quality?" None of the three changes the model, so quality stays out of the matrix; quantization, from Day 2, is what changes it. **Deeper:** Operations get harder with every step to the right: a balancer, health probes and a rollout plan for replicas; a multi-GPU launch and a failure domain of several cards for tensor parallelism.
-->

---
layout: default
heading: "Replicas or one model split across GPUs"
---

<D12ReplicaScaling />

<!--
**Key:** Replicas are N complete copies, each with its own weights, KV cache and GPU; tensor parallelism is one copy split across GPUs that exchange data in every layer. **Example:** Click once: a balancer in front of replicas, each repeating weights and cache, so memory and price are multiplied. Click again: one server whose layers are halved across two GPUs with an all-reduce between them, which on this card goes over PCIe because there is no NVLink. **Transition:** If you pick replicas, the balancer's decision matters more than it looks. **Question:** "Can I do both?" Yes: tensor parallelism inside a replica for a model that is too large, replicas around it for throughput; each step multiplies the operational surface. **Deeper:** Each data-parallel engine has its own KV cache, so prefix caching depends on where the balancer sends a request.
-->

---
layout: default
heading: "Load balancing is not round robin"
---

| Strategy | Works when | Weak when |
| --- | --- | --- |
| Round robin | requests cost about the same | lengths vary: one replica collects the long ones |
| Least loaded | lengths vary | the signal lags; needs queue depth or the load endpoint of each replica |
| Prefix-aware | many requests share a prompt or document | one replica can become hot; the balancer must track the caches |

<Takeaway>

Each replica has its own KV cache. Where a request lands decides how much prefill it pays.

</Takeaway>

<!--
**Key:** Requests are not equal, and a balancer that ignores prompt length, queue depth and cache contents spreads load evenly by count and unevenly by work. **Example:** Two replicas, round robin, and every second request is a 20,000-token document: one replica prefills all the documents while the other idles. A least-loaded policy reads waiting and running requests per replica instead. **Transition:** Whichever policy you choose, a new replica takes time to appear, so let us look at how long, measured on our setup. **Question:** "Does vLLM give the balancer a load signal?" There is a load endpoint, but it is meaningful only when the server starts with server-load tracking enabled, so scraping the waiting and running gauges is the dependable route. **Deeper:** vLLM's production-stack reference describes prefix-aware routing on Kubernetes; the idea matters more than the product.
-->

---
layout: default
heading: "Start-up time of this setup (measured)"
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Cold start" source="measured:benchmark/results/reference/startup/cold-start.json" metric="log_seconds_to_ready" unit="s" note="no compile or kernel cache yet" />
<MetricCard label="Warm start" source="measured:benchmark/results/reference/startup/warm-start.json" metric="log_seconds_to_ready" unit="s" note="caches from an earlier start" />
<MetricCard label="Restart" source="measured:benchmark/results/reference/startup/restart.json" metric="log_seconds_to_ready" unit="s" note="wsctl restart, caches kept" />
</div>

<Provenance source="measured:benchmark/results/reference/startup/cold-start.json" />

<Warning title="Weights were already on local disk">

A fresh node must also pull the image and fetch the weights. That time is not measured here.

</Warning>

<!--
**Key:** The same engine, model and profile took three different times to become ready, and the difference is cache state, not hardware. **Example:** About three minutes for the first start in a freshly rebuilt container, under a minute for a start after an earlier one in the same container, and about half a minute for a restart. These are seconds until the log says the engine is ready; the wsctl wall time includes process launch and is longer. **Transition:** Where do those seconds go? **Question:** "Is a real fresh node slower?" Almost certainly: add pulling a roughly 9 GB compressed image and downloading 16 GB of weights; the workshop plan measures one fresh pod once and records it in the facilitator notes. **Deeper:** The embedding server held about 7.8 GiB of GPU memory during the warm start; the files' descriptions say exactly what kind of start each one was.
-->

---
layout: default
heading: "Where the seconds go"
---

<ResultTable
  source="measured:benchmark/results/reference/startup"
  :columns='["log_seconds_to_ready", "startup_log.timeline_seconds.engine_core_started", "startup_log.timeline_seconds.weights_loaded", "startup_log.timeline_seconds.kv_cache_sized", "startup_log.graph_capture_seconds", "wsctl_startup_seconds"]'
  :headers='["Ready at (s)", "Engine started at (s)", "Weights loaded at (s)", "KV cache sized at (s)", "Graph capture took (s)", "wsctl wall time (s)"]'
  :digits='{ "wsctl_startup_seconds": 1 }'
/>

Rows, top to bottom: cold start, restart, warm start.

<Consequence>

Compile and kernel caches are part of the deployment state. Lose them with the container and the next start is slow again.

</Consequence>

<!--
**Key:** In the cold start the weights are in memory by second 25 of 176; the rest is compiling, profiling memory and capturing CUDA graphs, and those steps shrink sharply when the caches exist. **Example:** Compare the graph-capture column across the rows: it is the clearest difference. The timestamps are cumulative from process start, and the weights were local in all three starts. Rows are cold start, restart, warm start; the cold-start file has no wsctl wall time. **Transition:** Now ask what this does to autoscaling. **Question:** "Why is the wsctl time longer than the log time?" It runs from process launch until the API answers, so it includes imports and polling that the log's clock does not see. **Deeper:** On the pods the compile cache lives on the container disk and is lost with a pod restart; a volume is the container-side fix.
-->

---
layout: default
heading: "Autoscaling: what to watch, how fast to react"
---

<Formula :terms='[{ "t": "DETECT" }, { "op": "+" }, { "t": "DECIDE" }, { "op": "+" }, { "t": "PROVISION" }, { "op": "+" }, { "t": "START", "hot": true }, { "op": "=" }, { "t": "TIME TO NEW CAPACITY" }]' />

| Signal | Why | Caveat |
| --- | --- | --- |
| Waiting requests | demand above capacity | already late: users are waiting |
| KV cache usage | memory limits concurrency | lags behind a short burst |
| TTFT p95 against the SLO | the user's objective | noisy over short windows |
| GPU utilisation | none | reads busy with one request |

<!--
**Key:** A scaler reacts to a signal and then waits for new capacity, and the start-up time we just measured is the largest term in that wait, so scale on signals that lead the queue and not on the ones that follow it. **Example:** If a burst fills the queue in ten seconds and a replica needs minutes to start, the burst is over before the help arrives; scale on a rising trend or a schedule. **Transition:** The extreme case is scaling to zero. **Question:** "Can GPU utilisation drive the scaler?" It is the wrong signal here: a card serving one request at a time already reads almost fully utilised. **Deeper:** Waiting requests and KV usage are the two gauges the dashboard already shows; a scaler can read the same Prometheus series.
-->

---
layout: default
heading: "Scale to zero: what a cold start costs"
---

The first request after scale-to-zero waits for a whole start. The TTFT objective is 0.8 s.

| Option | What it trades |
| --- | --- |
| Keep one replica warm | pays for an idle GPU, no wait for the first user |
| Scale on a schedule | fine for known peaks, wrong for surprises |
| Queue and answer later | fine for offline pipelines, not for chat |
| Keep weights and caches local | shortens the start, does not remove it |

<!--
**Key:** Scale to zero turns idle cost into first-user latency: the saving is real, and the first request after a quiet period waits for a complete start. **Example:** The measured starts are tens of seconds to minutes against a TTFT objective of 0.8 s, so for an interactive assistant scale to zero breaks the SLO for the first user; for an offline document pipeline it is the right design. **Transition:** What does an idle GPU cost, and what does a useful request cost? **Question:** "Where do I draw the line?" At the user: interactive workloads keep a warm replica, batch workloads can scale to zero; scenario D in Lab 5 is the batch case and scenario C the interactive one. **Deeper:** Providers advertise faster cold starts by snapshotting or pre-pulling images; ask what is measured, with which model and which cache state.
-->

---
layout: default
heading: "Cost per useful workload"
---

<Formula :terms='[{ "t": "USD / 1,000 REQ", "sub": "cost", "hot": true }, { "op": "=" }, { "t": "PRICE/H × 1,000", "sub": "USD per GPU-hour" }, { "op": "÷" }, { "t": "REQ/S × 3,600", "sub": "requests per hour" }]' />

<div class="ki-grid ki-cols-2">
<MetricCard label="Requests per second" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="request_throughput_rps" digits="4" note="one request at a time" />
<MetricCard label="Output tokens per second" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="aggregate_tps" digits="1" note="whole server" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

Price: **2.49 USD** per GPU-hour (one Runpod catalogue read; check the current price). Derived: 2.49 ÷ (0.4652 × 3,600) × 1,000 = **1.49 USD**, with one request at a time. Your Lab 3 sweep gives the cost at the SLO.

<!--
**Key:** Cost per useful workload is the hourly price divided by the useful work done in that hour; the price never changes, so everything depends on how much useful work the card does. **Example:** One request at a time delivers about 0.47 requests per second, which prices 1,000 requests at about 1.49 USD: 2.49 divided by 1,674.7 requests per hour, times 1,000. Useful is yours to define: a request that met the SLO, a ticket, a thousand documents. **Transition:** The same card, busy or idle, costs very different amounts per request. **Question:** "Is 1.49 the number to quote?" No: it is arithmetic on a single-stream run, ignores prefill share and idle time, and uses one catalogue price; use it as a method and redo it with your Lab 3 sweep. **Deeper:** Lab 5 asks you to say that your own prices differ.
-->

---
layout: default
heading: "Idle time multiplies the cost"
---

| GPU busy for | Effective cost of a request |
| --- | --- |
| 100 % of the hour | 1× |
| 50 % | 2× |
| 25 % | 4× |

Effective cost = cost while busy ÷ busy share.

<Warning title="Busy share is not GPU utilisation">

A card serving one request at a time already reads almost fully utilised. Count the time it spends on useful requests.

</Warning>

<!--
**Key:** Billing is per second, so an idle card costs as much as a busy one, and the cost of a request grows with one over the share of the hour spent on useful work. **Example:** Halve the busy share and every request costs twice as much; at a quarter it costs four times. Scale to zero, a warm pool sized to the load and batching are three ways to raise that share, each with its own trade. **Transition:** If cost depends on how well we use each card, when do replicas or tensor parallelism pay? **Question:** "Should I keep the GPU 100 percent busy?" No: a queue at full load breaks the latency SLO; you want the highest busy share that still meets it. **Deeper:** nvidia-smi utilisation is not busy share; the dashboard's power and running-request panels say more.
-->

---
layout: default
heading: "When do replicas beat tensor parallelism?"
---

<Prediction title="Hypothesis, to be checked against your Day 2 results">

For an 8B model that fits on one card, two replicas give more total throughput than tensor parallelism across two cards.

</Prediction>

| Condition | Favours replicas | Favours tensor parallel |
| --- | --- | --- |
| The model fits on one GPU | yes: copies, no per-layer traffic | not needed |
| Many independent requests | throughput scales with copies | one shared batch |
| One request must be faster | no help | maybe, if the link is fast |
| GPUs linked by PCIe, no NVLink | no effect | an all-reduce per layer over PCIe |
| Model larger than one GPU | impossible | the reason it exists |

<!--
**Key:** Replicas win when the model fits on one GPU and the goal is capacity, since copies share no per-layer traffic; tensor parallelism wins when the model does not fit or a fast link makes one request faster. **Example:** The workshop card has no NVLink, so tensor parallelism pays an all-reduce in every layer over PCIe; the tensor-parallel experiment predicts a latency gain smaller than the bandwidth arithmetic suggests. Read your own Day 2 numbers before you accept or reject this. **Transition:** Two more ideas sit at the edge of scaling, both conceptual. **Question:** "Why not always replicate?" Each replica carries full weights and its own cache, so memory is multiplied, and a model larger than one card cannot be replicated. **Deeper:** Whether a two-GPU pod puts the cards on a shared PCIe root is unverified; run nvidia-smi topo -m and keep the output with the result.
-->

---
layout: two-col
heading: "KV-aware routing and disaggregation (skippable)"
---

### KV-aware routing

Send a request to the replica that already holds its prefix.

Kubernetes reference stacks such as production-stack describe it.

::right::

### Prefill/decode disaggregation

Prefill and decode on different GPUs, the KV cache moved between them.

**Experimental** in vLLM v0.31.0; it tunes TTFT and tail ITL, not throughput.

<Consequence>

Both add moving parts. Try them after replicas, caching and measurement.

</Consequence>

<!--
**Key:** Both ideas answer the same observation: prefill and decode, and cached and uncached prefixes, want different treatment, so a smart router or a split pool can serve an SLO that a plain pool cannot. **Example:** KV-aware routing keeps a long shared system prompt on one replica so it is prefilled once; disaggregation lets prefill spikes stop disturbing the inter-token latency of running decodes. **Transition:** Skip this slide if you are behind: curriculum section 7 allows cutting it to this one. Next: what replicas buy beyond throughput. **Question:** "Does disaggregation raise throughput?" The vLLM documentation says it does not; it tunes TTFT and tail ITL independently, and the DistServe paper that introduced the idea defines goodput as the maximum rate that meets an SLO. **Deeper:** Treat both as hypotheses to test with your workload, not as defaults.
-->

---
layout: default
heading: "Replicas buy availability, not only throughput"
---

<Formula :terms='[{ "t": "30 × 24 × 3,600" }, { "op": "×" }, { "t": "0.001" }, { "op": "=" }, { "t": "2,592 s", "sub": "a 99.9 % monthly budget", "hot": true }]' />

- **1** Start the new replica and **wait until it is ready**.
- **2** Shift traffic to it.
- **3** **Drain** the old one: let open streams finish.
- **4** Stop it.

With one replica every restart is downtime. During a rollout you need capacity for one more.

<!--
**Key:** With one replica every restart and crash is downtime, so a 99.9 percent target gives 2,592 seconds a month and the start-up time decides how many restarts you can afford. **Example:** The cold start of 176 seconds is about 6.8 percent of that budget and three of them use about a fifth; a restart of 29 seconds costs about 1.1 percent. A second replica and the rolling sequence keep one copy serving throughout. **Transition:** We have the levers; the last slide is a recipe for choosing how many. **Question:** "What does draining mean for streams?" Stop sending new requests and let open streams finish, up to a limit; cutting them turns every deploy into a user-visible error. **Deeper:** Readiness must mean the model is loaded, which is why the container health check allows a long start period.
-->

---
layout: default
heading: "From SLO to GPU count"
---

<Formula :terms='[{ "t": "20 users", "sub": "course SLO" }, { "op": "×" }, { "t": "25 tokens/s", "sub": "per user" }, { "op": "=" }, { "t": "500 tokens/s", "sub": "needed", "hot": true }]' />

- **1** Tokens per second **needed** at peak.
- **2** Tokens per second **one GPU delivers at the SLO**: your Lab 3 sweep.
- **3** **Replicas** = needed ÷ per GPU, rounded up.
- **4** Add a **spare** for failure and rollout.
- **5** Price × replicas × hours, then ask what is useful.

<!--
**Key:** Start from the SLO and work backwards: tokens per second needed, tokens per second one GPU delivers at that SLO, replicas, then spare capacity, then cost. **Example:** The course SLO of 20 users each reading at 25 tokens per second needs 500 tokens per second from the server. Divide by the per-GPU figure at the SLO from your own sweep, round up and add one; that is the number to defend in Lab 5. **Transition:** Lab 5 comes after lunch and security; keep this recipe next to your design. **Question:** "Which per-GPU number do I use?" The one at the SLO, not the maximum: peak throughput with a queue and a bad TTFT does not meet the objective. **Deeper:** Goodput, the rate of requests that meet every target, is the honest per-GPU figure; the benchmark harness can report it with its SLO option.
-->
