---
layout: section
module: 5
heading: "Inference mechanics: prefill, decode, latency"
layer: runtime
question: "Where does the time of one request go, and what limits each part?"
can:
  - "Draw a request through prefill and decode and mark TTFT, ITL and tokens per second"
  - "Predict which phase a change affects"
  - "Explain why decode waits for memory and prefill for compute"
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
**Key:** A request is not one computation but two: a single pass that reads the whole prompt and produces the first token, then a loop that produces the remaining tokens one at a time.

**Example:** The workload we use throughout is 1,200 input tokens and 180 output tokens, so one pass is followed by 179 loop iterations. When a chat answer streams word by word, that is the decode loop made visible.

**Transition:** Let us look at what each phase does to the model and the KV cache.

**Question:** "Is the first token produced by prefill or by decode?" The pass over the prompt yields the next-token distribution at the last prompt position, so the first output token comes out of prefill; every later token needs one more step.

**Deeper:** Reasoning models add many decode steps of thinking before the visible answer, changing TTFT and cost but not the mechanics.
-->

---
layout: default
heading: "Prefill: one big pass. Decode: one token at a time."
---

<D03PrefillDecode />

<!--
**Key:** Prefill pushes all prompt tokens through the model in parallel and leaves their keys and values in the cache; decode runs once per output token, reading all the weights and the whole cache each step.

**Example:** Click 1: the 1,200 prompt tokens enter one pass, and the weights are read once for all of them. Click 2: each decode step takes one token and emits one; the new token is the next input. Click 3: TTFT spans the wait and prefill, ITL is one step.

**Transition:** Let us define the metrics a user feels.

**Question:** "Can decode steps run in parallel for one request?" No: token n+1 needs token n; parallelism comes from other requests or from speculative decoding, which we only demo.

**Deeper:** The cache prefill fills is the KV cache of the sizing module; each decode step appends one entry per layer.
-->

---
layout: default
heading: "Four numbers a user can feel"
---

| Metric | What it measures | Phase |
| --- | --- | --- |
| TTFT | request clock to the first streamed text: queueing and prefill, ending with the first token | prefill |
| ITL | gap between two consecutive streamed chunks of text | decode |
| Output tokens per second per request | 1 ÷ TPOT, the time per output token after the first | decode |
| End-to-end latency | request clock to the end of the stream | both |

<Formula :terms='[{ "t": "LATENCY" }, { "op": "=" }, { "t": "TTFT" }, { "op": "+" }, { "t": "(N − 1) × TPOT", "sub": "179 decode gaps for N = 180", "hot": true }]' />

<!--
**Key:** TTFT belongs to prefill, ITL and tokens per second belong to decode, and end-to-end latency is the sum, so a long answer is dominated by decode and a long prompt with a short answer by prefill.

**Example:** For 180 output tokens there are 179 decode gaps, so a few milliseconds of inter-token latency matter more to total time than the first-token wait. Definitions: docs/METRICS.md section 3.

**Transition:** Seeing the numbers on a real stream is quicker than defining them: one request with its timestamps.

**Question:** "ITL or TPOT?" Tools disagree: here TPOT (time per output token) is (latency minus TTFT) divided by N minus 1 per request and ITL is a pooled chunk gap. Always say which tool you mean.

**Deeper:** If the server groups tokens into one streamed event, chunk gaps no longer equal token gaps; TPOT stays correct because it uses the server's token count.
-->

---
layout: code
heading: "One streamed request, with its timestamps"
file: apps/inference-client/chat.py
---

<Terminal title="your group's GPU machine, in ki-ohne-cloud/">

```bash
python3 apps/inference-client/chat.py "Explain batching in one paragraph."
```

</Terminal>

```text
prompt_tokens=<n>  ttft=<ms> ms  completion_tokens=<n>  decode=<tokens/s> tok/s  total=<s> s
```

| Field of the last line | Metric |
| --- | --- |
| `ttft` | TTFT, measured at the client from the moment of sending |
| `decode` | tokens per second after the first token, about 1 ÷ TPOT |
| `total` | end-to-end latency |

Run it yourself on your group's server and read your own last line.

<!--
**Key:** The client script prints the whole chain on one line: TTFT, decode speed and total time of a request everyone just watched stream.

**Example:** Everyone runs the command on their group's server, lets the text stream and reads the last line field by field. Ask how long a ten times longer prompt would take; keep the answers for Lab 2.

**Transition:** One more thing to run: where does the number in prompt_tokens come from?

**Question:** "Why does ttft here differ from the server's TTFT?" The script measures at the client, including network and SSH tunnel; server histograms start when the server has the request.

**Deeper:** The line goes to standard error, so redirecting output leaves it on screen.
-->

