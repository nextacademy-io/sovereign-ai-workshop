# Curriculum

How the three days fit together: what each block teaches, which demonstration and experiment makes it concrete, which exercise practises it, and what observable outcome shows that it worked.

The schedule itself is data in [`config/workshop.yaml`](../config/workshop.yaml); `pnpm check` verifies that this document names every block in it, that daily teaching time fits, and that task timeboxes match. Evidence for every technical statement is in [`RESEARCH.md`](RESEARCH.md).

## 1. Design principles

- **Inference is a system.** Every block says which layer it is about. The stack is `MODEL → RUNTIME → GPU → INFERENCE ENGINE → SERVING → OBSERVABILITY → APPLICATION`, grouped into three layers: **Runtime** (model, GPU, engine), **Infrastructure** (containers, networking, scaling, monitoring, security) and **Application** (APIs, structured output, tools, RAG, MCP, agents).
- **Every optimisation is a trade-off** between quality, latency, throughput, concurrency, memory, cost and operational complexity. No slide says "X makes inference faster"; it says which metric improves, under which workload, which resource becomes the bottleneck, and what is traded.
- **SLO first.** Optimisation needs a target. The workshop's running example is a workload (1,200 input tokens, 180 output tokens, 20 concurrent users) with an SLO (TTFT p95 800 ms, 25 output tokens/s per request, 99.9 % availability) and a quality bound (at most 2 % regression). There is no universally fastest configuration, only one that fits a workload and its constraints.
- **Measure, then teach.** Slides show measured results from `benchmark/results/` or carry an **ILLUSTRATIVE EXAMPLE** badge. Experiments that contradict the explanation are investigated before the explanation is taught.
- **The smallest model that reliably does the task.** Model selection is argued from the task, not from leaderboards.
- **Teaching rhythm**, repeated in every experiment block:

```text
CONCEPT → SYSTEM → EXPERIMENT → PREDICTION → MEASUREMENT → EXPLANATION → PRODUCTION CONSEQUENCE
```

- **Application layers do not dominate.** RAG, tool calling, MCP and agents are shown on top of the inference infrastructure, framework-free, and reconnected to capacity planning (one user request becomes several model calls).

## 2. Agenda

Times are relative to each day's start. Teaching time per day is about seven hours (breaks excluded). Block ids are the section files in `slides/sections/`.

### Day 1: UNDERSTAND & RUN (question: what are we actually running?)

| Block id | Title | Min | Layer | Kind | Task |
| --- | --- | --- | --- | --- | --- |
| `pre-00-preflight` | Preflight on the participant laptop (before Day 1) | 15 | all | homework | 00 |
| `d1-01-opening` | Opening: why run models yourself | 30 | all | lecture | |
| `d1-02-models` | Modern language models | 60 | runtime | lecture | |
| `d1-03-model-selection` | Model selection | 60 | runtime | mixed | |
| `d1-04-lab-model-selection` | Lab 1: select models for four scenarios | 40 | runtime | lab | 01 |
| `d1-05-gpu-fundamentals` | GPU fundamentals for inference | 60 | runtime | lecture | |
| `d1-06-gpu-sizing` | GPU sizing: weights, KV cache, overhead | 45 | runtime | mixed | |
| `d1-07-inference-mechanics` | Inference mechanics: prefill, decode, latency | 45 | runtime | mixed | |
| `d1-08-first-vllm` | First vLLM deployment (trainer demo) | 30 | runtime | demo | |
| `d1-09-lab-first-server` | Lab 2: first inference server | 45 | runtime | lab | 02 |

### Day 2: MEASURE & OPTIMIZE (question: how do we make it fast and efficient?)

| Block id | Title | Min | Layer | Kind | Task |
| --- | --- | --- | --- | --- | --- |
| `d2-01-recap` | Recap and bottleneck predictions | 30 | all | discussion | |
| `d2-02-measuring` | Measuring inference | 60 | runtime | mixed | |
| `d2-03-lab-benchmark` | Lab 3: benchmark the baseline | 60 | runtime | lab | 03 |
| `d2-04-continuous-batching` | Continuous batching | 45 | runtime | mixed | |
| `d2-05-kv-cache` | KV cache, PagedAttention and prefix caching | 45 | runtime | mixed | |
| `d2-06-quantization` | Quantization | 45 | runtime | mixed | |
| `d2-07-parallelism` | Parallelism: replicas, tensor, pipeline, expert | 45 | runtime | mixed | |
| `d2-08-lab-optimize` | Lab 4: optimize the deployment | 60 | runtime | lab | 04 |
| `d2-09-demos` | Trainer demos: speculative decoding, OOM, tensor parallelism | 30 | runtime | demo (skippable) | |

