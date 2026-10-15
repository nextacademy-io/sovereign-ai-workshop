# Curriculum

How the material fits together: what each module teaches, which demonstration and experiment makes it concrete, which exercise practices it, and what observable outcome shows that it worked. The material is one ordered module path of about three days, paced freely: it has no days, clock times or durations.

The path itself is data in [`config/workshop.yaml`](../config/workshop.yaml); `pnpm check` verifies that this document names every module in it, that the slide dividers agree with it and that every learning outcome is covered by at least one module. Evidence for every technical statement is in [`RESEARCH.md`](RESEARCH.md).

## 1. Design principles

- **Inference is a system.** Every module says which layer it is about. The stack is `MODEL → RUNTIME → GPU → INFERENCE ENGINE → SERVING → OBSERVABILITY → APPLICATION`, grouped into three layers: **Runtime** (model, GPU, engine), **Infrastructure** (containers, networking, scaling, monitoring, security) and **Application** (APIs, structured output, tools, RAG, MCP, agents).
- **Every optimization is a trade-off** between quality, latency, throughput, concurrency, memory, cost and operational complexity. No slide says "X makes inference faster"; it says which metric improves, under which workload, which resource becomes the bottleneck, and what is traded.
- **SLO first.** Optimization needs a target. The workshop's running example is a workload (1,200 input tokens, 180 output tokens, 20 concurrent users) with an SLO (TTFT p95 800 ms, 25 output tokens/s per request, 99.9 % availability) and a quality bound (at most 2 % regression). There is no universally fastest configuration, only one that fits a workload and its constraints.
- **Measure, then teach.** Slides show measured results from `benchmark/results/` or carry an **ILLUSTRATIVE EXAMPLE** badge. Experiments that contradict the explanation are investigated before the explanation is taught.
- **The smallest model that reliably does the task.** Model selection is argued from the task, not from leaderboards.
- **Teaching rhythm**, repeated in every experiment module:

```text
CONCEPT → SYSTEM → EXPERIMENT → PREDICTION → MEASUREMENT → EXPLANATION → PRODUCTION CONSEQUENCE
```

- **Application layers do not dominate.** RAG, tool calling, MCP and agents are shown on top of the inference infrastructure, framework-free, and reconnected to capacity planning (one user request becomes several model calls).

## 2. The module path

The modules run in the order below. Module ids are the section files in `slides/sections/`, and `config/workshop.yaml` holds the order. The path has three parts, each with a guiding question: *understand and run* (modules 01 to 09: what are we actually running?), *measure and optimize* (10 to 18: how do we make it fast and efficient?) and *operate* (19 to 27: how do we operate this as infrastructure?). Lab 1 (`07-lab-model-selection`) comes after the GPU, sizing and mechanics modules, because it needs KV-cache sizing, TTFT and prefill.

