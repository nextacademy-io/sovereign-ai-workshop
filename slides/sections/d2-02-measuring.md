---
layout: section
heading: "Measuring inference"
time: "09:30"
minutes: 60
layer: runtime
question: "Which numbers describe what a user feels and what the server does, and how do you know a measurement is trustworthy?"
---

---
layout: default
heading: "Every metric answers a question from one side"
---

| Question | Asked by | Metric |
| --- | --- | --- |
| Did it start quickly? | user | TTFT |
| Does the text stream at reading speed? | user | output tokens/s per request, ITL |
| How long until the whole answer? | user | end-to-end latency |
| How many users fit? | operator | aggregate tokens/s, requests/s, goodput |
| How close to the limit are we? | operator | running and waiting requests, KV-cache usage |
| Are we paying for an idle GPU? | operator | power, VRAM, estimated MFU and MBU |
| What does a token cost? | operator | price per hour ÷ tokens per hour |

<Takeaway>

Most benchmarking mistakes answer one side's question with the other side's metric.

</Takeaway>

<!--
**Key:** The user sits at the end of one stream and feels the wait, the speed and the completeness; the operator sits behind many streams and cares about capacity, headroom and cost, so a good measurement keeps the two views apart and reads them side by side. **Example:** A high aggregate tokens/s is good news for the operator and says nothing about one user's wait; a fast first token for one user says nothing about how many such users fit. **Transition:** Start with the user's side, drawn on one request. **Question:** "Where do we measure, client or server?" Both, and say which: the harness measures at the client including the network, the server histograms start when the server has the request. **Deeper:** The list is docs/METRICS.md section 2; error rate and quality regression belong to both sides and are not on this slide.
-->

---
layout: default
heading: "Where each user metric starts and stops"
---

<D19RequestTimeline />

<!--
**Key:** All user metrics are slices of one timeline with one clock start: TTFT, latency, ITL and TPOT are not four separate measurements. **Example:** Click 1: TTFT is the queue plus prefill up to the first text; latency runs to the last token. Click 2: ITL is the gap between two text chunks. Click 3: TPOT spreads the decode part over its N minus 1 gaps, and one divided by TPOT is the speed a user sees after the first token. **Transition:** Next, how the harness defines each of them, because other tools do not. **Question:** "Why N minus 1 gaps?" The first token ends the wait; only later tokens have a gap before them. **Deeper:** In closed loop the clock starts at the send time, in open loop at the scheduled arrival.
-->

---
layout: default
heading: "How the harness defines them"
---

| Term | Definition in the harness | Result key |
| --- | --- | --- |
| TTFT | `t_first − t_sched`: queueing, prefill, first token | `ttft_ms` |
| ITL | gap between consecutive text chunks, pooled over all requests | `itl_ms` |
| TPOT | `(latency − TTFT) ÷ (N − 1)` per request | `tpot_ms` |
| Output tokens/s per request | `1 ÷ TPOT`: the speed after the first token | `output_tps_per_request` |
| End-to-end latency | `t_end − t_sched` | `latency_ms` |

- `N` comes from the server's `usage` block, not from counting chunks.
- Output length is pinned and thinking is off, so runs compare.

<!--
**Key:** Words like TTFT and ITL are shared across tools but the quantities are not, so we fix them once: every number in this workshop, and every result file, uses these definitions. **Example:** ITL is a chunk gap pooled over all requests; TPOT is per request, so every request weighs the same. They agree only when each chunk holds one token. The pinned output length comes from ignore_eos and min_tokens, which is why every request here emits exactly 180 tokens, unlike real traffic. **Transition:** Now the operator's side: what the whole server delivers. **Question:** "Why is thinking switched off?" A reasoning model changes TTFT, output length and cost; it deserves its own measurement. **Deeper:** Reasoning deltas count as text for TTFT, and failed requests are left out of every latency number and counted in requests_failed.
-->

---
layout: default
heading: "System metrics: what the whole server delivers"
---

