---
layout: section
module: 14
heading: "KV cache, PagedAttention and prefix caching"
layer: runtime
question: "What does the engine do when the KV cache is the limit, and how do we avoid computing the same prefix twice?"
can:
  - "Explain why the KV cache limits concurrency and what PagedAttention changes"
  - "Read three signals: waiting requests, KV usage and preemptions"
  - "Tell when a shared prefix saves prefill and when it cannot"
---

---
layout: default
heading: "Recompute or reuse: the trade behind this module"
---

| Level | What the engine keeps | What it pays when it cannot |
| --- | --- | --- |
| Inside one request | the keys and values of every earlier token: the KV cache | every new token would reprocess the whole history |
| Across requests | the blocks of an identical prompt prefix: the prefix cache | every request prefills the shared part again |
| Under memory pressure | the blocks of the running requests | a request is preempted: its blocks are freed and its prompt is prefilled again later |

<Takeaway>

Reuse costs VRAM. Recompute costs time. This module measures both sides.

</Takeaway>

<!--
**Key:** The KV cache, the prefix cache and preemption are one idea at three scales: keep what was computed or compute it again, and memory decides which.

**Example:** The decode step already read the cache instead of recomputing the history. Prefix caching extends that to requests that start the same way. Preemption is the opposite case: vLLM V1 only recomputes, there is no swap to host memory, so a preempted request pays a second prefill.

**Transition:** Reuse costs memory, so first: what happens when the pool is full?

**Question:** "Is preemption a failure?" No, a cost: the request goes to the front of the queue and its prompt is processed again; watch the counter instead of fearing it.

**Deeper:** RESEARCH 3.9 records the V1 behavior: recompute only, and the most recently admitted request is the victim.
-->

---
layout: default
heading: "When the pool is full: three outcomes"
---

<Formula :terms='[{ "t": "LONGER CONTEXT", "hot": true }, { "op": "+" }, { "t": "MORE CONCURRENT REQUESTS", "hot": true }, { "op": "=" }, { "t": "MORE KV CACHE" }]' />

The bytes per token are those of the sizing module. What is new is what the engine does at the limit.

| Outcome | When | You see |
| --- | --- | --- |
| Refuses to start | the pool is smaller than one request of `max-model-len` | an error at start; the supervisor rolls back to the previous profile |
| Waits | the whole prompt of a new request does not fit into the free blocks | waiting requests, TTFT grows |
| Preempts | a running request needs one more block and none is free | the preemption counter rises; the request is recomputed |

<!--
**Key:** A full pool does not crash the server. It has three different behaviors depending on when it runs out, and each leaves its own trace.

**Example:** At start-up the engine checks that one request of max-model-len fits. At admission the scheduler checks that the full input length fits into free blocks (scheduler_reserve_full_isl, on by default) and otherwise leaves the request waiting. Only a running request that needs another block during decode, with none free, is preempted.

**Transition:** How are those blocks organized?

**Question:** "Which one do I want in production?" Waiting is the mildest and the most visible, preemption the most wasteful, and a refused start is the cheapest to find.

**Deeper:** The sizing module already did the arithmetic for the refusal: 4.5 GiB for one 32,768-token request.
-->

---
layout: default
heading: "PagedAttention: blocks instead of one long reservation"
---

<D09PagedAttention />

<!--
**Key:** The KV cache is a pool of fixed-size blocks of 16 tokens, handed out as a request grows and taken back when it ends, so memory is never reserved for tokens that do not exist yet and fragmentation stays small.

**Example:** Click 1: with a full-length reservation per request, the unused room inside them and the gaps between them are fragmentation. The first server's log said 12.92 requests of 32,768 tokens; counted in real 1,380-token requests the same pool holds about 300. Click 2: blocks scattered over the pool. Click 3: requests come and go; D takes free blocks wherever they are.

**Transition:** Blocks make the arithmetic simple: we can count them.

**Question:** "Is this the vLLM paper?" Yes, Kwon et al., SOSP 2023; teach the allocation, not the CUDA kernel.

**Deeper:** The left side is a thought experiment, not another engine.
-->

---
layout: experiment
heading: "Experiment: long prompts, small pool"
step: experiment
experiment: context-length
---