<!-- agenda:curriculum:begin -->
| Module id | Title | Layer | Kind | Task |
| --- | --- | --- | --- | --- |
| `pre-00-preflight` | Preflight on the participant laptop (before the first module) | all | homework | 00 |
| `01-opening` | Opening: why run models yourself | all | lecture |  |
| `02-models` | Modern language models | runtime | lecture |  |
| `03-gpu-fundamentals` | GPU fundamentals for inference | runtime | lecture |  |
| `04-gpu-sizing` | GPU sizing: weights, KV cache, overhead | runtime | lecture and exercise |  |
| `05-inference-mechanics` | Inference mechanics: prefill, decode, latency | runtime | lecture and exercise |  |
| `06-model-selection` | Model selection | runtime | lecture and exercise |  |
| `07-lab-model-selection` | Lab 1: select models for four scenarios | runtime | lab | 01 |
| `08-first-vllm` | First vLLM deployment (trainer demo) | runtime | trainer demo |  |
| `09-lab-first-server` | Lab 2: first inference server | runtime | lab | 02 |
| `10-checkpoint` | Checkpoint: bottleneck predictions | all | discussion |  |
| `11-measuring` | Measuring inference | runtime | lecture and exercise |  |
| `12-lab-benchmark` | Lab 3: benchmark the baseline | runtime | lab | 03 |
| `13-continuous-batching` | Continuous batching | runtime | lecture and exercise |  |
| `14-kv-cache` | KV cache, PagedAttention and prefix caching | runtime | lecture and exercise |  |
| `15-quantization` | Quantization | runtime | lecture and exercise |  |
| `16-parallelism` | Parallelism: replicas, tensor, pipeline, expert | runtime | lecture and exercise |  |
| `17-lab-optimize` | Lab 4: optimize the deployment | runtime | lab | 04 |
| `18-demos` | Trainer demos: speculative decoding and OOM | runtime | trainer demo (skippable) |  |
| `19-production-architecture` | Production architecture | infrastructure | lecture |  |
| `20-containerization` | Containerization and reproducible deployments | infrastructure | lecture and exercise |  |
| `21-observability` | Observability: metrics, dashboards, incident investigation | infrastructure | lecture and exercise |  |
| `22-scaling` | Scaling strategies | infrastructure | lecture |  |
| `23-security-sovereignty` | Security, compliance and digital sovereignty | infrastructure | lecture and exercise |  |
| `24-rag` | RAG without framework hype | application | lecture and exercise |  |
| `25-tools-agents` | Tool calling, MCP and agents | application | lecture and exercise |  |
| `26-lab-architecture` | Lab 5: production architecture challenge | all | lab | 05 |
| `27-capstone-close` | Architecture defenses, decision framework, close | all | discussion |  |
<!-- agenda:curriculum:end -->

## 3. Learning outcomes: concept, demonstration, exercise, validation

Each outcome has an **observable validation**: something a participant produces or does that shows it was reached. Outcome numbers match the workshop specification (1 to 23) and `outcomes:` in `config/workshop.yaml`.

