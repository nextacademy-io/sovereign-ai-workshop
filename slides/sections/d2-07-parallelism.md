---
layout: section
heading: "Parallelism: replicas, tensor, pipeline, expert"
time: "15:15"
minutes: 45
layer: runtime
question: "When does a second GPU make a deployment faster, and when does it only make it bigger?"
---

---
layout: default
heading: "Four ways to use more than one GPU"
---

| Strategy | What is split | What the GPUs exchange | vLLM option |
| --- | --- | --- | --- |
| Replicas (data parallel) | the requests | nothing per token | `--data-parallel-size`, or separate servers behind a load balancer |
| Tensor parallel | the matrices of every layer | partial results, twice per layer | `--tensor-parallel-size` |
| Pipeline parallel | the layers, into stages | the activations between stages | `--pipeline-parallel-size` |
| Expert parallel | the experts of a mixture-of-experts model | the tokens, to the GPUs holding their experts | `--enable-expert-parallel` |

<Takeaway>

Replicas add requests in flight. The other three spread one model over several GPUs. Whether that lowers latency depends on the link.

</Takeaway>

<!--
**Key:** Four answers to "what do we do with a second GPU", told apart by what is split and what the cards must say to each other: the last column decides what you pay. **Example:** Replicas: each GPU holds the whole model and serves its own requests; vLLM's data-parallel option replicates the weights behind one endpoint, each engine with its own KV cache, so prefix-cache hits depend on routing. Tensor: every layer cut in two, a synchronisation per half-layer. Pipeline: consecutive layers on different GPUs, fed with micro-batches. Expert: only for mixture-of-experts models; the expert-parallel size is tensor times data parallel size. **Transition:** Draw the first two. **Question:** "Which one first?" Replicas, whenever the model fits one GPU. **Deeper:** The Megatron-LM scaling paper in the references puts tensor parallelism inside a node and pipeline parallelism across nodes.
-->

---
layout: default
heading: "Tensor parallelism next to replicas"
---

<D11TensorParallelism />

<!--
**Key:** The same two GPUs, two different bets: split the work of one request across both, or give each GPU its own requests. **Example:** Click 1: every layer is cut in half; after the attention part and after the MLP part the GPUs add their partial results (an all-reduce): 2 times 36 layers, 72 per decode step. The only link on this card is PCIe Gen5, 64 GB/s per direction; NVIDIA does not list NVLink for it and Lenovo's reprint of the spec says no. Click 2: replicas share nothing; a load balancer sends each request to one GPU. **Transition:** Numbers for the left side. **Question:** "Does tensor parallelism double the KV cache?" Each GPU holds half the weights and 4 of the 8 KV heads, so more bytes are free on each card: capacity, not latency. **Deeper:** Day 3 returns to replicas behind a load balancer.
-->

---
layout: default
heading: "Tensor parallelism: the arithmetic"
---

| Per decode step | One GPU | TP = 2, ideal split |
| --- | --- | --- |
| Weights read by each GPU | 16.38 GB | 8.19 GB |
| Floor at 1,597 GB/s | 10.3 ms | 5.1 ms |
| KV heads per GPU | 8 | 4 |
| All-reduces | 0 | 2 × 36 layers = 72 |

<Observation>

The bandwidth arithmetic promises up to 5.1 ms saved per step. The price is 72 synchronisations between two cards. Does the saving cover them?

</Observation>

<!--
**Key:** The best case halves the bytes each GPU must read; the bill is 72 synchronisation points per step, and the question of this block is whether the saving covers it. **Example:** Qwen3-8B has 36 layers; after attention and after the MLP of each layer the partial results are summed across the two GPUs, 72 per decode step. The 5.1 ms is the datasheet floor of an ideal split; the measured single-GPU step is 11.6 ms. **Transition:** What exactly travels over the link? **Question:** "Where does the count of 72 come from?" From the layer structure, as written in the experiment note; it has never been measured here. **Deeper:** For a model that does not fit one GPU, halving the weights per card is the main reason tensor parallelism exists, and then the latency question is secondary.
-->

---
layout: default
heading: "What crosses the link in one step"
---

<Formula :terms='[{ "t": "tokens in the step" }, { "op": "×" }, { "t": "4,096", "sub": "hidden size" }, { "op": "×" }, { "t": "2 B", "sub": "BF16" }, { "op": "=" }, { "t": "payload of one all-reduce", "hot": true }]' />

| Step | Tokens | Payload | Transfer at 64 GB/s | × 72 |
| --- | --- | --- | --- | --- |
| decode, 1 request | 1 | 8 KiB | 0.13 µs | 9 µs |
| decode, 16 requests | 16 | 128 KiB | 2.0 µs | 0.15 ms |
| prefill, 1,200-token prompt | 1,200 | 9.4 MiB | 154 µs | 11 ms |

