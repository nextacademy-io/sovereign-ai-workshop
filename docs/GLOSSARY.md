# Glossary

Short definitions of the terms the workshop uses, in alphabetical order. Each entry ends with a pointer to where the topic is covered:

- `RESEARCH n` is section n of [RESEARCH.md](RESEARCH.md), which holds the sources.
- `METRICS n` is section n of [METRICS.md](METRICS.md), which holds the measurement definitions.
- A block id such as `d1-07` is a block of the agenda in [CURRICULUM.md](CURRICULUM.md).

Where a number appears, it is a derived or datasheet value. Measured values are in `benchmark/results/` and in METRICS.

## A

- **Active parameters.** In a mixture-of-experts model, the parameters used for one token: the shared layers plus the few experts the router picked. Compute per token follows the active count, while memory still has to hold every parameter. Qwen3-30B-A3B has 30.5 billion in total and 3.3 billion active. Where: RESEARCH 5.1; `d1-02`, `d1-03`.
- **Agent.** An application loop in which a model chooses tools, reads their results and decides the next step until a goal is reached. One user request becomes several model calls, so an agent multiplies token use and GPU load. In the workshop demo one question took three model calls (indicative smoke run). Where: RESEARCH 13.6; `d3-07`.
- **Aggregate TPS.** Output tokens per second delivered by the whole server over a run: all generated tokens divided by the run duration. It is the operator's throughput number, not the speed one user sees, and it is not request throughput, which counts completed requests per second. Where: METRICS 3.
- **Air-gapped operation.** Running with no route to the internet: model files come from a local cache and telemetry is switched off. "Offline" is a property to test for each software version, not a flag to trust. Where: RESEARCH 3.6, 13.11; `d3-05`.
- **Arithmetic intensity.** The FLOP an operation performs per byte it moves from memory. Compared with the GPU's ops:byte it tells you whether the operation waits for memory or for the math units. Where: RESEARCH 6.4, 6.10; METRICS 12; `d1-07`.
- **AWQ.** Activation-aware weight quantization. It stores weights as 4-bit integers and uses activation statistics to protect the channels that matter most. Activations stay in 16-bit. Treat it as "test before you promise" on this GPU. Where: RESEARCH 8.5; `d2-06`.

## B

- **BF16.** A 16-bit floating-point format with the exponent range of FP32 and fewer mantissa bits. It uses 2 bytes per parameter and is the default precision of the workshop models. Where: RESEARCH 5.1, 6.1.

## C

- **Chunked prefill.** The scheduler cuts a long prompt into pieces that share each engine step's token budget with the running decodes. One long prompt then slows the others a little instead of freezing them. Where: RESEARCH 3.9; `d2-04`.
- **Chunking.** In RAG, splitting documents into pieces before they are embedded. Chunk size decides whether retrieval finds the right passage and how many extra prompt tokens each answer costs. Where: `d3-06`; RESEARCH 3.12.
- **Closed-loop load.** A load pattern in which a fixed number of users each wait for an answer before sending the next request. When the server slows down, the offered load drops with it, which can hide queueing. Where: METRICS 7; RESEARCH 10.5.
- **Context window.** The largest number of tokens, prompt and output together, a model handles in one request. It caps the KV cache one sequence can need. Where: RESEARCH 5.1, 5.2; `d2-05`.
- **Continuous batching.** The scheduler adds new requests to the running batch and removes finished ones at every step, instead of waiting for a whole batch to finish. The GPU stays full even when requests arrive at different times and have different lengths. Where: RESEARCH 3.9; `d2-04`.
- **Coordinated omission.** A load-test bias. A client that waits for each reply before sending the next stops sampling while the server stalls, so the slow period is under-represented and the percentiles look too good. Where: METRICS 7; RESEARCH 10.5.
- **CUDA graphs.** A recorded sequence of GPU kernel launches that is replayed as one unit, which removes launch overhead from small decode steps. vLLM captures them at start-up, which takes time and some memory. Where: RESEARCH 3.4, 3.8; `d1-08`.