| # | Participants can… | Concept (module) | Demonstration | Exercise | Observable validation |
| --- | --- | --- | --- | --- | --- |
| 1 | explain how modern LLM inference works | `module 02`, `module 05` | tokenizer and one forward pass walked through on the live server | Lab 2 | draws request → tokens → GPU → metrics from memory and labels prefill and decode |
| 2 | distinguish training, fine-tuning and inference | `module 01`, `module 02` | compute and memory profile of each, side by side | Lab 1 discussion | in Lab 1, justifies "no fine-tuning needed" or "fine-tune" for at least one scenario |
| 3 | select an open-weight model for a use case | `module 06` | selection matrix, license table | Lab 1 | `workshop-artifacts/model-selection.md` has model, precision, hardware, engine, context, reasoning and a defended trade-off per scenario |
| 4 | estimate GPU memory requirements | `module 04` | `scripts/sizing.py` against the server log | Lab 1, Lab 2 | the sizing script's estimate lands within about 3 % of the server's KV capacity line; the formula check against the server's own KV memory within 2 % |
| 5 | relate size, precision, VRAM, KV cache, context and concurrency | `module 04`, `module 14` | `kv-constrained` profile: context × concurrency vs capacity | Lab 4 (context and quantization groups) | predicts, before running, how many 8k-token requests fit and checks it |
| 6 | explain prefill, TTFT, decode, ITL and TPS | `module 05`, `module 11` | one streamed request with timestamps | Lab 2, Lab 3 | reads TTFT and ITL for a request from the client output and explains each |
| 7 | explain why the phases hit different bottlenecks | `module 03`, `module 05`, `module 10` | roofline sketch; context-length experiment (prefill grows with prompt, decode with KV read) | bottleneck predictions of the checkpoint (`module 10`) | predicts which phase a given change affects and is checked by measurement |
| 8 | deploy a model with vLLM | `module 08` | profile → `wsctl start` → ready log | Lab 2, Lab 4 | restarts the shared server with another profile and reads the startup log |
| 9 | expose and consume an OpenAI-compatible API | `module 08` | curl, Python client, streaming | Preflight, Lab 2 | `/v1/models`, a completion and a stream succeed from their own shell |
| 10 | benchmark an endpoint | `module 11`, `module 12` | `benchmark/run.sh` sweep | Lab 3 | JSON results at concurrency 1, 4, 8, 16 with provenance |
| 11 | measure TTFT, ITL, latency, TPS, throughput, percentiles, GPU use, VRAM | `module 11`, `module 21` | harness output next to Grafana | Lab 3 | results table and Markdown summary with p50 and p95 |
| 12 | understand continuous batching | `module 13` | concurrency sweep and `max-seqs-8` queueing | Lab 3 | locates the knee of aggregate TPS and explains it |
| 13 | understand KV-cache management and PagedAttention | `module 14` | KV usage panel, preemption counter under `kv-constrained` | Lab 4 | explains why a longer context reduces concurrent capacity |
| 14 | experiment with concurrency, context, batching, quantization, prefix caching, tensor parallelism | `module 12` to `module 17`, `module 18` | each as a controlled one-variable experiment; tensor parallelism is an exercise in arithmetic plus an optional demo on a two-GPU machine, and it was never measured here | Lab 3, Lab 4, trainer demos | group report: written prediction, before, after, metric improved, metric degraded, quality, memory, operations, recommendation |
| 15 | containerize inference services | `module 20` | Dockerfile and compose file read line by line; CPU-only client image built on laptops | laptop exercise of `module 20` | builds and runs `apps/inference-client` image against the group endpoint |
| 16 | monitor an inference deployment | `module 21` | live dashboard during load | incident exercise of `module 21` | names the metric that shows queueing, KV pressure and an idle GPU |
| 17 | understand production scaling strategies | `module 16`, `module 19`, `module 22` | replica vs tensor-parallel: an exercise in arithmetic plus an optional demo on a two-GPU machine; it was never measured here | Lab 5 | scaling strategy and bottleneck stated in the architecture document |
| 18 | reason about latency, throughput, quality, memory, concurrency, cost | all labs, `module 22` | cost per useful workload from measured TPS | Lab 4, Lab 5 | every recommendation names what is traded |
| 19 | understand security implications of self-hosted AI | `module 23` | exposure facts of the pods themselves; advisory timeline | Lab 5 | security boundary and threats listed in the architecture |
| 20 | understand digital sovereignty beyond "running Ollama locally" | `module 01`, `module 23` | sovereignty formula applied to this workshop's own setup | Lab 5 | classifies each component by data, model, infrastructure, operations, portability |
| 21 | integrate a local model into an application | `module 24`, `module 25` | `apps/inference-client`, structured output | guided runs of `module 24` and `module 25` | calls the model from code with a JSON-schema response |
| 22 | place RAG, tool calling, MCP and agents in the architecture | `module 24`, `module 25` | agent loop with token accounting | Lab 5 | architecture shows application layers on top of inference and counts their extra model calls |
| 23 | design a production inference architecture | `module 19`, `module 26`, `module 27` | decision framework | Lab 5 | `workshop-artifacts/production-architecture.md`, defended in a short defense with questions from another group (`module 27`) |

## 4. Module by module

Modules are listed in path order. Each lists goal, concepts, the demonstration or experiment, the production consequence, and what can be cut when the group needs the room elsewhere. The experiment rhythm is spelled out for modules that have one. Predictions are hypotheses to be tested, never results. Lab 1 follows the sizing and mechanics modules, because it uses their arithmetic.

### Understand and run (modules 01 to 09)

**`01-opening` (all layers).** Why organizations run models themselves: privacy, sovereignty, cost control, specialization, latency, regulation. Compare laptop, dedicated GPU server, private data center, dedicated GPU cloud, sovereign cloud. Introduce `TRAINING ≠ FINE-TUNING ≠ INFERENCE` and the three layers. Consequence: the rest of the workshop is about engineering a system, not about a download. Cut: shorten the comparison discussion; the opening round is optional.