| Metric | Definition | Where it is stored |
| --- | --- | --- |
| Aggregate output tokens/s | `Σ N ÷ run duration` | `aggregate_tps` |
| Input and total tokens/s | `Σ prompt tokens ÷ duration`; prompt plus output | `input_tps`, `total_tps` |
| Requests/s | successful requests ÷ run duration | `request_throughput_rps` |
| Running and waiting requests | server gauges, sampled once per second | `server.gauges.num_requests_running`, `server.gauges.num_requests_waiting` |
| KV-cache usage, preemptions | gauge and counter of the server | `server.gauges.kv_cache_usage_perc`, `server.counters_delta.preemptions` |

<Observation>

The first rows come from the client's clock, the last two from the server's `/metrics`. A good report stores both in one result file.

</Observation>

<!--
**Key:** Throughput is the operator's headline, but only the server gauges tell why it looks the way it does: a flat throughput with waiting requests is saturation, a flat throughput with an empty queue is a lack of load. **Example:** Aggregate tokens per second is total output tokens over the whole run including ramp-up and drain, so a short run at high concurrency underestimates the steady state. Prefill tokens show up in input tokens per second and are what users pay for in TTFT. **Transition:** All of these are summaries. A summary needs a distribution, or it lies. **Question:** "Why requests per second and tokens per second?" Requests per second depends on the output length; tokens per second does not, which makes it the better capacity unit. **Deeper:** The server numbers come from a once-per-second scrape of /metrics; the mean and max of each gauge go into the result file.
-->

---
layout: default
heading: "Average latency is not enough"
---

<ResultTable
  source="illustrative"
  :headers='["Statistic", "TTFT", "What it tells you"]'
  :rows='[
    ["mean", "296 ms", "No request had this TTFT."],
    ["p50", "60 ms", "The typical request is fine."],
    ["p90", "60 ms", "Nine in ten are fine."],
    ["p95", "4,000 ms", "The tail is a different experience: an SLO of p95 at most 800 ms fails."],
    ["max", "4,000 ms", ""]
  ]'
/>

Constructed example: 100 requests, **94** with a TTFT of 60 ms and **6** that waited behind a long prompt for 4,000 ms.

<!--
**Key:** An average describes no real request, and a user experiences their own request, so a service level objective is stated on a percentile and checked on a distribution. **Example:** Do the arithmetic aloud: 94 times 60 plus 6 times 4,000, divided by 100, is 296 milliseconds. The mean looks acceptable and p95 fails the 800 ms target. Ask which number the six unlucky users would quote. **Transition:** Percentiles are only as good as the number of samples behind them. **Question:** "Is this example from our server?" No: it is constructed to show the effect, and the badge says so; the real distributions come in the lab. **Deeper:** The harness reports p50, p90, p95, p99, mean, min, max and count, with linear interpolation between the closest ranks; per-request tokens per second also get p1 and p5 because for a bigger-is-better metric the low end is the tail.
-->

---
layout: default
heading: "How many requests make a percentile?"
---

<Formula :terms='[{ "t": "REQUESTS" }, { "op": "×" }, { "t": "1 − p", "sub": "share beyond the percentile" }, { "op": "=" }, { "t": "SAMPLES BEYOND IT", "hot": true }]' />

| Requests in the run | Beyond p95 | Beyond p99 |
| --- | --- | --- |
| 32 | 1.6 | 0.3 |
| 64 | 3.2 | 0.6 |
| 128 | 6.4 | 1.3 |
| 200 | 10 | 2 |
| 1,000 | 50 | 10 |

<Warning title="Rule of thumb: at least 10 samples beyond the percentile you quote">

About 200 requests for p95 and 1,000 for p99. Below that, p95 is a hint and p99 is an anecdote.

</Warning>

<!--
**Key:** A percentile rests on the few samples beyond it, so a p99 from 32 requests is essentially the slowest request, and interpolation hides how thin the data is. **Example:** The default run is eight requests per worker, at least 32, so the Lab 3 sweep at 1, 4, 8 and 16 runs 32, 32, 64 and 128 requests: read p50, treat p95 as a hint, and print the count next to the percentile you quote. **Transition:** One more family of numbers: what the hardware reports. **Question:** "Can I average the p95 of three runs?" No; percentiles neither average nor add. Run once with more requests, or report the spread. **Deeper:** ITL has thousands of samples, but one slow step delays every running request at once, so the effective count is much smaller.
-->

