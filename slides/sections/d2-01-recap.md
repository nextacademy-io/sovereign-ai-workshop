---
layout: section
day: 2
heading: "Recap and bottleneck predictions"
time: "09:00"
minutes: 30
layer: all
question: "Where will the bottleneck be when we change something, and which metric will show it?"
---

---
layout: default
heading: "Day 2: make it fast and efficient, against a target"
---

<RhythmBar />

<div class="ki-grid ki-cols-2">
<div>

| The running example | |
| --- | --- |
| Workload | 1,200 tokens in, 180 out |
| Load | 20 concurrent users |
| TTFT | p95 at most 800 ms |
| Speed per user | at least 25 output tokens/s |

</div>
<div>

Every change today is judged against this target, on **one GPU, one model, one engine**.

Each experiment ends with what was traded, not with a verdict.

</div>
</div>

<!--
**Key:** Day 2 is not a tour of tricks. Every block names the metric, the workload, the bottleneck and the price of a change, and judges it against the SLO from yesterday's example. **Example:** Read the four SLO lines aloud and say that one GPU, Qwen3-8B in BF16 and vLLM are held fixed all day, so any difference we see comes from the one thing we change. **Transition:** Before we change anything, we rebuild the picture from memory. **Question:** "Is the SLO realistic?" It is a teaching target between two MLPerf scenarios for an 8B model; your own SLO comes from your users, and Day 2 shows how to test one. **Deeper:** The rhythm bar on the experiment slides shows where we are in the sequence; the prediction step is the one people skip when they are in a hurry.
-->

---
layout: default
heading: "Reconstruct the chain from memory"
---

<Flow :items='[{ "label": "CLIENT", "layer": "application" }, { "label": "API" }, { "label": "vLLM", "layer": "runtime" }, { "label": "MODEL", "layer": "runtime" }, { "label": "GPU", "layer": "runtime" }]' />

Name one thing each link holds or decides, and one number from yesterday.

<div v-click>

| Link | Holds or decides | A number from Day 1 |
| --- | --- | --- |
| CLIENT | the prompt, the stream, the clock for TTFT | 1,200 tokens in, 180 out |
| API | OpenAI-compatible routes, token counts in `usage` | |
| vLLM | scheduler, KV cache, kernels | 16-token KV blocks |
| MODEL | weights, KV bytes per token | 16.38 GB; 147,456 B per token |
| GPU | memory bandwidth, compute | 1,597 GB/s; ridge about 315 FLOP per byte |

</div>

<!--
**Key:** Rebuilding the chain from memory shows which links the room actually owns: if nobody remembers where the KV cache lives or what limits a decode step, the predictions will be guesses. **Example:** Do not click yet. Ask two groups to draw the five boxes and say what sits in each; then click and compare. Listen for the gaps: the scheduler forgotten, the KV cache missing from the picture. **Transition:** The chain tells us where things live; the next slide says what can run out. **Question:** "Why is the client in the chain?" Because TTFT and tokens per second are measured there, including the network; the server's own histograms start later. **Deeper:** The bandwidth and ridge figures are datasheet values and arithmetic from Day 1, not measurements.
-->

---
layout: default
heading: "Four things can run out"
---

| Resource | Runs out when | You would see |
| --- | --- | --- |
| Compute | many prompt tokens are processed in one step (prefill) | TTFT grows |
| Memory bandwidth | every decode step re-reads the weights and the cache | ITL grows, tokens/s per request falls |
| KV capacity | tokens in flight × bytes per token exceed the cache | requests wait, preemptions |
| Queueing | more requests than running slots, or the step's token budget is used up | waiting requests, TTFT grows, aggregate tokens/s flat |

<Takeaway>

Yesterday: prefill waits for the math, decode waits for the memory. Memory capacity and the scheduler add two more limits.

</Takeaway>

<!--
**Key:** There are four candidate bottlenecks and three headline metrics, and the skill of the day is to connect them: which resource is full tells you which metric moves first. **Example:** A request with a 10,000-token prompt and a short answer mostly hits the compute row and shows up in TTFT. A chat with 180 output tokens at 16 users mostly hits the bandwidth and queueing rows and shows up in ITL and in waiting requests. **Transition:** Now you commit: six changes, one table, written down before anything is measured. **Question:** "Where do CPU and network fit?" They can limit a poorly built client or API path, and a cross-check against a second load generator is how we notice; today's workload stresses the GPU and the scheduler. **Deeper:** The sizing block showed that KV capacity is a ceiling on admitted work, not a promise of speed.
-->

---
layout: experiment
heading: "Predict the bottleneck before anything is measured"
step: prediction
---

| Change | Limiting resource | Metric that moves | Direction |
| --- | --- | --- | --- |
| More concurrent users | ? | ? | ? |
| Longer prompts | ? | ? | ? |
| Longer outputs | ? | ? | ? |
| A smaller model | ? | ? | ? |
| FP8 weights | ? | ? | ? |
| A second GPU | ? | ? | ? |