<ExperimentCard
  name="context-length"
  variable="prompt length, then the size of the KV pool"
  :profiles='["baseline", "kv-constrained", "kv-constrained-fp8kv"]'
  workload="256 to 28,672 prompt tokens, one request; then 8,192-token prompts at 1 to 16 clients; 128 output tokens"
  :metrics='["TTFT", "ITL", "running and waiting requests", "KV usage", "preemptions"]'
  hypothesis="TTFT grows with the prompt, ITL slowly with the context. A pool too small for the load makes requests queue or be preempted."
/>

`kv-constrained` simulates the memory pressure of a small GPU: a 4 GiB pool is 1,820 blocks, 29,120 tokens. Not its bandwidth, not its compute.

<!--
**Key:** One experiment with two questions: what does a longer prompt cost, and what does the engine do when the pool is too small for the load. The second needs a smaller pool, so we shrink it on purpose.

**Example:** The kv-constrained profile caps the pool at 4 GiB with a kv-cache-memory-bytes setting and lowers max-model-len to 16,384, because 32,768 would not even start. 29,120 tokens is less than one 32k request, so context and concurrency compete for it.

**Transition:** Predict before the data: two small tables.

**Question:** "Why 8,192-token prompts?" Long enough that a few of them fill 29,120 tokens, short enough to finish in seconds.

**Deeper:** One session, no repetitions, output length 128: longer answers would grow each request's cache and make preemption more likely.
-->

---
layout: experiment
heading: "Predict: a long prompt, a small pool"
step: prediction
experiment: context-length
---

<Prediction>

Commit in every cell: a number, or up, flat, down. Compute the second table with blocks.

</Prediction>

<div class="ki-grid ki-cols-2">
<div>

### One request, 1,024 to 28,672 tokens

| | Your call |
| --- | --- |
| TTFT grows by a factor of | below 28, about 28, above 28 |
| Prefill rate (prompt tokens/s) | rises, flat, falls |
| ITL p50 at 28,672 tokens | ? ms |

<span class="muted small">Per step: 16.38 GB of weights plus 147,456 B per context token, at 1,597 GB/s.</span>

</div>
<div>

### 8,192-token prompts, 8 clients

| 4 GiB pool against the full pool | Your call |
| --- | --- |
| Requests running at once | ? |
| TTFT p50, tokens/s per request | ?, ? |
| Aggregate tokens/s | ? |
| Preemptions | ? |
| FP8 KV cache, same 4 GiB: running | ? |

<span class="muted small">4 GiB = 1,820 blocks of 16 tokens. A request is 8,192 + 128 tokens.</span>

</div>
</div>

<!--
**Key:** Both predictions are derivable: the first from "prefill is compute, decode is bytes", the second from block arithmetic. Make the room compute the number of running requests instead of guessing it.

**Example:** 8,320 tokens per request is 520 blocks, and 1,820 divided by 520 is 3.5, so three fit. Ask who expects preemptions, and who expects the small pool to be faster per request; keep both hands up on the shared screen.

**Transition:** Prompt length first.

**Question:** "Can I use the bound from the mechanics module for ITL?" Yes: weights plus the KV bytes of the context, over bandwidth, with the context taken as the prompt plus about half of the output.

**Deeper:** The checkpoint hypothesis was that TTFT grows roughly in proportion to the prompt; this is the test of that sentence.
-->

---
layout: experiment
heading: "Measured: one request, growing prompt"
step: measurement
experiment: context-length
---

<div class="ki-grid ki-cols-2">
<ResultChart source="measured:benchmark/results/reference/context-length" match="baseline-in" x="tokens.prompt_mean" y="ttft_ms.p50" xlabel="prompt tokens" ylabel="TTFT p50 (ms)" />
<ResultTable
  source="measured:benchmark/results/reference/context-length"
  match="baseline-in"
  :columns='["tokens.prompt_mean", "ttft_ms.p50", "itl_ms.p50", "server.gauges.kv_cache_usage_perc.max"]'
  :headers='["Prompt tokens", "TTFT p50 (ms)", "ITL p50 (ms)", "KV usage (fraction)"]'
  :digits='{ "itl_ms.p50": 1, "server.gauges.kv_cache_usage_perc.max": 3 }'