---
layout: default
heading: "Measured: GPU utilization is flat, the work is not"
---

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  match="baseline-c"
  :columns='["concurrency", "gpu.utilization_pct.mean", "gpu.power_w.mean", "gpu.memory_used_mib.max", "aggregate_tps"]'
  :headers='["Concurrency", "GPU util (%)", "Power (W)", "VRAM max (MiB)", "Aggregate tokens/s"]'
/>

<Takeaway>

Utilization says a kernel was running. Power and tokens/s say how much work was done. VRAM is flat because vLLM reserves its budget at start-up.

</Takeaway>

<!--
**Key:** The utilization gauge is the share of time at least one kernel ran, so it reads about 100 percent from one request to sixty-four while throughput grows twentyfold; power follows the work. **Example:** Power over aggregate tokens per second is energy per token: 361.5 W over 83.9 tokens/s is 4.3 J at concurrency 1, 491.5 W over 1,692 is 0.29 J at 64. Read instead: power, running requests, KV usage, tokens/s against the bandwidth bound. **Transition:** So far one tool and one set of definitions; other tools use the same words differently. **Question:** "What about MFU and MBU?" They are estimates from counters, sensitive to the averaging window and the peak you divide by: hints, not grades. **Deeper:** Profiling counters such as DRAM-active need a capability a rented container probably lacks.
-->

---
layout: default
heading: "Tools use the same words for different quantities"
---

| Quantity | This harness | `vllm bench serve` | Other tools |
| --- | --- | --- | --- |
| TPOT | `(latency − TTFT) ÷ (N − 1)` | the same | GuideLLM: includes the first token. NIM calls this quantity ITL |
| ITL | gaps between text chunks, pooled over all requests | the same | AIPerf: per request, `(latency − TTFT) ÷ (OSL − 1)`, which is TPOT here |
| Per-user rate | `1 ÷ TPOT` per request | not reported | AIPerf: `1 ÷ ITL`. NIM: output length ÷ latency |
| Percentiles | p50, p90, p95, p99 always | mean, median, std, p99 unless asked | |

<Warning title="Say which tool">

One tool's ITL is another tool's TPOT. Do not compare numbers across tools until the definitions match.

</Warning>

<!--
**Key:** The vocabulary is shared but the quantities are not, so a number is only meaningful together with the tool and the definition that produced it; this is the commonest benchmarking error in this field. **Example:** AIPerf's ITL is vLLM's TPOT, and GuideLLM's TPOT includes the first token, so two reports can both say TPOT and differ by the whole wait for the first token. Also: vllm bench serve run as in its README prints a p99 but no p50 and no p95. **Transition:** That is why we wrote our own harness and check it against vllm bench serve. **Question:** "Which tool should I use at home?" Any, if you state the definitions and cross-check once with a second tool. **Deeper:** The sources are docs/RESEARCH.md section 10.4 and docs/METRICS.md section 4.
-->

---
layout: two-col
heading: "Our own harness, checked against a second tool"
---

Where it differs from `vllm bench serve`:

- the clock starts at the **scheduled arrival**
- ITL is pooled over **text chunks**
- percentiles and end-to-end latency are **always** reported

<Takeaway>

Run both on the same shape and compare. Throughput and TTFT agree within a few percent; tail percentiles differ more.

</Takeaway>

::right::

<Terminal title="gpu host">

```bash
./benchmark/scripts/crosscheck.sh \
  --concurrency 8 --input-tokens 1000 \
  --output-tokens 200 --requests 64
```

</Terminal>

A gap above 10 % means: a harness bug, a client-side bottleneck, different prompts and a cache pattern, or a definition mismatch.

