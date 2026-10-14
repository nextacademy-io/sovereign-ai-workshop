---
layout: section
heading: "Inference mechanics: prefill, decode, latency"
time: "15:30"
minutes: 45
layer: runtime
question: "Where does the time of one request go, and what limits each part?"
---

---
layout: default
heading: "One request, two phases"
---

<Flow :items='[{ "label": "Prompt", "sub": "1,200 tokens" }, { "label": "Prefill", "sub": "one parallel pass", "layer": "runtime" }, { "label": "First token", "sub": "end of prefill" }, { "label": "Decode loop", "sub": "one token per step", "layer": "runtime" }, { "label": "Last token", "sub": "180 tokens in all" }]' />

The running example of this workshop: **1,200 tokens in, 180 tokens out**.

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Prefill** reads the prompt. Its cost grows with the prompt length and shows up as **TTFT**.

</div>
<div class="ki-card">

**Decode** writes the answer. Its cost grows with the output length and shows up as **ITL** and tokens per second.

</div>
</div>

<!--
**Key:** A request is not one computation but two: a single pass that reads the whole prompt and produces the first token, then a loop that produces the remaining tokens one at a time. **Example:** The workload we use throughout is 1,200 input tokens and 180 output tokens, so one pass is followed by 179 loop iterations. When a chat answer streams word by word, that is the decode loop made visible. **Transition:** Let us look at what each phase does to the model and the KV cache. **Question:** "Is the first token produced by prefill or by decode?" The pass over the prompt yields the next-token distribution at the last prompt position, so the first output token comes out of prefill; every later token needs one more step. **Deeper:** Reasoning models add many decode steps of thinking before the visible answer, changing TTFT and cost but not the mechanics.
-->

---
layout: default
heading: "Prefill: one big pass. Decode: one token at a time."
---

<D03PrefillDecode />

<!--
**Key:** Prefill pushes all prompt tokens through the model in parallel and leaves their keys and values in the cache; decode runs once per output token, reading all the weights and the whole cache each step. **Example:** Click 1: the 1,200 prompt tokens enter one pass, and the weights are read once for all of them. Click 2: each decode step takes one token and emits one; the new token is the next input. Click 3: TTFT spans the wait and prefill, ITL is one step. **Transition:** Let us define the metrics a user feels. **Question:** "Can decode steps run in parallel for one request?" No: token n+1 needs token n; parallelism comes from other requests or from speculative decoding, which we only demo. **Deeper:** The cache prefill fills is the KV cache of the sizing block; each decode step appends one entry per layer.
-->

---
layout: default
heading: "Four numbers a user can feel"
---

| Metric | What it measures | Phase |
| --- | --- | --- |
| TTFT | request clock to the first streamed text: queueing and prefill, ending with the first token | prefill |
| ITL | gap between two consecutive streamed chunks of text | decode |
| Output tokens per second per request | 1 ÷ TPOT: the speed after the first token | decode |
| End-to-end latency | request clock to the end of the stream | both |

<Formula :terms='[{ "t": "LATENCY" }, { "op": "=" }, { "t": "TTFT" }, { "op": "+" }, { "t": "(N − 1) × TPOT", "sub": "179 decode gaps for N = 180", "hot": true }]' />

<!--
**Key:** TTFT belongs to prefill, ITL and tokens per second belong to decode, and end-to-end latency is the sum, so a long answer is dominated by decode and a long prompt with a short answer by prefill. **Example:** For 180 output tokens there are 179 decode gaps, so a few milliseconds of inter-token latency matter more to total time than the first-token wait. Definitions: docs/METRICS.md section 3. **Transition:** Seeing the numbers on a real stream is quicker than defining them: one request with its timestamps. **Question:** "ITL or TPOT?" Tools disagree: here TPOT is (latency minus TTFT) divided by N minus 1 per request, ITL is a pooled chunk gap, and some tools swap the names. Always say which tool you mean. **Deeper:** If the server groups tokens into one streamed event, chunk gaps no longer equal token gaps; TPOT stays correct because it uses the server's token count.
-->

---
layout: code
heading: "One streamed request, with its timestamps"
file: apps/inference-client/chat.py
---

