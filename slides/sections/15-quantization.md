---
layout: section
module: 15
heading: "Quantization"
layer: runtime
question: "What do fewer bits buy, what do they cost, and how would we know?"
can:
  - "Say what weights, activations and the KV cache each gain from fewer bits"
  - "Read a quality probe honestly, including what it cannot show"
  - "Choose the lever that fits the limit you measured"
---

---
layout: default
heading: "Three things can be stored in fewer bits"
---

| Quantize | What gets smaller | What it changes in a step | In this workshop |
| --- | --- | --- | --- |
| Weights | the matrices of the model | the bytes every decode step reads | `fp8`: the publisher's FP8 checkpoint |
| Activations | the values flowing between layers | the arithmetic: FP8 runs at twice the BF16 rate on this GPU | inside the FP8 kernels; no separate profile |
| KV cache | the keys and values of every token | cache memory and the cache read | `kv-fp8`: `--kv-cache-dtype fp8` |

<Takeaway>

Three separate decisions. Each one changes a different resource.

</Takeaway>

<!--
**Key:** Quantization is not one switch: weights, activations and the KV cache are separate decisions, and each changes a different part of the resource profile.

**Example:** In an FP8 W8A8 kernel weights and activations are both FP8 and the Tensor Cores run at twice the BF16 rate, but a decode step is limited by bytes, so the stored weights matter most. The KV cache is a vLLM option of its own and is the only one that changes capacity per token.

**Transition:** Which formats exist, and which did we actually run?

**Question:** "Can we quantize a model ourselves?" The workshop uses the publisher's FP8 checkpoint; online quantization at load time exists but is not tested here.

**Deeper:** RESEARCH 8.3: the old quantization fp8 flag on a BF16 checkpoint is deprecated in 0.31.0; the name to teach is fp8_per_tensor.
-->

---
layout: default
heading: "Formats, and what we ran"
---

| Format | Bits | What to know | On this GPU |
| --- | --- | --- | --- |
| BF16 | 16 | the range of FP32, fewer mantissa bits: the default of the workshop models | `baseline`: measured |
| FP16 | 16 | same size as BF16 | not run |
| FP8 | 8 | values are scaled to fit: per tensor or per 128 × 128 block | `fp8`, `kv-fp8`: measured |
| INT8 | 8 | integers with a scale | not run |
| INT4 (AWQ, GPTQ) | 4 | weight-only; "test before you promise" | not run, unverified here |
| NVFP4 | about 4.5 | block scales included; bug reports concentrate here | not used |

<span class="muted small">`kv-fp8` uses vLLM's default KV scales of 1.0: not calibrated.</span>

<!--
**Key:** The formats differ in bits, but also in what they need next to the numbers: scales, kernels for your GPU generation and a quality check. This table is the map of what we ran and what we did not.

**Example:** FP8 E4M3 tops out at 448, so values are scaled to fit, per tensor or per block. The kv-fp8 profile uses the engine's default scales, not calibrated ones. For INT4 formats and for NVFP4 no profile exists, and the research notes label 4-bit weight formats as test before you promise.

**Transition:** Next, which bytes a decode step reads under each choice we did run.

**Question:** "vLLM's table has no Blackwell column: is FP8 unsupported?" No: absence is not proof either way, which is why we ran FP8 on the card instead of arguing from the table.

**Deeper:** RESEARCH 8.1 to 8.6; the checkpoint's FP8 recipe is the publisher's.
-->

---
layout: default
heading: "What is stored, and what one step reads"
---

<D10Quantization />

<!--
**Key:** A decode step reads the weights and the KV cache, so each precision choice changes a different share of the bytes, and the floor is bytes divided by bandwidth.

**Example:** Click 1: BF16 reads 16.38 GB of weights plus about 3.0 GB of cache for sixteen requests of 1,290 tokens, floor 12.2 ms. Click 2: FP8 weights read 9.44 GB, not 8.2, because the embeddings and the output head stay BF16, floor 7.8 ms. Click 3: an FP8 cache halves the amber part, floor 11.2 ms. All arithmetic, none measured.