## D

- **Data minimisation.** The GDPR principle that personal data must be adequate, relevant and limited to what is necessary (Art. 5(1)(c)). For inference it means: log request metadata such as ids, token counts and latency, and do not keep prompt and response bodies by default. Where: RESEARCH 12.8, 13.12; `d3-05`.
- **Data parallelism.** Several full copies of the model, each serving its own requests behind one endpoint. It raises throughput and does not shorten a single request. Every copy has its own KV cache. Where: RESEARCH 3.13; `d2-07`.
- **DCGM.** NVIDIA's Data Center GPU Manager. Its exporter publishes GPU metrics to Prometheus under names that start with `DCGM_FI_`. The profiling fields need extra privileges, so the workshop pods use an NVML-based exporter that reuses the same names. Where: RESEARCH 6.9; METRICS 10.
- **Decode.** The phase after prefill. The model produces output tokens one at a time, and each step reads all the weights and the KV cache. With typical batch sizes it is limited by memory bandwidth. Where: RESEARCH 6.10; METRICS 12; `d1-07`.
- **Dense and sparse TFLOPS.** Vendor peak rates are often quoted for 2:4 structured sparsity, which doubles the headline number. The dense rate is the one a normal model gets. This repository quotes dense values and says so. Where: RESEARCH 6.1.
- **Dense model.** A model that uses all of its parameters for every token, as opposed to a mixture-of-experts model. Qwen3-8B is dense. Where: RESEARCH 5.1.
- **DPA (data processing agreement).** The contract under GDPR Art. 28 in which a processor promises to handle personal data only on the controller's documented instructions, with security duties and rules for sub-processors. A GPU provider that can touch your data is a processor. Where: RESEARCH 7.10, 12.8; `d3-05`.

## E

- **Embeddings.** Lists of numbers that represent a piece of text so that similar meanings lie close together. An embedding model produces them (the workshop uses Qwen3-Embedding-0.6B) and retrieval compares them. Where: RESEARCH 3.12, 5.1; `d3-06`.
- **End-to-end latency.** The time from the start of the request clock to the end of the response stream. It is TTFT plus the time to decode the rest. Where: METRICS 3.
- **Expert parallelism.** For mixture-of-experts models, the experts live on different GPUs and each token is sent to the GPU that holds the expert it needs. It applies to MoE models only. Where: RESEARCH 3.13; `d2-07`.

## F

- **FP8.** An 8-bit floating-point format. FP8 weights halve the bytes read per decode step compared with BF16, apart from layers kept in higher precision. Qwen3-8B-FP8 needs 8.85 GiB in memory against 15.27 GiB (indicative smoke run), because embeddings and the output head stay in BF16. Where: RESEARCH 8.2; METRICS 12; `d2-06`.

## G

- **GDDR and HBM.** Two kinds of GPU memory. HBM is stacked next to the GPU die and gives very high bandwidth, as on H100 (3,350 GB/s). GDDR is graphics memory on a wide bus. The workshop GPU has 96 GB of GDDR7 at 1,597 GB/s. Where: RESEARCH 6.2, 6.5; `d1-05`.
- **Goodput.** The rate of requests that meet the SLO. The harness measures it at one tested load. The DistServe paper means the highest rate per GPU at which a stated share of requests still meets the SLO, which needs a sweep. Where: METRICS 3, 14; RESEARCH 10.5.
- **GPTQ.** A post-training method that rounds weights to 3 or 4 bits layer by layer, using calibration data to keep the output error small. Like AWQ it is weight-only. vLLM supports it through GPTQModel and Marlin kernels. Where: RESEARCH 8.5; `d2-06`.
- **gpu-memory-utilization.** The vLLM option that sets the share of total GPU memory one server instance may budget for weights, activation peaks, CUDA graphs and KV cache. The default is 0.92. The workshop uses 0.80 and gives the embedding server 0.08. Where: RESEARCH 3.4, 3.12; `d1-06`.
- **GPU-Util.** The `nvidia-smi` field `utilization.gpu`: the share of the sampling period in which at least one kernel was running. It tells you the GPU is not idle. It does not tell you how efficiently it works. Where: RESEARCH 6.7; METRICS 10.
- **GQA (grouped-query attention).** Several query heads share one key and value head. The KV cache shrinks by the sharing factor. Qwen3-8B has 32 query heads and 8 KV heads, so its KV cache is 144 KiB per token. Where: RESEARCH 5.1, 5.2; `d1-06`.