**`02-models` (runtime).** Tokens, embeddings, transformer blocks, attention, context, autoregressive generation, dense vs mixture-of-experts, reasoning and multimodal models; training only as far as it explains inference. Demonstration: tokenise a sentence on the live server (`/tokenize`); the KV-cache arithmetic for the pinned model is a forward reference to `module 04` and is not done here. Consequence: parameters decide memory, architecture (KV heads, layers) decides KV cost. Cut: multimodal and reasoning detail.

**`03-gpu-fundamentals` (runtime).** CPU vs GPU, SMs, Tensor Cores, VRAM, memory bandwidth, FLOPS, PCIe and NVLink, GPU generations, and how to reason about hardware rather than memorise a catalog. Dense vs sparse numbers; the workshop GPU in detail (1,597 GB/s, no NVLink). The roofline is taught here: the ops:byte ratio of a GPU decides which phase is limited by what (it is revisited for prefill and decode in `05-inference-mechanics`). `nvidia-smi` utilization is not efficiency.

**`04-gpu-sizing` (runtime).** `WEIGHTS + KV CACHE + RUNTIME OVERHEAD = VRAM`; `weights ≈ parameters × bytes per parameter` for BF16, FP16, FP8, INT8, INT4; then why it is incomplete: KV cache, context, concurrency, batch behavior, runtime memory, CUDA graphs. Experiment: predict the KV capacity of the pinned model with `scripts/sizing.py`, then compare with the server log line `GPU KV cache size: N tokens` (experiment `baseline`). Consequence: capacity planning is arithmetic you can check; Lab 1 uses it and Lab 2 checks it against the server.

**`05-inference-mechanics` (runtime).** Prompt → prefill → first token → decode loop; TTFT, ITL, TPS, end-to-end latency; the roofline from `03-gpu-fundamentals` applied to the two phases, conceptually, with no mathematical lecture. Demonstration: one streamed request with timestamps. A prediction is written down here and scored later: prefill scales with prompt length and is compute-heavy; decode is limited by moving weights and KV through memory. Lab 1 relies on prefill and TTFT from this module.

**`06-model-selection` (runtime).** Families (Qwen, Llama, Gemma, Mistral, DeepSeek, Kimi), general vs reasoning vs coding vs multilingual, tool use and structured output; size and active parameters, context, licenses, quantization and engine compatibility, memory. Evaluation beyond leaderboards. Licenses are read per repository at the pinned revision because they drift (RESEARCH 11.4). It comes after the sizing and mechanics modules, so the memory and latency arguments are available. Consequence: the smallest model that reliably does the task.

**`07-lab-model-selection` (Lab 1, task `01-model-selection`).** Four scenarios (internal German-language assistant, customer-service classification and extraction, coding assistant, high-volume document pipeline). Each sub-group takes one scenario first, finishes it, then takes another or swaps; groups fill model, precision, hardware, engine, context and reasoning, and defend the trade-offs. Validation: `workshop-artifacts/model-selection.md`. Cut: reduce to two scenarios; reduced scope is a legitimate outcome.

**`08-first-vllm` (demo).** Trainer shows `nvidia-smi`, `/v1/models`, a completion, streaming, server logs, and the startup log (weights, KV cache, CUDA graphs, time to ready). Consequence: the API is the product; everything else is what makes it behave.

**`09-lab-first-server` (Lab 2, task `02-first-inference-server`).** SSH in, inspect the GPU and the service, query the API, stream, read logs, watch GPU utilization, vary prompt length, output length and temperature, record observations. The point is the chain `REQUEST → MODEL → GPU → TOKENS → METRICS`, not "the API returns text". Recovery: `./scripts/reset.sh lab-02`.

### Measure and optimize (modules 10 to 18)

**`10-checkpoint` (discussion).** Reconstruct `CLIENT → API → vLLM → MODEL → GPU` and ask groups to predict bottlenecks before measuring anything. Predictions are written down and scored in the last slides of `18-demos`.