**Transition:** Now predict what the real server does with each bar.

**Question:** "Why sixteen requests?" At one request the cache is 0.19 GB, one percent of the bytes: the amber segment would be invisible, which is also the lesson about the KV cache.

**Deeper:** The floor ignores scheduling, kernel launches and de-quantization.
-->

---
layout: experiment
heading: "Experiment: weights, then KV cache"
step: experiment
experiment: quantization
---

<ExperimentCard
  name="quantization"
  variable="weight precision (BF16, FP8 checkpoint), then KV-cache precision (BF16, FP8)"
  :profiles='["baseline", "fp8", "kv-fp8"]'
  workload="1,200 input, 180 output tokens, 1 and 16 clients; plus a quality probe of 240 items"
  :metrics='["ITL", "aggregate tokens/s", "weights memory", "KV capacity", "start-up", "accuracy"]'
  hypothesis="FP8 weights read fewer bytes per decoded token, so decode speeds up, and the freed memory holds more KV cache. Quality moves by less than a small check can resolve."
/>

The FP8 checkpoint is the publisher's build, with the publisher's calibration. Not ours.

<!--
**Key:** Two variables in turn, never together, with quality as a first-class metric next to speed: a speed-up without a quality check is half a result.

**Example:** The fp8 profile serves Qwen/Qwen3-8B-FP8 under the same served name, so dashboards keep one model label across runs; kv-fp8 is the BF16 model with an FP8 cache. The probe is 240 generated items, greedy decoding, thinking off.

**Transition:** Predict before the data.

**Question:** "Why not quantize it ourselves?" Calibration is its own project; the publisher's checkpoint is what most teams would try first, and it keeps the experiment to one variable.

**Deeper:** One session, 24 requests at one client and 96 at sixteen: the speed differences are far larger than the run-to-run variation of about 1 percent, the quality differences are not.
-->

---
layout: experiment
heading: "Predict: FP8 weights, FP8 KV cache"
step: prediction
experiment: quantization
---

<Prediction>

Faster, same or slower, and by roughly how much? Name the limiting resource in each column.

</Prediction>

| Against BF16 | FP8 weights | FP8 KV cache |
| --- | --- | --- |
| ITL at one client | ? | ? |
| Aggregate tokens/s at 16 clients | ? | ? |
| Weights in memory | ? | ? |
| KV capacity (tokens) | ? | ? |
| Accuracy on our probe | ? | ? |

<span class="muted small">The earlier floor for FP8 weights: 9.44 GB ÷ 1,597 GB/s = 5.9 ms, against 10.3 ms. An FP8 cache costs 73,728 B per token instead of 147,456.</span>

<!--
**Key:** The table asks for a direction and a size in every cell, and the two columns should differ: FP8 weights act on the bytes of every step, an FP8 cache on the bytes of the cache.

**Example:** Typical guesses: ITL halves with FP8 weights; capacity doubles with FP8 weights. Push back with the sizing arithmetic: the checkpoint is 9.44 GB, not 8.2, and the freed bytes are about 6.4 GiB out of a pool of nearly 60. Ask who expects the quality column to move, and by how many points.

**Transition:** The measurements: speed first.

**Question:** "Do we expect a quality loss?" Write down a number of points; the interesting part comes when we see what the probe can resolve.

**Deeper:** The checkpoint hypothesis put the FP8 floor at 5.9 ms; the data will land above it.
-->

---
layout: experiment
heading: "Measured: speed at 1 and 16 clients"
step: measurement
experiment: quantization
---

<ResultTable
  source="measured:benchmark/results/reference/quantization"
  match="-c0"
  label-by="configuration.server_profile"
  label-header="Profile"
  :columns='["concurrency", "ttft_ms.p50", "itl_ms.p50", "output_tps_per_request.p50", "aggregate_tps"]'
  :headers='["Clients", "TTFT p50 (ms)", "ITL p50 (ms)", "Tokens/s each", "Aggregate tokens/s"]'
  :digits='{ "itl_ms.p50": 1, "output_tps_per_request.p50": 1 }'