<div class="ki-grid ki-cols-3">
<div class="ki-card">

**Resource:** compute, memory bandwidth, KV capacity, queueing

</div>
<div class="ki-card">

**Metric:** TTFT, ITL, aggregate tokens/s

</div>
<div class="ki-card">

**Direction:** up, down, flat. One resource per row, one sentence of why.

</div>
</div>

<!--
**Key:** The table forces a commitment: one limiting resource, one metric and one direction per change, with a reason, so that later a wrong cell is a finding about our model and not an embarrassment. **Example:** Give the groups about ten minutes in their breakout rooms. Tell them to leave a cell empty rather than write "it depends", and to write the reason in one sentence under the table. **Transition:** Compare the tables, and argue about the rows where groups split. **Question:** "Can we use numbers?" Direction is enough; if a group wants to commit to a number, welcome it, but do not ask for one. **Deeper:** Collect one table per group, because the end-of-day revisit in the demo block opens these predictions again and scores them against what was measured.
-->

---
layout: default
heading: "Compare, then argue about the rows where you disagree"
---

<div class="ki-grid ki-cols-3">
<div class="ki-card">

### A second GPU

Latency, throughput, or both? Which link carries the traffic between the cards?

</div>
<div class="ki-card">

### FP8 weights

Compute or bandwidth? What is stored in fewer bytes, and what stays in BF16?

</div>
<div class="ki-card">

### A smaller model

Faster per token, yes. What does it cost, and which metric hides that cost?

</div>
</div>

<Warning title="Predictions are hypotheses">

Only measured files are results. A wrong cell tells us which part of our model to fix.

</Warning>

<!--
**Key:** The three rows that split most groups are the ones where a plausible argument points in two directions, so they are the best use of the next ten minutes; the point is the reasoning, not who guessed right. **Example:** Second GPU: tensor parallelism splits every layer and pays an all-reduce per layer, over PCIe on this card; replicas add capacity without making one request faster. FP8: weights shrink, but embeddings and the output head stay in BF16. Smaller model: quality is the hidden cost, and no latency metric shows it. **Transition:** Here is which of your predictions we can test today, and how. **Question:** "Who decides who is right?" Nobody in this room: the measurement does, and where we cannot measure we say so. **Deeper:** Keep a list of the disagreements on the shared screen; the end-of-day revisit starts from it.
-->

---
layout: default
heading: "Which predictions we test today, and how"
---

| Change | How it is tested | Where |
| --- | --- | --- |
| More concurrent users | measured: `concurrency` sweep, 1 to 64 | Lab 3, continuous batching |
| Longer prompts | measured: `context-length` | KV cache block |
| Longer outputs | reasoned with the latency formula | not a separate run |
| A smaller model | reasoned with bytes per step: 4.06 GB instead of 16.38 GB | not measured today |
| FP8 weights | measured: `quantization`, with a quality spot check | quantization block |
| A second GPU | a hypothesis: needs a two-GPU machine | parallelism block, trainer demo |

<Warning title="Reasoned is not measured">

Where a row says reasoned or hypothesis, the slides show arithmetic and a plain statement that no measurement exists yet.

</Warning>

<!--
**Key:** Not every prediction becomes a measurement today, and the table is honest about which ones do; a reasoned prediction is still worth writing down, but it keeps the label "reasoned". **Example:** Smaller model: Qwen3-1.7B is 4.06 GB in BF16 in config/models.yaml, so the weights-over-bandwidth floor drops to about 2.5 ms per step, a prediction that nobody has measured here. The second GPU stays a hypothesis because the tensor-parallel experiment needs a two-GPU pod. **Transition:** One sentence to hold on to for the whole day. **Question:** "Why not measure everything?" Time and hardware: each experiment restarts the shared server, and the tensor-parallel one needs a different machine. **Deeper:** Lab 4 lets groups pick one of the measured changes; the end-of-day demo block revisits the predictions collected in this block.
-->

---
layout: statement
---

# Name the metric, the workload, the bottleneck, and what is traded. In that order.

<!--
**Key:** This is the contract for every experiment today: no change is "faster" without a metric, a workload, a bottleneck and a price. **Example:** Not "FP8 is faster", but "FP8 weights read fewer bytes per decode step, which lowers ITL for this workload; the price is memory format complexity and a quality check". Hold the room to this phrasing when they report in Lab 4. **Transition:** The first tool for that is a measurement you can trust, so we start with what to measure. **Question:** "What if two things change at once?" Then we cannot say which one moved the metric; every experiment today changes one variable through one profile. **Deeper:** The predictions collected in this block are revisited at the end of the day, in the demo block, against what was measured.
-->