**`11-measuring`.** User-facing metrics (TTFT, ITL, output TPS, end-to-end latency), system metrics (requests/s, input/output/total tokens/s, running and waiting requests), distributions (p50, p90, p95, p99), hardware (GPU utilization, VRAM, power). "Average latency is not enough." Metric definitions differ between tools (RESEARCH 10.4), which is why the workshop harness defines its own and cross-checks against `vllm bench serve`. Closed-loop vs open-loop load and coordinated omission, goodput against an SLO. Little's law (concurrency = arrival rate × time in the system) is first explained here.

**`12-lab-benchmark` (Lab 3, task `03-benchmark`).** Concurrency 1, 4, 8 and 16 on the same deployment; capture TTFT p50/p95, latency p50/p95, output TPS, aggregate TPS, GPU utilization, VRAM; JSON plus Markdown. Four roles per group (driver, dashboard reader, recorder, skeptic) rotate for the contention round. Questions: when does throughput stop scaling, when does latency deteriorate, what looks saturated, what would you deploy, why. Experiment (`baseline`, `concurrency`): **hypothesis** aggregate TPS rises with concurrency until another resource saturates; **measure** the sweep; **explain** batching raises useful work per weight read; **consequence** concurrency and batching trade throughput against latency. Cut: reduce to concurrency 1, 8, 16.

**`13-continuous-batching`.** Why naive one-request-at-a-time execution wastes the GPU; static, dynamic and continuous batching; scheduling, arrival, different output lengths, queueing; chunked prefill. Connect directly to Lab 3 observations; show `max-seqs-8` to make queueing visible (experiment `concurrency`).

**`14-kv-cache`.** Recompute vs reuse; why the KV cache consumes VRAM; `LONGER CONTEXT + MORE CONCURRENT REQUESTS = MORE KV CACHE`; PagedAttention (fragmentation, page-based allocation, dynamic workloads); prefix caching. Experiments `context-length` (profiles `baseline` and `kv-constrained`: KV usage, queueing, preemptions) and `prefix-cache` (profiles `baseline` and `no-prefix-cache` with the `shared-prefix` workload: TTFT and hit rate).

**`15-quantization`.** BF16, FP16, FP8, INT8, INT4; weight, activation and KV-cache quantization; effects on memory, quality, compute, bandwidth, throughput, latency and compatibility. Not "lower precision is always faster": quantization changes the resource profile. Experiment `quantization`: profiles `baseline`, `fp8`, `kv-fp8`; memory, KV capacity, TTFT, TPS and a small quality spot check (so the 2 % regression bound in the SLO is a measured number).

**`16-parallelism`.** Replica (data-parallel) serving vs tensor parallelism; pipeline and expert parallelism; communication over PCIe, NVLink, NVSwitch, network. "More GPUs do not automatically mean lower latency." Tensor parallelism is an exercise in arithmetic plus an optional demo on a two-GPU machine (PCIe, no NVLink on this card); it was never measured here (no two-GPU stock in the validation), so the slides present its design and hypothesis and say so (experiment `tensor-parallel`).

**`17-lab-optimize` (Lab 4, task `04-optimization`).** Each group takes one lever (quantization, prefix caching, context length and pool size, or the concurrency cap; an optional fifth, tensor parallelism, only if a two-GPU machine is available) and a variation of it that the lectures did not show. Written prediction before anything runs → experiment → measurement → comparison of prediction, result and the lecture's reference → explanation in terms of the resource model, then a short report that leads with the trade-off and with what the prediction got wrong: before, after, metric improved, metric degraded, quality impact, memory impact, operational impact, recommendation. Reference results exist for what the lectures showed, not for the variations. Groups change the server only through `wsctl` profiles, coordinated within the group.

**`18-demos` (skippable).** Trainer demonstrations that are risky or expensive for every group: n-gram speculative decoding (`spec-ngram`) and the intentional failure `oom-demo`, both measured (`experiments/demos/RESULTS.md`). Prepared but not run in the validation: vLLM against Ollama or llama.cpp under concurrency and the MoE model; tensor parallelism only on a two-GPU machine, never measured. Skip the demos, not the last three slides: predictions scored, five sentences, the bridge to production.

### Operate (modules 19 to 27)