### Day 3: OPERATE (question: how do we operate this as infrastructure?)

| Block id | Title | Min | Layer | Kind | Task |
| --- | --- | --- | --- | --- | --- |
| `d3-01-production-architecture` | Production architecture | 45 | infrastructure | lecture | |
| `d3-02-containerization` | Containerization and reproducible deployments | 45 | infrastructure | mixed | |
| `d3-03-observability` | Observability: metrics, dashboards, incident investigation | 60 | infrastructure | mixed | |
| `d3-04-scaling` | Scaling strategies | 45 | infrastructure | lecture | |
| `d3-05-security-sovereignty` | Security, compliance and digital sovereignty | 60 | infrastructure | mixed | |
| `d3-06-rag` | RAG without framework hype | 45 | application | mixed | |
| `d3-07-tools-agents` | Tool calling, MCP and agents | 30 | application | mixed | |
| `d3-08-lab-architecture` | Lab 5: production architecture challenge | 60 | all | lab | 05 |
| `d3-09-capstone-close` | Architecture defenses, decision framework, close | 30 | all | discussion | |

## 3. Learning outcomes: concept, demonstration, exercise, validation

Each outcome has an **observable validation**: something a participant produces or does that shows it was reached. Outcome numbers match the workshop specification (1 to 23) and `outcomes:` in `config/workshop.yaml`.

| # | Participants can… | Concept (block) | Demonstration | Exercise | Observable validation |
| --- | --- | --- | --- | --- | --- |
| 1 | explain how modern LLM inference works | `d1-02`, `d1-07` | tokenizer and one forward pass walked through on the live server | Lab 2 | draws request → tokens → GPU → metrics from memory and labels prefill and decode |
| 2 | distinguish training, fine-tuning and inference | `d1-01`, `d1-02` | compute and memory profile of each, side by side | Lab 1 discussion | in Lab 1, justifies "no fine-tuning needed" or "fine-tune" for at least one scenario |
| 3 | select an open-weight model for a use case | `d1-03` | selection matrix, licence table | Lab 1 | `workshop-artifacts/model-selection.md` has model, precision, hardware, engine, context, reasoning and a defended trade-off per scenario |
| 4 | estimate GPU memory requirements | `d1-06` | `scripts/sizing.py` against the server log | Lab 1, sizing questions | own estimate of KV capacity is within 10 % of the server's `GPU KV cache size` line |
| 5 | relate size, precision, VRAM, KV cache, context and concurrency | `d1-06`, `d2-05` | `kv-constrained` profile: context × concurrency vs capacity | Lab 4 (context and quantization groups) | predicts, before running, how many 8k-token requests fit and checks it |
| 6 | explain prefill, TTFT, decode, ITL and TPS | `d1-07`, `d2-02` | one streamed request with timestamps | Lab 2, Lab 3 | reads TTFT and ITL for a request from the client output and explains each |
| 7 | explain why the phases hit different bottlenecks | `d1-05`, `d1-07`, `d2-01` | roofline sketch; context-length experiment (prefill grows with prompt, decode with KV read) | Day 2 prediction exercise | predicts which phase a given change affects and is checked by measurement |
| 8 | deploy a model with vLLM | `d1-08` | profile → `wsctl start` → ready log | Lab 2, Lab 4 | restarts the shared server with another profile and reads the startup log |
| 9 | expose and consume an OpenAI-compatible API | `d1-08` | curl, Python client, streaming | Preflight, Lab 2 | `/v1/models`, a completion and a stream succeed from their own shell |
| 10 | benchmark an endpoint | `d2-02`, `d2-03` | `benchmark/run.sh` sweep | Lab 3 | JSON results at concurrency 1, 4, 8, 16 with provenance |
| 11 | measure TTFT, ITL, latency, TPS, throughput, percentiles, GPU use, VRAM | `d2-02`, `d3-03` | harness output next to Grafana | Lab 3 | results table and Markdown summary with p50 and p95 |
| 12 | understand continuous batching | `d2-04` | concurrency sweep and `max-seqs-8` queueing | Lab 3 | locates the knee of aggregate TPS and explains it |
| 13 | understand KV-cache management and PagedAttention | `d2-05` | KV usage panel, preemption counter under `kv-constrained` | Lab 4 | explains why a longer context reduces concurrent capacity |
| 14 | experiment with concurrency, context, batching, quantization, prefix caching, tensor parallelism | `d2-03` to `d2-08`, `d2-09` | each as a controlled one-variable experiment | Lab 3, Lab 4, trainer demos | group report: before, after, metric improved, metric degraded, quality, memory, operations, recommendation |
| 15 | containerize inference services | `d3-02` | Dockerfile and compose file read line by line; CPU-only client image built on laptops | Day 3 laptop exercise | builds and runs `apps/inference-client` image against the group endpoint |
| 16 | monitor an inference deployment | `d3-03` | live dashboard during load | Day 3 investigation exercise | names the metric that shows queueing, KV pressure and an idle GPU |
| 17 | understand production scaling strategies | `d2-07`, `d3-01`, `d3-04` | replica vs tensor-parallel results | Lab 5 | scaling strategy and bottleneck stated in the architecture document |
| 18 | reason about latency, throughput, quality, memory, concurrency, cost | all labs, `d3-04` | cost per useful workload from measured TPS | Lab 4, Lab 5 | every recommendation names what is traded |
| 19 | understand security implications of self-hosted AI | `d3-05` | exposure facts of the pods themselves; advisory timeline | Lab 5 | security boundary and threats listed in the architecture |
| 20 | understand digital sovereignty beyond "running Ollama locally" | `d1-01`, `d3-05` | sovereignty formula applied to this workshop's own setup | Lab 5 | classifies each component by data, model, infrastructure, operations, portability |
| 21 | integrate a local model into an application | `d3-06`, `d3-07` | `apps/inference-client`, structured output | Day 3 guided runs | calls the model from code with a JSON-schema response |
| 22 | place RAG, tool calling, MCP and agents in the architecture | `d3-06`, `d3-07` | agent loop with token accounting | Lab 5 | architecture shows application layers on top of inference and counts their extra model calls |
| 23 | design a production inference architecture | `d3-01`, `d3-08`, `d3-09` | decision framework | Lab 5 | `workshop-artifacts/production-architecture.md`, defended in five minutes |

