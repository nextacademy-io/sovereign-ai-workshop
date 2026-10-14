---
layout: section
heading: "GPU fundamentals for inference"
time: "13:30"
minutes: 60
layer: runtime
question: "What limits a GPU when it generates tokens, and how do you find out without memorising a catalogue?"
---

---
layout: statement
---

# On a GPU the question is not "how fast" but "which limit comes first".

<!--
**Key:** Hardware reduces to a handful of numbers, and every inference problem in this workshop is one of them running out: memory capacity, memory bandwidth, compute, or the link between cards. **Example:** Our claim, tested this afternoon: the same Qwen3-8B is limited by bandwidth while it generates and by compute while it reads a long prompt; no catalogue tells you that, the arithmetic does. **Transition:** To use those numbers we need a picture of what is inside the chip, and first of what a GPU is not: a faster CPU. **Question:** "Do I need to know CUDA?" No. You need four numbers and the habit of asking which phase they limit; engines like vLLM carry the kernels. **Deeper:** Everything in this block is public datasheet material, and where NVIDIA does not publish a number (Server Edition boost clock, L2 size) we say so instead of guessing.
-->

---
layout: two-col
heading: "CPU and GPU: latency versus throughput"
---

**CPU:** a few strong cores that finish one task quickly.

**GPU:** thousands of simple lanes that finish many identical operations per second.

A language model is mostly one operation, **matrix multiplication**, repeated for every layer and token.

::right::

| The workshop GPU | Datasheet |
| --- | --- |
| CUDA cores | 24,064 |
| Tensor Cores | 752 |
| Streaming multiprocessors | 188 |
| Memory | 96 GB GDDR7 |
| Memory bandwidth | 1,597 GB/s |

<!--
**Key:** A GPU trades single-task speed for throughput: it wins when the work is the same simple operation applied to a lot of data, which is exactly what a transformer layer is. **Example:** The workshop card has 24,064 CUDA cores and 752 Tensor Cores; a server CPU has far fewer, stronger cores. The CPU can run the same matrix multiplications, llama.cpp and Ollama do it, but it does fewer at once and feeds them from slower memory. **Transition:** Inside the chip the cores are organised into units that we will reuse all afternoon: the streaming multiprocessors. **Question:** "So CPUs are useless for LLMs?" No: a small model at low concurrency can be fine on a CPU; the Day 2 comparison demo shows what changes under concurrency. **Deeper:** NVIDIA's own description: prefill is a matrix-matrix operation that saturates the GPU, decode is closer to matrix-vector and underuses it.
-->

---
layout: default
heading: "Inside the chip: 188 streaming multiprocessors"
---

| Resource | Per SM | × 188 SMs |
| --- | --- | --- |
| CUDA cores | 128 | 24,064 |
| Tensor Cores | 4 | 752 |
| Register file | 256 KB | 48,128 KB |
| L1 cache + shared memory | 128 KB | 24,064 KB |

<Takeaway>

The **SM** is the building block: its own registers, its own fast memory, its own math units. The card is 188 of them side by side, and a kernel is spread over all of them.

</Takeaway>

<!--
**Key:** Every large number in a datasheet is a per-SM resource multiplied by 188, so the SM is the unit to reason with. **Example:** 188 times 128 is the 24,064 CUDA cores of the datasheet, and 188 times 4 is the 752 Tensor Cores; the full GB202 die has 192 SMs and this product enables 188. **Transition:** Of everything in the SM, the Tensor Cores matter most for language models, so let us look at what they do. **Question:** "Where does a thread run?" Threads are grouped in warps of 32 and in blocks; each block is scheduled on one SM. We do not write kernels in this workshop, but the hierarchy explains why small kernels leave SMs idle. **Deeper:** The register-file and L1 totals are the whitepaper's per-die figures divided by 188; the cores-per-SM and Tensor-Cores-per-SM figures are our derivation from the datasheet totals.
-->

---
layout: default
heading: "Tensor Cores: where the FLOPS come from"
---

<Flow :items='[{ "label": "BF16", "sub": "2 bytes per weight", "note": "since Ampere" }, { "label": "FP8", "sub": "1 byte per weight", "note": "since Ada" }, { "label": "FP4", "sub": "0.5 byte per weight", "note": "since Blackwell" }]' />