```bash
python3 apps/inference-client/chat.py "Explain batching in one paragraph."
```

```text
prompt_tokens=<n>  ttft=<ms> ms  completion_tokens=<n>  decode=<tokens/s> tok/s  total=<s> s
```

| Field of the last line | Metric |
| --- | --- |
| `ttft` | TTFT, measured at the client from the moment of sending |
| `decode` | tokens per second after the first token, about 1 ÷ TPOT |
| `total` | end-to-end latency |

<!--
**Key:** The client script prints the whole chain on one line, so everyone can read TTFT, decode speed and total time of a request they just watched stream. **Example:** Trainer: run the command once on the shared server, let the text stream, then read the last line aloud field by field. Ask the room how long they expect the same request to take with a prompt ten times longer; keep the answers for the lab. **Transition:** Why does the first number behave so differently from the second? The answer sits in the arithmetic of each phase. **Question:** "Why does ttft here differ from the server's TTFT?" The script measures at the client, including the network and the SSH tunnel if there is one; server histograms start when the server has the request. **Deeper:** The line goes to standard error, so redirecting output to a file leaves it on screen.
-->

---
layout: default
heading: "Why the two phases limit differently"
---

<Formula :terms='[{ "t": "FLOP PER BYTE", "hot": true }, { "op": "≈" }, { "t": "TOKENS PER WEIGHT READ", "sub": "BF16: 2 FLOP per weight per token ÷ 2 bytes per weight" }]' />

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Prefill**: 1,200 tokens share one read of the weights. About **1,200 FLOP per byte**, above the ridge of about 315: **compute-bound**.

</div>
<div class="ki-card">

**Decode**: one token per request per step. About **1 FLOP per byte**, far below the ridge: **bandwidth-bound**.

</div>
</div>

<!--
**Key:** The intensity of a pass over the weights is roughly the number of tokens sharing one read: each weight does two FLOP per token and costs two bytes in BF16. **Example:** Prefill: 1,200 tokens give about 1,200 FLOP per byte, above 315. Decode with one request: one token per read, about 1, so the weights are fetched for almost no arithmetic. Batching raises decode's intensity: 64 requests in a step give about 64. **Transition:** That is a hypothesis built on peak numbers, so let us test the decode half with a single request. **Question:** "What about attention?" Attention reads the KV cache, which is extra bytes per step for each request and with almost no data reuse; at short context it is small next to the weights. **Deeper:** The rule ignores activations and the cache; it is a first-order argument, and the measurement shows how close it gets.
-->

---
layout: experiment
heading: "The experiment: one request at a time"
step: experiment
experiment: baseline
---

<ExperimentCard
  name="baseline"
  variable="none: default engine settings, one request at a time"
  :profiles='["baseline"]'
  workload="1,200 input tokens, 180 output tokens, concurrency 1"
  :metrics='["ITL", "TTFT"]'
  hypothesis="A single request decodes at a speed close to the memory-bandwidth bound: bytes of weights divided by bandwidth."
/>

Closed loop, one request after the other: no queueing, no sharing of the weight read.

<!--
**Key:** The cleanest test of the decode argument is a single request with nothing else on the server, because then each step reads the weights for exactly one token. **Example:** The profile is the baseline from the start-up demo, the workload is our standard 1,200 in and 180 out, and the harness sends requests one after the other, so inter-token latency is the length of one decode step. **Transition:** Before we look at the number, you predict it. **Question:** "Why a closed loop?" Because with only one request in flight the arrival pattern cannot hide or add waiting time; concurrency comes on Day 2. **Deeper:** The harness defines TTFT and ITL as in METRICS.md and cross-checks against vllm bench serve; the single-stream result file records hardware, model revision, engine version and server arguments next to the numbers.
-->

---
layout: experiment
heading: "Predict the length of one decode step"
step: prediction
experiment: baseline
---

<Formula :terms='[{ "t": "WEIGHTS", "sub": "16.38 GB (BF16 checkpoint)" }, { "op": "÷" }, { "t": "BANDWIDTH", "sub": "1,597 GB/s" }, { "op": "=" }, { "t": "? ms", "sub": "one decode step", "hot": true }]' />