## 4. Block by block

Each block lists goal, concepts, the demonstration or experiment, the production consequence, and what can be cut when time is short. The experiment rhythm is spelled out for blocks that have one. Predictions are hypotheses to be tested, never results.

### Day 1

**`d1-01-opening` (30 min, all layers).** Why organisations run models themselves: privacy, sovereignty, cost control, specialisation, latency, regulation. Compare laptop, dedicated GPU server, private data centre, dedicated GPU cloud, sovereign cloud. Introduce `TRAINING ≠ FINE-TUNING ≠ INFERENCE` and the three layers. Consequence: the rest of the workshop is about engineering a system, not about a download. Cut: shorten the comparison discussion.

**`d1-02-models` (60 min, runtime).** Tokens, embeddings, transformer blocks, attention, context, autoregressive generation, dense vs mixture-of-experts, reasoning and multimodal models; training only as far as it explains inference. Demonstration: tokenise a sentence on the live server (`/tokenize`); the KV-cache arithmetic for the pinned model is a forward reference to `d1-06` and is not done here. Consequence: parameters decide memory, architecture (KV heads, layers) decides KV cost.

**`d1-03-model-selection` (60 min, runtime).** Families (Qwen, Llama, Gemma, Mistral, DeepSeek, Kimi), general vs reasoning vs coding vs multilingual, tool use and structured output; size and active parameters, context, licences, quantization and engine compatibility, memory. Evaluation beyond leaderboards. Licences are read per repository at the pinned revision because they drift (RESEARCH 11.4). Consequence: the smallest model that reliably does the task.

**`d1-04-lab-model-selection` (40 min, Lab 1, task `01-model-selection`).** Four scenarios (internal German-language assistant, customer-service classification and extraction, coding assistant, high-volume document pipeline). Groups fill model, precision, hardware, engine, context and reasoning, and defend the trade-offs. Validation: `workshop-artifacts/model-selection.md`. Cut: reduce to two scenarios.