- A Tensor Core multiplies small matrix tiles and adds the result in **one** operation.
- Transformer layers are matrix multiplications, so most of the peak rate is Tensor Core rate.
- Each generation added a smaller number format: **fewer bytes per weight and a higher peak rate**.

<!--
**Key:** Tensor Cores are the part of the SM that does matrix multiply-accumulate, and each new generation added a smaller number format that both shrinks the model and raises the peak rate. **Example:** Volta introduced Tensor Cores, BF16 arrived with Ampere, FP8 with Ada, FP4 with Blackwell; the workshop card has all of them, but our baseline runs BF16 on purpose. **Transition:** Those peak rates are where datasheets mislead most, so the next slide is about reading them. **Question:** "Why does a smaller format raise the rate?" The same silicon handles more small values per clock, and fewer bytes also mean less to move. Quality is the price, and Day 2 measures it. **Deeper:** Whether a format is fast in your engine also depends on whether kernels exist for your architecture; the vLLM quantization table has no Blackwell column, so run it before you trust it.
-->

---
layout: default
heading: "The datasheet trap: dense and sparse"
---

| Precision | Product page, unlabelled | Dense reading (÷ 2, derived) |
| --- | --- | --- |
| BF16 / FP16 | 1 PFLOP | about 500 TFLOPS |
| FP8 | 2 PFLOPS | about 1,000 TFLOPS |
| FP4 | 4 PFLOPS | about 2,000 TFLOPS |

<Warning title="Which number is it?">

The page does not say sparse, but its figures equal the sparse peaks of the sibling card in NVIDIA's whitepaper. 2:4 structured sparsity needs a specially pruned model. Quote the **dense** number and say "dense".

</Warning>

<!--
**Key:** A peak-rate number without a label can be off by a factor of two, because vendors often print the sparse rate; ordinary checkpoints run dense, so dense is the number that predicts your speed. **Example:** The product page lists 1 PFLOP for FP16; the whitepaper's sparse FP16 for the sibling card is 1,007.6 and its dense rate is 503.8. For GeForce the gap is worse: the RTX 4090's headline 1,321 AI TOPS against 165.2 dense BF16 TFLOPS, about eight times. **Transition:** Compute is half of the picture; the other half is how fast data reaches the cores. **Question:** "What is the Server Edition's dense peak, then?" NVIDIA states none; we use about 504 TFLOPS, derived at the Workstation card's clocks, and treat 468 to 504 as the plausible range. **Deeper:** That is why estimated MFU on the dashboard is good to several percent only; 1,597 GB/s is published.
-->

---
layout: default
heading: "VRAM: capacity and bandwidth are two numbers"
---

| | Workshop GPU | Workstation card, same die | H100 SXM |
| --- | --- | --- | --- |
| Memory type | GDDR7 | GDDR7 | HBM3 |
| Capacity | 96 GB | 96 GB | 80 GB |
| Bandwidth | 1,597 GB/s | 1,792 GB/s | 3,350 GB/s |

Reading all 96 GB once: 96 GB ÷ 1,597 GB/s = **60 ms**.

Reading the 16.38 GB of weights once: **10.3 ms**.

<Takeaway>

Capacity decides what **fits**. Bandwidth decides how fast it can be **read**. Check which card a benchmark used.

</Takeaway>

<!--
**Key:** Capacity and bandwidth are independent properties of the memory system, and this card has a lot of the first and a middling amount of the second. **Example:** One full sweep over 96 GB takes 60 ms, and a decode step is one sweep over the 16.38 GB of weights, 10.3 ms, which is the floor we will compare with a measurement this afternoon. An H100 has less capacity but about twice the bandwidth. **Transition:** Memory is not one pool: the next picture shows the four levels a kernel sees. **Question:** "Why GDDR7 and not HBM?" HBM is stacked next to the GPU die and gives very high bandwidth, GDDR is graphics memory on a wide bus; the workshop card is a 512-bit GDDR7 design. **Deeper:** Published RTX PRO 6000 benchmarks often quote 1,792 GB/s because they used the Workstation or Max-Q card; decode speed scales with that number.
-->

---
layout: default
heading: "Four levels of memory; the weights live in the last one"
---

<D05GpuMemoryHierarchy />