/>

<Observation>

FP8 weights change the stream of one request and the throughput of sixteen. An FP8 KV cache changes little at one request and a little at sixteen.

</Observation>

<!--
**Key:** The two profiles act in different places: FP8 weights shorten every decode step, which shows at one client and at sixteen; an FP8 cache is almost invisible at one client and visible only when many requests carry cache.

**Example:** ITL at one client falls from 11.6 to 7.3 ms (86 to 138 tokens per second per request); at sixteen clients aggregate throughput rises from 897 to 1,323 tokens per second and TTFT p50 from 616 to 360 ms. The FP8 cache gives 11.5 against 11.6 ms at one client and 963 against 897 tokens per second at sixteen.

**Transition:** Memory and capacity next.

**Question:** "Why does TTFT improve with FP8 weights?" The results document reports it without a separate explanation; shorter decode steps and FP8 matrix math are plausible, and this experiment does not separate them.

**Deeper:** Power falls with FP8 weights too: the energy slide shows it.
-->

---
layout: experiment
heading: "Measured: memory and start-up"
step: measurement
experiment: quantization
---

<div class="ki-grid ki-cols-3" style="gap: 12px">
<MetricCard label="baseline: weights in memory" source="measured:benchmark/results/reference/quantization/startup.json" metric="baseline.startup.model_memory_gib" unit="GiB" digits="2" />
<MetricCard label="fp8: weights in memory" source="measured:benchmark/results/reference/quantization/startup.json" metric="fp8.startup.model_memory_gib" unit="GiB" digits="2" tone="good" />
<MetricCard label="kv-fp8: weights in memory" source="measured:benchmark/results/reference/quantization/startup.json" metric="kv-fp8.startup.model_memory_gib" unit="GiB" digits="2" />
<MetricCard label="baseline: KV capacity" source="measured:benchmark/results/reference/quantization/startup.json" metric="baseline.startup.kv_cache_tokens" unit="tokens" />
<MetricCard label="fp8: KV capacity" source="measured:benchmark/results/reference/quantization/startup.json" metric="fp8.startup.kv_cache_tokens" unit="tokens" />
<MetricCard label="kv-fp8: KV capacity" source="measured:benchmark/results/reference/quantization/startup.json" metric="kv-fp8.startup.kv_cache_tokens" unit="tokens" tone="good" />
<MetricCard label="baseline: warm restart" source="measured:benchmark/results/reference/quantization/startup.json" metric="baseline.startup_seconds" unit="s" digits="1" />
<MetricCard label="fp8: warm restart" source="measured:benchmark/results/reference/quantization/startup.json" metric="fp8.startup_seconds" unit="s" digits="1" />
<MetricCard label="kv-fp8: warm restart" source="measured:benchmark/results/reference/quantization/startup.json" metric="kv-fp8.startup_seconds" unit="s" digits="1" />
</div>

<Provenance source="measured:benchmark/results/reference/quantization/startup.json" />

<!--
**Key:** FP8 weights free memory and the KV pool takes it, so capacity grows modestly here, because the weights are a small part of 96 GB. An FP8 cache doubles the tokens in the same gigabytes.

**Example:** Weights fall from 15.27 to 8.85 GiB, capacity rises from 426,992 to 473,312 tokens (about 11 percent); the FP8 cache gives 848,400 tokens from almost the same GiB. Warm restarts take about the same time; the first start of the fp8 profile loads and compiles a new checkpoint and took 143 seconds, as Lab 4 warns.

**Transition:** Why did the speed not double?

**Question:** "Are FP8 weights pointless on this card?" For capacity, mostly; for speed, no. On a card the weights mostly fill, the same saving matters far more.

**Deeper:** The cards read startup.json of the experiment.
-->

---
layout: experiment
heading: "Why: bytes, and what a step carries"
step: explanation
experiment: quantization
---