**`d1-05-gpu-fundamentals` (60 min, runtime).** CPU vs GPU, SMs, Tensor Cores, VRAM, memory bandwidth, FLOPS, PCIe and NVLink, GPU generations, and how to reason about hardware rather than memorise a catalogue. Dense vs sparse numbers; the workshop GPU in detail (1,597 GB/s, no NVLink). `nvidia-smi` utilisation is not efficiency. Consequence: the ops:byte ratio of a GPU decides which phase is limited by what.

**`d1-06-gpu-sizing` (45 min, runtime).** `WEIGHTS + KV CACHE + RUNTIME OVERHEAD = VRAM`; `weights ≈ parameters × bytes per parameter` for BF16, FP16, FP8, INT8, INT4; then why it is incomplete: KV cache, context, concurrency, batch behaviour, runtime memory, CUDA graphs. Experiment: predict the KV capacity of the pinned model with `scripts/sizing.py`, then compare with the server log line `GPU KV cache size: N tokens` (experiment `baseline`). Consequence: capacity planning is arithmetic you can check.

**`d1-07-inference-mechanics` (45 min, runtime).** Prompt → prefill → first token → decode loop; TTFT, ITL, TPS, end-to-end latency; arithmetic intensity and the roofline, conceptually, with no mathematical lecture. Demonstration: one streamed request with timestamps. Prediction for Day 2: prefill scales with prompt length and is compute-heavy; decode is limited by moving weights and KV through memory.

**`d1-08-first-vllm` (30 min, demo).** Trainer shows `nvidia-smi`, `/v1/models`, a completion, streaming, server logs, and the startup log (weights, KV cache, CUDA graphs, time to ready). Consequence: the API is the product; everything else is what makes it behave.

**`d1-09-lab-first-server` (45 min, Lab 2, task `02-first-inference-server`).** SSH in, inspect the GPU and the service, query the API, stream, read logs, watch GPU utilisation, vary prompt length, output length and temperature, record observations. The point is the chain `REQUEST → MODEL → GPU → TOKENS → METRICS`, not "the API returns text". Recovery: `./scripts/reset.sh lab-02`.

### Day 2

**`d2-01-recap` (30 min, discussion).** Reconstruct `CLIENT → API → vLLM → MODEL → GPU` and ask groups to predict bottlenecks before measuring anything. Predictions are written down and revisited at the end of the day.

**`d2-02-measuring` (60 min).** User-facing metrics (TTFT, ITL, output TPS, end-to-end latency), system metrics (requests/s, input/output/total tokens/s, running and waiting requests), distributions (p50, p90, p95, p99), hardware (GPU utilisation, VRAM, power). "Average latency is not enough." Metric definitions differ between tools (RESEARCH 10.4), which is why the workshop harness defines its own and cross-checks against `vllm bench serve`. Closed-loop vs open-loop load and coordinated omission, goodput against an SLO.

**`d2-03-lab-benchmark` (60 min, Lab 3, task `03-benchmark`).** Concurrency 1, 4, 8 and 16 on the same deployment; capture TTFT p50/p95, latency p50/p95, output TPS, aggregate TPS, GPU utilisation, VRAM; JSON plus Markdown. Questions: when does throughput stop scaling, when does latency deteriorate, what looks saturated, what would you deploy, why. Experiment (`baseline`, `concurrency`): **hypothesis** aggregate TPS rises with concurrency until another resource saturates; **measure** the sweep; **explain** batching raises useful work per weight read; **consequence** concurrency and batching trade throughput against latency. Cut: reduce to concurrency 1, 8, 16.

**`d2-04-continuous-batching` (45 min).** Why naive one-request-at-a-time execution wastes the GPU; static, dynamic and continuous batching; scheduling, arrival, different output lengths, queueing; chunked prefill. Connect directly to Lab 3 observations; show `max-seqs-8` to make queueing visible (experiment `concurrency`).

**`d2-05-kv-cache` (45 min).** Recompute vs reuse; why the KV cache consumes VRAM; `LONGER CONTEXT + MORE CONCURRENT REQUESTS = MORE KV CACHE`; PagedAttention (fragmentation, page-based allocation, dynamic workloads); prefix caching. Experiments `context-length` (profiles `baseline` and `kv-constrained`: KV usage, queueing, preemptions) and `prefix-cache` (profiles `baseline` and `no-prefix-cache` with the `shared-prefix` workload: TTFT and hit rate).