<!--
**Key:** An independent second load generator is how a home-made harness earns trust: if both tools agree on the same shape, the definitions and arithmetic are right, and a larger gap points to a specific cause. **Example:** The script runs benchmark/run.sh and vllm bench serve against the same server with a fresh seed for each and writes a comparison; it needs OPENAI_API_KEY because vllm bench serve has no key flag. Throughput and TTFT agree within a few percent; tails differ most. **Transition:** Next, how the load is generated, because that decides what queueing you can see. **Question:** "Why trust the harness?" Not on faith: it has tests against a fake server with known timing, and this cross-check. **Deeper:** The comparison flags pairs that differ by more than 10 percent, tail percentiles at three times that.
-->

---
layout: default
heading: "Closed loop and open loop answer different questions"
---

| | Closed loop | Open loop |
| --- | --- | --- |
| Harness flag | `--concurrency N` | `--request-rate R`, Poisson arrivals |
| What is fixed | N users, each waits for the answer | R arrivals per second, whatever the server does |
| Question | What happens with N users who wait? | What happens when R requests per second arrive? |
| Under overload | load backs off with the server: queueing hides | queue grows, latency climbs: queueing shows |
| Use it for | interactive users, finding the knee | capacity planning, SLO checks |

<Warning title="Report which one you ran">

The result file records it as `load_mode`.

</Warning>

<!--
**Key:** The two loops are two different questions, and a closed loop cannot overload a server: when the server slows down the clients send less, so the queue never exceeds the number of users. **Example:** Lab 3 is closed loop: sixteen clients put at most sixteen requests into the system. An open loop at five requests per second keeps sending five per second even when the server cannot keep up, and the waiting requests pile up. **Transition:** The reason this matters has a name: coordinated omission. **Question:** "Which for an SLO check?" Open loop at the expected rate: it shows what real arrivals do to the tail. **Deeper:** In open loop the harness measures from the scheduled arrival; --max-inflight caps requests and makes the run partly closed loop again.
-->

---
layout: default
heading: "Coordinated omission: the stall that is not recorded"
---

<ResultTable
  source="illustrative"
  :headers='["Latency measured from", "Requests affected by a 10 s stall", "What the percentiles see"]'
  :rows='[
    ["the send time of a client that waits for each answer", "1", "one slow sample"],
    ["the scheduled arrival, 5 requests per second", "50", "fifty requests, waiting between 0.2 s and 10 s"]
  ]'
/>

Constructed example: the server stalls for 10 s while requests were *meant* to arrive at 5 per second.

<Takeaway>

A client that waits stops sampling exactly when the server stalls. Measure from the scheduled arrival.

</Takeaway>

<!--
**Key:** A client that waits for each answer also stops sampling during a stall, so the stall appears as one slow request instead of every request that would have arrived meanwhile, and percentiles look far better than reality. **Example:** Five requests per second for ten seconds is 50 arrivals during the stall. The waiting client records one 10-second sample; measured from the scheduled arrival, 50 requests wait from 10 down to 0.2 seconds. This is Gil Tene's coordinated omission; the harness avoids it in open loop. **Transition:** With honest percentiles we can state a target and count the requests that met it. **Question:** "Does closed loop suffer from it?" By design: it never offers more than N requests, so say so next to the numbers. **Deeper:** Keep to the mechanism: the talk itself was not reviewed in the research.
-->

---
layout: default
heading: "The course SLO, and what it implies"
---

| Objective | Target | Checked with |
| --- | --- | --- |
| Time to first token | p95 at most 800 ms | `ttft_ms.p95` |
| Speed per user | at least 25 output tokens/s per request, a TPOT of at most 40 ms | `output_tps_per_request` |

Workload: 1,200 tokens in, 180 out, **20 concurrent users**.

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Latency ceiling:** 0.8 s + 180 ÷ 25 = 8.0 s for a request that just meets both targets.

</div>
<div class="ki-card">

**Aggregate rate:** 20 users × 25 tokens/s = 500 tokens/s, if all stream at once.

</div>
</div>