<Prediction>

Write down two things: the time of one step, and whether the measured inter-token latency will be **below, near or above** it. Give a reason.

</Prediction>

Inputs: `weights_gb` in `config/models.yaml` and the datasheet bandwidth from the GPU block.

<!--
**Key:** The point is to commit to a number and a direction before the server answers, and to be able to say what a result on the wrong side would mean. **Example:** Give the room a minute. The arithmetic gives about 10 milliseconds, or 97 tokens per second as a ceiling for one request. Most people say "near" or "a bit above"; the interesting person is the one who says "below" and has to explain which input would be wrong. **Transition:** Now the server's answer. **Question:** "Should I include the KV cache?" You may; at 1,300 tokens of context it adds 147,456 bytes times 1,300, about 0.19 GB, so only 0.1 millisecond. **Deeper:** A measurement below the bound is a bug in the inputs, for example quantized weights or the Workstation card's bandwidth of 1,792 GB/s instead of 1,597.
-->

---
layout: experiment
heading: "Measured: one request at a time"
step: measurement
experiment: baseline
---

<Formula :terms='[{ "t": "16.38 GB" }, { "op": "÷" }, { "t": "1,597 GB/s" }, { "op": "=" }, { "t": "10.3 ms", "sub": "floor per step (arithmetic)", "hot": true }]' />

<div class="ki-grid ki-cols-3">
<MetricCard label="ITL p50" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="itl_ms.p50" unit="ms" digits="1" note="measured step" />
<MetricCard label="ITL p95" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="itl_ms.p95" unit="ms" digits="1" />
<MetricCard label="Output tokens per second per request" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="output_tps" unit="tok/s" digits="1" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

<!--
**Key:** The measured inter-token latency lands just above the weights-over-bandwidth floor, so one decode step of this model on this card is essentially the time to read its weights once. **Example:** Floor: 16.38 divided by 1,597 gives 10.26 ms, or 97.5 tokens per second. Measured p50: 11.6 ms and 86 tokens per second per request, about 13 percent above the floor, with a p95 only 0.2 ms higher, so the steps are very regular. **Transition:** Why is it above, and what fills the gap? **Question:** "Does the card run at full bandwidth?" We do not know: the step contains more than weight traffic. If it were all weight traffic, it would be about 88 percent of the datasheet figure. **Deeper:** The run has 24 requests with 180 output tokens each and no failures; the result file stores GPU power, clocks and utilisation next to the latency numbers.
-->

---
layout: experiment
heading: "Explanation: the floor, the cache and the rest"
step: explanation
experiment: baseline
---

<div class="ki-grid ki-cols-2">
<div>

| Part of one step | Arithmetic |
| --- | --- |
| Weights | 16.38 GB ÷ 1,597 GB/s = 10.26 ms |
| KV cache, about 1,300 tokens | 147,456 B × 1,300 = 0.19 GB, 0.12 ms |
| **Floor** | **about 10.4 ms** |

</div>
<div>

<MetricCard label="Measured ITL p50" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="itl_ms.p50" unit="ms" digits="1" note="above the floor, as it must be" />

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

</div>
</div>

<Takeaway>

The floor is a **sanity check, not a forecast**. We have not profiled kernels, so the remainder is named, not measured: attention kernels below peak bandwidth, sampling, scheduling.

</Takeaway>

<!--
**Key:** The weights explain nearly all of the step; the KV cache read adds a tenth of a millisecond; what remains, about 1.2 ms, is overhead we can name but did not measure. **Example:** 10.26 ms for the weights plus 0.12 ms for the cache gives 10.4 ms; measured is 11.6, so the unexplained part is about 1.2 ms, roughly a ninth of the step. If someone had measured 8 ms, we would stop and check whether they ran FP8. **Transition:** The prefill half of the hypothesis has one data point, so let us look at it honestly. **Question:** "Can we shrink the remaining 1.2 ms?" CUDA graphs already remove most launch overhead; what is left is attention, sampling and scheduling work the engine owns. **Deeper:** The average context during decode is about 1,200 plus half of 180, so 1,300 tokens is a fair figure for the cache term.
-->