**`d2-06-quantization` (45 min).** BF16, FP16, FP8, INT8, INT4; weight, activation and KV-cache quantization; effects on memory, quality, compute, bandwidth, throughput, latency and compatibility. Not "lower precision is always faster": quantization changes the resource profile. Experiment `quantization`: profiles `baseline`, `fp8`, `kv-fp8`; memory, KV capacity, TTFT, TPS and a small quality spot check (so the 2 % regression bound in the SLO is a measured number).

**`d2-07-parallelism` (45 min).** Replica (data-parallel) serving vs tensor parallelism; pipeline and expert parallelism; communication over PCIe, NVLink, NVSwitch, network. "More GPUs do not automatically mean lower latency." Experiment `tensor-parallel` is a trainer demonstration on a two-GPU pod (PCIe, no NVLink on this card); it could not be run in the validation (no two-GPU stock), so the slides present its design and hypothesis and say so.

**`d2-08-lab-optimize` (60 min, Lab 4, task `04-optimization`).** Each group gets one hypothesis: quantization, prefix caching, context length, or concurrency/batching (optional fifth: tensor parallelism). Hypothesis → experiment → measurement → result → explanation, then a five-minute report: before, after, metric improved, metric degraded, quality impact, memory impact, operational impact, recommendation. Groups change the server only through `wsctl` profiles, coordinated within the group.

**`d2-09-demos` (30 min, skippable).** Trainer demonstrations that are risky or expensive for every group: n-gram speculative decoding (`spec-ngram`), the intentional failure `oom-demo`, vLLM against Ollama or llama.cpp under concurrency, the MoE model, tensor parallelism if not shown earlier.

### Day 3

**`d3-01-production-architecture` (45 min, infrastructure).** From `CLIENT → API → INFERENCE SERVER → GPU` to API gateway, auth, load balancer, inference replicas and a GPU pool, then metrics, logs, traces, model registry, secrets, storage, health checks. State, stateless services, streaming, timeouts, retries, queues and backpressure.

**`d3-02-containerization` (45 min).** Docker, CUDA base images, host drivers and CUDA compatibility, image size, build-time vs runtime model downloads, the model cache, reproducibility, configuration. `docker run model-server` does not imply a reproducible deployment. Participants build the CPU-only `apps/inference-client` image on their laptops and run it against the group endpoint through their SSH tunnel; the vLLM image and `monitoring/docker-compose.yml` are read line by line. The pods themselves cannot run Docker (RESEARCH 7.3), which is itself a lesson: on a managed platform the image is the deployment unit.

**`d3-03-observability` (60 min).** vLLM metrics, Prometheus, Grafana, GPU metrics. The compact dashboard (request rate, TTFT, latency, tokens/s, running, waiting, GPU utilisation, VRAM) plus KV usage, prefix hit rate, preemptions and estimated MFU/MBU. Investigation exercise: the trainer generates an incident (burst, long prompts, KV pressure) and groups diagnose it from the dashboard.

**`d3-04-scaling` (45 min).** Vertical, horizontal and model-parallel scaling; replicas, load balancing, autoscaling, queues, cold starts (measured startup time of this setup), GPU utilisation; KV-aware routing and prefill/decode disaggregation conceptually.

**`d3-05-security-sovereignty` (60 min).** Data-flow mapping (prompts, responses, logs, embeddings, weights, telemetry), GDPR and PII, retention, auditability, EU AI Act roles and Art. 50 as engineering inputs (not legal advice), supply-chain pinning (model, tokenizer, container, packages, CUDA, engine), open weights vs open source, the sovereignty formula `DATA + MODEL + INFRASTRUCTURE + OPERATIONAL CONTROL + PORTABILITY`, production security (TLS, keys, isolation, secrets, least privilege, air-gapped operation) and LLM application security (prompt and tool injection, output validation, authorisation). The workshop's own pods are the case study: open model, EU region, US provider.

**`d3-06-rag` (45 min).** `DOCUMENTS → CHUNKING → EMBEDDINGS → INDEX → RETRIEVAL → CONTEXT → LLM` with `apps/rag-demo`: no framework, each step prints what it costs, including the extra prompt tokens. Chunk size, retrieval quality, reranking, freshness (the handbook contains a superseded policy on purpose). Frameworks are discussed after the architecture is understood.

**`d3-07-tools-agents` (30 min).** Tool calling as a protocol between model and application; MCP as an interface layer (the demo ships a stdlib server and client); agents as loops. The token ledger of `apps/tool-calling-demo` shows `ONE USER REQUEST → MULTIPLE MODEL CALLS → MORE TOKENS → MORE GPU LOAD`, which reconnects the application layer to capacity planning.