/>
</div>

<Formula :terms='[{ "t": "16.38 GB", "sub": "weights" }, { "op": "+" }, { "t": "context × 147,456 B", "sub": "context = prompt + 64 tokens" }, { "op": "÷" }, { "t": "1,597 GB/s" }, { "op": "=" }, { "t": "10.3 → 12.9 ms", "sub": "floor, 256 → 28,672 tokens", "hot": true }]' />

<!--
**Key:** Prompt length costs TTFT faster than linearly, because prefill is compute and the attention work per token grows with the context, while the decode step grows only by the extra cache bytes.

**Example:** TTFT p50 goes from 60 ms at 1,024 tokens to 2,018 ms at 28,672: 28 times the tokens, about 34 times the wait. The prefill rate peaks near 21,000 tokens per second at 4,096 tokens and falls to 14,200. ITL rises from 11.6 to 14.3 ms, and the formula, with the context as prompt plus 64, stays within 10 to 13 percent of it at every length (RESULTS).

**Transition:** Now shrink the pool.

**Question:** "Why is 256 tokens slow per token?" Fixed costs dominate the 27 ms.

**Deeper:** The floor is arithmetic from the datasheet bandwidth, not a measurement; KV usage here is one request, 6.7 percent at 28,672 tokens.
-->

---
layout: experiment
heading: "Measured: eight clients, three pools"
step: measurement
experiment: context-length
---

<ResultTable
  source="measured:benchmark/results/reference/context-length"
  :match='["baseline-c008-in08192/c008.json", "kv-constrained-c008-in08192/c008.json", "fp8kv-c008-in08192/c008.json"]'
  :labels='["full pool", "4 GiB pool", "4 GiB pool, FP8 KV cache"]'
  label-header="Pool"
  :columns='["server.gauges.num_requests_running.max", "ttft_ms.p50", "output_tps_per_request.p50", "aggregate_tps", "server.counters_delta.preemptions"]'
  :headers='["Running max", "TTFT p50 (ms)", "Tokens/s each", "Aggregate tokens/s", "Preemptions"]'
  :digits='{ "output_tps_per_request.p50": 1 }'
/>

<Observation>

The small pool is faster per request and slower in TTFT and in aggregate. The same 4 GiB with an FP8 KV cache runs more requests at once; the next slide shows how full each pool got.

</Observation>

<!--
**Key:** The surprise: with the small pool every running request is faster and the whole system is slower, because the pool acts as admission control.

**Example:** Eight clients, 8,192-token prompts. Full pool: 8 running, TTFT p50 1.6 s, 34 tokens per second each, 189 aggregate. Small pool: 3 running, 5.1 s, 58 each, 129 aggregate. FP8 KV in the same 4 GiB: 7 running, 1.4 s, 38 each, 189 aggregate, one preemption.

**Transition:** Why did nothing get preempted in the middle row, and how full did each pool get?

**Question:** "Is the full pool's memory a waste?" For this workload yes: it uses 15.6 percent of it, and compute runs out first.

**Deeper:** One session; tail percentiles from 24 requests are noisy, so read the medians.
-->

---
layout: experiment
heading: "Why: it queues, it does not preempt"
step: explanation
experiment: context-length
---

<div class="ki-grid ki-cols-2">
<ResultChart source="measured:benchmark/results/reference/context-length" :match='["baseline-c0", "baseline-in08192", "kv-constrained-c0"]' x="concurrency" y="ttft_ms.p50" by="configuration.server_profile" xlabel="clients, 8,192-token prompts" ylabel="TTFT p50 (ms)" />
<div class="ki-stack">

<Formula :terms='[{ "t": "3 × 520", "sub": "blocks in use" }, { "op": "÷" }, { "t": "1,820", "sub": "blocks in the pool" }, { "op": "=" }, { "t": "0.857", "sub": "KV usage", "hot": true }]' />

<ResultTable
  source="measured:benchmark/results/reference/context-length"
  :match='["baseline-c008-in08192/c008.json", "kv-constrained-c008-in08192/c008.json", "fp8kv-c008-in08192/c008.json"]'
  :labels='["full pool", "4 GiB pool", "4 GiB, FP8 KV"]'
  label-header="Pool"
  :columns='["server.gauges.kv_cache_usage_perc.max", "gpu.memory_used_mib.max"]'
  :headers='["KV usage", "GPU MiB"]'
  :digits='{ "server.gauges.kv_cache_usage_perc.max": 3 }'