**`19-production-architecture` (infrastructure).** From `CLIENT → API → INFERENCE SERVER → GPU` to API gateway, auth, load balancer, inference replicas and a GPU pool, then metrics, logs, traces, model registry, secrets, storage, health checks. State, stateless services, streaming, timeouts, retries, queues and backpressure.

**`20-containerization`.** Docker, CUDA base images, host drivers and CUDA compatibility, image size, build-time vs runtime model downloads, the model cache, reproducibility, configuration. `docker run model-server` does not imply a reproducible deployment. Participants build the CPU-only `apps/inference-client` image on their laptops and run it against the group endpoint through their SSH tunnel; the vLLM image and `monitoring/docker-compose.yml` are read line by line. The pods themselves cannot run Docker (RESEARCH 7.3), which is itself a lesson: on a managed platform the image is the deployment unit.

**`21-observability`.** vLLM metrics, Prometheus, Grafana, GPU metrics. The compact dashboard (request rate, TTFT, latency, tokens/s, running, waiting, GPU utilization, VRAM) plus KV usage, prefix hit rate, preemptions and estimated MFU/MBU. Incident exercise: each group gets one ticket, in parallel; the trainer starts the load on each group's server with the profiles and harness options named in the slides, and groups diagnose it from the dashboard. The expected readings in the answer key are hypotheses until a dry run: no measured file exists for these conditions.

**`22-scaling`.** Vertical, horizontal and model-parallel scaling; replicas, load balancing, autoscaling, queues, cold starts (measured start-up time of this setup), GPU utilization; KV-aware routing and prefill/decode disaggregation conceptually.

**`23-security-sovereignty`.** Data-flow mapping (prompts, responses, logs, embeddings, weights, telemetry), GDPR and PII, retention, auditability, EU AI Act roles and Art. 50 as engineering inputs (not legal advice), supply-chain pinning (model, tokenizer, container, packages, CUDA, engine), open weights vs open source, the sovereignty formula `DATA + MODEL + INFRASTRUCTURE + OPERATIONAL CONTROL + PORTABILITY`, production security (TLS, keys, isolation, secrets, least privilege, air-gapped operation) and LLM application security (prompt and tool injection, output validation, authorization). The workshop's own pods are the case study: open model, EU region, US provider.

**`24-rag`.** `DOCUMENTS → CHUNKING → EMBEDDINGS → INDEX → RETRIEVAL → CONTEXT → LLM` with `apps/rag-demo`: no framework, each step prints what it costs, including the extra prompt tokens. Chunk size, retrieval quality, reranking, freshness (the handbook contains a superseded policy on purpose). Frameworks are discussed after the architecture is understood.

**`25-tools-agents`.** Tool calling as a protocol between model and application; MCP as an interface layer (the demo ships a stdlib server and client); agents as loops. The token ledger of `apps/tool-calling-demo` shows `ONE USER REQUEST → MULTIPLE MODEL CALLS → MORE TOKENS → MORE GPU LOAD`, which reconnects the application layer to capacity planning.

**`26-lab-architecture` (Lab 5, task `05-production-design`).** Scenario per group (sensitive internal assistant, German customer service, coding assistant for 100 developers, offline document pipeline). Design model, precision, GPU, engine, context, replicas, API, authentication, observability, RAG, scaling, security, SLO; estimate concurrency, latency target, GPU requirement, expected bottleneck and scaling strategy. Deliverable: `workshop-artifacts/production-architecture.md`. The lab ends at what the groups produce; the defenses happen in `27-capstone-close`.

**`27-capstone-close`.** Each group gives a short defense and another group asks the questions; there is no single correct answer, only the quality of the reasoning. The defenses are the debrief of Lab 5. Close with the 15-question decision framework and the final slide.

### The 15 decision questions (closing slide)