---
layout: experiment
heading: "Prefill: a floor, one data point, and a question"
step: explanation
experiment: baseline
---

<Formula :terms='[{ "t": "2 × 8.2 B × 1,200" }, { "op": "÷" }, { "t": "504 TFLOPS" }, { "op": "=" }, { "t": "39 ms", "sub": "compute floor of prefill", "hot": true }]' />

<div class="ki-grid ki-cols-2">
<MetricCard label="TTFT p50" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="ttft_ms.p50" unit="ms" digits="1" note="measured, 1,200-token prompt" />
<MetricCard label="Requests waiting, max" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="server.gauges.num_requests_waiting.max" digits="0" note="no queue in this run" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

<Observation>

One prompt length cannot show how TTFT scales with the prompt. In Lab 2 you will see the direction; Day 2 measures it.

</Observation>

<!--
**Key:** The measured TTFT is above the compute floor and has no queue in it; one prompt length cannot tell us whether prefill scales with prompt length. **Example:** Two FLOP times 8.2 billion parameters times 1,200 tokens, divided by 504 TFLOPS, is 39 ms; measured p50 is 69.6 ms. Real kernels do not reach peak, and TTFT also includes tokenisation, scheduling, sampling and the first chunk. We do not know the split. **Transition:** Next: what we expect when we change one thing. **Question:** "Is prefill really compute-bound then?" The argument says it is close to it; the proof is the context-length experiment on Day 2, and in Lab 2 you will already see the direction by pasting a long prompt. **Deeper:** The 504 TFLOPS is derived, with a plausible range of 468 to 504, so the floor is between 39 and 42 ms.
-->

---
layout: experiment
heading: "Predictions for Day 2"
step: consequence
experiment: baseline
---

| If you change | Predicted effect | Because | Day 2 experiment |
| --- | --- | --- | --- |
| Prompt length up | TTFT grows roughly in proportion; ITL moves little | prefill is compute-heavy | `context-length` |
| Context length up | ITL grows: every step also reads the cache | 32,768 tokens × 147,456 B = 4.8 GB more per step: floor 13.3 ms, not 10.3 ms | `context-length` |
| Concurrency up | aggregate tokens/s rises, ITL changes little at first | requests share one weight read | `concurrency` |
| FP8 weights | ITL falls | 9.44 GB instead of 16.38 GB per step: floor 5.9 ms | `quantization` |

<Warning title="Predictions, not results">

Every row is a hypothesis. Day 2 measures each one and reports where it is wrong.

</Warning>

<!--
**Key:** The block ends with four falsifiable predictions, each tied to the bytes or FLOP it changes, so Day 2 starts as a test of our understanding. **Example:** Second row: one request holding a full 32k context reads 4.8 GB of cache on top of 16.38 GB of weights each step, so the floor rises 29 percent, from 10.3 to 13.3 ms. Ask which row the room is least sure about and keep it for the Day 2 recap. **Transition:** Next: a real server, driven by me first, then by you. **Question:** "Why does concurrency not raise ITL at once?" Extra requests add cache reads and some compute, but the weight read is shared; the step grows slowly until those take over. **Deeper:** Prompt and context length are one variable seen from two sides: prefill pays for the prompt once, decode pays for the cache at every step.
-->

---
layout: statement
---

# Prefill waits for the math. Decode waits for the memory. Most of what we tune follows from that.

<!--
**Key:** If participants keep one sentence from the afternoon, it is this one; it tells them which resource to look at for a slow first token and which for a slow stream. **Example:** A long RAG prompt with a short answer is a prefill problem and a compute problem; a short question with a long answer is a decode problem and a bandwidth problem. Quantization, batching, caching and parallelism each act on one of the two. **Transition:** Now the trainer starts a real server, and you will see the log lines these numbers come from. **Question:** "What if both limits are close?" That is the knee of the roofline; real workloads at moderate batch sizes sit there, and Day 2 shows where. **Deeper:** Every optimisation on Day 2 is introduced by naming its metric, its workload, its bottleneck and its price, in that order.
-->