<Takeaway>

Decode messages are tiny: the fixed cost of 72 synchronisations decides. Prefill messages are large: bandwidth decides. Transfer time only, a lower bound.

</Takeaway>

<!--
**Key:** In decode each all-reduce carries a few kilobytes, so bandwidth hardly matters and the fixed latency of 72 synchronisations decides; in prefill the messages are megabytes and bandwidth enters. **Example:** One decode token is 4,096 values of 2 bytes, 8 KiB: a tenth of a microsecond at 64 GB/s, under 10 microseconds over 72. A 1,200-token prompt is 9.4 MiB per all-reduce, 154 microseconds, 11 ms over 72, against a measured TTFT of 70 ms on one GPU. Neither includes the fixed latency of an all-reduce, which no source here measured. **Transition:** Now what replicas give. **Question:** "What would NVLink change?" Seven times the bandwidth per direction (450 against 64 GB/s), which should matter mostly for prefill; the fixed latency is a separate question. **Deeper:** For NVSwitch and the network our sources give no figures; slower links cost more per synchronisation.
-->

---
layout: default
heading: "Two replicas: arithmetic from one GPU"
---

<ResultTable
  source="measured:benchmark/results/reference/concurrency"
  :match='["baseline-c001", "baseline-c008", "baseline-c016", "baseline-c032"]'
  :columns='["concurrency", "aggregate_tps", "output_tps_per_request.p50", "ttft_ms.p95"]'
  :headers='["Clients on one GPU", "Aggregate tokens/s", "Tokens/s per request", "TTFT p95 (ms)"]'
  :digits='{ "output_tps_per_request.p50": 1 }'
/>

<div class="ki-grid ki-cols-2">
<div>

| Arithmetic from the table | At best |
| --- | --- |
| Two replicas, 16 clients each | 2 × 900.0 = 1,800 tokens/s |
| One GPU, 32 clients | 1,294.3 tokens/s |
| Per user, 32 clients on two replicas | 68.7 instead of 51.0 tokens/s |

</div>
<Warning title="Best case, not measured">

Nothing is shared in this arithmetic. The load balancer, the host and the prefix cache are: each replica has its own cache.

</Warning>
</div>

<!--
**Key:** A second replica is the cheapest capacity because nothing is exchanged between GPUs; the figures are arithmetic from the one-GPU measurement, not a measurement of two. **Example:** One GPU delivers 900 tokens per second with 16 clients and 1,294 with 32. Two replicas with 16 clients each: 2 times 900, 1,800 at best, about 1.4 times one GPU at 32 clients, and every user keeps the speed of the 16-client row. For the course SLO of 20 users, 10 per replica sits between the 8 and 16 rows, so TTFT p95 should stay under 800 ms: reasoned, not measured. **Transition:** Mixture of experts: another reason for several GPUs. **Question:** "And for one request?" Its speed stays at the one-GPU level: a replica does not help a single user. **Deeper:** Routing matters: a prefix cached on replica A gains nothing on replica B.
-->

---
layout: two-col
heading: "Pipeline and expert parallelism"
---

### Pipeline

Consecutive layers sit on different GPUs. Micro-batches keep every stage busy; the idle time is the pipeline bubble. Stages hand over activations at their boundaries.

Usual placement: tensor parallelism inside a node, pipeline parallelism across nodes.

::right::

### Expert

A mixture-of-experts layer has many expert networks, and a router sends each token to a few. Expert parallelism puts different experts on different GPUs and ships the tokens to them.

<Warning title="Not run here">

MoE only; the size is tensor times data parallel size. Open Blackwell reports concern MoE kernels (RESEARCH 3.3).

</Warning>

<!--
**Key:** Pipeline parallelism cuts the model by depth, expert parallelism by experts; both exist because some models do not fit one GPU, and both pay for communication differently from tensor parallelism. **Example:** A pipeline stage passes activations to the next stage once, so it should tolerate slower links than a per-layer synchronisation, which fits the placement in the Megatron-LM scaling paper: across nodes. The price is the bubble while stages fill and drain. Expert parallelism sends each token to the GPUs holding its experts and back. **Transition:** The mixture-of-experts side needs one more look: memory against speed. **Question:** "Do we run any of this?" No: single-GPU pods; these are slides, not experiments. **Deeper:** GPipe and GShard in the references describe the bubble and the all-to-all dispatch; no vLLM profile of ours uses either.
-->

---
layout: default
heading: "Mixture of experts: stored against active"
---

| | Qwen3-8B, dense | Qwen3-30B-A3B-FP8, MoE |
| --- | --- | --- |
| Weights resident in VRAM | 16.38 GB | 32.45 GB |
| Parameters used per token | 8.2 B | 3.3 B of 30.5 B (8 of 128 experts) |
| Weight bytes one token needs | 16.38 GB | about 3.5 GB (3.3 ÷ 30.5 × 32.45) |
| Floor of a one-token step, if only those are read | 10.3 ms | about 2.2 ms |