<!--
**Key:** A kernel sees registers, a per-SM L1 and shared memory, one L2 shared by all SMs, and global memory, which is the VRAM; the first three are tiny next to the weights, so every decode step goes to VRAM for them. **Example:** Click once: the 16.38 GB of weights only fit in global memory. Click again: one decode step reads all of them, 16.38 GB at 1,597 GB/s is 10.3 ms, and the L2 holds about one 128th of that. **Transition:** Bandwidth inside one GPU is the number we keep; between GPUs it is a different, much smaller number. **Question:** "Why no bandwidth for L1 and L2?" NVIDIA does not publish one for this card; do not quote numbers you read in a blog. **Deeper:** The L2 size is the Workstation figure of the same die; for the Server Edition it is inferred, hence the asterisk.
-->

---
layout: default
heading: "Between GPUs: PCIe and NVLink"
---

| Link | Per direction | Note |
| --- | --- | --- |
| Own VRAM, workshop GPU | 1,597 GB/s | datasheet |
| PCIe Gen5 x16, workshop GPU | 64 GB/s | its only link to other GPUs: no NVLink (derived from 128 GB/s, both directions) |
| NVLink 4, H100 SXM | 450 GB/s | quoted as 900 GB/s, both directions |
| NVLink 5, Blackwell data center | 900 GB/s | quoted as 1.8 TB/s, both directions |

<Consequence>

Between two workshop GPUs data moves about **25 times slower** than a GPU reads its own memory (1,597 ÷ 64). Tensor parallelism on this card is a trade-off, not free capacity.

</Consequence>

<!--
**Key:** Splitting a model across GPUs means exchanging data at every layer, and without NVLink that exchange goes over PCIe, a link far slower than the memory next to each GPU. **Example:** 1,597 GB/s divided by 64 GB/s is about 25; an H100 on NVLink 4 has 450 GB/s per direction, seven times PCIe Gen5. We test tensor parallelism on a two-GPU pod on Day 2 and report it as a trade-off. **Transition:** A quick look at how the generations got here. **Question:** "Is it really true there is no NVLink?" NVIDIA's own pages do not list one for this card; Lenovo's reprint of the spec sheet says "NVLink support: No"; `nvidia-smi topo -m` on a two-GPU pod will show only PCIe paths. **Deeper:** Always compare like with like: NVIDIA quotes NVLink bidirectionally and PCIe sometimes per direction, sometimes doubled; the table halves the bidirectional figures.
-->

---
layout: default
heading: "GPU generations: what each one added for inference"
---

| Generation | Examples | Added for inference |
| --- | --- | --- |
| Volta | V100 | first Tensor Cores |
| Ampere | A100, A10 | BF16 and TF32, 2:4 sparsity, MIG, NVLink 3 |
| Ada | L4, L40S, RTX 4090 | FP8 Tensor Cores, GDDR memory |
| Hopper | H100, H200 | Transformer Engine (FP8), HBM3 and HBM3e, NVLink 4 |
| Blackwell | B200, RTX PRO 6000 | FP4, NVLink 5 on data-center parts, GDDR7 on RTX parts |

<Takeaway>

"Blackwell" is a family, not a specification. The RTX PRO 6000 is compute capability 12.0 and the B200 is 10.0: different instruction targets.

</Takeaway>

<!--
**Key:** Each generation added a lower precision, more memory bandwidth or a faster link; none of them changed the basic constraint that decode waits for memory. **Example:** The A100 has no FP8; an Ada or Hopper card has; only Blackwell has FP4. And the workshop card shares a name with the B200 but not its memory, link or instruction target, so "Blackwell supported" does not mean "this card supported". **Transition:** Instead of memorising this table, we compress any card into four numbers. **Question:** "Is vLLM verified on this card?" The vLLM documentation never names it; the release notes contain SM120 fixes, and our own baseline runs with vLLM 0.31.0 are the evidence we have. **Deeper:** Treat generation as a hint about which formats and kernels exist, then verify by running.
-->

---
layout: default
heading: "Reason from four numbers, not from the name"
---

| The question | The number | What it decides |
| --- | --- | --- |
| Does it fit? | memory capacity | model, context length and concurrency |
| How fast does one request generate? | memory bandwidth | decode speed per request |
| How fast is a long prompt read? | dense compute at your precision | prefill time, so TTFT |
| Can several GPUs cooperate? | interconnect | the cost of tensor parallelism |

<Takeaway>