<div class="ki-grid ki-cols-2">
<div>

### Arithmetic: bytes ÷ 1,597 GB/s

| Profile, load | Bytes per step | Floor |
| --- | --- | --- |
| BF16, 1 request | 16.38 GB | 10.3 ms |
| BF16, 16 requests | 16.38 + 3.04 = 19.42 GB | 12.2 ms |
| FP8 weights, 1 request | 9.44 GB | 5.9 ms |
| FP8 KV, 16 requests | 16.38 + 1.52 = 17.90 GB | 11.2 ms |

</div>
<div>

### Measured

<ResultTable
  source="measured:benchmark/results/reference/quantization"
  :match='["quantization/baseline-c001", "quantization/baseline-c016", "quantization/fp8-c001", "quantization/kv-fp8-c016"]'
  label-by="configuration.server_profile"
  label-header="Profile"
  :columns='["concurrency", "itl_ms.p50"]'
  :headers='["Clients", "ITL p50 (ms)"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>
</div>

<Takeaway>

The step follows the bytes, a little above the floor: the embeddings and output head stay BF16, and scheduling, launches and de-quantization do not shrink. One request reads 0.19 GB of cache, 1 % of its step: an FP8 cache cannot show there.

</Takeaway>

<!--
**Key:** Every measured step sits above its floor, and FP8 weights cut it by less than the bytes suggest, so half the bits is not half the step. The same arithmetic says where an FP8 cache can matter at all.

**Example:** The checkpoint is 9.44 GB, 42 percent smaller, not 50; the floor falls from 10.3 to 5.9 ms and the measured step from 11.6 to 7.3, a 1.6 times faster stream. One request holds about 0.19 GB of cache, so halving it saves 0.06 ms; sixteen requests read 3.0 GB, and the 1.5 GB saved, about 0.95 ms by arithmetic, shows: 13.5 down to 12.3 ms.

**Transition:** Faster is half the answer: now the quality check.

**Question:** "Is the GPU still memory-bound with FP8 weights?" At one client yes, which is why they pay off.

**Deeper:** Measured over floor: 1.13 for BF16, 1.23 for FP8 (RESULTS).
-->

---
layout: experiment
heading: "Measured: the quality probe"
step: measurement
experiment: quantization
---

<ResultTable
  source="measured:benchmark/results/reference/quantization"
  :match='["quality-baseline", "quality-fp8", "quality-kv-fp8"]'
  label-by="label"
  label-header="Profile"
  :columns='["items", "accuracy", "accuracy_by_kind.arith", "accuracy_by_kind.extract", "accuracy_by_kind.classify"]'
  :headers='["Items", "Accuracy (fraction)", "Arithmetic", "Extraction", "Classification"]'
  :digits='{ "accuracy": 3, "accuracy_by_kind.arith": 3, "accuracy_by_kind.extract": 3, "accuracy_by_kind.classify": 3 }'
/>

<div class="ki-grid ki-cols-4">
<MetricCard label="FP8 weights: right in BF16, wrong here" source="measured:benchmark/results/reference/quantization/quality-comparison.json" metric="fp8.reference_right_other_wrong" tone="bad" />
<MetricCard label="FP8 weights: wrong in BF16, right here" source="measured:benchmark/results/reference/quantization/quality-comparison.json" metric="fp8.other_right_reference_wrong" />
<MetricCard label="Identical completions, FP8 weights" source="measured:benchmark/results/reference/quantization/quality-comparison.json" metric="fp8.greedy_completions_identical" digits="2" />
<MetricCard label="Identical completions, FP8 KV cache" source="measured:benchmark/results/reference/quantization/quality-comparison.json" metric="kv-fp8.greedy_completions_identical" digits="2" />
</div>

<Provenance source="measured:benchmark/results/reference/quantization/quality-comparison.json" />

<!--
**Key:** The check that has to sit next to the speed-up: three profiles score within a few points of each other, and the table alone cannot say whether that is "no loss" or "a loss we cannot see".