## H

- **Histogram (Prometheus).** A metric type that counts observations into buckets and exposes `_bucket`, `_sum` and `_count`. Percentiles computed from it are estimates and cannot resolve differences inside one bucket. Where: METRICS 5; RESEARCH 9.1, 9.3.

## I

- **Indirect prompt injection.** An attack in which the malicious instructions arrive inside content the model reads on the user's behalf: a web page, a document, a retrieved passage or a tool result. Everything a RAG system retrieves is such a channel. Where: RESEARCH 13.7; `d3-05`, `d3-06`.
- **ITL (inter-token latency).** The time between two consecutive streamed chunks of text. The harness pools these gaps over all requests. Other tools use the same name for a different quantity. Where: METRICS 3, 4.

## K

- **KV cache.** The stored key and value vectors of all earlier tokens of a sequence, kept so the model does not recompute attention over the history at every step. It grows with context length and concurrency. For Qwen3-8B it takes 147,456 bytes per token in BF16. Where: RESEARCH 3.8, 5.2; `d1-06`, `d2-05`.
- **KV-cache quantization.** Storing keys and values in 8 bits (`--kv-cache-dtype fp8`) instead of 16. It doubles the number of tokens that fit in the same memory. The effect on quality depends on the model and needs a check. Where: RESEARCH 8.6; `d2-06`.

## L

- **Little's law.** The average number of items in a system equals the arrival rate times the average time each spends there. It lets you check that the concurrency, throughput and latency of one run agree with each other. Where: METRICS 7; RESEARCH 10.5.

## M

- **MBU.** Memory bandwidth utilisation: bytes moved per second divided by the peak memory bandwidth. vLLM can estimate it from its own accounting. It is an estimate against a datasheet peak, not a hardware counter. Where: METRICS 11; RESEARCH 9.2.
- **MCP (Model Context Protocol).** An open protocol through which an application offers tools and data to a model-driven client in a standard way, over stdio or HTTP. Tool descriptions come from the server, so the client must treat them as untrusted input. Where: RESEARCH 13.8; `d3-07`.
- **Memory bandwidth.** The bytes per second the GPU can move between its memory and its compute units. It sets the speed of decode. The workshop GPU has 1,597 GB/s, about 11 % less than the Workstation card of the same family. Where: RESEARCH 6.3; METRICS 12; `d1-05`.
- **MFU.** Model FLOPs utilisation: the FLOP per second achieved divided by the peak. It is low in decode by nature, because decode waits for memory, not for math. Where: METRICS 11; RESEARCH 9.2.
- **MIG (Multi-Instance GPU).** Hardware partitioning of one GPU into isolated instances with their own compute and memory. The workshop GPU supports up to four 24 GB instances. MIG separates tenants. It adds no capacity, and the utilisation queries do not work on it. Where: RESEARCH 6.12.
- **MoE (mixture of experts).** A transformer variant in which each layer holds many expert networks and a router sends every token to a few of them. It gives more total parameters at a similar compute cost per token. Where: RESEARCH 5.1; `d1-02`.

## N

- **NVFP4.** NVIDIA's 4-bit floating-point format for Blackwell, with small block scales. It needs a little over a quarter of the bytes of BF16, block scales included. Bug reports for the workshop GPU concentrate here, so the labs do not use it. Where: RESEARCH 8.4; `d2-06`.
- **NVLink.** NVIDIA's direct GPU-to-GPU link, much faster than PCIe on the cards that have it (900 GB/s per GPU on Hopper, quoted bidirectionally). The workshop GPU has none. Where: RESEARCH 6.6; `d2-07`.
- **NVML.** NVIDIA Management Library, the C interface behind `nvidia-smi` (Python module `pynvml`). It reports utilisation, memory, power, clocks and temperature. The pod's GPU exporter reads it. Where: RESEARCH 6.7; METRICS 10.