<!--
**Key:** An SLO turns "fast" into a test: two numbers per request, and arithmetic that says what the server must deliver before we measure anything. **Example:** A request that just meets both targets waits 0.8 seconds and decodes 180 tokens at 25 per second, 7.2 seconds, so 8.0 in total. Twenty users all streaming need 500 tokens per second. The harness checks both targets per request, stricter than a p95 alone: say which form you checked. **Transition:** What does it mean to count the requests that met it? **Question:** "And availability and quality?" The full SLO adds 99.9 percent availability and at most 2 percent quality regression; today's labs cover latency and speed, the quantization block a quality spot check. **Deeper:** The course SLO sits between two MLPerf server scenarios for an 8B model.
-->

---
layout: default
heading: "Goodput: requests that met every target"
---

<div class="ki-grid ki-cols-2">
<div>

<ResultTable
  source="illustrative"
  :headers='["Outcome of 21 requests in 10 s", "Requests"]'
  :rows='[
    ["met both targets", "17"],
    ["TTFT above 800 ms, speed fine", "2"],
    ["speed below 25 tokens/s, TTFT fine", "1"],
    ["failed (HTTP error)", "1"]
  ]'
/>

</div>
<div>

| Reported | Arithmetic |
| --- | --- |
| Request throughput | 20 ÷ 10 s = 2.0 requests/s |
| SLO attainment | 17 ÷ 21 = 0.81 |
| Goodput | 17 ÷ 10 s = 1.7 requests/s |

</div>
</div>

<Observation>

2 of the 20 successful requests (10 %) exceed 800 ms: TTFT p95 fails, yet 81 % were fully good. Two different questions.

</Observation>

<!--
**Key:** Goodput counts only requests that met every stated target, which separates "the server is busy" from "the server serves users well"; it is stated at one load, and a capacity number needs a sweep. **Example:** Constructed run: 21 requests, 17 good. Throughput ignores the failed one; attainment divides by all 21; goodput is 17 over ten seconds. The percentile form fails because 10 percent of the successful requests exceed 800 ms, more than the 5 percent a p95 allows. **Transition:** A last trap before we run anything: measuring the cache instead of the server. **Question:** "Is this DistServe's goodput?" Not quite: DistServe means the maximum rate that keeps a stated share of requests within the SLO, which needs a sweep. **Deeper:** Repeat at several loads and take the highest whose attainment stays at your target, for example 95 percent.
-->

---
layout: default
heading: "The prefix-cache pitfall: measuring the cache"
---

<div class="ki-grid ki-cols-2">
<div>

vLLM reuses the KV blocks of prompts it has seen when a new prompt starts with the same tokens. A repeated prompt needs almost no prefill, so **TTFT collapses and throughput rises**.

The benchmark measured the cache, not the server.

</div>
<div>

| Guard in the harness | Prevents |
| --- | --- |
| random seed per run, stored as `workload.seed` | the same command sending the same prompts |
| a different seed per level of a sweep | one level warming the next |
| a random nonce line in every prompt | accidental sharing |
| a warning when the cache hit rate is high | silent flattery |

</div>
</div>

<Warning title="In Lab 3 do not pass --seed">

`--seed` repeats a run on purpose. The hit rate is stored in `server.prefix_cache_hit_rate`.

</Warning>

<!--
**Key:** The prefix cache is a feature in production and a trap in a benchmark: with identical prompts the second run is answered mostly from the cache, TTFT collapses, and you have measured the cache. **Example:** The same command run twice on the pod gave a much better second result, and the server's hit rate explained it. The harness answers with a fresh random seed per invocation, a nonce line per prompt and a warning when the hit rate is high and no shared prefix is declared. **Transition:** Now the harness itself: the command and the options that matter. **Question:** "When is sharing the point?" The prefix-cache experiment declares a shared prefix on purpose and compares cache on and off. **Deeper:** With --prompts-file prompts are cycled, so a short file repeats them; read the stored hit rate before you believe the warning.
-->

---
layout: two-col
heading: "The harness: one command, one directory per run"
---

<Terminal title="gpu host">

```bash
./scripts/benchmark.sh \
  --concurrency 1,4,8,16 --label baseline
```

</Terminal>

Writes `benchmark/results/mine/<time>-baseline/`: one `cNNN.json` per level and a `summary.md`. Each file carries hardware, model revision, engine version, server arguments and date.

::right::