<Warning title="A ceiling, not a prediction">

Arithmetic from `config/models.yaml`. The MoE demo was not run in the validation. More requests per step touch more experts, and the kernels need testing on this GPU.

</Warning>

<!--
**Key:** A mixture-of-experts model has two sizes: what must sit in VRAM, all the experts, and what one token uses, a few. Memory follows the first; compute, and at best the bytes read per token, follow the second. **Example:** Qwen3-30B-A3B needs 32.45 GB resident, twice the dense 8B in BF16, yet a token uses 3.3 B of 30.5 B parameters: a best-case floor of about 2.2 ms for a one-token step against 10.3. With many requests per step, different tokens choose different experts, more of the 32.45 GB is read, and the ceiling falls: reasoning, not measured. **Transition:** Now the experiment we wrote and did not run. **Question:** "Is MoE faster on this card?" Unknown: the demo was not run, and open Blackwell reports concentrate on MoE kernels. **Deeper:** DeepSeek and Kimi (alternatives in models.yaml) do not fit one 96 GB card: there expert parallelism matters.
-->

---
layout: experiment
heading: "Experiment: written, not run"
step: experiment
experiment: tensor-parallel
---

<ExperimentCard
  name="tensor-parallel"
  variable="one GPU, tensor parallelism across two GPUs, and two replicas (one server per GPU)"
  :profiles='["baseline", "tp2", "baseline-replica"]'
  workload="1,200 input, 180 output tokens; 1, 8 and 32 clients; replicas share the clients, half each"
  :metrics='["ITL", "TTFT", "aggregate tokens/s", "tokens/s per request", "GPU power", "nvidia-smi topo -m"]'
  hypothesis="Tensor parallelism pays an all-reduce per layer over PCIe, so its latency gain is smaller than the bandwidth arithmetic suggests. Two replicas give more total throughput."
/>

`tp2` runs at `gpu-memory-utilization` 0.80, like the baseline, for a fair comparison. The embedding server is stopped.

<!--
**Key:** The design is complete and honest about its hypothesis: three setups at the same total load, one variable each, and the topology printed next to the results so nobody argues about the link. **Example:** One GPU gives the reference at 1, 8 and 32 clients. TP=2 serves one model on both GPUs at the same levels. The replica run starts two servers, one per GPU on ports 8000 and 8001, each driven by its own harness process with half of the clients, at 8 and 32 in total; throughputs add, latency percentiles are kept per replica. **Transition:** Before anything is known, you commit. **Question:** "Why the same memory setting for tp2?" So the KV pools are comparable; the profile's own default is higher. **Deeper:** The runner is experiments/runner.py, experiment tensor-parallel; it needs a pod with two GPUs.
-->

---
layout: experiment
heading: "Predict: commit before anyone knows"
step: prediction
experiment: tensor-parallel
---

<Prediction>

Write a factor against one GPU for every row, and the reason. The floor arithmetic allows tensor parallelism at most twice the speed at one client. Replicas can at most double the aggregate.

</Prediction>

| Setup, against one GPU | Metric | Your call |
| --- | --- | --- |
| TP = 2, 1 client | ITL p50 | ? |
| TP = 2, 32 clients | aggregate tokens/s | ? |
| Two replicas, 32 clients in total | aggregate tokens/s | ? |
| Two replicas, 32 clients in total | tokens/s per request | ? |

<!--
**Key:** Asking for a factor forces a model of the link: the room has the floor (5.1 against 10.3 ms), the 72 all-reduces and the 64 GB/s, and no data. Wrong cells will be informative, not embarrassing. **Example:** Give five minutes in the groups. Common answers: tensor parallelism nearly halves ITL (ignoring the link), or makes it worse (ignoring the saved bytes). Ask the replica rows separately: most groups say aggregate doubles and per-request speed stays; the interesting question is the tokens per second per request against one GPU at 32 clients, which should rise because each replica carries 16. **Transition:** Here is what we can actually show. **Question:** "Can I answer with a range?" Yes; a range is a better prediction than a point. **Deeper:** Collect the cells: if the experiment is ever run, the sheet is the comparison.
-->

---
layout: experiment
heading: "Measurement: not run in the validation"
step: measurement
experiment: tensor-parallel
---

<div class="ki-grid ki-cols-2">
<Warning title="There is no result">

No pod with two RTX PRO 6000 GPUs could be created: the stock read "Out". The block therefore states no speed for tensor parallelism.

</Warning>
<div class="ki-card">

### What exists

The runner and the profiles. The function that adds the replicas' throughput is unit-tested. The two-server start and the `tp2` start never ran on hardware: expect problems with NCCL shared memory and the start order.

</div>
</div>