## O

- **OpenAI-compatible API.** An HTTP interface that follows the shape of OpenAI's (`/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/v1/models`). Existing clients work against a self-hosted server by changing the base URL. Where: RESEARCH 3.4, 3.7; `d1-08`.
- **Open-loop load.** Requests arrive on a schedule that does not depend on how fast the server answers. The harness uses Poisson arrivals. A slow server builds a queue, so the queueing becomes visible. Where: METRICS 7; RESEARCH 10.5.
- **Open weights vs open source.** Open weights means the trained parameters are published, under some licence and often with conditions. Open source AI in the OSI definition also requires the training-data information and the complete code needed to reproduce the system. The course says "open-weight" for every model it uses. Where: RESEARCH 11.1; `d3-05`.
- **Ops:byte.** NVIDIA's name for the ridge point of a GPU: the peak math rate divided by the peak memory bandwidth, in FLOP per byte. For the workshop GPU it is about 315. Where: RESEARCH 6.4; METRICS 12; `d1-05`.

## P

- **PagedAttention.** The KV cache is stored in fixed-size blocks that need not be contiguous and are allocated on demand. That avoids fragmentation and waste when sequence lengths are unpredictable. vLLM uses 16 tokens per block by default. Where: RESEARCH 3.4, 3.9; `d2-05`.
- **PCIe.** The bus that connects a GPU to the CPU and, without NVLink, to other GPUs. Generation 5 with 16 lanes moves about 64 GB/s per direction. Tensor parallelism between such GPUs runs over it. Where: RESEARCH 6.6; `d2-07`.
- **Percentile.** The value at or below which a stated share of the observations fall. With few samples a high percentile rests on a handful of points. Where: METRICS 6.
- **Pipeline parallelism.** The layers of a model are split into stages on different GPUs, and each request passes through the stages in turn. It fits models that are too large for one GPU. It does not make a single request faster. Where: RESEARCH 3.4; `d2-07`.
- **Preemption.** When the KV cache is full, the scheduler stops a running request, frees its blocks and recomputes it later. It is a cost, not an error. vLLM exposes it as `vllm:num_preemptions_total`. Where: RESEARCH 3.9; METRICS 13; `d2-05`.
- **Prefill.** The first phase of a request. The model processes the whole prompt at once, builds the KV cache and produces the first token. It is compute-heavy and makes up most of TTFT for long prompts. Where: RESEARCH 6.10; METRICS 12; `d1-07`.
- **Prefix caching.** The server keeps the KV blocks of earlier prompts and reuses them when a new prompt starts with the same tokens (full blocks only). It saves prefill time and lowers TTFT. It is also why a benchmark that repeats prompts looks too fast. Where: RESEARCH 3.9; METRICS 8; `d2-05`.
- **Prompt injection.** Input that makes a model follow instructions the application did not intend. The model has no reliable boundary between instructions and data. Filtering lowers the risk. Privilege limits and human approval are the controls that hold. Where: RESEARCH 13.7; `d3-05`.

## Q

- **Quantization.** Storing numbers with fewer bits (weights, activations or the KV cache) to save memory and to cut the bytes read per step. It changes the resource profile and can change quality. "Lower precision is always faster" is not true. Where: RESEARCH 8; `d2-06`.

## R

- **RAG (retrieval-augmented generation).** Retrieve passages that fit the question, put them into the prompt and let the model answer from them. It costs extra prompt tokens, and so extra prefill, on every request. Where: `d3-06`; RESEARCH 3.12.
- **Reasoning model.** A model that writes a thinking trace before its answer. Outputs get longer and cost more time and tokens. Qwen3 thinks by default, and the harness switches that off for chat requests. Where: RESEARCH 3.11, 5.1; METRICS 3.
- **Roofline.** A performance model: the attainable rate is the smaller of the peak compute rate and the memory bandwidth times the arithmetic intensity. It shows what limits an operation and gives a lower bound for the time of a decode step. Where: RESEARCH 6.10; METRICS 12; `d1-07`.