/>

</div>
</div>

<Takeaway>

A request is admitted only when its whole prompt fits: three fit, the rest wait, and the three running keep spare blocks for output. No preemption. FP8 KV doubles the tokens in the same bytes.

</Takeaway>

<!--
**Key:** Memory acts as admission control: a request is admitted only if its whole prompt fits into free blocks, so the fourth waits and the running ones never run out of space.

**Example:** An 8,192-token prompt is 512 blocks; three use 1,536 of 1,820, leaving 284: fewer than the 512 a fourth needs, more than the 24 the three outputs add. At the end three requests hold 520 blocks each, 85.7 percent; measured 85.8. Less prefill between decodes means 58 tokens per second each instead of 34, and the queue pays.

**Transition:** What to size and what to watch.

**Question:** "Is a small pool good, then?" For the running requests; it costs TTFT and throughput.

**Deeper:** With FP8 KV seven requests ran, the pool reached 99.6 percent and one was preempted: the only preemption in the experiment.
-->

---
layout: experiment
heading: "Size the pool, read three signals"
step: consequence
experiment: context-length
---

<div class="ki-grid ki-cols-2">
<div>

<Terminal title="first start of kv-constrained: refused">

```text
To serve at least one request with the model's
max seq len (32768), (4.5 GiB KV cache is needed,
which is larger than the available KV cache
memory (4.0 GiB) ... the estimated maximum model
length is 29104
```

</Terminal>

The profile now sets `max-model-len` to 16,384. The refusal is the sizing arithmetic, enforced.

</div>
<div>

| Signal | Reading |
| --- | --- |
| `vllm:num_requests_waiting` above zero, KV usage high | a queue: the pool is the limit |
| `vllm:num_preemptions_total` rising | running requests outgrow the pool |
| waiting requests, KV usage low | not memory: a cap, or prefill |

</div>
</div>

<Consequence>

Memory sizing is a promise about concurrency times context. On the full pool nothing ran out of memory; prefill compute did. Plan for the prompt tokens per second you must prefill.

</Consequence>

<!--
**Key:** Two production rules from one experiment: size the pool for concurrency times context and check that the largest request starts, and read three signals to tell a memory limit from a compute limit.

**Example:** The first kv-constrained profile was written from arithmetic and never started: the 4 GiB pool held less than one request of the default 32,768 context. Every profile is now started once before it is documented. On the full pool the 8,192-token load stopped scaling near 190 to 217 tokens per second with 31 percent of the cache used.

**Transition:** If many requests share their start, we can avoid some of that prefill.

**Question:** "Which gauge first?" Waiting requests, then KV usage and preemptions to say why.

**Deeper:** The small pool simulates memory only; a real 24 GB card would also be slower per step.
-->

---
layout: default
heading: "Prefix caching: what must match"
---

<div class="ki-grid ki-cols-2">
<div>

A new request reuses the longest run of **whole 16-token blocks** from its first token that the cache already holds.

| Must be identical | Why |
| --- | --- |
| every token from the start | a block's hash includes the block before it |
| whole blocks of 16 tokens | a 100-token prefix reuses 96 |
| LoRA adapter, `cache_salt` | they are part of the hash |

</div>
<div class="ki-stack">

<div class="ki-card">

### Helps

A long system prompt or document that many requests share.

</div>
<div class="ki-card">

### Does not help

Prompts that share nothing. A changing token early in the prompt. A pool so small that cached blocks are evicted. Replicas: each has its own cache.

</div>

</div>
</div>

<!--
**Key:** Prefix caching reuses KV blocks across requests, so it needs an identical start and works in whole blocks. It is automatic in V1, which is also how a benchmark gets fooled.

**Example:** The block hash is the previous block's hash plus its 16 tokens plus extras such as the LoRA id and cache_salt. A 2,200-token prompt with 2,000 shared tokens shares 125 whole blocks; a timestamp in the first line ends the match at block one. Where it hurts: not in throughput, the control will show that; it hurts honest measurement, and with replicas, since each holds its own cache, unless routing is cache-aware.