**Example:** Accuracy is 0.796 for BF16, 0.771 for FP8 weights and 0.788 for an FP8 cache. Under FP8 weights 12 items flipped from right to wrong and 6 from wrong to right, all in the arithmetic kind, which falls from 0.388 to 0.313. Extraction and classification sit at 1.0 in every profile. Only 3 percent of the open completions under FP8 weights, and 28 percent under an FP8 cache, equal the BF16 text.

**Transition:** What can a probe like this resolve?

**Question:** "Which profile would you pick on this evidence?" None: the evidence is too coarse to pick on; the next slide says why.

**Deeper:** Probe: experiments/quality_probe.py, greedy decoding, thinking off.
-->

---
layout: experiment
heading: "Why: reading the probe honestly"
step: explanation
experiment: quantization
---

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Resolution of about ± 5 points.** 1.96 × √(0.8 × 0.2 ÷ 240) = 5.1 points. A 2.5-point drop sits inside it.

</div>
<div class="ki-card">

**The floor effect is fixed.** The first probe cut arithmetic answers at 16 tokens: 14 % in every profile. It allows 48 now.

</div>
<div class="ki-card">

**One category discriminates.** Extraction and classification score 100 % everywhere. Only arithmetic can move.

</div>
<div class="ki-card">

**Same answers, different text.** Most greedy completions differ from BF16 even where the answer agrees.

</div>
</div>

<Warning title="What the probe cannot do">

It cannot prove the 2 % regression bound of the course SLO. It says the loss is below about five points. A decision needs your own items.

</Warning>

<!--
**Key:** A quality check has a resolution, and a result smaller than it is not "no change" but "no change we can see". Say the limits as plainly as the speed-up.

**Example:** At about 80 percent accuracy and 240 items, the half-width of a 95 percent interval is 1.96 times the square root of 0.8 times 0.2 over 240: 5.1 points. The first version of the probe scored arithmetic at 14 percent in every profile, because answers were cut at 16 tokens, so it could show no loss at all. Tests that compare exact text, golden files for instance, change with the precision.

**Transition:** Put speed and quality into the seven dimensions.

**Question:** "How big must my eval be?" For a 2-point bound at 80 percent, about 1,500 items by the same formula.

**Deeper:** Extraction and classification are saturated, not easy: harder items would discriminate.
-->

---
layout: default
heading: "What was traded: direction only"
---

<TradeoffMatrix :rows='[
  { "name": "FP8 weights", "note": "measured", "effects": { "quality": "risk", "latency": "up", "throughput": "up", "concurrency": "up", "memory": "up", "cost": "up", "ops": "down" } },
  { "name": "FP8 KV cache", "note": "measured, default scales", "effects": { "quality": "risk", "latency": "flat", "throughput": "up", "concurrency": "up", "memory": "up", "ops": "down" } },
  { "name": "INT4 weights", "note": "not run here", "effects": { "quality": "risk", "latency": "risk", "throughput": "risk", "memory": "up", "ops": "down" } }
]' />

<Takeaway>

Every row has a ? or a ▼. Sizes come from measurements, and the quality column is where the measurement is weakest.

</Takeaway>

<!--
**Key:** Quantization is a trade across the seven dimensions, not a speed-up: memory, latency and cost improve, quality and operations carry a question mark or a price.

**Example:** FP8 weights: a faster stream and higher throughput, a bit more room for requests, a lower cost per token; quality unknown to within about five points, and one more checkpoint to pin and evaluate. FP8 cache: no latency change at one request, more concurrency, the same quality question, and default scales that nobody calibrated. INT4: memory improves, everything else is a question until it is run.

**Transition:** Two of the dimensions, energy and cost per token, we can put in numbers.

**Question:** "Why is operations a ▼?" A new artifact to version, an eval to maintain and a rollback profile to keep.

**Deeper:** The matrix is direction only; sizes belong to the tables in this module.
-->

---
layout: default
heading: "Per token: energy and cost, as arithmetic"
---