<Observation>

What we can do instead: argue from the datasheet and from the one-GPU measurements, and say which parts are arithmetic. See `experiments/tensor-parallel/RESULTS.md`.

</Observation>

<!--
**Key:** Say it plainly: this is the one experiment of the day with no data, and the room should not leave thinking they saw a result. **Example:** The first attempt to create the pod returned that no instances were available with the requested specification; a later read of the capacity showed two-GPU stock as Out on both CUDA versions. The runner and the three profiles are written, the combination of the replicas' throughput is unit-tested, and the process handling for two servers has never run. Ask the room how they would want to be told. **Transition:** What would we need to see to change our mind? **Question:** "Can we rent a pod now?" Possibly, but a first run needs time to debug; RESULTS lists what to budget. **Deeper:** A trainer demo on a two-GPU machine, if one is available, turns this slide into a result; until then the label stays.
-->

---
layout: experiment
heading: "What would change our mind"
step: explanation
experiment: tensor-parallel
---

<Formula :terms='[{ "t": "5.1 ms", "sub": "saved per step, ideal" }, { "op": "÷" }, { "t": "72", "sub": "all-reduces" }, { "op": "=" }, { "t": "71 µs", "sub": "each, at most", "hot": true }]' />

| If the measurement shows | Our reading |
| --- | --- |
| TP ITL near 5 to 6 ms | the link is not the bottleneck: the hypothesis is wrong |
| TP ITL near the one-GPU step or above | the all-reduces eat the saving, as predicted |
| replicas below twice the one-GPU aggregate at 16 clients each | something is shared that we missed |
| `nvidia-smi topo -m` shows an NV entry | the link assumption is wrong |

<!--
**Key:** A hypothesis is useful only if we can say in advance what would refute it; here the break-even comes from the datasheet and the layer count. **Example:** 10.3 minus 5.1 leaves 5.1 ms of ideal saving, over 72 all-reduces: 71 microseconds each at most, assuming an ideal split and no overlap. If a PCIe synchronisation costs less, tensor parallelism wins at one client; if more, it loses. We predicted a small gain or a loss; the experiment would decide. The last row guards the premise: the research notes expect only PIX, PXB, PHB, NODE or SYS paths on this card. **Transition:** Which lever for which goal? **Question:** "Is 71 microseconds a lot for PCIe?" No source here measures it; that is why it is the experiment. **Deeper:** Real kernels overlap communication and compute does not halve perfectly: read 71 as a scale, not a threshold.
-->

---
layout: experiment
heading: "Which lever for which goal"
step: consequence
experiment: tensor-parallel
---

| Goal | Lever | Evidence in this workshop |
| --- | --- | --- |
| More users at the same speed each | replicas | arithmetic from one GPU: not measured |
| A model larger than one GPU | tensor or pipeline parallelism; experts for MoE | none: bigger, not faster |
| Lower latency of one request | FP8 weights on one GPU first; tensor parallelism with a fast link | FP8 measured, tensor parallelism a hypothesis |
| The 20-user SLO on this card | a second replica, FP8 weights, or a looser SLO | each reasoned from measurements |

<Consequence>

Compare a second GPU with the options that stay on one. A second GPU adds cost, a link to operate and a failure mode; say what it buys in the metric of the SLO.

</Consequence>

<!--
**Key:** The block ends with a decision table: each goal has a different lever, and the evidence column is as important as the lever, because most rows rest on arithmetic and one on a measurement. **Example:** For 20 users the one-GPU results miss the TTFT target slightly; three ways out are named in the concurrency results: a second GPU used as a replica, FP8 weights, or a looser SLO. Lab 4 lets groups measure the one-GPU options. A model that does not fit one card is the only case where tensor or pipeline parallelism is not optional. **Transition:** The last sentence of the day's technical part, then Lab 4. **Question:** "Would you buy a second card?" For capacity and availability, a replica; for one request's latency, only after measuring the link. **Deeper:** Day 3 covers replicas behind a load balancer, health checks and scaling policy.
-->

---
layout: statement
---

# More GPUs do not automatically mean lower latency.

<!--
**Key:** More GPUs buy capacity or size; latency is bought by moving fewer bytes per step, and the bytes live on one GPU unless the link between cards is fast enough to share the work. **Example:** Replicas for users, tensor or pipeline parallelism for models that do not fit, FP8 weights for latency on one card. If a group's recommendation in Lab 4 or the Day 3 architecture says add a GPU, ask which metric it improves and what the link costs. **Transition:** Lab 4 now: each group tests one hypothesis on its own server, with a baseline, one change and a trade-off. **Question:** "Is tensor parallelism ever worth it for latency?" It depends on the link and the model; on PCIe it is the hypothesis we could not test here. **Deeper:** The research notes call tensor parallelism on this card a trade-off, not a scaling recipe.
-->
