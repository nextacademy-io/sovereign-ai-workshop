---
layout: section
heading: "GPU sizing: weights, KV cache, overhead"
time: "14:30"
minutes: 45
layer: runtime
question: "Will this model fit on the GPU, and for how many users?"
---

---
layout: default
heading: "The question behind every deployment"
---

<Formula :terms='[{ "t": "WEIGHTS" }, { "op": "+" }, { "t": "KV CACHE", "hot": true }, { "op": "+" }, { "t": "RUNTIME OVERHEAD" }, { "op": "=" }, { "t": "VRAM" }]' />

<div class="ki-grid ki-cols-2">
<div>

### What people say

"It is an 8B model, so it needs 16 GB."

That is only the first term. It answers *can I load it*, not *can I serve it*.

</div>
<div>

### What decides the deployment

- how much **context** each request carries
- how many requests are **in flight at once**
- the **precision** of weights and cache
- what the **engine** reserves for itself

</div>
</div>

<!--
**Key:** "Will it fit?" has three terms, and only the first one is on the model card. The weights are fixed, the KV cache depends on how the model is used, and the runtime needs working memory of its own. **Example:** An 8B model in BF16 loads into about 15 GiB, and the same server can still run out of memory with a handful of long requests. **Transition:** We start with the term everybody knows, the weights, then spend most of the block on the term that decides how many users you can serve. **Question:** "Is the 80 % memory setting a limit?" It is a budget for the engine, not a promise: the rest stays unclaimed on purpose. **Deeper:** Activation memory and CUDA graphs are small here, but they grow with batch size and with the number of captured graph shapes.
-->

---
layout: two-col
heading: "Weights: parameters × bytes per parameter"
---

| Format | Bytes / parameter |
| --- | --- |
| BF16 / FP16 | 2 |
| FP8 / INT8 | 1 |
| INT4 / FP4 | 0.5 |

Qwen3-8B has 8.2 B parameters:

| Precision | Arithmetic |
| --- | --- |
| BF16 | 8.2 B × 2 = 16.4 GB |
| FP8 | 8.2 B × 1 = 8.2 GB |
| INT4 | 8.2 B × 0.5 = 4.1 GB |

::right::

<Warning title="The arithmetic is a floor">

The published FP8 checkpoint is **9.44 GB**, not 8.2 GB: embeddings and the output head stay in BF16. Quantization tables on model cards are the starting point, not the answer.

</Warning>

<Takeaway>

Weights are the term you can compute on paper from the model card. Everything else needs the architecture.

</Takeaway>

<!--
**Key:** Weight memory is parameters times bytes per parameter, and it is a lower bound: some tensors stay in higher precision, so real files are larger than the clean arithmetic. **Example:** Qwen3-8B in BF16 comes out at 16.4 GB by arithmetic and the checkpoint is 16.38 GB on disk, but the FP8 build is 9.44 GB instead of 8.2 GB because of the BF16 embeddings and output head. **Transition:** With weights settled, the interesting question is what else the GPU holds while the model answers. **Question:** "Why not INT4 everywhere?" Memory is one of seven dimensions, and we measure the quality cost on Day 2. **Deeper:** GB here are 10^9 bytes and GiB are 2^30 bytes; vLLM logs GiB, model cards usually quote GB, and the 7 % difference matters when you size close to the limit.
-->

---
layout: default
heading: "The model is not the whole bill"
---

<D04KvCache />

<!--
**Key:** Every token the model has processed leaves its attention keys and values in every layer, and the decode loop reads them again for each new token instead of recomputing them. That stored state is the KV cache, and it lives in VRAM next to the weights. **Example:** Click once: the prompt is processed and the cache fills. Click again: a decode step computes one new column and only reads the old ones. **Transition:** The cache is why generation is fast, and also why memory depends on the traffic, so let us put a number on it. **Question:** "Why cache K and V but not Q?" Queries are only needed at the moment a token is processed; later tokens never look at an old query. **Deeper:** Grouped-query attention shares each K/V head between several query heads, which is why Qwen3-8B stores 8 KV heads although it has 32 attention heads.
-->

---
layout: default
heading: "KV cache: the part that grows"
---