1. What task are we solving? 2. What quality do we need? 3. What is the smallest model that satisfies it? 4. What traffic do we expect? 5. What is our latency budget? 6. How large is the context? 7. What concurrency do we expect? 8. How much VRAM is required? 9. What hardware bottleneck do we expect? 10. What does the baseline benchmark show? 11. Which optimization addresses the measured bottleneck? 12. Does it degrade quality? 13. What should we monitor? 14. What security boundary is required? 15. What does this cost per useful workload?

## 5. Experiments catalog

Every experiment lives in `experiments/<name>/` with a README (hypothesis, variable, procedure), a `run.sh`, raw results under `benchmark/results/` and a `RESULTS.md` that states what was measured and what surprised. Predictions below are hypotheses, not results; the results documents replace them.

| Experiment | Question | One variable | Profiles | Primary metrics | Used in |
| --- | --- | --- | --- | --- | --- |
| `baseline` | Does the KV-cache formula predict the server? What does one request cost? | none (single request, then low load) | `baseline` | startup time, weights memory, KV tokens, TTFT, ITL | `module 04`, `module 08`, Lab 3 |
| `concurrency` | Where does aggregate throughput stop scaling? | concurrency 1 to 64; `max-num-seqs` | `baseline`, `max-seqs-8` | aggregate TPS, TTFT p95, output TPS per request, running/waiting | `module 12`, `module 13`, Lab 4 |
| `context-length` | How do prompt length and KV capacity change TTFT, ITL and concurrency? | input tokens 512 to 32k; KV budget | `baseline`, `kv-constrained` | TTFT, ITL, KV usage, preemptions, waiting | `module 14`, Lab 4 |
| `quantization` | What does FP8 change in memory, speed and quality? | weights FP8; KV cache FP8 | `baseline`, `fp8`, `kv-fp8` | VRAM, KV tokens, TTFT, TPS, quality spot check | `module 15`, Lab 4 |
| `prefix-cache` | How much prefill does a shared prefix save? | prefix caching on/off | `baseline`, `no-prefix-cache` | TTFT, hit rate, prefill tokens | `module 14`, Lab 4 |
| `tensor-parallel` | When do two GPUs help latency or throughput? | TP=2 vs one replica per GPU | `tp2`, `baseline` | latency, TPS, GPU power | `module 16`, `module 17` (optional fifth lever); never measured |
| `demos` | Speculative decoding, intentional OOM; prepared but not run: vLLM vs Ollama, MoE | per demo | `spec-ngram`, `oom-demo`, others | per demo | `module 18` |

## 6. Heise coverage matrix

Every advertised item of the public workshop page ([RESEARCH 1](RESEARCH.md)) has a home. "Guided run" means the trainer drives and participants follow with their own copy; "extension" means optional work in the task's *Further Exploration*.