**`d3-08-lab-architecture` (60 min, Lab 5, task `05-production-design`).** Scenario per group (sensitive internal assistant, German customer service, coding assistant for 100 developers, offline document pipeline). Design model, precision, GPU, engine, context, replicas, API, authentication, observability, RAG, scaling, security, SLO; estimate concurrency, latency target, GPU requirement, expected bottleneck and scaling strategy. Deliverable: `workshop-artifacts/production-architecture.md`.

**`d3-09-capstone-close` (30 min).** Each group defends its architecture; there is no single correct answer, only the quality of the reasoning. Close with the 15-question decision framework and the final slide.

### The 15 decision questions (closing slide)

1. What task are we solving? 2. What quality do we need? 3. What is the smallest model that satisfies it? 4. What traffic do we expect? 5. What is our latency budget? 6. How large is the context? 7. What concurrency do we expect? 8. How much VRAM is required? 9. What hardware bottleneck do we expect? 10. What does the baseline benchmark show? 11. Which optimisation addresses the measured bottleneck? 12. Does it degrade quality? 13. What should we monitor? 14. What security boundary is required? 15. What does this cost per useful workload?

## 5. Experiments catalogue

Every experiment lives in `experiments/<name>/` with a README (hypothesis, variable, procedure), a `run.sh`, raw results under `benchmark/results/` and a `RESULTS.md` that states what was measured and what surprised. Predictions below are hypotheses, not results; the results documents replace them.

| Experiment | Question | One variable | Profiles | Primary metrics | Used in |
| --- | --- | --- | --- | --- | --- |
| `baseline` | Does the KV-cache formula predict the server? What does one request cost? | none (single request, then low load) | `baseline` | startup time, weights memory, KV tokens, TTFT, ITL | `d1-06`, `d1-08`, Lab 3 |
| `concurrency` | Where does aggregate throughput stop scaling? | concurrency 1 to 64; `max-num-seqs` | `baseline`, `max-seqs-8` | aggregate TPS, TTFT p95, output TPS per request, running/waiting | `d2-03`, `d2-04`, Lab 4 |
| `context-length` | How do prompt length and KV capacity change TTFT, ITL and concurrency? | input tokens 512 to 32k; KV budget | `baseline`, `kv-constrained` | TTFT, ITL, KV usage, preemptions, waiting | `d2-05`, Lab 4 |
| `quantization` | What does FP8 change in memory, speed and quality? | weights FP8; KV cache FP8 | `baseline`, `fp8`, `kv-fp8` | VRAM, KV tokens, TTFT, TPS, quality spot check | `d2-06`, Lab 4 |
| `prefix-cache` | How much prefill does a shared prefix save? | prefix caching on/off | `baseline`, `no-prefix-cache` | TTFT, hit rate, prefill tokens | `d2-05`, Lab 4 |
| `tensor-parallel` | When do two GPUs help latency or throughput? | TP=2 vs one replica per GPU | `tp2`, `baseline` | latency, TPS, GPU power | `d2-07`, `d2-09` |
| `demos` | Speculative decoding, intentional OOM, vLLM vs Ollama, MoE | per demo | `spec-ngram`, `oom-demo`, others | per demo | `d2-09` |

## 6. Heise coverage matrix

Every advertised item of the public workshop page ([RESEARCH 1](RESEARCH.md)) has a home. "Guided run" means the trainer drives and participants follow with their own copy; "extension" means optional work in the task's *Further Exploration*.