Ask for these four numbers, dense and per direction, for the precision you will actually run.

</Takeaway>

<!--
**Key:** Any card, including one that does not exist yet, can be judged by capacity, bandwidth, dense compute and interconnect, each tied to a question you will have to answer in a design. **Example:** For a new card with 48 GB and 864 GB/s, the first number says whether Qwen3-8B plus a cache fits, the second that a single-request decode step has a floor about twice as long as here, because bandwidth sets it. **Transition:** One more number combines two of these and tells us which phase is limited by what: the ops-to-byte ratio. **Question:** "Where is price in this list?" Outside it on purpose: cost per useful workload comes on Day 2 from measured tokens per second, not from the datasheet. **Deeper:** Power and cooling matter too: the Server Edition is passively cooled with a configurable limit, so sustained clocks depend on the chassis.
-->

---
layout: default
heading: "ops:byte: how much math per byte the card can feed"
---

<Formula :terms='[{ "t": "PEAK COMPUTE", "sub": "503.8 TFLOPS dense BF16" }, { "op": "÷" }, { "t": "PEAK BANDWIDTH", "sub": "1,597 GB/s" }, { "op": "=" }, { "t": "OPS:BYTE", "sub": "about 315 FLOP per byte", "hot": true }]' />

A kernel that does **fewer** FLOP per byte than this waits for memory. One that does **more** waits for the math units.

<Observation>

ops:byte is a property of the **hardware**. FLOP per byte is a property of the **work**. Their comparison decides the limit.

</Observation>

<!--
**Key:** NVIDIA calls the ratio of peak math rate to peak memory rate the ops:byte ratio; it is the break-even intensity between memory-limited and math-limited work. **Example:** 503.8 TFLOPS divided by 1,597 GB/s is 315 FLOP per byte; if the Server Edition runs at lower clocks, with 468 TFLOPS, it is 293, so say "about 300" and do not quote three digits. **Transition:** How do other cards compare on this ratio? **Question:** "Is 315 a precise figure?" No, it uses a derived peak; the memory half is published, the compute half is the uncertain one. **Deeper:** The ridge is quoted per precision: with FP8 Tensor Cores the dense rate is about twice as high, so the FP8 ridge is about 630. We use the BF16 figure because the baseline runs BF16.
-->

---
layout: default
heading: "Cards differ more in bandwidth than in ops:byte"
---

| GPU | Memory | Bandwidth (GB/s) | Dense BF16 (TFLOPS) | ops:byte |
| --- | --- | --- | --- | --- |
| RTX PRO 6000 Server (workshop) | 96 GB | 1,597 | about 504 | 315 |
| H100 SXM | 80 GB | 3,350 | 989.5 | 295 |
| A100 80 GB PCIe | 80 GB | 1,935 | 312 | 161 |
| L40S | 48 GB | 864 | 362 | 419 |
| L4 | 24 GB | 300 | 121 | 403 |
| RTX 4090 | 24 GB | 1,008 | 165.2 | 164 |

<Observation>

Bandwidth spans 11× in this table, ops:byte only 2.6×. On every one of these cards a single-request decode sits far below the ridge.

</Observation>

<!--
**Key:** The hardware ratio is roughly the same across very different cards, so what changes the user-visible speed from card to card is mostly bandwidth, and what changes what fits is capacity. **Example:** From 300 GB/s (L4) to 3,350 GB/s (H100) is 11 times; from 161 to 419 FLOP per byte is 2.6 times. A card with a ridge near 300 needs about 300 tokens per weight read to be compute-bound. **Transition:** Let us put the two phases of one request on this ratio. **Question:** "Why is the RTX 4090 at 165 and not 330?" BF16 serving accumulates in FP32, and GeForce runs that at half the FP16-accumulate rate; the workshop card does not have that penalty. **Deeper:** All rows are dense peak values; the Server Edition row uses the derived 503.8 and H100 and L40S are the datasheet's sparse numbers divided by two where NVIDIA's footnote says so.
-->

---
layout: default
heading: "Same model, same card, two different limits"
---

<D06ComputeVsBandwidth />