| Option | Meaning |
| --- | --- |
| `--concurrency 1,4,8,16` | closed loop; a list is a sweep |
| `--request-rate 5` | open loop, Poisson arrivals |
| `--requests N` | requests per run (default: 8 per worker, at least 32) |
| `--slo ttft_ms=800,output_tps=25` | share that met the targets, goodput |
| `--seed N` | the same prompts again, on purpose |

<!--
**Key:** The harness wraps everything we just discussed into one command with defaults for our workload, and every result file carries its own provenance, because a number without hardware, model revision, engine version, server arguments and date is an anecdote. **Example:** scripts/benchmark.sh fills in the endpoint, the model and the key from your environment and defaults to the workshop-baseline workload of 1,200 input and 180 output tokens. One file per concurrency level plus summary.md, which holds the same table you will paste into the report. **Transition:** Here is what one run looks like when we read it with three lenses. **Question:** "Can I point it at another server?" Yes: benchmark/run.sh takes any OpenAI-compatible endpoint; scripts/benchmark.sh is the workshop wrapper. **Deeper:** Small runs inflate TTFT because the first wave arrives at once; raise --requests for the run you quote.
-->

---
layout: default
heading: "One measured run, three lenses (concurrency 8)"
---

<div class="ki-grid ki-cols-3">
<div>

### User

<Benchmark title="Benchmark run" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" />

<Provenance source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" />

</div>
<div class="ki-stack">

### System

<MetricCard label="Requests per second" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="request_throughput_rps" digits="2" />
<MetricCard label="Latency p50" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="latency_ms.p50" unit="ms" />
<MetricCard label="Waiting requests, max" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="server.gauges.num_requests_waiting.max" />

</div>
<div class="ki-stack">

### Hardware

<MetricCard label="GPU utilization, mean" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="gpu.utilization_pct.mean" unit="%" />
<MetricCard label="Power, mean" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="gpu.power_w.mean" unit="W" />
<MetricCard label="VRAM in use, max" source="measured:benchmark/results/reference/concurrency/baseline-c008/c008.json" metric="gpu.memory_used_mib.max" unit="MiB" />

</div>
</div>

<!--
**Key:** One result file answers three questions: what the user felt, what the server did, what the hardware reported; read them together, and the numbers must agree with each other. **Example:** Little's law as a sanity check: eight users divided by 3.06 requests per second is 2.61 seconds, and the measured median latency is 2,610 milliseconds. If they disagree, the run or the definitions are wrong. Nothing waits at this level, utilization reads 100 percent, and power is the number that moves with work. **Transition:** One last slide before the lab: the checklist for every number. **Question:** "Where do the system numbers come from?" The harness scrapes /metrics once per second and stores the mean and max next to its own client-side numbers. **Deeper:** The result file also stores the seed, the hit rate and the request count: look at them first.
-->

---
layout: default
heading: "Before you trust a number"
---

<div class="ki-grid ki-cols-2">
<div>

- Which **tool**, and which definition of TTFT, TPOT, ITL?
- How many **requests**, warm-up excluded, with the count next to the percentile?
- **Closed or open** loop, at what concurrency or rate?
- A **fresh seed**, and what was the prefix-cache hit rate?

</div>
<div>

- Did any request **fail**, and were failures counted?
- What were the **SM clock and power**?
- Is the result stored with its **provenance**?
- Does it respect the **bandwidth bound** and Little's law, and was **quality** checked?

</div>
</div>

<!--
**Key:** Each question guards against an error documented in docs/METRICS.md, so the checklist is not decoration: apply it to every number before it goes into a decision, and especially to the ones that look good. **Example:** A great TTFT with a high cache hit rate is flattery; a great p99 from 32 requests is the slowest request; a great throughput with failed requests left out is a partial answer. Ask the room to pick the question they would have forgotten. **Transition:** Lab 3: predict first, then run the sweep and read it with these questions. **Question:** "Do I have to check all nine?" For a number that goes into a decision, yes; for a first look, the first four. **Deeper:** The full list is docs/METRICS.md section 15; the hardware part depends on the pod, because clocks and power limits cannot be set on a rented container.
-->