<Formula :terms='[{ "t": "2", "sub": "K and V" }, { "op": "×" }, { "t": "36", "sub": "layers" }, { "op": "×" }, { "t": "8", "sub": "KV heads" }, { "op": "×" }, { "t": "128", "sub": "head dim" }, { "op": "×" }, { "t": "2 B", "sub": "BF16" }, { "op": "=" }, { "t": "147,456 B", "sub": "per token", "hot": true }]' />

<div class="ki-grid ki-cols-2">
<div>

| Context of one request | KV cache |
| --- | --- |
| 4,096 tokens | 0.56 GiB |
| 8,192 tokens | 1.13 GiB |
| 32,768 tokens | 4.50 GiB |

</div>
<div>

<Formula :terms='[{ "t": "LONGER CONTEXT", "hot": true }, { "op": "+" }, { "t": "MORE REQUESTS", "hot": true }, { "op": "=" }, { "t": "MORE KV CACHE" }]' />

16 requests of 8k tokens: **18 GiB**.

</div>
</div>

<!--
**Key:** The KV cache costs a fixed number of bytes per token, determined by the architecture, and the total is that number times every token currently held for every request in flight. **Example:** 147,456 bytes per token for Qwen3-8B, so a single 8k-token request holds 1.13 GiB and sixteen of them hold 18 GiB, more than the model itself. **Transition:** Before we look at what the server actually reports, make a prediction. **Question:** "Does max-model-len change the bytes per token?" No, it only caps how long one request may become; the cost per token is architecture. **Deeper:** The per-token cost is read straight from config.json: num_hidden_layers, num_key_value_heads and head_dim, so you can size a model you have never run.
-->

---
layout: default
heading: "Same weights class, different cache bill"
---

| Model (pinned in `config/models.yaml`) | Parameters | Layers | KV heads | KV bytes / token |
| --- | --- | --- | --- | --- |
| Qwen3-1.7B | 1.7 B | 28 | 8 | 114,688 |
| Qwen3-8B | 8.2 B | 36 | 8 | 147,456 |
| Qwen3-30B-A3B (mixture of experts) | 30.5 B, 3.3 B active | 48 | 4 | 98,304 |

<Takeaway>

The cache cost follows the **architecture**, not the parameter count. A mixture-of-experts model needs memory for all 30.5 B weights but caches *less* per token than the dense 8B.

</Takeaway>

<!--
**Key:** KV bytes per token depend on layers, KV heads and head dimension, not on parameter count, so a bigger model can be cheaper per token and a smaller one can be surprisingly expensive. **Example:** Qwen3-1.7B caches 78 percent of what Qwen3-8B does per token although it has a fifth of the parameters, and the 30B mixture-of-experts model caches only two thirds of the 8B because it has 4 KV heads. **Transition:** Now the real server: what does vLLM do with 95 GiB? **Question:** "Active parameters are 3.3 B, so is memory small too?" No: all experts must be resident, so memory follows total parameters while speed follows active ones. **Deeper:** Multi-head latent attention and sliding-window layers change the formula again; always read the architecture, never assume the Qwen numbers.
-->

---
layout: default
heading: "Where the 95 GiB go (measured)"
---

<MemoryBar
  source="measured:benchmark/results/reference/baseline/memory-accounting.json"
  total="startup_log.memory_accounting_gib.device_total"
  :segments='[
    { "label": "Weights + non-torch", "metric": "startup_log.memory_accounting_gib.weights_and_non_torch", "tone": "runtime" },
    { "label": "Peak activations", "metric": "startup_log.memory_accounting_gib.peak_activation", "tone": "infrastructure" },
    { "label": "CUDA graphs", "metric": "startup_log.memory_accounting_gib.cuda_graphs", "tone": "info" },
    { "label": "KV cache", "metric": "startup_log.kv_cache_memory_gib", "tone": "application" },
    { "label": "Not claimed (about 20 %)", "rest": true, "tone": "muted" }
  ]'
/>

<Terminal title="vLLM start-up log (excerpt)">