<!--
**Key:** For each phase there are two minimum times, one for the math and one for moving the weights, and the longer one is the limit; prefill is math-limited, decode is memory-limited. **Example:** Click through: a 1,200-token prefill needs at least 39 ms of math and 10.3 ms to read the weights once, so math wins; a decode step needs 0.03 ms of math for one token and still 10.3 ms to read the weights, so the math needs about 0.3 percent of the step. **Transition:** The roofline draws exactly this on one chart. **Question:** "Is 39 ms the real prefill time?" No, it is a floor at peak rate; we will compare it with a measured TTFT in the next hour and a half. **Deeper:** Batching fills the gap: 64 sequences share one weight read, so the math grows 64-fold while the memory time stays 10.3 ms.
-->

---
layout: default
heading: "The roofline: a map of what limits what"
---

<D07Roofline />

<!--
**Key:** The roofline plots attainable performance against arithmetic intensity: a slanted memory roof up to the ridge point, then a flat compute roof; the position of a workload on the x axis tells you which roof it is under. **Example:** Click once: decode with one sequence is 1 FLOP per byte and with 64 sequences 64 FLOP per byte, both far left of 315, so bandwidth sets the speed and batching moves the dot to the right for free. Click again: a 1,200-token prefill is right of the ridge. **Transition:** One more hardware reading you will meet in the lab, the utilisation gauge, because it says something different. **Question:** "Does this need maths?" No more than shown: roof = min(peak, bandwidth × intensity), used only to decide which resource to look at. **Deeper:** Williams, Waterman and Patterson introduced it; their x axis is operational intensity, NVIDIA says arithmetic intensity.
-->

---
layout: default
heading: "GPU-Util: busy is not the same as efficient"
---

<div class="ki-grid ki-cols-3">
<MetricCard label="GPU-Util, mean" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="gpu.utilization_pct.mean" unit="%" digits="1" note="nvidia-smi, 1 s samples" />
<MetricCard label="Requests running, max" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="server.gauges.num_requests_running.max" digits="0" note="one request at a time" />
<MetricCard label="Output tokens per second" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="aggregate_tps" unit="tok/s" digits="1" note="the whole server" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

<Warning title="What the gauge says">

`utilization.gpu` is the share of time **any** kernel was running. It does not say how many of the 188 SMs, Tensor Cores or how much bandwidth were in use. Judge the work by tokens per second and the engine's own metrics.

</Warning>

<!--
**Key:** The gauge reads about 99 percent while the server handles one request at a time, which shows it measures "something was running", not how well the hardware was used. **Example:** In the reference run one request is in flight and the GPU averages 99.1 percent. Day 2 measures what the card delivers with more requests in flight; our prediction is that the gauge cannot tell the difference. In Lab 2 you will see 100 percent for a single request. **Transition:** Let us close by putting hardware and the two phases into one table. **Question:** "What should I watch instead?" Tokens per second against the bandwidth bound, running and waiting requests, KV-cache usage and, on your own hardware, DRAM-active and tensor-active. **Deeper:** Profiling counters need privileges a rented pod lacks, so the dashboard uses power and the engine's estimated MFU and MBU as relative signals.
-->

---
layout: default
heading: "Which phase is limited by what"
---

| | Prefill | Decode |
| --- | --- | --- |
| Tokens per weight read | the whole prompt | one per request |
| Intensity vs ridge (about 315) | far above for long prompts | far below |
| Limited by | compute | memory bandwidth |
| The spec that helps | dense TFLOPS at your precision | GB/s, fewer bytes per weight, more requests sharing a read |
| User-visible metric | TTFT | inter-token latency |

<Consequence>

This is a hypothesis built from datasheets. This afternoon we test it against one measured run, and on Day 2 against changes of prompt length, concurrency and precision.

</Consequence>

<!--
**Key:** The two phases of a request sit on opposite sides of the ridge point, so the same card is compute-limited while it reads the prompt and bandwidth-limited while it writes the answer, and different tricks help each. **Example:** Quantizing weights shortens decode steps by cutting bytes read but does little for a compute-bound prefill; batching fills the memory-bound decode and barely helps a prefill that saturates the math. **Transition:** Next is sizing: what fits in the 96 GB. We return to prefill and decode in the mechanics block, with a prediction and a measurement. **Question:** "Is the prefill row always true?" For short prompts with few tokens per pass it is closer to the ridge; the claim gets sharper with prompt length and is tested on Day 2. **Deeper:** Chunked prefill and prefix caching change how much prefill work a request pays; they are Day 2 topics.
-->