<ResultTable
  source="measured:benchmark/results/reference/quantization"
  :match='["quantization/baseline-c001", "quantization/baseline-c016", "quantization/fp8-c001", "quantization/fp8-c016"]'
  label-by="configuration.server_profile"
  label-header="Profile"
  :columns='["concurrency", "gpu.power_w.mean", "aggregate_tps"]'
  :headers='["Clients", "Power (W)", "Aggregate tokens/s"]'
  :digits='{ "gpu.power_w.mean": 1 }'
/>

<div class="ki-grid ki-cols-2">
<div>

| Arithmetic from the table | BF16 | FP8 weights |
| --- | --- | --- |
| Energy per token, 1 client | 4.3 J | 2.4 J |
| USD per million tokens, 16 clients | 0.77 | 0.52 |

</div>
<Warning title="Arithmetic, not a measurement">

J per token = power ÷ aggregate tokens/s. USD per million = 2.49 ÷ (aggregate tokens/s × 3,600) × 10^6. GPU time only.

</Warning>
</div>

<!--
**Key:** Energy and cost per token are quotients of two measured numbers: arithmetic with a visible formula, carrying the caveats of the numbers it comes from.

**Example:** One client: 362.7 W over 84.0 tokens per second is 4.3 J per token; with FP8, 317.9 W over 133.8 is 2.4 J. At sixteen clients, 2.49 USD per GPU hour over 896.6 tokens per second gives 0.77 USD per million output tokens, and 0.52 with FP8 weights, 32 percent less. Input tokens, idle time and operations are not in it.

**Transition:** So which lever for which limit?

**Question:** "Is the pod price my cost?" It is the workshop pod's hourly price; use your own hardware cost or rental price.

**Deeper:** Energy per token also falls with concurrency: 4.3 J at one client, 0.29 J at 64 on the BF16 server.
-->

---
layout: experiment
heading: "Choose the lever by the limit"
step: consequence
experiment: quantization
---

| The limit is | Lever | What it costs | What we saw |
| --- | --- | --- | --- |
| memory bandwidth in decode | FP8 weights | a quality check, a second checkpoint to pin | shorter step, higher throughput, little capacity |
| the KV pool | FP8 KV cache | a quality check, uncalibrated scales | twice the tokens in the same bytes, little speed |
| neither | keep BF16 | nothing | the reference and the rollback |

<Consequence>

Treat the precision as part of the model version: pin the checkpoint, run your own eval on your own items, and keep the BF16 profile as the rollback.

</Consequence>

<!--
**Key:** The decision follows the limit you measured, not the format name: bandwidth-bound decode wants FP8 weights, a full KV pool wants an FP8 cache, and a workload limited by neither gets nothing from either.

**Example:** On this card at 20 users the course SLO misses the TTFT target slightly; FP8 weights are one of the three ways out the concurrency results name, next to a second GPU and a looser SLO. Compare them on the same sheet, with quality next to speed. Keep both profiles installed so the rollback is one wsctl command.

**Transition:** Next: more than one GPU.

**Question:** "Can groups try INT4 in Lab 4?" Unverified on this GPU: label it an experiment and expect to debug it.

**Deeper:** Both changes alter the outputs, so regression tests that compare exact text must be regenerated per precision.
-->

---
layout: statement
---

# Quantization changes the resource profile. It does not make everything faster.

<!--
**Key:** The sentence to take into Lab 4: name the resource that limits you, pick the precision that relieves it, and measure speed and quality in the same table.

**Example:** FP8 weights relieved bandwidth and bought a faster stream; an FP8 cache relieved memory and bought tokens; neither changed what the model knows, and both changed what it writes. If a group reports a speed-up without a quality column, send them back.

**Transition:** Next, parallelism: when a second GPU helps, and when it only makes the deployment bigger.

**Question:** "What if my hardware has no FP8?" Then weight-only paths exist, and the gain comes from bandwidth alone; measure it.

**Deeper:** RESULTS caveat: one GPU generation with native FP8 was tested.
-->