---
layout: default
heading: "Count the same sentence yourself"
---

<Terminal title="your group's GPU machine">

```bash
curl -s http://127.0.0.1:8000/tokenize -H "Content-Type: application/json" \
  -d '{"model": "'"$WORKSHOP_MODEL"'", "return_token_strs": true,
       "prompt": "Explain batching in one paragraph."}' | python3 -m json.tool
```

</Terminal>

- Compare `count` with `prompt_tokens` from your last `chat.py` line.
- `prompt_tokens` is larger: `chat.py` also sends a system message, and the chat template adds role markers.

<Takeaway>

KV memory and prefill work count every prompt token, template included.

</Takeaway>

<!--
**Key:** The tokens a request costs are the tokens the model sees, and that includes the system message and the chat template, so the count of your own sentence alone understates it.

**Example:** Everyone runs the /tokenize call from the models module with the sentence they sent to chat.py and compares count with prompt_tokens. The second number is larger by the system message and the role markers. Prefill reads all of them, and all of them stay in the KV cache.

**Transition:** Why does the first number of the last line behave so differently from the second? The arithmetic of each phase answers it.

**Question:** "Can I count the template too?" Send messages instead of prompt, as the models module notes; the count then includes the template.

**Deeper:** The endpoint is not covered by the API key, which is why this call needs no Authorization header.
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
**Key:** The intensity of a pass over the weights is roughly the number of tokens sharing one read: each weight does two FLOP per token and costs two bytes in BF16.

**Example:** Prefill: 1,200 tokens give about 1,200 FLOP per byte, above 315. Decode with one request: one token per read, about 1, so the weights are fetched for almost no arithmetic. Batching raises decode's intensity: 64 requests in a step give about 64.

**Transition:** That is a hypothesis built on peak numbers, so let us test the decode half with a single request.

**Question:** "What about attention?" Attention reads the KV cache, which is extra bytes per step for each request and with almost no data reuse; at short context it is small next to the weights.

**Deeper:** The rule ignores activations and the cache; it is a first-order argument, and the measurement shows how close it gets.
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
**Key:** The cleanest test of the decode argument is a single request with nothing else on the server, because then each step reads the weights for exactly one token.

**Example:** The profile is the baseline from the start-up demo, the workload is our standard 1,200 in and 180 out, and the harness sends requests one after the other, so inter-token latency is the length of one decode step.

**Transition:** Before we look at the number, you predict it.

**Question:** "Why a closed loop?" Because with only one request in flight the arrival pattern cannot hide or add waiting time; the concurrency experiment comes later.

**Deeper:** The harness defines TTFT and ITL as in METRICS.md and cross-checks against vllm bench serve; the single-stream result file records hardware, model revision, engine version and server arguments next to the numbers.
-->

---
layout: experiment
heading: "Predict the length of one decode step"
step: prediction
experiment: baseline
---

<Formula :terms='[{ "t": "BYTES READ", "sub": "per step: the weights" }, { "op": "÷" }, { "t": "BANDWIDTH", "sub": "of this card" }, { "op": "=" }, { "t": "? ms", "sub": "one decode step", "hot": true }]' />

<Prediction>

Write down two things: the time of one step, and whether the measured inter-token latency will be **below, near or above** it. Give a reason.

</Prediction>

Inputs: `weights_gb` in `config/models.yaml` and the datasheet bandwidth from the GPU fundamentals module.

<!--
**Key:** The point is to commit to a number and a direction before the server answers, and to be able to say what a result on the wrong side would mean.

**Example:** Give the room time to write the number down. The arithmetic gives about 10 milliseconds, or 97 tokens per second as a ceiling for one request. Most people say "near" or "a bit above"; the interesting person is the one who says "below" and has to explain which input would be wrong.

**Transition:** Now the server's answer.

**Question:** "Should I include the KV cache?" You may; at 1,300 tokens of context it adds 147,456 bytes times 1,300, about 0.19 GB, so only 0.1 millisecond.

**Deeper:** A measurement below the bound is a bug in the inputs, for example quantized weights or the Workstation card's bandwidth of 1,792 GB/s instead of 1,597.
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
**Key:** The measured inter-token latency lands just above the weights-over-bandwidth floor, so one decode step of this model on this card is essentially the time to read its weights once.

**Example:** Floor: 16.38 divided by 1,597 gives 10.26 ms, or 97.5 tokens per second. Measured p50: 11.6 ms and 86 tokens per second per request, about 13 percent above the floor, with a p95 only 0.2 ms higher, so the steps are very regular.

**Transition:** Why is it above, and what fills the gap?

**Question:** "Does the card run at full bandwidth?" We do not know: the step contains more than weight traffic. If it were all weight traffic, it would be about 88 percent of the datasheet figure.