```text
Model loading took 15.27 GiB memory and 3.782364 seconds
Available KV cache memory: 58.14 GiB
GPU KV cache size: 423,328 tokens, Maximum concurrency for 32,768 tokens per request: 12.92x
```

</Terminal>

<!--
**Key:** vLLM takes a fraction of the GPU, 80 percent in our profile, subtracts what the weights, the profiled activations and the CUDA graphs need, and gives the entire remainder to the KV cache. **Example:** Of 94.97 GiB usable, weights and non-torch memory take 16.14, peak activations 1.7 and CUDA graphs 0.21, so about 58 GiB become cache (the log's own figure is 58.14: vLLM first over-estimates the graph memory and gives 0.24 GiB back). **Transition:** That log line is a number we can predict, so let us do exactly that. **Question:** "Why is the weights term 16.14 and not 15.27?" The extra 0.87 GiB is memory outside PyTorch's allocator, such as the CUDA context and NCCL buffers. **Deeper:** The embedding server on the same GPU claimed about 7.8 GiB first, which is why free memory at start was lower than the device total; two vLLM instances do not see each other's budget.
-->

---
layout: experiment
heading: "Predict before you look"
step: prediction
experiment: baseline
---

<Prediction>

The server will report how many tokens its KV cache can hold. Using only the model card, the architecture and this slide's budget, estimate it.

</Prediction>

<div class="ki-card">

`0.80 × 94.97 GiB` budget, minus about `16 GiB` weights and runtime, minus about `2 GiB` activations and graphs, divided by `147,456 B` per token.

</div>

Write your number down, then run `python3 scripts/sizing.py --model primary --precision bf16 --context 8192 --concurrency 16 --gpu-gib 94.97`.

<!--
**Key:** The point of the prediction is to find out whether we understand the memory model well enough to be wrong by less than a few percent, before the server tells us. **Example:** Roughly 57 GiB left for the cache divided by 147,456 bytes gives a bit more than 400,000 tokens; participants who forget the overhead land at 480,000, which is the classic error. **Transition:** Now the server's answer. **Question:** "Can I use the tool instead?" Yes, scripts/sizing.py does the same arithmetic and states its overhead assumption, but write your own number first. **Deeper:** The overhead term in sizing.py is a stated assumption of 4 GiB; the measured value for this model is smaller, and which one you use matters less than comparing it to the log afterwards.
-->

---
layout: experiment
heading: "Measured: formula vs server"
step: measurement
experiment: baseline
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Predicted from the formula" source="measured:benchmark/results/reference/baseline/kv-formula-check.json" metric="predicted_tokens" unit="tokens" note="58.14 GiB ÷ 147,456 B" />
<MetricCard label="Reported by vLLM" source="measured:benchmark/results/reference/baseline/kv-formula-check.json" metric="reported_tokens" unit="tokens" tone="good" note="GPU KV cache size" />
<MetricCard label="Reported ÷ predicted" source="measured:benchmark/results/reference/baseline/kv-formula-check.json" metric="ratio" digits="4" note="one server start" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/kv-formula-check.json" />

<Observation>

Because the formula takes the server's own *available KV memory* as input, this check tests the per-token arithmetic, not the budget. The budget is what you predicted on the previous slide.

</Observation>

<!--
**Key:** Within 0.01 percent, the per-token formula reproduces the capacity the server reports, so the arithmetic from the model's config is the memory model of the engine. **Example:** 58.14 GiB divided by 147,456 bytes predicts 423,363 tokens and the log says 423,328. **Transition:** What does a capacity of 423,328 tokens mean for users? **Question:** "Is it always this exact?" Across restarts we saw about one percent variation in the available memory, so capacity moves a little between starts, but the formula stays. **Deeper:** This honest framing matters: the prediction check uses the logged cache memory, so it validates the bytes-per-token formula only; predicting the budget itself needs the overhead estimate from the previous slide.
-->

---
layout: experiment
heading: "What 423,328 tokens means"
step: explanation
experiment: baseline
---

<div class="ki-grid ki-cols-2">
<div>

The log says **12.92×** for 32,768-token requests.

For our workload (1,200 in, 180 out, so 1,380 tokens each) the same cache would hold about **300 requests**.

</div>
<div>

<Warning title="Capacity is not performance">

Cache space says how many requests *fit*. It does not say how many get a good response time. Compute and memory bandwidth run out long before the cache does, and Day 2 measures where.

</Warning>

</div>
</div>

<!--
**Key:** KV capacity is a ceiling on admitted work, not a promise about latency; on this card with an 8B model the cache is almost never the first thing to run out. **Example:** 423,328 tokens divided by 1,380 tokens per request is about 306 requests that could be resident at once, far more than the number that can all decode quickly. **Transition:** The cache becomes the bottleneck as soon as the card or the context changes, and that is the production consequence. **Question:** "So is the big card wasting memory?" For a single 8B model, mostly yes, which is why we simulate a small card in the context-length experiment. **Deeper:** The 12.92x figure is vLLM's pessimistic bound for requests that all reach the full context length; real traffic is shorter, and prefix sharing makes the real capacity larger still.
-->

---
layout: default
heading: "The same model on a smaller card"
---

| | Workshop GPU | Assumed 24 GiB card |
| --- | --- | --- |
| Memory budget (90 % / 80 %) | about 76 GiB | about 21.6 GiB |
| Weights BF16 | 15.3 GiB | 15.3 GiB |
| Overhead (assumed) | about 3 GiB | about 3 GiB |
| KV cache left | **58.1 GiB** (measured) | **about 3.3 GiB** |
| Tokens at 147,456 B | 423,328 | about 23,500 |

<Consequence>

On the small card the cache holds less than one 32k-token request. Memory is not a detail of the deployment: it *is* the deployment. Options are FP8 weights, FP8 KV cache, a shorter context limit or a smaller model, each with a quality or operations price.

</Consequence>

<!--
**Key:** The same weights on a 24 GiB card leave a few GiB for the cache, so context length and concurrency become hard limits; the right-hand column is arithmetic under stated assumptions, not a measurement. **Example:** About 21.6 GiB budget minus 15.3 GiB of weights minus 3 GiB of overhead leaves 3.3 GiB, or roughly 23,500 tokens, which is less than one request at the full 32k context. **Transition:** Tomorrow we constrain the cache on purpose, with the kv-constrained profile, to watch what the engine does when it runs short. **Question:** "Would you ever run BF16 8B on 24 GiB?" With FP8 weights and a 16k context limit, yes, but measure quality first. **Deeper:** The assumed overhead and the 90 percent utilisation are choices; the point is to redo the arithmetic with your own numbers, and sizing.py is built for that.
-->

---
layout: code
class: ki-code-sm
heading: "Your tool: the sizing script"
file: scripts/sizing.py
---

```bash
python3 scripts/sizing.py --model primary --precision bf16 \
    --context 8192 --concurrency 16 --gpu-gib 94.97
```

```text
WEIGHTS   8.2 B params x 2 bytes =   15.27 GiB
KV CACHE  2 x 36 layers x 8 kv heads x 128 head_dim x 2 bytes = 147,456 bytes/token
          x 8,192 tokens x 16 requests = 131,072 tokens =   18.00 GiB
OVERHEAD  assumed                                       =    4.00 GiB
TOTAL                                                   =   37.27 GiB
GPU: 94.97 GiB x 0.8 utilization = 76.0 GiB budget  ->  FITS
The KV cache can hold about 412,893 tokens, i.e. 50.4 requests of 8,192 tokens at the same time.
```

<!--
**Key:** The script shows the arithmetic line by line and states its overhead as an assumption, so the first thing to do with a real server is to compare its output with the start-up log. **Example:** For sixteen 8k requests it says 37.27 GiB in total and 412,893 tokens of capacity, within 2.5 percent of the server's 423,328, and the difference is the assumed 4 GiB overhead against the real 2 to 3 GiB. **Transition:** In Lab 1 you use it for the four scenarios; in Lab 2 you read the real log line yourself. **Question:** "What if my model has no config in models.yaml?" Pass the numbers by hand with --params-b, --layers, --kv-heads and --head-dim, the usage text shows an example for a 70B model. **Deeper:** For mixture-of-experts models, pass the total parameters for weight memory; active parameters matter for speed, not for memory.
-->