## S

- **Safetensors.** A tensor file format that stores raw numbers with a JSON header and cannot run code when it is loaded, unlike pickle-based PyTorch checkpoints. It protects against code execution on load. It does not protect against poisoned weights. Where: RESEARCH 4.2; `d3-05`.
- **SCC (standard contractual clauses).** Contract clauses approved by the EU Commission that provide safeguards when personal data goes to a country without an adequacy decision (GDPR Art. 46). The provider's DPA for the workshop pods uses a controller-to-processor module. Where: RESEARCH 7.10, 12.10; `d3-05`.
- **SLO (service level objective).** A measurable target for a service, for example "TTFT p95 at most 800 ms". It gives optimisation a goal. The course SLO also has a per-user speed, an availability and a quality bound. Where: CURRICULUM 1; METRICS 14.
- **SM (streaming multiprocessor).** The basic compute block of an NVIDIA GPU. It holds registers, shared memory and L1 cache, CUDA cores and Tensor Cores. The workshop GPU has 188. Where: RESEARCH 6.3, 6.5; `d1-05`.
- **Sovereignty dimensions.** The axes along which control over an AI system can be judged. The workshop formula uses data, model, infrastructure, operational control and portability. The EU Cloud Sovereignty Framework scores eight objectives, from strategic and legal to supply chain, technology and environment. Where: RESEARCH 12.11; `d3-05`.
- **Speculative decoding.** A cheap drafter proposes several tokens and the main model checks them in one pass. Accepted tokens cost less per token. It helps at low concurrency and can hurt at high batch size. Where: RESEARCH 3.10; `d2-09`.
- **Structured output.** Constrained decoding that forces the output to match a JSON schema, a regular expression, a grammar or a list of choices. It guarantees syntax, not meaning: a schema can be satisfied by padding with whitespace. Where: RESEARCH 3.11; `d3-07`.
- **Supply-chain pinning.** Fixing every external input to an exact version: the model by its full commit hash, the container image by digest, the packages by version. It gives reproducibility. It does not prove where an artifact came from. Where: RESEARCH 4.1, 13.10; `d3-05`.

## T

- **Tensor Core.** A matrix-multiply-and-accumulate unit inside an SM. It supplies most of a GPU's peak FLOPS at BF16, FP8 and lower precisions. Where: RESEARCH 6.5; `d1-05`.
- **Tensor parallelism.** The weight matrices of each layer are split across GPUs, which compute their parts and exchange partial results at every layer. It holds larger models and can cut the time per token. It needs a fast link, so over PCIe it is a trade-off. Where: RESEARCH 6.6; `d2-07`.
- **Token.** The unit of text a model reads and writes, usually a word piece. Prefill work, KV memory, decode steps and price are all counted in tokens. Where: `d1-02`.
- **Tool calling.** A protocol in which the model returns a structured request to call a named function with arguments. The application runs the function and returns the result. vLLM needs `--enable-auto-tool-choice` and a parser for the model family. Where: RESEARCH 3.11; `d3-07`.
- **TPOT (time per output token).** In vLLM and in this repository, `(latency - TTFT) / (N - 1)` for a request with N output tokens. Other tools use the name for other quantities. Where: METRICS 3, 4.
- **trust_remote_code.** An option that lets a model repository run its own Python code inside your process when it is loaded. It needs a pinned code revision as well as pinned weights. No pinned workshop model needs it. Where: RESEARCH 4.3; `d3-05`.
- **TTFT (time to first token).** The wait from the start of the request clock to the first text: queueing, prefill and the first decode step. Where: METRICS 3.

## W

- **Warm-up.** Requests sent before timing starts and then discarded, so start-up effects do not enter the measurement. Where: METRICS 7.