**Deeper:** The run has 24 requests with 180 output tokens each and no failures; the result file stores GPU power, clocks and utilization next to the latency numbers.
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
**Key:** The weights explain nearly all of the step; the KV cache read adds a tenth of a millisecond; what remains, about 1.2 ms, is overhead we can name but did not measure.

**Example:** 10.26 ms for the weights plus 0.12 ms for the cache gives 10.4 ms; measured is 11.6, so the unexplained part is about 1.2 ms, roughly a ninth of the step. If someone had measured 8 ms, we would stop and check whether they ran FP8.

**Transition:** The prefill half of the hypothesis has one data point, so let us look at it honestly.

**Question:** "Can we shrink the remaining 1.2 ms?" CUDA graphs already remove most launch overhead; what is left is attention, sampling and scheduling work the engine owns.

**Deeper:** The average context during decode is about 1,200 plus half of 180, so 1,300 tokens is a fair figure for the cache term.
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

One prompt length cannot show how TTFT scales with the prompt. In Lab 2 you will see the direction; the context-length experiment measures it.

</Observation>

<!--
**Key:** The measured TTFT is above the compute floor and has no queue in it; one prompt length cannot tell us whether prefill scales with prompt length.

**Example:** Two FLOP times 8.2 billion parameters times 1,200 tokens, divided by 504 TFLOPS, is 39 ms; measured p50 is 69.6 ms. Real kernels do not reach peak, and TTFT also includes tokenisation, scheduling, sampling and the first chunk. We do not know the split.

**Transition:** Next: both phases on one picture, with their floors.

**Question:** "Is prefill really compute-bound then?" The argument says it is close to it; the proof is the context-length experiment later in the path, and in Lab 2 you will already see the direction by pasting a long prompt.

**Deeper:** The 504 TFLOPS is derived, with a plausible range of 468 to 504, so the floor is between 39 and 42 ms.
-->

---
layout: experiment
heading: "Same model, same card, two different limits"
step: explanation
experiment: baseline
---

<D06ComputeVsBandwidth />

<!--
**Key:** For each phase there are two minimum times, one for the math and one for moving the weights, and the longer one is the limit; prefill is math-limited, decode is memory-limited.

**Example:** Click through: a 1,200-token prefill needs at least 39 ms of math and 10.3 ms to read the weights once, so math wins; a decode step needs 0.03 ms of math and still 10.3 ms to read the weights, so the math fills about 0.3 percent of the step.

**Transition:** Both phases are explained; next, what the later modules will test.

**Question:** "Is 39 ms the real prefill time?" No, a floor at peak rate; the measured TTFT is higher, and one data point cannot say why.

**Deeper:** Batching fills the gap: 64 sequences share one weight read, so the math grows 64-fold while the memory time stays 10.3 ms.
-->

---
layout: experiment
heading: "What the later modules will test"
step: consequence
experiment: baseline
---

| You change | Experiment |
| --- | --- |
| Prompt length | `context-length` |
| Context length | `context-length` |
| Concurrency | `concurrency` |
| FP8 weights | `quantization` |
| A second GPU | `tensor-parallel` |

<Prediction title="Your job before each experiment">

Write which resource limits, which metric moves and in which direction, and why.

</Prediction>

<!--
**Key:** The module ends with the list of changes the later modules will try, one at a time, and with the habit that each of them gets your own written prediction first; no effect is predicted for you here.

**Example:** Read the five changes aloud and say that the checkpoint module hands out the blank prediction table. A good prediction names the limiting resource, the metric and the direction, built from what this module taught: bytes read per step, FLOP per byte, the ridge.

**Transition:** One sentence to carry out of this module, before a real server enters.

**Question:** "Why not predict them now?" You will, in the checkpoint module, after the chain from client to GPU has been rebuilt from memory.

**Deeper:** Prompt and context length are one variable seen from two sides: prefill pays for the prompt once, decode pays for the cache at every step.
-->

---
layout: statement
---

# Prefill waits for the math. Decode waits for the memory. Most of what we tune follows from that.

<!--
**Key:** If participants keep one sentence from this module, it is this one; it tells them which resource to look at for a slow first token and which for a slow stream.

**Example:** A long RAG prompt with a short answer is a prefill problem and a compute problem; a short question with a long answer is a decode problem and a bandwidth problem. Quantization, batching, caching and parallelism each act on one of the two.

**Transition:** Next the trainer starts a real server, and you will see the log lines these numbers come from.

**Question:** "What if both limits are close?" That is the knee of the roofline; real workloads at moderate batch sizes sit there, and the batching module shows where.

**Deeper:** Every optimization later in the path is introduced by naming its metric, its workload, its bottleneck and its price, in that order.
-->