| Heise block | Where it is taught | How |
| --- | --- | --- |
| 1 Fundamentals: models, transformer, attention, training, tokenization, embeddings, inference, context windows, reasoning, fine-tuning and alignment, limits and errors | `module 02`, `module 01`, `module 05` | lecture with live server demonstrations; fine-tuning and alignment compactly (what changes, what it costs, when not to) |
| 2 Model evaluation and selection (all criteria, benchmarks, licenses, exercise) | `module 06`, `module 07` | Lab 1; `docs/MODEL-SELECTION.md` |
| 3 Security, compliance, sovereignty (AI Act roles, data flows, labeling duties, logging, supply chain, open weights vs open source, lock-in, reproducibility, air-gapped, PII, prompt and tool injection, guardrails, model cards, security by design) | `module 23`, `module 01`, `module 06` | lecture and data-flow exercise; labeling duty (Art. 50) and model cards as engineering inputs; `docs/SECURITY.md`, `docs/DIGITAL-SOVEREIGNTY.md` |
| 4 Hardware and architecture (CPU vs GPU, memory, quantization, on-prem, cloud, hybrid) | `module 03`, `module 04`, `module 15` | lecture, sizing, experiment; CPU inference (llama.cpp, Ollama) is discussed in `module 03`; the comparison demo is prepared but was not run (`experiments/demos/RESULTS.md`, `VALIDATION.md`) |
| 5 Inference servers (vLLM, SGLang, Ollama, LM Studio; OpenAI-compatible APIs; exercises) | `module 08`, `module 09`, `module 18` | Labs 1 and 2; positioning table of engines; an Ollama comparison demo is prepared but was not run, so Ollama is positioned on slides only |
| 6 Deployment and scaling (Docker, load balancing, parallelization, cost; compare deployment approaches) | `module 20`, `module 22`, `module 16` | container exercise on laptops; replica vs tensor-parallel as arithmetic (never measured); the vLLM vs Ollama comparison is a prepared demo that was not run |
| 7 Security and operations (monitoring, logging, access, data protection; performance measurement and optimization) | `module 21`, `module 23`, Labs 3 and 4 | dashboard investigation; benchmark and optimization labs |
| 8 RAG (fundamentals, embeddings, chunking, vector databases, knowledge management; build a RAG system) | `module 24` | guided run of `apps/rag-demo` (numpy index); vector databases discussed as the next step; extension: change chunking and observe retrieval |
| 9 Agentic AI (tool calling, structured output, multi-agent, MCP; build a simple agent) | `module 25`, `module 24` | guided run of the agent loop and the MCP server; multi-agent systems explained as more model calls (token ledger); extension: add a tool |
| 10 Frameworks (LangChain/LangGraph, Python AI apps) | `module 24`, `module 25` | positioning slide after the framework-free implementation; what a framework adds and hides |
| 11 Integration (REST, web apps, chatbots, automation, local model in an application, near-production proof of concept) | `module 24`, `module 25`, `module 26`, `apps/` | `apps/inference-client` (structured output, batch pipeline); Lab 5 architecture as the near-production design |
| 12 Best practices (errors, pitfalls, production recommendations) | `module 27`, all labs | decision framework; common-failure notes in each task and in `docs/TROUBLESHOOTING.md` |

## 7. Optional and skippable content

When the group needs the room elsewhere, cut in this order and keep every lab's debrief:

1. The demos of `18-demos` (the only module marked `skippable` in `config/workshop.yaml`); the trainer can show one demo inside `module 16`. Keep the last three slides of the module (predictions scored, the five sentences of the runtime part, the bridge to production): they close the runtime part.
2. In `02-models`, skip multimodal and reasoning detail.
3. In Lab 1, two scenarios instead of four.
4. In `12-lab-benchmark`, concurrency 1, 8, 16 only.
5. In `22-scaling`, shorten KV-aware routing and disaggregation to one slide.
6. Lab 5: one scenario defended per group, shorter defenses.

`FACILITATOR.md` (section 8) carries the same list with pacing advice that needs no clock.

## 8. Assumptions, and what validation found

Decided in advance, re-checked on the actual hardware; the evidence for each is in [`VALIDATION.md`](VALIDATION.md).

- vLLM v0.31.0 runs the pinned dense BF16 and FP8 models correctly on the RTX PRO 6000 (SM120). **Confirmed** on two different hosts; the vLLM documentation still never names the card (RESEARCH 3.3).
- Multi-user SSH over a single exposed TCP port, accounts, isolation and revocation. **Confirmed**. Persisted accounts after a pod restart: **not possible by design**, because the shared volume enforces no permissions; accounts come back from `infra/participants.yaml` in a rebuild of about 5 min 41 s (`docs/GPU-POOL.md`).
- Whether pods expose enough privilege for `nvidia-smi` and NVML metrics. **Confirmed**: the exporter and the dashboard work; the proxy limit of 100 seconds is never used because access is through SSH tunnels.
- Cold start of a fresh pod: **measured** (176 s to ready in the engine log, about 198 s as `wsctl` measures it; 5.5 minutes for the whole deployment); the canonical statement of all start-up times is in `FACILITATOR.md`, section 3.
- Human time: the **machine time** of tasks 02 to 04 was measured as a participant on a fresh pod; the human time with real participants is **not** measured and remains the trainer's dry run (`FACILITATOR.md`, section 2). No timeboxes exist any more: the tasks say what counts as done, not how long it takes.