| Heise block | Where it is taught | How |
| --- | --- | --- |
| 1 Fundamentals: models, transformer, attention, training, tokenization, embeddings, inference, context windows, reasoning, fine-tuning and alignment, limits and errors | `d1-02`, `d1-01`, `d1-07` | lecture with live server demonstrations; fine-tuning and alignment compactly (what changes, what it costs, when not to) |
| 2 Model evaluation and selection (all criteria, benchmarks, licences, exercise) | `d1-03`, `d1-04` | Lab 1; `docs/MODEL-SELECTION.md` |
| 3 Security, compliance, sovereignty (AI Act roles, data flows, labelling duties, logging, supply chain, open weights vs open source, lock-in, reproducibility, air-gapped, PII, prompt and tool injection, guardrails, model cards, security by design) | `d3-05`, `d1-01`, `d1-03` | lecture and data-flow exercise; labelling duty (Art. 50) and model cards as engineering inputs; `docs/SECURITY.md`, `docs/DIGITAL-SOVEREIGNTY.md` |
| 4 Hardware and architecture (CPU vs GPU, memory, quantization, on-prem, cloud, hybrid) | `d1-05`, `d1-06`, `d2-06` | lecture, sizing, experiment; CPU inference through the llama.cpp/Ollama comparison demo |
| 5 Inference servers (vLLM, SGLang, Ollama, LM Studio; OpenAI-compatible APIs; exercises) | `d1-08`, `d1-09`, `d2-09` | Labs 1 and 2; positioning table of engines; Ollama demo |
| 6 Deployment and scaling (Docker, load balancing, parallelization, cost; compare deployment approaches) | `d3-02`, `d3-04`, `d2-07` | container exercise on laptops; replica vs tensor-parallel and vLLM vs Ollama comparisons |
| 7 Security and operations (monitoring, logging, access, data protection; performance measurement and optimization) | `d3-03`, `d3-05`, Labs 3 and 4 | dashboard investigation; benchmark and optimisation labs |
| 8 RAG (fundamentals, embeddings, chunking, vector databases, knowledge management; build a RAG system) | `d3-06` | guided run of `apps/rag-demo` (numpy index); vector databases discussed as the next step; extension: change chunking and observe retrieval |
| 9 Agentic AI (tool calling, structured output, multi-agent, MCP; build a simple agent) | `d3-07`, `d3-06` | guided run of the agent loop and the MCP server; multi-agent systems explained as more model calls (token ledger); extension: add a tool |
| 10 Frameworks (LangChain/LangGraph, Python AI apps) | `d3-06`, `d3-07` | positioning slide after the framework-free implementation; what a framework adds and hides |
| 11 Integration (REST, web apps, chatbots, automation, local model in an application, near-production proof of concept) | `d3-06`, `d3-07`, `d3-08`, `apps/` | `apps/inference-client` (structured output, batch pipeline); Lab 5 architecture as the near-production design |
| 12 Best practices (errors, pitfalls, production recommendations) | `d3-09`, all labs | decision framework; common-failure notes in each task and in `docs/TROUBLESHOOTING.md` |

## 7. Time recovery and optional content

If the workshop runs behind, cut in this order and keep every lab's debrief:

1. The demos of `d2-09-demos` (about 20 of its 30 min); the trainer can show one demo inside `d2-07`. Keep the last three slides of the block (predictions scored, the five sentences of Day 2, the bridge to Day 3): they close the day.
2. In `d1-02-models`, skip multimodal and reasoning detail (10 min).
3. In Lab 1, two scenarios instead of four (10 min).
4. In `d2-03-lab-benchmark`, concurrency 1, 8, 16 only (10 min).
5. In `d3-04-scaling`, shorten KV-aware routing and disaggregation to one slide (10 min).
6. Lab 5: one scenario defended per group, shorter defences (15 min).

`FACILITATOR.md` carries the minute-level run sheet and the same list with the exact slides to skip.

## 8. Assumptions, and what validation found

Decided in advance, re-checked on the actual hardware; the evidence for each is in [`VALIDATION.md`](VALIDATION.md).

- vLLM v0.31.0 runs the pinned dense BF16 and FP8 models correctly on the RTX PRO 6000 (SM120). **Confirmed** on two different hosts; the vLLM documentation still never names the card (RESEARCH 3.3).
- Multi-user SSH over a single exposed TCP port, accounts, isolation and revocation. **Confirmed**. Persisted accounts after a pod restart: **not possible by design**, because the shared volume enforces no permissions; accounts come back from `infra/participants.yaml` in a rebuild of about 5 min 41 s (`docs/GPU-POOL.md`).
- Whether pods expose enough privilege for `nvidia-smi` and NVML metrics. **Confirmed**: the exporter and the dashboard work; the proxy limit of 100 seconds is never used because access is through SSH tunnels.
- Cold start of a fresh pod: **measured** (about 3 minutes for vLLM, 5.5 minutes for the whole deployment); written into `FACILITATOR.md`.
- Every timebox in the tasks: the **machine time** of tasks 02 to 04 was measured as a participant on a fresh pod (minutes, well inside the timeboxes); the human time with real participants is **not** measured and remains the trainer's dry run (`FACILITATOR.md`, section 2).