**Transition:** Test it, cache on and off.

**Question:** "Is it on by default?" Yes in V1, although one documentation page still says to enable it.

**Deeper:** cache_salt isolates tenants from each other's entries.
-->

---
layout: experiment
heading: "Experiment: shared prefix, cache on or off"
step: experiment
experiment: prefix-cache
---

<ExperimentCard
  name="prefix-cache"
  variable="prefix caching on against off"
  :profiles='["baseline", "no-prefix-cache"]'
  workload="shared-prefix: 2,200 input tokens, the first 2,000 identical, 150 output tokens; 1 and 8 clients"
  :metrics='["TTFT p50", "aggregate tokens/s", "tokens/s per request", "hit rate"]'
  hypothesis="A long shared prefix is prefilled once. With nothing shared, caching changes nothing."
/>

The control: 2,200 unique tokens with the cache on. Each profile starts fresh, so the cache begins empty.

<!--
**Key:** One variable, one control. The control matters as much as the treatment: it shows that caching costs nothing when there is nothing to share, which separates "the cache helps" from "this run was different".

**Example:** The workload declares a shared prefix on purpose: the first 2,000 of 2,200 tokens are identical in every request, the rest is fresh random text. Profiles baseline (caching is the vLLM default) and no-prefix-cache. Restarting each profile empties the cache, so the first request pays full price.

**Transition:** Predict the factor.

**Question:** "Why 2,000 of 2,200?" It is the best case, chosen to make the effect visible; real system prompts are shorter.

**Deeper:** One session, 32 requests at one client and 64 at eight, so the p95 values are soft.
-->

---
layout: experiment
heading: "Predict: 2,000 shared tokens of 2,200"
step: prediction
experiment: prefix-cache
---

<Prediction>

Cache on against cache off: a factor or a direction in every cell, with a reason.

</Prediction>

| | 1 client | 8 clients |
| --- | --- | --- |
| TTFT p50, on against off | ? | ? |
| Aggregate tokens/s, on against off | ? | ? |
| Tokens/s per request, on against off | ? | ? |
| Hit rate with the cache on | ? | ? |
| Control, nothing shared, cache on: like on or like off? | ? | ? |

<span class="muted small">2,000 of 2,200 tokens are 125 whole blocks of 16.</span>

<!--
**Key:** Four things to separate: what the cache saves (prefill, so TTFT), what it cannot save (decode, so tokens per second per request), what load changes (prefill competes with decode), and what the control must show.

**Example:** Collect a factor for TTFT at one client and at eight. Most groups guess a larger gain at one client, because one request has the GPU to itself; the data go the other way, and the explanation is the point. Ask for the hit rate as a number: 2,000 of 2,200 is 0.91.

**Transition:** The measurement, five runs.

**Question:** "What if the hit rate is below the shared fraction?" Evictions, or a first request that missed: both appear in the counters.

**Deeper:** The cache is empty at the start of each profile, so the first request of every run is a miss.
-->

---
layout: experiment
heading: "Measured: cache on, off, and the control"
step: measurement
experiment: prefix-cache
---

<ResultTable
  source="measured:benchmark/results/reference/prefix-cache"
  :match='["baseline-shared", "baseline-unique", "no-prefix-cache-shared"]'
  :labels='["cache on, shared prefix", "cache on, shared prefix", "cache on, nothing shared (control)", "cache off, shared prefix", "cache off, shared prefix"]'
  label-header="Run"
  :columns='["concurrency", "ttft_ms.p50", "output_tps_per_request.p50", "aggregate_tps", "server.prefix_cache_hit_rate"]'
  :headers='["Clients", "TTFT p50 (ms)", "Tokens/s each", "Aggregate tokens/s", "Hit rate"]'
  :digits='{ "output_tps_per_request.p50": 1, "server.prefix_cache_hit_rate": 3 }'
/>

<Observation>

TTFT falls with the cache on, and the speed of the stream does not move. With nothing shared, the cache behaves like no cache.

</Observation>

<!--
**Key:** The cache saves prefill and nothing else: TTFT and aggregate move, tokens per second per request at one client does not, and with nothing shared the cache is free.

**Example:** At one client TTFT p50 is 33 ms against 111; at eight clients 106 against 588, and aggregate throughput is 620 against 444 tokens per second. The control, 2,200 unique tokens with the cache on, gives 635 ms and 443 tokens per second, the same as cache off. The hit rate 0.909 is 2,000 of 2,200 tokens.

**Transition:** Why is the effect bigger at eight clients, and what nearly went wrong with the control?

**Question:** "Why n/a for the off profile?" The server reports no cache queries when the cache is off, so no rate exists.

**Deeper:** A 2,000-token shared prefix is the best case; a system prompt of a few hundred tokens saves proportionally less.
-->

---
layout: experiment
heading: "Why: only prefill is saved"
step: explanation
experiment: prefix-cache
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Prompt tokens, shared-prefix runs" source="measured:benchmark/results/reference/prefix-cache/counters.json" metric="baseline.vllm:prompt_tokens_total" />
<MetricCard label="Served from the cache, cache on" source="measured:benchmark/results/reference/prefix-cache/counters.json" metric="baseline.vllm:prompt_tokens_cached_total" tone="good" />
<MetricCard label="Served from the cache, cache off" source="measured:benchmark/results/reference/prefix-cache/counters.json" metric="no-prefix-cache.vllm:prompt_tokens_cached_total" />
</div>

<Provenance source="measured:benchmark/results/reference/prefix-cache/counters.json" />

<div class="ki-grid ki-cols-2">
<Takeaway>

Decode is untouched: the cache removes only prefill. At eight clients prefill competes with decoding for one GPU, so saving it helps more.

</Takeaway>
<Warning title="The control that was not a control">

The first "cache off" run switched nothing off: vLLM's config loader drops a `false`. Proof is the start-up line with `'enable_prefix_caching': False`.

</Warning>
</div>

<!--
**Key:** The cache removes only prefill work, so the gain is largest where prefill is a big share and competes with decode, as at eight clients; and a control must be verified, not assumed.

**Example:** Of 233,200 prompt tokens in the shared-prefix runs, 208,016 came from the cache with caching on and none with it off. At one client the saved prefill is 78 ms; at eight clients it also frees the GPU for other requests' decoding, so aggregate throughput rises by about 40 percent.

**Transition:** A control that was not a control leads to a last pitfall: repeating your own benchmark.

**Question:** "How do I verify a flag took effect?" Read the engine's non-default args line in the start-up log.

**Deeper:** wsctl info echoed the flag we meant, not the one the engine received; the profile renderer now writes the explicit negative flag.
-->

---
layout: experiment
heading: "The pitfall: measuring the cache"
step: consequence
experiment: prefix-cache
---

<ResultTable
  source="measured:benchmark/results/reference/prefix-cache"
  match="pitfall"
  :labels='["same prompts again (same seed)", "first run", "new prompts (new seed)"]'
  label-header="Run, 8 clients, 1,200 tokens"
  :columns='["ttft_ms.p50", "aggregate_tps", "server.prefix_cache_hit_rate"]'
  :headers='["TTFT p50 (ms)", "Aggregate tokens/s", "Hit rate"]'
  :digits='{ "server.prefix_cache_hit_rate": 3 }'
/>

<Consequence>

Put the part of the prompt that never changes first and keep it byte-identical. Watch `vllm:prefix_cache_hits_total` over `vllm:prefix_cache_queries_total`. Never publish a benchmark that repeated its prompts (`docs/TROUBLESHOOTING.md` records the first time it happened).

</Consequence>

<!--
**Key:** A repeated benchmark is answered by the cache, so the better number measures the cache; the harness guards against it with a fresh seed per run, if you do not override it.

**Example:** The same 1,200-token workload three times: the first run 359 ms TTFT p50 at hit rate 0, the same prompts again 50 ms at 0.987, new prompts 360 ms. The repeat looks seven times faster at the first token and nothing about the deployment changed.

**Transition:** Next module: quantization, where the check next to the speed-up is the point.

**Question:** "Can I reset the cache between runs?" The harness option needs a developer-mode flag the workshop servers do not set; use a new seed or a restart.

**Deeper:** The first occurrence happened during the pod validation; this experiment reproduced it on purpose.
-->
