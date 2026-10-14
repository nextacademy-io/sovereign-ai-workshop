# Research

> Status: working reference for the workshop authors, not participant material.
> Verified 2026-10-14. Every number that appears on a slide traces back to a section here or to a result file under `benchmark/results/`.
> This is engineering context. **It is not legal advice.**

## How to read this document

Each topic separates three kinds of statement, in this order:

- **Source facts**: what a primary source says, with a link. Flag names, defaults, metric names, numbers and licence names are verbatim. `Unverified:` marks anything not confirmed from a primary source; `Caution:` marks a stale document or a contradiction between sources; `DERIVED` marks arithmetic done here, with the arithmetic shown.
- **Interpretation**: what the facts mean for teaching or operating inference. This is the author's inference.
- **Workshop decision**: what this repository does because of it, naming the implementing file.

Sources are primary where possible: vLLM source and docs at the `v0.31.0` tag, Hugging Face model cards and licence files, NVIDIA datasheets and documentation, original papers, EU legal texts and official guidance, the Runpod documentation and live reads of the Runpod API. The book *Inference Engineering* is cited by chapter only. Web pages were mostly read through a summarising fetch tool: **re-read a primary source before putting a quotation on a slide.**

| # | Topic | Spec topic |
|---|---|---|
| 1 | Heise workshop promises | 1 |
| 2 | The *Inference Engineering* book | 2 |
| 3 | vLLM capabilities | 3 |
| 4 | Hugging Face ecosystem | 4 |
| 5 | Suitable open models | 5 |
| 6 | GPU options and hardware reasoning | 6 |
| 7 | Infrastructure provider and Runpod capabilities | 7 |
| 8 | Quantization support | 8 |
| 9 | vLLM metrics | 9 |
| 10 | Benchmark tooling | 10 |
| 11 | Model licences | 11 |
| 12 | EU regulatory information | 12 |
| 13 | Security of self-hosted inference | (security and sovereignty block) |
| 14 | Decision log | |

## 1. Heise workshop promises

Verified 2026-10-14. The public workshop page is the contract with participants. Every advertised topic is kept; `docs/CURRICULUM.md` maps each to a block, a task, a trainer demo or an optional extension.

**Source facts**

- Title: "KI ohne Cloud: Modelle lokal betreiben, eigene Daten anbinden, Prozesse automatisieren". Trainer named on the page: Pawel Sawicki. Format: remote via Zoom, hands-on, three days, maximum 15 participants per group. Tags: AI, GenAI, AI Agents, Local AI, RAG, Agentic AI. ([Heise Conferences](https://heise-conferences.de/workshop/ki-ohne-cloud-modelle-lokal-betreiben-eigene-daten-anbinden-prozesse-automatisieren-7pGZZ_Av1UVbYi))
- Status when checked: the page shows "Event abgesagt" (event cancelled), mentions "weitere Termine" (further dates) and lists no dates, times or price. ([Heise Conferences](https://heise-conferences.de/workshop/ki-ohne-cloud-modelle-lokal-betreiben-eigene-daten-anbinden-prozesse-automatisieren-7pGZZ_Av1UVbYi))
- Learning goals advertised: choose suitable models for different use cases; run local models efficiently and at reasonable cost; build inference servers and deployment architectures; connect own data to models with RAG; automate routine tasks with agents; judge what local AI can and cannot do. ([Heise Conferences](https://heise-conferences.de/workshop/ki-ohne-cloud-modelle-lokal-betreiben-eigene-daten-anbinden-prozesse-automatisieren-7pGZZ_Av1UVbYi))
- Target audience: software developers adding AI features with local models; AI/ML engineers and data scientists connecting their own data to local models; IT architects running and deploying local AI. Prior knowledge: basic Python, software development experience, basic API knowledge. Technical requirements: laptop with admin rights and Docker, at least 20 GB free disk, internet access; Python 3.11+ and VS Code optional. Included: workshop materials, certificate of participation. ([Heise Conferences](https://heise-conferences.de/workshop/ki-ohne-cloud-modelle-lokal-betreiben-eigene-daten-anbinden-prozesse-automatisieren-7pGZZ_Av1UVbYi))
- Trainer profile: Senior ML Engineer and software architect with over 15 years of experience; focus on deep learning, NLP, LLM systems, end-to-end AI pipelines, LoRA/PEFT fine-tuning, RAG, high-performance inference and agents; tools PyTorch, Hugging Face Transformers, vLLM, LangChain, LangGraph. ([Next Academy trainer page](https://www.nextacademy.io/de/trainers/pawel-sawicki))

**The twelve advertised agenda blocks** (translated; the page lists every sub-item, all are kept):

| # | Block as advertised | Sub-items on the page |
|---|---|---|
| 1 | Fundamentals | model overview (Llama, Qwen, Gemma, Mistral, DeepSeek, Kimi); transformer and attention; LLM training; tokenization and embeddings; inference and context windows; reasoning and capabilities; fine-tuning and alignment; limits and typical errors |
| 2 | Model evaluation and selection | selection criteria for open models; task-oriented selection; general-purpose vs reasoning models; coding models and models for agentic AI; backbone models for multi-agent systems; models for RAG and tool calling; fine-tuning and domain adaptation; structured output and function calls; context windows and multimodality; benchmarks, evaluation, quality criteria; resources, inference speed, operating costs; licences and commercial use; exercise: select models for concrete scenarios |
| 3 | Security, compliance, sovereignty | EU AI Act roles (provider vs deployer); data protection and data flows; labelling duties for AI-generated content; logging, tracing, auditability; model supply chain; open weights vs open source; licensing and commercial use; vendor lock-in and model portability; reproducible deployments and versioning; air-gapped and on-prem architectures; PII detection and data minimization; prompt injection and tool injection; guardrails and policy enforcement; model cards and technical documentation; security-by-design |
| 4 | Hardware and architecture | CPU vs GPU systems; memory needs; quantization; on-prem, cloud, hybrid |
| 5 | Inference servers | vLLM, SGLang, Ollama, LM Studio; OpenAI-compatible APIs; exercises: install and run an inference server, provide custom interfaces |
| 6 | Deployment and scaling | Docker, model deployment, load balancing, parallelization, cost optimization; exercise: compare deployment approaches |
| 7 | Security and operations | monitoring, logging, access concepts, data protection and security; exercise: performance measurement and optimization |
| 8 | RAG | fundamentals, embeddings, chunking strategies, vector databases, knowledge management with local models; exercise: build your own RAG system |
| 9 | Agentic AI | tool calling, structured output, multi-agent systems, MCP, agentic AI; exercise: build a simple agent |
| 10 | Frameworks | LangChain/LangGraph, Python-based AI apps |
| 11 | Integration | REST APIs, web apps, chatbots, automation and workflows; integrating a local model into an application; building a near-production proof of concept |
| 12 | Best practices | typical errors and pitfalls, recommendations for production use |

**Interpretation.** The public page is broad: twelve blocks, six exercises, RAG, agents and frameworks. The workshop spec for this repository asks for the same breadth with an inference-engineering centre of gravity, a ceiling of six substantial tasks, and RAG/tools/agents positioned as application layers. Three items need care because they would otherwise dominate the schedule: "build your own RAG system", "build a simple agent" and "LangChain/LangGraph". The page also names Zoom as the remote tool and says laptops need Docker, which shapes where the containerization block can run (see section 7).

**Workshop decision.**

- All twelve blocks stay. RAG, tool calling/MCP and agents become guided runs of `apps/rag-demo` and `apps/tool-calling-demo` inside Day 3 blocks (`config/workshop.yaml`, blocks `d3-06-rag`, `d3-07-tools-agents`); frameworks get a positioning slide after the framework-free implementation is understood; "compare deployment approaches" is covered by the vLLM-vs-Ollama/llama.cpp concurrency demo and the replica-vs-tensor-parallel experiment.
- The mapping from each advertised sub-item to a block, task, demo or extension lives in `docs/CURRICULUM.md`.
- Content never records event dates, because the page currently lists none (`pnpm check` rejects calendar dates in teaching content).

**Not verified.** Whether the event will be rescheduled, its dates, price and group sizes. The page text above was read through a summarising fetch tool on 2026-10-14; re-read the page before the workshop.

## 2. The "Inference Engineering" book as a technical reference

Verified 2026-10-14 against the local PDF text. The book is a reference, not a source of text or figures: concepts are re-explained in original words, with original diagrams and with experiments.

**Source facts**

- *Inference Engineering*, Philip Kiely (Baseten Books, 2026), ISBN 979-8-9943597-2-3; copyright © 2026 Baseten Labs, Inc.; no edition number stated; the author works for Baseten.
- Structure by printed page: Ch. 0 Inference (p. 15); Ch. 1 Prerequisites (p. 23: 1.3 Model Selection p. 31, 1.4 Measuring Latency & Throughput p. 35); Ch. 2 Models (p. 39: 2.2 LLM Inference Mechanics p. 46, 2.4 Calculating Inference Bottlenecks p. 61, 2.5 Optimizing Attention p. 67); Ch. 3 Hardware (p. 71: 3.1 GPU Architecture p. 74, 3.2 Generations p. 77, 3.3 Instances p. 83, 3.5 Local Inference p. 89); Ch. 4 Software (p. 93: 4.1 CUDA p. 96, 4.3 Inference Engines p. 105, 4.5 Benchmarking & Load Testing p. 112); Ch. 5 Techniques (p. 117: 5.1 Quantization p. 120, 5.2 Speculative Decoding p. 129, 5.3 Caching p. 136, 5.4 Model Parallelism p. 142, 5.5 Disaggregation p. 148); Ch. 6 Modalities (p. 153); Ch. 7 Production (p. 177: 7.1 Containerization p. 179, 7.2 Autoscaling p. 183, 7.4 Testing & Deployment p. 199 incl. observability); Appendix A Glossary (p. 209); Appendix B Recommended Reading (p. 231).
- Topics the book covers that the workshop uses as conceptual anchors: prefill vs decode and their different bottlenecks (Ch. 2.2, 2.4); TTFT / TPS / percentiles and the end-to-end vs inference-only distinction (Ch. 1.4); ops:byte ratio and arithmetic intensity (Ch. 2.4); static, dynamic and continuous batching (Ch. 7.2); quantization formats and which tensors tolerate lower precision (Ch. 5.1); speculative decoding variants (Ch. 5.2); prefix caching and cache-aware routing (Ch. 5.3); tensor, expert and pipeline parallelism (Ch. 5.4); prefill/decode disaggregation and when it pays (Ch. 5.5); containers, autoscaling, cold starts, canary deployment, observability (Ch. 7).
- Gaps in the book, relevant to the workshop (checked by reading the whole text): no per-token KV-cache formula; no GQA/MQA/MLA effect on KV size; no `vllm bench`, GuideLLM or metric names; no discussion of open-loop vs closed-loop load or coordinated omission; only a two-sentence PagedAttention definition without attribution; one passing mention of llama.cpp and Ollama; no data parallelism for LLMs; no $/GPU-hour figures or worked cost-per-million-tokens example; no Prometheus metric names.
- Internal inconsistencies to avoid repeating: B200 memory is given as 180 GB in one place and 192 GB in another; MIG slice counts differ between the chapter and the glossary; one hardware line says "Grace GPUs" where Grace CPUs are meant.
- Bias: the book is written by a vendor employee and favours TensorRT-LLM (the vendor uses it most); the engine comparison table should be read with that in mind.

**Interpretation.** The book gives the workshop its systems vocabulary and its optimisation menu, but not the numbers or tooling. Every gap above is a place where this repository must bring its own primary sources and its own measurements, which matches the workshop's measure-then-teach principle.

**Workshop decision.**

- Cite the book by chapter and section only, never by quotation; diagrams are original (`slides/components/`); the formulas the book omits come from vLLM source and docs (sections 3 and 9) and from the original papers (`docs/REFERENCES.md`).
- The KV-cache formula is taught and checked against the vLLM startup log (`scripts/sizing.py`, `infra/pod/server-info.py`).

**Not verified.** Equations and code in the book are images in the extracted text; anything quoted from them must be checked in the PDF first.

## 3. vLLM capabilities

Verified 2026-10-14. Release under test: vLLM v0.31.0. "SRC" below means the source tree or `docs/` folder at the `v0.31.0` tag on GitHub; docs.vllm.ai builds from the same `docs/` files, but `/en/latest` is a developer preview and can be ahead of the release.

Caution: `docs.vllm.ai/en/latest` lists metrics that are not in the v0.31.0 source (see section 9). Use `/en/stable` or the tag for release-accurate statements.

### 3.1 Current release and install artifacts

**Source facts**

- Latest stable release is v0.31.0, published 2026-10-05T06:44:55Z (`prerelease=false`). Earlier: v0.30.0 (2026-09-22), v0.29.0 (2026-09-09), v0.28.0 (2026-08-26), v0.27.1 (2026-08-11), v0.27.0 (2026-08-10). ([GitHub releases API](https://api.github.com/repos/vllm-project/vllm/releases?per_page=8))
- "This release features 717 commits from 307 contributors (96 new)!" ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- PyPI `vllm` 0.31.0: licence Apache-2.0; `requires_python` `<3.15,>=3.10`; pins `torch==2.13.0`, `torchaudio==2.11.0`, `torchvision==0.28.0`, `flashinfer-python==0.7.0.post1`, `xgrammar==0.2.7`, `transformers<5.18.0,>=5.10.4`, `nvidia-cutlass-dsl[cu13]==4.7.1`. ([PyPI JSON](https://pypi.org/pypi/vllm/0.31.0/json))
- Release artifact table: `pip install vllm` is "PyPI (CUDA 13.0)"; Docker "CUDA 13.0 (Default)" is `vllm/vllm-openai:v0.31.0`; "CUDA 12.9" is `vllm/vllm-openai:v0.31.0-cu129`. ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Docs state "GPU: compute capability 7.5 or higher (e.g., T4, RTX20xx, A100, L4, H100, B200, etc.)" and "NVIDIA Blackwell GPUs (B200, GB200) require a minimum of CUDA 12.8". ([SRC install doc](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md))
- Caution: the same install doc still says wheels are "compiled with CUDA 12.9 ... by default" and shows `--extra-index-url https://download.pytorch.org/whl/cu129`. That contradicts the release-notes table (PyPI = CUDA 13.0). Treat release notes plus Docker image metadata as authoritative. ([SRC install doc](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md))
- Breaking changes in 0.31.0 that touch workshop topics: online `quantization="fp8"` now redirects to `fp8_per_tensor`; `--enforce-eager` now also disables JIT kernel warmup; `--collect-detailed-traces` comma syntax removed; AllSpark INT8 W8A16 backend removed. ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- New in 0.31.0: `--max-num-active-seqs`; `--long-prefill-token-threshold` adaptive to the number of waiting prefills; `vllm preload` (weight-cache daemon); experimental `vllm snapshot create/restore`; `--tool-strict-level`; `openai-responses` backend and `model_id` in the JSON of `vllm bench`. ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Model Runner V2 (MRV2) is the default runner. `VllmConfig.use_v2_model_runner` returns `VLLM_USE_V2_MODEL_RUNNER` if set, otherwise True unless Triton is missing or an unsupported feature is configured. Then it logs "Model Runner V2 does not yet support ...; using the V1 model runner instead." Unsupported in MRV2: stock torch.compile mode, sequence parallelism with TP>1, speculative methods `ngram`, `ngram_gpu`, `suffix`, `medusa`, `mlp_speculator`, `custom_class`, `mamba_cache_mode='all'`, and others. ([SRC vllm/config/vllm.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/vllm.py))
- vLLM licence: Apache-2.0 (GitHub API and PyPI agree). ([GitHub API](https://api.github.com/repos/vllm-project/vllm))

**Interpretation** (inference)

- "Which CUDA is the default" depends on which page you read. Pin the image digest and read CUDA from the image, not from the docs.
- The n-gram speculative profile silently runs the whole engine on the V1 runner. Any comparison against `baseline` mixes a runner change with a speculation change.

**Workshop decision**

- `infra/versions.env` pins `vllm/vllm-openai:v0.31.0` and its digest. The docs-vs-release-notes CUDA contradiction is why SETUP material must say "CUDA 13.0 image, driver R580 or newer".
- `config/vllm-profiles/spec-ngram.yaml` is labelled a trainer demo. Teach the V1-runner fallback together with it.

### 3.2 Docker image and CUDA/driver requirements

**Source facts**

| Item | Value | Source |
|---|---|---|
| Tag `v0.31.0` manifest list | `sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3` (last updated 2026-10-04T01:11:23Z) | [Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31) |
| `v0.31.0` amd64 image | `sha256:a4a4c0437bf7240089da5f08aa370c4aee17ae5290f7a3b468825ee26c4c3a6b`; 9.04 GB compressed, 40 gzip layers | [registry manifest](https://registry-1.docker.io/v2/vllm/vllm-openai/manifests/sha256:a4a4c0437bf7240089da5f08aa370c4aee17ae5290f7a3b468825ee26c4c3a6b) |
| `v0.31.0` arm64 image | `sha256:3f7dd5b777d34d1724456ce71f87385dca288c3bb23029ab27dee358f5d2b971` | [Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31) |
| `v0.31.0-cu129` | list `sha256:ff29e51a9457f191deb332b96fa6440584fa941aa2a548449b604e2b1e5e1eeb`; CUDA 12.9.1; 11.02 GB | [Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31) |
| `v0.31.0-ubuntu2404` | list `sha256:3fb023cc987cc7c2bca7ca14c1e0aff5ae06bd9431bf07773731ce7e8a682460`; same CUDA 13.0.2 | [Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31) |
| `v0.31.0-x86_64-zstd` | `sha256:017d6959239eec662c0f6b05e1f6bf5a33b69d4b6cd701236e289defbc2c081a`; zstd layers, 7.16 GB vs 9.04 GB gzip | [Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31) |

- 13 `v0.31*` tags exist on Docker Hub (arch and CUDA variants of `v0.31.0`). There is no `v0.31.0-cu130` tag: the default IS CUDA 13.0. Older `latest-cu130` tags are stale since 2026-04-28. ([Docker Hub tags API](https://hub.docker.com/v2/repositories/vllm/vllm-openai/tags?name=v0.31))
- Image env of `v0.31.0` amd64: `CUDA_VERSION=13.0.2`, `TORCH_CUDA_ARCH_LIST=7.5 8.0 8.6 8.9 9.0 10.0 12.0` (no 11.0, although the Dockerfile ARG default at the tag includes 11.0), `VLLM_ENABLE_CUDA_COMPATIBILITY=0`, `NVIDIA_DRIVER_CAPABILITIES=compute,utility`, `VLLM_IMAGE_TAG=vllm/vllm-openai:v0.31.0`, `VLLM_BUILD_COMMIT=db9527a46873454610df6dbedf79a36d6bf1a7f6`. ([registry config blob](https://registry-1.docker.io/v2/vllm/vllm-openai/manifests/sha256:a4a4c0437bf7240089da5f08aa370c4aee17ae5290f7a3b468825ee26c4c3a6b), [Dockerfile](https://github.com/vllm-project/vllm/blob/v0.31.0/docker/Dockerfile))
- `Entrypoint = ["vllm","serve"]`, no `Cmd`, `WorkingDir=/vllm-workspace`, default user root. Arguments after the image name are `vllm serve` arguments. For a shell use `--entrypoint /bin/bash`. A non-root user `vllm` (UID 2000/GID 0) is available via `--user 2000:0` or the build target `vllm-openai-nonroot`. ([docker.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/docker.md), [Dockerfile](https://github.com/vllm-project/vllm/blob/v0.31.0/docker/Dockerfile))
- Base is Ubuntu 24.04 with Python 3.12 (deadsnakes). `curl` and `ps` exist. `sshd`, `wget`, `git` and `nvidia-smi` are not in the image (`nvidia-smi` is injected by the NVIDIA runtime). Only part of the layers was listed for `sshd`; the large pip layers were not streamed. ([Dockerfile](https://github.com/vllm-project/vllm/blob/v0.31.0/docker/Dockerfile))
- `nvcc` and CUDA dev packages are installed because "FlashInfer, DeepGEMM, EP kernels all require compilation at runtime". The image carries `examples/`, `benchmarks/` and a `vllm-rs` binary on PATH. ([Dockerfile](https://github.com/vllm-project/vllm/blob/v0.31.0/docker/Dockerfile), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Docs run line: `docker run --runtime nvidia --gpus all -v ~/.cache/huggingface:/root/.cache/huggingface --env "HF_TOKEN=$HF_TOKEN" -p 8000:8000 --ipc=host vllm/vllm-openai:latest --model Qwen/Qwen3-0.6B`. `--ipc=host` (or `--shm-size`) is required. To persist torch.compile artifacts mount a volume at `/root/.cache/vllm` (`VLLM_CACHE_ROOT`). ([install doc](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md), [docker.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/docker.md))
- Driver: "CUDA 13 requires an R580 or newer driver." Compat mode (`VLLM_ENABLE_CUDA_COMPATIBILITY=1`) "supports R535 and R570 host drivers" but "only supports select professional and datacenter NVIDIA GPUs"; the image ships with it set to 0. ([install doc](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md))
- NVIDIA: CUDA 13.0 maps to driver branch R580; "minor version compatibility for all 13.x releases requires driver >= 580". For reference CUDA 12.9 Update 1 needs >= 575.57.08. ([CUDA toolkit release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html))
- The image's `NVIDIA_REQUIRE_CUDA` is `cuda>=13.0` OR brand/driver ranges for 535, 550, 565, 570, 575. The NVIDIA container runtime refuses to start the container if neither matches. ([registry config blob](https://registry-1.docker.io/v2/vllm/vllm-openai/manifests/sha256:a4a4c0437bf7240089da5f08aa370c4aee17ae5290f7a3b468825ee26c4c3a6b))
- Unverified: the exact lowest 580.x driver for CUDA 13.0.2 (an older NVIDIA table gave 580.65.06 for 13.0 GA and 580.95.05 for 13.0 U2; not re-confirmed on a primary page). Safe guidance: host driver >= 580, or the `-cu129` tag with >= 575.57.08.
- Unverified (inference in the notes): with a 570/575 host driver the CUDA-13 image may pass the runtime's brand/driver check, but CUDA 13 userspace runs only on R580+ or if forward-compat supports the SKU. No primary source says whether compat mode covers RTX PRO 6000.

**Interpretation** (inference)

- The container-start check and the CUDA-userspace check are different things. A pod that starts the container can still fail at CUDA init on a 570/575 driver.
- Pull by digest, not by tag: tags on Docker Hub are mutable. The digests above were observed 2026-10-14 and must be re-checked before a delivery.

**Workshop decision**

- `infra/versions.env` carries `VLLM_IMAGE_TAG` and `VLLM_IMAGE_DIGEST` (the multi-arch list digest above). `docs/SETUP.md` should state the R580+ driver requirement and the `-cu129` fallback.
- `infra/pod/wsctl` exports `HF_HOME`, `HF_HUB_OFFLINE=1`, `VLLM_CACHE_ROOT` and `VLLM_API_KEY`, then runs `vllm serve --config <rendered profile>`.

### 3.3 Blackwell SM120 (RTX PRO 6000) support status

**Source facts**

- No sentence in the install or requirements docs names "RTX PRO 6000", "RTX 5090" or "SM120" as supported. A `grep` of `docs/` finds only `docs/design/attention_backends.md` (the b12x backend "supports causal decoder attention on NVIDIA SM120 and SM121 GPUs") and `docs/features/quantization/b12x.md`. ([SRC docs/design/attention_backends.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/attention_backends.md))
- Evidence that SM120 is a build target: compute capability 12.0 is in `TORCH_CUDA_ARCH_LIST`; `vllm/platforms/cuda.py` special-cases `is_device_capability_family(120)`; an SM120 MLA backend list is `[TRITON_MLA, FLASHINFER_MLA_SPARSE_SM120]`. ([SRC vllm/platforms/cuda.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/platforms/cuda.py))
- SM120 items in release notes: 0.31.0 "DeepGEMM pin bump with SM120 fixes (#57218)", "NoPE sparse MLA on the FlashInfer SM120 backend (#55277)", "SM120 batch-invariant matmul configs (#57456)"; 0.30.0 "B12X causal paged attention for SM120/SM121 via `--attention-backend B12X_ATTN` (#52017)", "SM12x blockwise FP8 CTA raster swizzle for GB10/DGX Spark (#55180)", "W4A4 NVFP4 preferred on SM120/121 (#55170)". ([0.31.0 notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0), [0.30.0 notes](https://github.com/vllm-project/vllm/releases/tag/v0.30.0))
- Attention backend priority for non-MLA models on SM120 (`device_capability.major == 12`): `FLASH_ATTN`, `FLASHINFER`, `TRITON_ATTN`, `FLEX_ATTENTION`, `TURBOQUANT`. On SM100 the order starts with `FLASHINFER`. ([SRC vllm/platforms/cuda.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/platforms/cuda.py))
- FlashAttention version: FA3 on SM90; FA4 only when `device_capability.major == 10` ("restrict to SM100 for now"); otherwise FA2. The docs sentence "Default is FA4 on SM100+ (Blackwell)" is therefore wrong for SM120, which runs FA2. Override with `--attention-config.flash_attn_version=2|3|4`. ([SRC fa_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/attention/backends/fa_utils.py), [attention_backends.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/attention_backends.md))
- Optional SM120/SM121-only backends: `uv pip install "vllm[b12x]"`, then `--attention-backend b12x`, `--linear-backend b12x --moe-backend b12x` (linear: per-tensor FP8, 128x128 block FP8, MXFP8, NVFP4, MXFP4; MoE: NVFP4/MXFP4 only, no expert parallelism). Not in the stock image. ([SRC b12x.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/b12x.md))
- Open SM120 issues, state checked via GitHub API 2026-10-14:

| Issue | State | What |
|---|---|---|
| [vllm #50189](https://github.com/vllm-project/vllm/issues/50189) | open | Xid 31 MMU fault with `flashinfer_b12x` MoE under concurrent chunked prefill, SM120, Qwen3.5-122B-A10B-NVFP4 |
| [vllm #57932](https://github.com/vllm-project/vllm/issues/57932) | open | GLM-5.3-Flash fails with FlashInfer attention on SM120 |
| [vllm #59203](https://github.com/vllm-project/vllm/issues/59203) | open | DeepSeek-V4.1-Flash on SM120: no FlashInfer sparse-MLA kernel for page_block_size=32 |
| [vllm #40677](https://github.com/vllm-project/vllm/issues/40677) | open | Gemma-4 fails when forcing FLASHINFER attention on SM120: head_size not supported |
| [vllm #32826](https://github.com/vllm-project/vllm/issues/32826) | closed, not_planned | MiniMax-M2.1 NVFP4 + expert parallel on RTX PRO 6000 |
| [flashinfer #2577](https://github.com/flashinfer-ai/flashinfer/issues/2577) | closed, completed 2026-07-23 | NVFP4 `mm_fp4` GEMM broken on SM120, all backends |

- All six reports concern MoE, MLA, NVFP4 or forced-FlashInfer paths. None is a plain dense BF16 or FP8 model on default backends. (sources: the six issue links in the table)
- Unverified: that `vllm/vllm-openai:v0.31.0` runs a dense BF16/FP8 model correctly end-to-end on an RTX PRO 6000 Blackwell. All evidence is indirect. A smoke test on the workshop hardware is required.

**Interpretation** (inference)

- SM120 is a compiled-in, actively patched target, but vLLM does not promise it in prose. The risk for this workshop is low for dense Qwen3 on default backends and high for MoE/NVFP4/MLA demos.
- A user who forces `--attention-backend FLASHINFER` or picks an NVFP4 MoE checkpoint walks into the open issues above.

**Workshop decision**

- All profiles in `config/vllm-profiles/` use default attention backends. None forces FlashInfer, b12x or NVFP4.
- The MoE demo (`Qwen/Qwen3-30B-A3B-FP8` in `config/models.yaml`) needs its own smoke test on the pod before it is shown; no evidence in the notes covers MoE FP8 on SM120.
- Open item: record the smoke-test result (model, image digest, driver version, first log lines) in `docs/SETUP.md` before each delivery.

### 3.4 `vllm serve` flags and defaults that matter

**Source facts** (v0.31.0 source; the CLI page confirms the same values)

| Flag | Default | Why it matters |
|---|---|---|
| `--gpu-memory-utilization` | **0.92** (not 0.9) | Fraction of TOTAL device memory budgeted for this instance (weights + profile peak + CUDA-graph estimate + KV). Per instance: two servers on one GPU need fractions that sum below 1. Startup raises `ValueError` if currently free memory < requested. Alias `--device-memory-utilization`. |
| `--kv-cache-memory-bytes` | None | Explicit KV budget per GPU; ignores `--gpu-memory-utilization`. Suffixes: `G` = GiB, `g` = 10^9. NOT `--kv-cache-memory`. |
| `--max-model-len` | from model config | `1k`=1000, `1K`=1024; `-1`/`auto` picks the largest length that fits GPU memory. Sets "Maximum concurrency" in the KV log line. |
| `--max-num-seqs` | not static; `vllm serve` on >=70 GiB non-A100: 1024; else 256 | Running-batch cap. Derived by `get_batch_defaults`. |
| `--max-num-batched-tokens` | not static; `vllm serve` on >=70 GiB non-A100: 8192; >=160 GiB: 16384; else 2048 | Per-step token budget. Raising it lowers KV capacity (profile run at this size). |
| `--max-num-active-seqs` | None (new in 0.31.0) | Caps RUNNING admission below `max_num_seqs` without resizing CUDA graphs. Must be <= `max_num_seqs`. |
| `--performance-mode` | `balanced` | `throughput` doubles unset batch limits; `interactivity` captures fine-grained CUDA graphs 1..32. |
| `--enable-prefix-caching` / `--no-...` | None, resolved to True for generative decoders | ON by default in V1. Off by default for encoder-only/bidirectional pooling models. |
| `--enable-chunked-prefill` / `--no-...` | None, resolved to True for generative decoders | With it off, `max_num_batched_tokens` must be >= `max_model_len`. |
| `--prefix-caching-hash-algo` | `sha256` | Choices `sha256`, `sha256_cbor`, `xxhash`, `xxhash_cbor`. |
| `--block-size` | 16 | Tokens per KV block; backends may override. |
| `--kv-cache-dtype` | `auto` | `fp8` (= `fp8_e4m3`), `fp8_e5m2`, plus newer dtypes (section 8). |
| `--dtype` | `auto` | FP16 for FP32/FP16 models, BF16 for BF16 models. |
| `--quantization`, `-q` | None | None means "read `quantization_config` from the model config". See section 8. |
| `--generation-config` | `auto` | Sampling defaults come from the model's `generation_config.json`; `vllm` uses vLLM's own. A `max_new_tokens` there becomes a server-wide output cap. |
| `--seed` | 0 | Was None in older V1 releases. |
| `--max-logprobs` | 20 | `-1` is uncapped and may OOM. |
| `--enforce-eager` | False | Disables torch.compile and CUDA graphs; in 0.31.0 also disables JIT kernel warmup. |
| `--cudagraph-capture-sizes`, `-cc` | auto list | No `--cuda-graph-sizes` flag exists. Cap is 512 on SM120 (1024 only on SM100-family). `-O2` default gives `FULL_AND_PIECEWISE`. |
| `--speculative-config` | None | One JSON object (YAML: nested mapping). Old `--speculative-model` is deprecated. |
| `--tensor-parallel-size`/`-tp`, `--pipeline-parallel-size`/`-pp`, `--data-parallel-size`/`-dp` | 1 | `--enable-expert-parallel` False. |
| `--runner` | `auto` | `generate`, `pooling`, `draft`. `--task` no longer exists; `--convert embed` adapts a generative checkpoint. |
| `--host` | None (binds all interfaces) | Not loopback. |
| `--port` | 8000 | |
| `--api-key` | None | One or more keys. `VLLM_API_KEY` is used only if the flag is absent. Guards only some paths (section 3.7). |
| `--served-model-name` | model id | First name is the `model_name` Prometheus label and the `model` in responses. |
| `--enable-auto-tool-choice` | False | Requires `--tool-call-parser`, else `TypeError` at startup. |
| `--reasoning-parser` | empty | `qwen3` for Qwen3. |
| `--default-chat-template-kwargs` | None | e.g. `'{"enable_thinking": false}'`; request-level kwargs override. |
| `--enable-log-requests` | False | There is no `--disable-log-requests`. `--disable-log-stats` still exists. |
| `--enable-mfu-metrics` | off | Needed for the `vllm:estimated_*` series. |
| `--trust-remote-code` | False | |
| `--stream-interval` | 1 | Tokens per streamed event (scheduler field; see unverified note below). |
| `--async-scheduling` | None (auto) | Scheduler prepares step N+1 while the GPU runs step N. |

Sources for the table: [cache.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/cache.py), [model.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py), [scheduler.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/scheduler.py), [arg_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py), [cli_args.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/cli_args.py), [vllm.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/vllm.py), [CLI docs page](https://docs.vllm.ai/en/latest/cli/serve/).

**Source facts** (continued)

- `requested_memory = ceil(total_device_memory * gpu_memory_utilization)`. Memory used by other processes before startup is excluded from the measurement but must still leave enough free memory. ([SRC v1/worker/utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/utils.py))
- After defaulting: `max_num_seqs = min(max_num_seqs, max_num_batched_tokens)` and `max_num_batched_tokens = min(max_num_seqs * max_model_len, max_num_batched_tokens)`. ([SRC arg_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py))
- Human-readable ints (`k/K/m/M/g/G/t/T`; lower-case decimal, upper-case binary) work for `--max-model-len`, `--max-num-batched-tokens`, `--max-num-scheduled-tokens`, `--kv-cache-memory-bytes`. Help forms: `vllm serve --help=all`, `--help=ModelConfig`, `--help=max-num-seqs`. Sub-commands: `vllm {chat,complete,serve,launch,bench,collect-env,run-batch,preload}`. ([SRC docs/cli/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/cli/README.md))
- Other scheduler fields in source: `--scheduling-policy` {`fcfs` default, `priority`}, `--long-prefill-token-threshold` 0, `--max-num-queued-reqs` and `--max-num-queued-tokens` (None; beyond them HTTP 503), `scheduler_reserve_full_isl` True. ([SRC scheduler.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/scheduler.py))
- Unverified: which of those scheduler dataclass fields are exposed as `--` flags. Only `--max-num-seqs`, `--max-num-batched-tokens`, `--max-num-active-seqs` and (in `docs/usage/v1_guide.md`) `--scheduling-policy` were cross-checked.
- Unverified: the 8192/1024 defaults on the workshop card. Derived from `get_batch_defaults` assuming `get_device_total_memory()` reports about 95.6 GiB for a 96 GB RTX PRO 6000; no primary source for the memory figure was fetched. Check the actual startup log.
- Flags that do NOT exist in 0.31.0: `--kv-cache-memory`, `--cuda-graph-sizes`, `--disable-log-requests`, `--task`, `--swap-space`. ([SRC arg_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py))

**Interpretation** (inference)

- The two defaults most often misquoted are `--gpu-memory-utilization` (0.92) and the batch limits (hardware-dependent). Always print them from the startup log instead of quoting a number.
- `--generation-config auto` silently changes sampling. A benchmark or an eval that does not set it is not reproducible across models.

**Workshop decision**

- `config/vllm-profiles/base.yaml` sets `generation-config: vllm`, `gpu-memory-utilization: 0.80` (the embedding server takes 0.08), `max-model-len: 32768`, `host: 127.0.0.1`, `port: 8000`, `enable-mfu-metrics: true`, tool and reasoning parsers.
- `infra/pod/render-profile.py` allowlists only these `--set` overrides: `max-num-seqs`, `max-num-batched-tokens`, `max-model-len`, `gpu-memory-utilization`, `kv-cache-memory-bytes`, `kv-cache-dtype`, `enable-prefix-caching`, `enable-chunked-prefill`, `long-prefill-token-threshold`, `quantization`, `stream-interval`.

### 3.5 Config-file format

**Source facts**

- `vllm serve --config file.yaml`; the file must be `.yaml` or `.yml`. Keys are long flag names without `--`; docs use kebab-case, and the parser accepts underscores or dashes. ([SRC serve_args.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/serve_args.md), [argparse_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/utils/argparse_utils.py))
- Booleans: `true` emits `--key`; `false` emits `--no-key` only if that negation exists. Lists become space-separated values after one flag. Nested mappings are converted to JSON strings, so use a nested mapping for `speculative-config` and `compilation-config`. `model:` may be a YAML key. ([SRC serve_args.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/serve_args.md))
- Precedence: "command line > config file values > defaults". A model given positionally on the CLI beats `model` in the file. ([SRC serve_args.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/serve_args.md))

**Interpretation** (inference)

- Illustration built from the rules above (not copied from the docs): `tensor-parallel-size: 2`, `enable-prefix-caching: false` and a nested `speculative-config:` mapping with `method: ngram` are all valid.
- Because `false` only maps to `--no-key` when the negation exists, test every boolean you rely on.

**Workshop decision**

- Profiles in `config/vllm-profiles/*.yaml` use this format. `infra/pod/render-profile.py` resolves `extends:` chains, strips its own meta keys (`description`, `extends`, `abstract`, `role`, `experiment`), and refuses `api-key`, `trust-remote-code`, `download-dir`, SSL keys, `allowed-origins`, `uds`, `model-loader-extra-config`, `tool-parser-plugin`, a non-loopback `host`, and ports other than 8000 and 8001.

### 3.6 Offline mode

**Source facts**

- vLLM honours `HF_HUB_OFFLINE=1` through `huggingface_hub.constants`: downloads use `local_files_only=True`, and at engine-arg post-init the model and tokenizer ids are replaced by the local snapshot path. Use a pre-populated `~/.cache/huggingface` or `--download-dir`. The v0.31.0 docs mention it only in the snapshot quickstart. ([SRC arg_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py), [initialized_snapshots.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/initialized_snapshots.md))
- `HF_TOKEN` passes the Hugging Face token; a `--hf-token` model-config field also exists. ([install doc](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md), [model.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py))
- Related 0.31.0 start-up helpers: `vllm preload` keeps post-quantized weights resident in GPU memory across restarts; `vllm snapshot create/restore` (CRIU, TP1) is experimental. ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))

**Interpretation** (inference)

- Offline mode is behaviour, not documentation: it works through the Hub library constant. Pre-download pinned revisions and set the variable, then a network cut-off cannot change what the server loads.

**Workshop decision**

- `infra/pod/wsctl` sets `HF_HUB_OFFLINE=1` and `HF_HOME=/workspace/hf-cache`; `infra/pod/fetch-models.py` and `config/models.yaml` (SHA-pinned revisions) fill the cache.

### 3.7 API-server security facts

**Source facts**

- `--host` defaults to None: the server binds all interfaces, not loopback. `--allowed-origins`, `--allowed-methods`, `--allowed-headers` default to `["*"]`. ([SRC cli_args.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/cli_args.py))
- `--api-key` accepts several keys; `VLLM_API_KEY` is used only if the flag is not given. The middleware guards ONLY paths starting with `/v1`, `/v2`, `/inference`, `/cohere` (Bearer token, sha256 comparison). The flag help warns: "Do not rely on `--api-key` alone to secure vLLM". ([SRC authenticate.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/middleware/authenticate.py), [register.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/middleware/register.py), [security.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/security.md))

| Path | With `--api-key` set |
|---|---|
| `/v1/*` (chat, completions, embeddings, models), `/v2/*`, `/inference/*`, `/cohere/*` | requires `Authorization: Bearer <key>` |
| `/health`, `/metrics`, `/version`, `/load`, `/ping` | open |
| `/tokenize`, `/detokenize` | open |
| `/invocations`, `/classify`, `/score`, `/rerank`, `/pooling` | open |

(source: [authenticate.py and register.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/middleware/authenticate.py))

- Always-registered routers per the source: health, `/version`, `/load`, `/kv_event_sources`, `/metrics`, LoRA load/unload, `/start_profile` and `/stop_profile`, `/tokenize`, `/detokenize`, `/v1/models`. ([SRC routers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/api_server/routers.py))
- Dev routers (`/reset_prefix_cache`, `/reset_mm_cache`, `/reset_encoder_cache`, `/sleep`, `/wake_up`, `/is_sleeping`, `/release_kv_cache_memory`, `/server_info`, `/collective_rpc`, `/pause`, `/resume`, `/update_weights`) exist only when env `VLLM_SERVER_DEV_MODE=1`. Startup then logs "SECURITY WARNING: Development endpoints are enabled! This should NOT be used in production!". ([SRC routers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/api_server/routers.py))
- `GET /health` returns 200 with an empty body, 503 on `EngineDeadError`. `GET /version` returns `{"version": ...}`. `GET /load` returns `{"server_load": N}` (meaningful only with `--enable-server-load-tracking`). `/tokenize` takes either `{"model","prompt","add_special_tokens","return_token_strs"}` or the chat form with `messages`; response `{"count","max_model_len","tokens","token_strs"}`. ([SRC instrumentator/health.py and tokenize/protocol.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/tokenize/protocol.py))
- Security-relevant 0.31.0 changes: per-request `mm_processor_kwargs`/`media_io_kwargs` are rejected unless `--trust-request-mm-kwargs`; prefix-cache extra keys are tagged by source and LoRA path is included in the hash; `cache_salt` isolates prefix-cache entries per tenant. ([release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0), [prefix_caching.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/prefix_caching.md))
- Unverified: whether each always-registered router (LoRA load/unload, profiler) is functional without a further flag or env variable. The notes list them as registered, not as enabled.

**Interpretation** (inference)

- `--api-key` is an application-level token on the OpenAI-compatible routes only. `/metrics`, `/tokenize` and `/pooling` leak operational data or compute to anyone who can reach the port. The network boundary is the security control.
- On the embedding server (`runner: pooling`), `/pooling` is unauthenticated while `/v1/embeddings` is not.

**Workshop decision**

- `config/vllm-profiles/base.yaml` and `infra/pod/render-profile.py` bind to 127.0.0.1 and reject any other host. Participants reach the pods over SSH. `infra/pod/wsctl` reads the key from a state file and passes `VLLM_API_KEY` as an environment variable, so no key is written into a profile. `docs/SECURITY.md` must list the open paths from the table.

### 3.8 Startup log lines and the KV-cache size formula

**Source facts** (exact wording from source, `v0.31.0`)

| Log line | Where | Note |
|---|---|---|
| `Model loading took %s GiB memory and %.6f seconds` | `v1/worker/gpu_model_runner.py` and the MRV2 `v1/worker/gpu/model_runner.py` | weights only |
| `Loading weights took %.2f seconds` | `default_loader.py` | |
| `Available KV cache memory: %s GiB` | `v1/worker/gpu_worker.py` | |
| `%s KV cache size: %s tokens, Maximum concurrency for %s tokens per request: %.2fx` | `v1/core/kv_cache_utils.py` | ONE line in 0.31.0, e.g. `GPU KV cache size: 1,234,560 tokens, Maximum concurrency for 32,768 tokens per request: 37.67x` (example from the format string, not a captured log) |
| `Initial free memory %s GiB, reserved %s GiB memory for KV Cache as specified by kv_cache_memory_bytes config and skipped memory profiling...` | `gpu_worker.py` | only with `--kv-cache-memory-bytes` |
| `CUDA graph memory profiling is enabled (default since v0.21.0). The current --gpu-memory-utilization=%.4f is equivalent to --gpu-memory-utilization=%.4f without CUDA graph memory profiling...` | `gpu_worker.py` | disable with `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` |
| `Graph capturing finished in %.0f secs, took %.2f GiB` | `gpu_worker.py` or `gpu_model_runner.py` (the notes do not pin which) | |
| `init engine (profile, create kv cache, warmup model) took %.2f s` | `v1/engine/core.py` | |
| `Avg prompt throughput: %.1f tokens/s, Avg generation throughput: %.1f tokens/s, Running: %d reqs, Waiting: %d reqs` then optional `Deferred`, `Preemptions: %d` (only if >0), `GPU KV cache usage: %.1f%%`, `Prefix cache hit rate: %.1f%%` | `v1/metrics/loggers.py` | INFO when busy, DEBUG when idle; interval `VLLM_LOG_STATS_INTERVAL` default 10.0 s |

Sources for the table: [gpu_model_runner.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/gpu_model_runner.py), [kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/kv_cache_utils.py), [gpu_worker.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/gpu_worker.py), [loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py), [envs.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/envs.py).

- Older versions emitted two lines (`GPU KV cache size: N tokens` and `Maximum concurrency ...`) and used `# GPU blocks:`. In 0.31.0 the numbers carry thousands separators. ([SRC kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/kv_cache_utils.py))
- Failure messages to recognise: "To serve at least one request with the model's max seq len (N), (X GiB KV cache is needed, which is larger than the available KV cache memory (Y GiB). Based on the available memory, the estimated maximum model length is Z. ..." and "No available memory for the cache blocks. Try increasing gpu_memory_utilization...". ([SRC kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/kv_cache_utils.py))
- Memory accounting: `available_kv_cache_memory_bytes = requested_memory - non_kv_cache_memory - cudagraph_memory_estimate`. `non_kv_cache_memory = total_consumed + transient_peak_headroom`; `total_consumed` is the drop in free memory (via `mem_get_info`) caused by this instance, including weights and non-torch memory such as NCCL/cuBLAS workspaces; `transient_peak_headroom = torch_peak_after_profile - torch_allocated_after_profile`. The profile run is a dummy forward at `max_num_batched_tokens`. ([SRC gpu_worker.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/gpu_worker.py), [mem_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/utils/mem_utils.py))
- Block count for uniform attention: `num_blocks = available_memory // bytes_per_block`; `page_size_bytes = num_kv_heads(per TP rank) * block_size * (head_size + head_size_v) * dtype_size`, summed over layers. For FP8 KV `dtype_size` is 1. `--num-gpu-blocks-override` replaces `num_blocks`. Hybrid, sliding-window and Mamba models use several KV groups over one pool. ([SRC kv_cache_utils.py and kv_cache_interface.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/kv_cache_interface.py))
- The reported token count is NOT `num_blocks * block_size`. `get_kv_cache_capacity` returns `(int(max_concurrency * max_model_len), max_concurrency)` with `max_concurrency = num_blocks / ceil(max_model_len / block_size)` for plain full attention. The two agree only when `max_model_len` is a multiple of the block size. ([SRC kv_cache_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/kv_cache_utils.py))
- Doc tips for conserving memory: lower `--max-model-len`, lower `--max-num-seqs`, quantize, `--kv-cache-dtype fp8`, add TP. ([SRC conserving_memory.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/conserving_memory.md))

**Interpretation** (inference; arithmetic from the formula plus the architecture fields pinned in `config/models.yaml`, not from a log)

- Dense GQA, TP=1, BF16 KV: `bytes_per_token = 2 * layers * kv_heads * head_dim * 2`. Qwen3-8B has 36 layers, 8 KV heads, head_dim 128, so 147,456 B/token (144 KiB) and 2.25 MiB per 16-token block. FP8 KV halves both.
- With `kv-cache-memory-bytes: 4G` (4 GiB): 1,820 blocks, about 29,120 tokens, "Maximum concurrency for 32,768 tokens per request" of 0.89x. With FP8 KV: 3,640 blocks, 58,240 tokens, 1.78x. A 1,048,576-token context would need 144 GiB of KV.
- Compare the hand calculation with the logged line. A mismatch means a different architecture (hybrid or sliding-window layers), a different block size, or a different dtype.

**Workshop decision**

- `config/vllm-profiles/kv-constrained.yaml`, `kv-constrained-fp8kv.yaml` and `oom-demo.yaml` implement these numbers (4 GiB budget with a 16,384-token context limit, because 32,768 tokens do not fit into 4 GiB and the server refuses to start, measured; FP8 KV; the model's full context in 4 GiB, which fails on purpose). `scripts/sizing.py` is the repository's hand-sizing tool; compare its output with the `KV cache size` log line, as in the arithmetic above.

### 3.9 Scheduler, continuous batching, chunked prefill, prefix caching, preemption

**Source facts**

- V1 scheduler: "treats both prompt and output tokens the same way by using a simple dictionary (e.g., `{request_id: num_tokens}`) to dynamically allocate a fixed token budget per request". Policies: FCFS (default) and priority. ([SRC v1_guide.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/v1_guide.md))
- Each step has a token budget `max_num_batched_tokens`. Decodes (1 token per running request) are scheduled first; the remaining budget goes to prefill chunks. A request cannot exceed `max_num_seqs` running sequences. In 0.31.0 requests already holding KV blocks are scheduled first from the waiting queue. ([SRC optimization.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Tuning advice in the docs: smaller `max_num_batched_tokens` (e.g. 2048) gives better ITL; larger gives better TTFT; "For optimal throughput, we recommend setting `max_num_batched_tokens > 8192` especially for smaller models on large GPUs." ([SRC optimization.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md))
- Prefix caching: hash-based, only full blocks are cached; block hash = parent hash + block tokens + extra hashes (LoRA id, multimodal hashes, `cache_salt`); default hash `sha256` since v0.11; block pool with a doubly linked free list (LRU-like eviction). ([SRC prefix_caching.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/prefix_caching.md))
- Doc sentence: "In V1, with prefix caching being better (zero over head) and therefore on by default, the preemption and recompute strategy should work better." ([SRC design/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/metrics.md))
- Caution: `docs/features/automatic_prefix_caching.md` still says "Set `enable_prefix_caching=True` ... to enable APC". The code default is True. ([SRC automatic_prefix_caching.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/automatic_prefix_caching.md))
- Prompt logprobs bypass the prefix cache: the engine "will ignore the prefix cache and recompute the prefill of full prompt". ([SRC v1_guide.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/v1_guide.md))
- Preemption: V1 uses RECOMPUTE only (no swap; `--swap-space` removed). `_preempt_request` frees the KV blocks, sets `num_computed_tokens = 0`, increments `num_preemptions`, and puts the request at the FRONT of the waiting queue. Victim: lowest priority under the priority policy, else the most recently admitted (`self.running[-1]`). ([SRC scheduler.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/sched/scheduler.py), [optimization.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md))
- Legacy warning text still in the docs: "Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size ...". Mitigations: raise `gpu_memory_utilization`, lower `max_num_seqs`/`max_num_batched_tokens`, raise TP/PP. ([SRC optimization.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md))
- `scheduler_reserve_full_isl` (default True): the scheduler checks that the full input length fits in KV before admitting a request, "rather than only checking the first chunk". ([SRC scheduler.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/scheduler.py))
- Observability of these behaviours: `vllm:num_preemptions_total`, `vllm:prefix_cache_hits_total` / `vllm:prefix_cache_queries_total`, the `Preemptions: N` log field (section 9).
- `docs/design/paged_attention.md` describes the V0-era CUDA kernel; treat it as kernel background, not as the V1 scheduler. ([SRC paged_attention.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/paged_attention.md))

**Interpretation** (inference)

- Chunked prefill is why one long prompt does not freeze the running decodes: it competes for the same per-step token budget instead of monopolising a step.
- Preemption is a recompute cost, not an error. A rising `vllm:num_preemptions_total` with a full `vllm:kv_cache_usage_perc` means KV pressure; the fix is more KV, shorter contexts or fewer sequences, not more clients.
- Prefix-cache benefits depend on identical prefixes and full 16-token blocks. A benchmark with unique prompts shows no benefit; that is correct behaviour.

**Workshop decision**

- Profiles `no-prefix-cache`, `max-seqs-8` and `kv-constrained` implement the control experiments for prefix caching, queueing and preemption. The harness option `--reset-prefix-cache` in `benchmark/infbench/cli.py` calls `POST /reset_prefix_cache`, which exists only with `VLLM_SERVER_DEV_MODE=1`; `infra/pod/wsctl` does not set that variable, so the option warns and continues on the workshop servers.

### 3.10 Speculative decoding

**Source facts**

- Methods documented in 0.31.0: EAGLE/EAGLE3, MTP, draft model (`draft_model`), parallel draft model (PARD), MLP speculator, n-gram (`ngram`, `ngram_gpu`), suffix decoding (`suffix`, needs `pip install arctic-inference`), custom proposer (`custom_class`), dynamic speculative decoding. The docs say speculation is to "reduce inter-token latency under medium-to-low QPS, memory-bound workloads". ([SRC speculative_decoding/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md))
- Configuration is one JSON object `--speculative-config` (keys `method`, `model`, `num_speculative_tokens`, `draft_tensor_parallel_size`, `rejection_sample_method`, ...). n-gram: `prompt_lookup_min`/`prompt_lookup_max` (default 5 when both omitted). `tensor_parallel_size` is not a valid key. Old `--speculative-model`/`--num-speculative-tokens` are deprecated. ([SRC README](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md))
- Qualitative gains (docs): at high QPS EAGLE and MTP "Medium to high gain", draft model, n-gram and suffix "Medium gain"; at low QPS EAGLE/MTP/draft "High gain", n-gram/suffix "Low to medium gain". "Real gains depend on your model family, traffic pattern, hardware, and sampling settings." ([SRC README](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md))
- Why high batch hurts: "As BS increases, the effective BS becomes BS*K ... When this BS*K goes beyond a critical BS then SD negatively impacts the decode speed (TPOT)." Mitigation: `num_speculative_tokens_per_batch_size: [[start_bs,end_bs,K],...]`. Example commands set `VLLM_USE_V2_MODEL_RUNNER=0`. ([SRC dynamic_speculative_decoding.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/dynamic_speculative_decoding.md))
- Lossless claim: sampling is "theoretically lossless up to the precision limits of hardware numerics"; "vLLM does not currently guarantee stable token log probabilities (logprobs)". ([SRC README](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md))
- Examples: draft model `{"model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5, "method": "draft_model"}` on `Qwen/Qwen3-8B` (online example uses `--gpu-memory-utilization 0.8`); n-gram `{"method":"ngram","num_speculative_tokens":5,"prompt_lookup_max":4}`; MTP only for models with native MTP. ([SRC speculative_decoding docs](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md))
- `vllm bench serve` prints a "Speculative Decoding" block and writes `spec_decode_*` keys when the server exposes `vllm:spec_decode_*` metrics. ([SRC benchmarks/serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- Unverified: any measured speed-up for Qwen3 dense models on RTX PRO 6000. The docs give only qualitative tables.

**Interpretation** (inference)

- Speculation trades compute for latency. It is a low-concurrency tool and can hurt at high batch size. Teach it with a concurrency sweep, not a single number.
- n-gram drafts work when the output copies the prompt (RAG answers, code edits) and do little for free-form generation.

**Workshop decision**

- `config/vllm-profiles/spec-ngram.yaml` (`method: ngram`, `num_speculative_tokens: 4`, `prompt_lookup_min: 2`, `prompt_lookup_max: 5`) is a trainer demo. `Qwen/Qwen3-1.7B` is marked in `config/models.yaml` as a draft-model candidate; no profile uses a draft model.

### 3.11 Structured outputs, tool calling, reasoning parsers

**Source facts**

- Structured outputs: `guided_json`, `guided_regex`, `guided_choice`, `guided_grammar`, `guided_whitespace_pattern`, top-level `structural_tag` and `guided_decoding_backend` were REMOVED in v0.12.0. Use the nested `structured_outputs` extra-body object with keys `choice`, `regex`, `json`, `grammar`, `structural_tag`. JSON schema also works via `response_format={"type":"json_schema",...}`. Offline: `SamplingParams(structured_outputs=StructuredOutputsParams(...))`. ([SRC structured_outputs.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/structured_outputs.md))
- Backend: `--structured-outputs-config.backend` (default `auto`; `xgrammar`, `guidance`, `outlines`, `lm-format-enforcer`); `enable_in_reasoning` default False. 0.31.0: native Lark grammars in xgrammar, XGrammar 0.2.7, `json_object` rejected with the outlines backend. ([SRC structured_outputs.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/structured_outputs.py), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- First use of a schema pays grammar-compile latency: "several seconds of latency (or more) as the FSM is compiled for the first time before it is cached". ([SRC tool_calling.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/tool_calling.md))
- Tool calling: `tool_choice` supports named function, `auto`, `required`, `none`. The server needs BOTH `--enable-auto-tool-choice` and `--tool-call-parser <name>`. `tool_choice="auto"` is unconstrained unless a tool sets `strict: true` or the server uses `--tool-strict-level function|parameter` (new in 0.31.0; env `VLLM_ENFORCE_STRICT_TOOL_CALLING` default true). `response_format` with `tool_choice=auto` is supported in 0.31.0. ([SRC tool_calling.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/tool_calling.md), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Qwen: docs say the Qwen2.5 chat template "has already included support for the Hermes-style tool use. Therefore, you can use the `hermes` parser" (listed: `Qwen/Qwen2.5-*`, `Qwen/QwQ-32B`). The reasoning table lists "Qwen3 series" with reasoning parser `qwen3` and tool calling supported. Qwen3-Coder uses `--tool-call-parser qwen3_xml`. ([SRC tool_calling.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/tool_calling.md), [reasoning_outputs.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/reasoning_outputs.md))
- Registered tool-parser names in 0.31.0 include `hermes`, `qwen3_coder`, `qwen3_xml`, `llama3_json`, `mistral`, `pythonic`, `granite`, `glm45`, `kimi_k2`, `deepseek_v3`, `minimax_m2`, `openai`, `gemma4` and more (full list in [vllm/tool_parsers/**init**.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/tool_parsers/__init__.py)).
- Unverified: that plain `Qwen/Qwen3-<size>` (non-Coder, non-2507) chat templates work with vLLM's `hermes` parser in 0.31.0. The vLLM docs name only Qwen2.5/QwQ for `hermes`; Qwen's own docs recommend it for Qwen3. Smoke-test a tool call before the workshop.
- Reasoning: `--reasoning-parser qwen3`. The response field is `reasoning` (streaming `delta.reasoning`). It used to be `reasoning_content`; the docs warn "your client code could silently read an empty `reasoning_content`, even when `reasoning` is populated". Tool calling parses only the `content` field, not `reasoning`. ([SRC reasoning_outputs.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/reasoning_outputs.md))
- Qwen3 thinking is ON by default; disable per request with `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` or server-wide with `--default-chat-template-kwargs '{"enable_thinking": false}'`. Request kwargs override server defaults. Thinking budget: `--reasoning-config` plus per-request `thinking_token_budget`. ([SRC reasoning_outputs.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/reasoning_outputs.md))

**Interpretation** (inference)

- The rename `reasoning_content` to `reasoning` is a silent-failure trap for every client written against older docs, including benchmark clients that look for the first text chunk.
- Thinking mode changes output length and latency. A benchmark that leaves it on measures a different workload than one that switches it off.

**Workshop decision**

- `config/vllm-profiles/base.yaml` enables `enable-auto-tool-choice`, `tool-call-parser: hermes` and `reasoning-parser: qwen3`. `benchmark/infbench/client.py` sends `chat_template_kwargs: {"enable_thinking": false}` on chat requests and reads both `reasoning_content` and `reasoning` from stream deltas. `apps/tool-calling-demo` depends on the unverified hermes/Qwen3 pairing: smoke-test it per delivery.

### 3.12 Embedding serving

**Source facts**

- `--task` is gone in 0.31.0. Use `--runner pooling` (values `auto` default, `generate`, `pooling`, `draft`) and optionally `--convert {auto,embed,classify,...}`. "There is no need to set this option in the vast majority of cases as vLLM can automatically detect the appropriate model runner via `--runner auto`." ([SRC pooling_models/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/models/pooling_models/README.md))
- Endpoint `POST /v1/embeddings` (also `POST /v2/embed`, `POST /pooling`). Extras: `encoding_format` (`float` default, `base64`), `dimensions`, `truncate_prompt_tokens`, `use_activation` (the old `normalize` was removed). Example: `vllm serve Qwen/Qwen3-Embedding-0.6B --runner pooling`. Listed supported: `Qwen/Qwen3-Embedding-0.6B`, `BAAI/bge-m3`, `intfloat/e5-mistral-7b-instruct`, `Alibaba-NLP/gte-Qwen2-7B-instruct`. ([SRC embed.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/models/pooling_models/embed.md))
- Pooling models with bidirectional (encoder-only) attention default to prefix caching OFF and chunked prefill OFF. ([SRC model.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py))

**Interpretation** (inference)

- A second engine process on the same GPU needs its own `--gpu-memory-utilization`; the fraction is per instance, so the sum must stay below 1.0 minus other consumers.

**Workshop decision**

- `config/vllm-profiles/embedding.yaml`: `runner: pooling`, port 8001, `gpu-memory-utilization: 0.08`, `max-model-len: 8192`; the main profile leaves 0.80. `apps/rag-demo` is the consumer. `infra/pod/wsctl embed start` starts it.

### 3.13 Other engines: positioning and licences

**Source facts** (versions checked 2026-10-14)

| Engine | Version checked | Licence | Positioning (primary source wording) | Source |
|---|---|---|---|---|
| vLLM | v0.31.0 | Apache-2.0 | OpenAI-compatible server and engine; this workshop | [GitHub API](https://api.github.com/repos/vllm-project/vllm) |
| SGLang | v0.5.21 (2026-10-02) | Apache-2.0 | "an open-source inference framework for large language, vision-language, and diffusion models, optimized for agentic workloads, large-scale serving, and RL rollouts"; hosted by LMSYS; README names "RTX 6000 Ada / PRO 6000" | [README](https://raw.githubusercontent.com/sgl-project/sglang/main/README.md), [releases](https://api.github.com/repos/sgl-project/sglang/releases) |
| TensorRT-LLM | v1.2.1 latest non-pre-release (2026-04-20); active line `v1.3.0rc29` (2026-09-29) | Apache 2.0 (GitHub licence API shows NOASSERTION because of third-party portions) | "an open-sourced library for optimizing LLM and Visual Gen inference"; NVIDIA-only; `trtllm-serve`, `trtllm-bench` | [repo](https://github.com/NVIDIA/TensorRT-LLM), [LICENSE](https://raw.githubusercontent.com/NVIDIA/TensorRT-LLM/main/LICENSE), [PyPI](https://pypi.org/pypi/tensorrt-llm/json) |
| llama.cpp | tags `b11612` (2026-10-14, pre-release flag); semver release v0.6.0 (2026-10-05) | MIT | "LLM inference in C/C++"; `llama-server` with OpenAI-compatible routes, `-np/--parallel` slots (default -1 = auto), continuous batching on by default, GGUF; metrics prefixed `llamacpp:` | [repo](https://github.com/ggml-org/llama.cpp), [server README](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md) |
| Ollama | v0.40.4 (2026-10-12) | MIT | local runner derived from llama.cpp; port 11434, binds 127.0.0.1; `OLLAMA_NUM_PARALLEL` default 1; `OLLAMA_MAX_QUEUE` default 512 (503 beyond); `OLLAMA_KV_CACHE_TYPE` default `f16` | [repo](https://github.com/ollama/ollama), [FAQ](https://raw.githubusercontent.com/ollama/ollama/main/docs/faq.mdx) |
| LM Studio | app 0.4.26 | GUI app not open source; `lms` CLI MIT; free for home and work since 2025-07-08 | Desktop app plus headless `llmster` daemon; OpenAI-compatible server on `localhost:1234/v1`; llama.cpp and MLX engines; "Max Concurrent Predictions" default 4 (llama.cpp engine only) | [headless docs](https://lmstudio.ai/docs/developer/core/headless_llmster), [parallel requests](https://lmstudio.ai/docs/app/advanced/parallel-requests), [blog](https://lmstudio.ai/blog/free-for-work), [lms repo](https://github.com/lmstudio-ai/lms) |
| NVIDIA Dynamo | v1.5.1 (2026-10-07) | Apache-2.0 (MIT-licensed test data noted) | "A Datacenter Scale Distributed Inference Serving Framework"; an orchestration layer above vLLM, SGLang and TensorRT-LLM backends, not an engine | [repo](https://github.com/ai-dynamo/dynamo), [vLLM docs](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/dynamo.md), [PyPI](https://pypi.org/pypi/ai-dynamo/json) |
| vLLM production-stack | Helm chart `vllm-stack-0.1.13` (2026-09-29) | Apache-2.0 | "vLLM's reference system for K8S-native cluster-wide deployment"; wraps upstream vLLM; Helm charts, Grafana dashboards, model-aware and prefix-aware routing, LMCache offloading; chart versions still 0.x | [repo API](https://api.github.com/repos/vllm-project/production-stack), [vLLM docs](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/production-stack.md) |

- Unverified: the MIT split for LM Studio components beyond the `lms` repo (the vendor blog fetched did not state it). The `lmstudio.ai/changelog` URL returned an unrelated "Bionic" product changelog; do not cite it.
- Other Kubernetes integrations named in vLLM docs: llm-d (CNCF Sandbox; v0.10.0, 2026-09-29), AIBrix (v0.8.0, 2026-10-13), KServe, KubeAI, KubeRay, Kthena, LlamaStack, KAITO, llmaz, Helm, LWS, Nginx. ([SRC docs/deployment](https://github.com/vllm-project/vllm/tree/v0.31.0/docs/deployment), [llm-d.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/llm-d.md))

**Scale-out features, conceptual only** (single GPU per pod in this workshop)

- Data parallel: `--data-parallel-size N` replicates weights behind one endpoint; `--max-num-seqs` applies per DP rank; each DP engine has its own KV cache, so prefix-cache benefit depends on routing. ([SRC data_parallel_deployment.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/data_parallel_deployment.md))
- Expert parallel `--enable-expert-parallel` (EP size = TP x DP) is MoE-only. ([SRC expert_parallel_deployment.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/expert_parallel_deployment.md))
- Disaggregated prefill/decode is "experimental"; "Disaggregated prefill DOES NOT improve throughput", it tunes TTFT and tail ITL independently. ([SRC disagg_prefill.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/disagg_prefill.md))
- KV offloading: `--kv-offloading-size <GiB>`, `--kv-offloading-backend {native,lmcache}` (default `native`). ([SRC kv_offloading_usage.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/kv_offloading_usage.md))

**Interpretation** (inference)

- Positioning in one line each: vLLM, SGLang and TensorRT-LLM are GPU serving engines; llama.cpp, Ollama and LM Studio are local runners built on llama.cpp (LM Studio also MLX); Dynamo and production-stack orchestrate engines.
- Default concurrency tells the story: Ollama defaults to 1 parallel request per model, LM Studio to 4, llama.cpp to auto slots, vLLM to a continuous-batching engine whose derived default is up to 1024 sequences on a >=70 GiB GPU (see the Unverified note in 3.4).

**Workshop decision**

- vLLM is the only engine run by the labs. `benchmark/infbench` accepts `--engine` and `--no-engine-extensions` so the same workload can be pointed at Ollama or llama.cpp for the comparison demo; `config/models.yaml` holds `Qwen/Qwen3-8B-GGUF` for that purpose.

---

## 4. Hugging Face ecosystem

Verified 2026-10-14. Package versions on PyPI that day: `huggingface_hub` 2.2.0, `hf-xet` 1.7.0, `transformers` 5.19.0, `safetensors` 0.8.0 ([PyPI huggingface_hub](https://pypi.org/pypi/huggingface_hub/json), [hf-xet](https://pypi.org/pypi/hf-xet/json), [transformers](https://pypi.org/pypi/transformers/json), [safetensors](https://pypi.org/pypi/safetensors/json)). Latest vLLM on PyPI is 0.31.0, uploaded 2026-10-05 ([PyPI vllm](https://pypi.org/pypi/vllm/json)).

### 4.1 Commit-SHA pinning

**Source facts**

- `hf_hub_download` / `snapshot_download` accept `revision` as branch, tag, PR ref (`refs/pr/3`) or commit hash. "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash" ([HF download guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/download.md)).
- `GET https://huggingface.co/api/models/<repo>` returns the current `sha` (40 hex); `/commits/main` lists history; `/tree/main?recursive=true` lists files with `lfs.size` ([HF API, Qwen3-8B example](https://huggingface.co/api/models/Qwen/Qwen3-8B)).
- vLLM has three separate settings: `--revision` (weights), `--tokenizer-revision`, `--code-revision` ([vLLM config/model.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/config/model.py)).
- Cache layout is `<HF_HUB_CACHE>/models--org--name/{blobs,refs,snapshots}`. `refs/main` stores the latest commit for a ref, `snapshots/<commit>/` holds symlinks to blobs. `huggingface_hub` can resolve a revision once so all files come from one commit and later loads need no HTTP call ([HF cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md)).
- Without pinning, two calls seconds apart "can land on two different commits if the repo is updated in between" ([HF cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md)).
- A README-only commit changes the `main` SHA. `Qwen/Qwen3-Embedding-0.6B` is at `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3` ("Update README.md (#55)", 2026-04-20). The previous commit `c54f2e6e80b2d7b7de06f51cec4959f6b3e03418` dates from 2025-06-20, and the weights have not changed since 2025-06 ([HF commits API](https://huggingface.co/api/models/Qwen/Qwen3-Embedding-0.6B/commits/main)).
- `zai-org/GLM-5.3` was still being committed to during the research session (`c5087a76...` on 2026-10-12, `ba32f8c1...` on 2026-10-14, chat-template changes). Every other SHA in section 5 matched `main` when re-checked at the end of the session ([HF API, GLM-5.3](https://huggingface.co/api/models/zai-org/GLM-5.3)).
- HF recommends signed commits (GPG): this "does not guarantee that your file is safe, but it does guarantee the origin" ([HF pickle security docs](https://huggingface.co/docs/hub/security-pickle)).

**Interpretation** (my inference). A SHA is a content address for the repo state, not a promise that the weights changed. A new `main` SHA for an unchanged model is normal. Pin the full 40-hex string, never a branch or a 7-character prefix, and re-resolve any repo that is still being edited before pinning it.

**Workshop decision.** `config/models.yaml` is the single place for the pins and holds the full 40-hex SHAs listed in section 5.1. Labs download with `hf download <repo> --revision <sha>` and serve with `vllm serve ... --revision <sha>` so every pod runs identical bytes.

### 4.2 safetensors vs pickle

**Source facts**

- Safetensors is "a new simple format for storing tensors safely (as opposed to pickle) and that is still fast (zero-copy)" ([safetensors docs](https://huggingface.co/docs/safetensors/index)).
- README comparison: pickle (PyTorch) is "Safe: no" and "Zero-copy: no"; safetensors is safe, zero-copy, lazy-loading, no file-size limit, and supports bf16/fp8. Pickle "runs arbitrary code" ([safetensors README](https://raw.githubusercontent.com/huggingface/safetensors/main/README.md)).
- Format: 8-byte little-endian u64 header size N, then N bytes of UTF-8 JSON header (tensor name -> dtype, shape, `data_offsets`; optional `__metadata__` of string-to-string only), then the raw buffer. The buffer "cannot contain holes", which prevents polyglot files. Header size limit is 100 MB against JSON DoS ([safetensors README](https://raw.githubusercontent.com/huggingface/safetensors/main/README.md)).
- Dangerous pickle opcodes are `STACK_GLOBAL`, `GLOBAL`, `REDUCE`. PyTorch `pytorch_model.bin` is pickle ([HF pickle security docs](https://huggingface.co/docs/hub/security-pickle)).
- The Hub scans every pushed file with ClamAV and a Pickle Import scan (imports shown, suspicious ones highlighted). The docs say it "is not 100% foolproof" and that checking is the user's responsibility ([HF pickle security docs](https://huggingface.co/docs/hub/security-pickle)).
- Malware scanning covers repository files smaller than 2 GB, triggered at each commit; files without a badge may be queued or errored ([HF malware docs](https://huggingface.co/docs/hub/security-malware)).
- vLLM `--load-format auto`: if the repo has `consolidated*.safetensors`, it uses the Mistral format. Otherwise it tries patterns `["*.safetensors", "*.bin"]` plus a `*.pt` fallback and takes the first pattern that exists, so safetensors wins and `.bin` (pickle) or `.pt` load only when no safetensors exist. `--load-format safetensors` restricts to `*.safetensors`. Default `ignore_patterns` is `["original/**/*"]` ([vLLM default_loader.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/model_loader/default_loader.py), [vLLM config/load.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/config/load.py)).
- All pinned workshop repos in section 5.1 ship safetensors. The GGUF repo is the exception; GGUF is not pickle ([HF API, Qwen3-8B-GGUF](https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF)).

**Interpretation** (my inference). Safetensors removes code execution on load only. It does not protect against poisoned weights or against a malicious tokenizer or chat template. Unverified: how strong the Jinja sandbox for chat templates is; it was not checked.

**Workshop decision.** Serve pinned repos with `--load-format safetensors` so a pickle fallback can never run. This belongs in the profiles under `config/vllm-profiles/*.yaml` (rendered by `infra/pod/render-profile.py`). The GGUF demo (`Qwen/Qwen3-8B-GGUF`) needs different handling. Unverified: how vLLM 0.31.0 loads that GGUF repo; the notes only give llama.cpp and Ollama commands for it.

### 4.3 `trust_remote_code`

**Source facts**

- Transformers custom models use modeling code that is "*not* from Transformers". The docs warn to "take extra precaution" and say Hub malware scanning does not remove the need for care ([Transformers models.md](https://raw.githubusercontent.com/huggingface/transformers/main/docs/source/en/models.md)).
- Extra layer: load custom models from a specific revision (`from_pretrained(..., trust_remote_code=True, revision=commit_hash)`) so changed code is not loaded ([Transformers models.md](https://raw.githubusercontent.com/huggingface/transformers/main/docs/source/en/models.md)).
- vLLM: `trust_remote_code: bool = False`, CLI `--trust-remote-code`; `revision`, `code_revision` ("branch name, a tag name, or a commit id") and `tokenizer_revision` are separate ([vLLM config/model.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/config/model.py), [vLLM supported models](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/models/supported_models.md)).
- Among all repos checked (every pinned model, Qwen3.5/3.8, Gemma 4, Mistral, DeepSeek V4, gpt-oss, Muse Glimmer, GLM-5.3-Flash, Granite 4.2, Nemotron 3.5, EuroLLM, Qwen3-Coder-Next), only `moonshotai/Kimi-K3` and `moonshotai/Kimi-K2.6` have an `auto_map` in `config.json`, meaning they ship custom `configuration_*.py` / `modeling_*.py` ([Kimi-K3 config](https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json), [Kimi-K2.6 config](https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/config.json)).
- Unverified: whether vLLM 0.31 still imports Kimi custom code when `trust_remote_code=False` (it may use a built-in implementation).

**Interpretation** (my inference). `--revision` alone does not pin the code. If `--code-revision` is left unset, remote code can come from `main` while the weights come from the pinned SHA.

**Workshop decision.** No pinned workshop model needs `trust_remote_code`; profiles in `config/vllm-profiles/*.yaml` must not set it. If a lab adds a repo with `auto_map`, the model-selection lab (`docs/MODEL-SELECTION.md`) requires `--trust-remote-code` together with `--revision <sha>` and `--code-revision <sha>`.

### 4.4 Gated models

**Source facts**

- Gating: authors enable access requests; users "must agree to share their contact information (username and email address)". Access is granted per user, not per organisation. Approval is automatic or manual; manual rejections cannot re-request. Authors can add `extra_gated_fields` / `extra_gated_prompt` (for example a licence checkbox) ([HF gated models docs](https://huggingface.co/docs/hub/models-gated)).
- The model JSON has `gated` = `False`, `"auto"` or `"manual"`. `meta-llama/*` is `manual`. `swiss-ai/Apertus-v1.5-8B` is `auto` yet Apache-2.0. The Qwen, Gemma 4, Mistral, DeepSeek and gpt-oss repos checked are `False` ([HF API, Llama-3.1-8B-Instruct](https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct), [HF API, Apertus-v1.5-8B](https://huggingface.co/api/models/swiss-ai/Apertus-v1.5-8B)).
- Raw files of gated repos return HTTP 401 without an authorised token (observed for `config.json` and `README.md` of Llama 3.1 8B, Llama 4 and Apertus). Download needs a user access token (`HF_TOKEN` or `hf auth login`, stored at `$HF_HOME/token`) from an account that was granted access ([HF raw config, Llama-3.1-8B](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/raw/main/config.json), [HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- `HF_TOKEN` overwrites the stored token. A logged-in client sends the token on every request by default (implicit token); `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` limits it to write calls. vLLM has an `hf_token` option ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md), [vLLM config/model.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/config/model.py)).

**Interpretation** (my inference). Gating is access control, not a licence. A gated Apache-2.0 repo exists. Manual approval adds lead time that a fixed three-day schedule cannot absorb. Accepting a licence on the Hub does not by itself settle redistribution duties (see 11.3 for Llama). Not legal advice.

**Workshop decision.** All pinned models are ungated, so participants need no HF account. Gated models (Llama class) are demo-only: the instructor downloads once with a token to a shared volume and distributes the local path.

### 4.5 Xet storage, `HF_XET_HIGH_PERFORMANCE` and first-download time

**Source facts**

- The Hub is "fully powered by the Xet storage backend" with chunk-level deduplication. `huggingface_hub >= 0.32.0` installs `hf_xet` automatically; it is used automatically when present and disabled with `HF_HUB_DISABLE_XET=1` ([HF Xet index](https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/xet/index.md), [using Xet storage](https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/xet/using-xet-storage.md)).
- `HF_HUB_ENABLE_HF_TRANSFER` is deprecated: all transfers go through `hf-xet` and "`hf_transfer` can't be used anymore". The replacement is `HF_XET_HIGH_PERFORMANCE=1`, which "will try to saturate the network bandwidth of this machine and utilize all CPU cores"; it is "analogous to the legacy `HF_HUB_ENABLE_HF_TRANSFER=1`" ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- Since `hf_xet` 1.3.0 download concurrency is adaptive. `HF_XET_NUM_CONCURRENT_RANGE_GETS` is no longer used, `HF_XET_CHUNK_CACHE_SIZE_BYTES` has no effect, and files are always written sequentially ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- Shared blob store: downloaded Xet files are stored once at `<CACHE_DIR>/blobs/<prefix>/<xet_hash>` and symlinked into repo caches, so identical files across repos are not downloaded twice. Disabled by `HF_HUB_DISABLE_XET=1`, `HF_HUB_DISABLE_SHARED_BLOBS=1`, or filesystems without symlinks (some NAS) ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md), [HF cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md)).
- Telemetry since `hf_xet` 1.7.0: a report of about 1 KB after each upload or download. It carries type, result, timing, file count, total size, bytes over network, throughput, `hf_xet` version, OS, CPU architecture, CPU count, user agent, random IDs and storage host. The server adds IP address, Hub account (or "anonymous"), repo and token access level. Opt out with `HF_HUB_DISABLE_TELEMETRY=1` (or `DO_NOT_TRACK`) ([HF Xet telemetry](https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/xet/telemetry.md), [HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- Defaults: `HF_HOME=~/.cache/huggingface`, `HF_HUB_CACHE=$HF_HOME/hub`, `HF_XET_CACHE=$HF_HOME/xet`, token at `$HF_HOME/token`. `HUGGINGFACE_HUB_CACHE` and `HUGGING_FACE_HUB_TOKEN` are deprecated aliases of `HF_HUB_CACHE` / `HF_TOKEN` ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- CLI is `hf`: `hf download <repo> [files] --revision ...`, `hf download ... --dry-run` (lists files and bytes), `hf auth login`, `hf cache rm/prune` ([HF download guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/download.md)).

| Variable | Status (2026-10-14) | Effect |
|---|---|---|
| `HF_XET_HIGH_PERFORMANCE=1` | current | max network and CPU use for transfers |
| `HF_HUB_ENABLE_HF_TRANSFER` | deprecated | `hf_transfer` "can't be used anymore" |
| `HF_HUB_DISABLE_XET=1` | current | turn off Xet; also disables the shared blob store |
| `HF_HUB_DISABLE_SHARED_BLOBS=1` | current | no cross-repo blob sharing |
| `HF_HUB_DISABLE_TELEMETRY=1` | current (hf-xet >= 1.7.0) | stops the transfer report |
| `HF_XET_NUM_CONCURRENT_RANGE_GETS`, `HF_XET_CHUNK_CACHE_SIZE_BYTES`, `HF_XET_RECONSTRUCT_WRITE_SEQUENTIALLY` | no longer used / no effect | adaptive since hf_xet 1.3.0 |

**Interpretation** (my inference). Caution: older guides still say `pip install hf_transfer` and `HF_HUB_ENABLE_HF_TRANSFER=1`; on current `huggingface_hub` that no longer works. DERIVED download time is bytes divided by the slower of network and disk write. At about 110 MB/s (a realistic 1 Gbit/s link), Qwen3-8B BF16 (16.38 GB) takes about 2.5 minutes and Qwen3-30B-A3B-FP8 (32.45 GB) about 5 minutes. At 10 Gbit/s it is 15 to 30 seconds if the disk keeps up. The telemetry means a "self-hosted" pod still tells Hugging Face, at download time, its IP and which repo it fetched. That is a sovereignty-relevant detail, because it is metadata, not content.

**Workshop decision.** In `docs/SETUP.md`, use `HF_XET_HIGH_PERFORMANCE=1` on fat links and never `hf_transfer`. Pre-stage weights once per pod or on a shared volume rather than per participant. List `HF_HUB_DISABLE_TELEMETRY=1` as an opt-out in `docs/SECURITY.md` and `docs/DIGITAL-SOVEREIGNTY.md`. If the cache sits on a NAS without symlinks, `HF_HUB_DISABLE_SYMLINKS=1` makes real copies (named in the notes' derived advice; not independently confirmed in the docs read).

### 4.6 `HF_HUB_OFFLINE` and `snapshot_download` semantics

**Source facts**

- `HF_HUB_OFFLINE`: "If set, no HTTP calls will be made to the Hugging Face Hub." Only cached files are read, and an error is raised if none exist. `HfApi` methods raise `OfflineModeIsEnabled`. Even with a cached file, `hf_hub_download` normally makes an HTTP call to check for newer versions; offline mode skips it ([HF env var docs](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/package_reference/environment_variables.md)).
- vLLM honours `huggingface_hub.constants.HF_HUB_OFFLINE` (`local_files_only`) in weight lookup and download and skips the remote file-list and index logic ([vLLM weight_utils.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/model_loader/weight_utils.py)).
- `snapshot_download` fetches a repo at `revision` (default `main`) concurrently via `hf_hub_download` into the cache and returns the `snapshots/<commit>` path, or into `local_dir` (original layout, `.cache/huggingface/` metadata so unchanged files are not re-downloaded). `allow_patterns` / `ignore_patterns` use fnmatch; `cache_dir` or `HF_HOME` relocates the cache ([HF download guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/download.md)).
- If the Hub is unreachable (offline, connection failure, `local_files_only=True`) and expected files are missing from the cached snapshot, `snapshot_download` raises `IncompleteSnapshotError` (exposes `snapshot_path`) instead of silently returning a partial folder. Files excluded by patterns are not counted missing ([HF cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md)).
- Offline, `HfApi.resolve_revision` falls back to the cached `refs/` mapping; if nothing is cached it raises `RevisionResolutionError` ([HF cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md)).
- Unverified: whether `TRANSFORMERS_OFFLINE` is still honoured in transformers 5.x.

**Interpretation** (my inference). The offline recipe has two phases. Online, once: `hf download <repo> --revision <sha>` into `HF_HOME` or `--local-dir`. Air-gapped runtime: `HF_HUB_OFFLINE=1 vllm serve <repo-or-local-path> --revision <sha>`; a local directory path bypasses the Hub entirely. A pinned revision resolves from `refs/` offline, which is another reason to pin.

**Workshop decision.** Run pods with `HF_HUB_OFFLINE=1` after staging so a lab cannot silently re-download or drift. Document the stage-then-offline sequence in `docs/SETUP.md` and record it as a supply-chain control in `docs/SECURITY.md`.

### 4.7 Duplicate-weights pitfall (repos with several formats)

**Source facts**

- Repo size is not download size. Some repos hold several copies of the weights, and `snapshot_download` without patterns fetches all of them:

| Repo | Full repo | Contents | What vLLM downloads |
|---|---|---|---|
| `openai/gpt-oss-20b` | 41.3 GB | root safetensors 13.76 GB + `original/` 13.76 GB + `metal/model.bin` 13.75 GB | one set (13.76 GB) |
| `openai/gpt-oss-120b` | 195.8 GB | 65.25 + 65.25 + 65.24 GB | one set (65.25 GB) |
| `mistralai/Ministral-3-8B-Instruct-2512` | about 21 GB | `consolidated.safetensors` 10,420,633,176 B + 3 sharded HF files 10,420,654,824 B | 10.4 GB (Mistral format) |
| `mistralai/Mistral-Small-4-119B-2603` | 241.85 GB | 7 `consolidated-*` shards (~121 GB) + 3 HF `model-*` shards (~121 GB) | one set (my inference from the loader logic) |
| `mistralai/Mistral-Medium-3.5-128B` | 267.2 GB | 3 `consolidated-*` (~133.6 GB) + 3 HF `model-*` (~133.6 GB) | one set (my inference from the loader logic) |
| `mistralai/Mistral-Small-3.2-24B-Instruct-2506` | 96.0 GB | consolidated + HF sets of 24.0B BF16 | one set (my inference from the loader logic) |
| `Qwen/Qwen3-8B-GGUF` | 32.04 GB | all quants together; one file is 5.03 to 8.71 GB | not stated in notes |
| `Qwen/Qwen3-8B` | 16.40 GB | safetensors 16.38 GB, no duplicate | whole repo |

  Sources: [gpt-oss-20b tree](https://huggingface.co/api/models/openai/gpt-oss-20b/tree/main?recursive=true), [gpt-oss-120b tree](https://huggingface.co/api/models/openai/gpt-oss-120b/tree/main?recursive=true), [Ministral-3-8B tree](https://huggingface.co/api/models/mistralai/Ministral-3-8B-Instruct-2512/tree/main), [Mistral-Small-4 card](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603), [Mistral-Medium-3.5 card](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B), [Mistral-Small-3.2 API](https://huggingface.co/api/models/mistralai/Mistral-Small-3.2-24B-Instruct-2506), [Qwen3-8B-GGUF API](https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF), [Qwen3-8B tree](https://huggingface.co/api/models/Qwen/Qwen3-8B/tree/main?recursive=true).

- With an index file, vLLM downloads exactly the files in `model.safetensors.index.json` `weight_map`, which avoids `original/` duplicates, and takes a file lock per model to prevent concurrent downloads ([vLLM weight_utils.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/model_loader/weight_utils.py)).
- With `--load-format auto`, vLLM picks the Mistral format whenever the repo contains `consolidated*.safetensors` and then downloads only those files ([vLLM default_loader.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/model_loader/default_loader.py)).

**Interpretation** (my inference). The trap is `hf download <repo>` or `snapshot_download(repo)` during pre-staging: it fetches two or three copies and can fill a pod volume. Per-set size for Mistral-Small-3.2 is DERIVED: 24.0B x 2 bytes = 48 GB, half of the 96.0 GB repo. Use `allow_patterns=["*.safetensors","*.json","*.txt","tokenizer*","*.jinja"]` and `ignore_patterns=["original/*","metal/*"]`, or run `hf download --dry-run` first.

**Workshop decision.** Pre-staging steps in `docs/SETUP.md` always pass patterns or run `--dry-run` first. Feed `scripts/sizing.py` the single-copy weights size, not the repo size.

---

## 5. Suitable open models

Verified 2026-10-14. Nothing in this section was measured on the workshop GPU. Sizes, SHAs and architecture fields are read from the HF API and `config.json`; "DERIVED" marks my arithmetic. "GB" = 10^9 bytes, "GiB" = 2^30 bytes. vLLM source and docs cited are `main`, read after the `v0.31.0` tag, so `main` may be ahead of 0.31.0 (noted where a fact was checked against the tag).

### 5.1 Pinned workshop models

**Source facts**

Identity, licence, size (all repos Apache-2.0 and not gated; SHA is `main` on 2026-10-14):

| Role | Repo | SHA (full) | Params (HF metadata) | dtype | safetensors |
|---|---|---|---|---|---|
| primary | [Qwen/Qwen3-8B](https://huggingface.co/api/models/Qwen/Qwen3-8B) | `b968826d9c46dd6066d109eabc6255188de91218` | 8,190,735,360 | BF16 | 16,381,516,776 B (16.38 GB / 15.26 GiB) |
| quantized | [Qwen/Qwen3-8B-FP8](https://huggingface.co/api/models/Qwen/Qwen3-8B-FP8) | `220b46e3b2180893580a4454f21f22d3ebb187d3` | 8,191,159,296 (F8_E4M3 6,945,767,424 + BF16 1,245,391,872) | FP8 E4M3 + BF16 | 9,436,628,784 B (9.44 GB / 8.79 GiB) |
| small | [Qwen/Qwen3-1.7B](https://huggingface.co/api/models/Qwen/Qwen3-1.7B) | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | 2,031,739,904 | BF16 | 4,063,515,592 B (4.06 GB / 3.78 GiB) |
| embedding | [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/api/models/Qwen/Qwen3-Embedding-0.6B) | `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3` | 595,776,512 | BF16 | 1,191,586,416 B (1.19 GB / 1.11 GiB) |
| demo MoE | [Qwen/Qwen3-30B-A3B-FP8](https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B-FP8) | `d206ba732169f29bb77fbf80fc2c4b81d4d30782` | 30,533,947,392 (F8_E4M3 29,896,998,912 + F32 636,948,480) | FP8 E4M3 + F32 | 32,449,487,768 B (32.45 GB / 30.22 GiB) |
| demo GGUF | [Qwen/Qwen3-8B-GGUF](https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF) | `7c41481f57cb95916b40956ab2f0b139b296d974` | n/a | Q4_K_M, Q5_0, Q5_K_M, Q6_K, Q8_0 | Q4_K_M 5,027,783,488 B; Q8_0 8,709,518,112 B; repo 32,035,095,205 B |
| sibling (not pinned) | [Qwen/Qwen3-30B-A3B-Instruct-2507-FP8](https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8) | `5a5a776300a41aaa681dd7ff0106608ef2bc90db` | 30,533,947,392 | FP8 E4M3 + BF16 | 31,175,618,584 B (31.18 GB / 29.04 GiB) |

Architecture fields used for KV sizing and context (from each repo's `config.json`; card values in the last column):

| Repo | Class | Layers | Hidden | Q heads | KV heads | head_dim | Experts | `max_position_embeddings` | Card context |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B (and -FP8) | `Qwen3ForCausalLM` | 36 | 4096 | 32 | 8 | 128 | dense | 40,960 | 32,768 native, 131,072 with YaRN |
| Qwen3-1.7B | `Qwen3ForCausalLM` | 28 | 2048 | 16 | 8 | 128 | dense, tied embeddings | 40,960 | 32,768 |
| Qwen3-Embedding-0.6B | `Qwen3ForCausalLM` | 28 | 1024 | 16 | 8 | 128 | dense, tied embeddings | 32,768 | 32k |
| Qwen3-30B-A3B-FP8 | `Qwen3MoeForCausalLM` | 48 | 2048 | 32 | 4 | 128 | 128 experts, 8 active | 40,960 | 32,768 native, 131,072 with YaRN |
| Qwen3-30B-A3B-Instruct-2507-FP8 | `Qwen3MoeForCausalLM` | 48 | 2048 | 32 | 4 | 128 | 128 experts, 8 active | 262,144 | 262,144 native |

Sources: [Qwen3-8B config](https://huggingface.co/Qwen/Qwen3-8B/raw/main/config.json), [Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B), [Qwen3-1.7B config](https://huggingface.co/Qwen/Qwen3-1.7B/raw/main/config.json), [Qwen3-Embedding-0.6B config](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/raw/main/config.json), [Qwen3-30B-A3B-FP8 config](https://huggingface.co/Qwen/Qwen3-30B-A3B-FP8/raw/main/config.json), [2507-FP8 config](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8/raw/main/config.json). Qwen3-8B-FP8 has the same config plus `quantization_config`: `quant_method=fp8`, `fmt=e4m3`, `activation_scheme=dynamic`, `weight_block_size=[128,128]` ([Qwen3-8B-FP8 config](https://huggingface.co/Qwen/Qwen3-8B-FP8/raw/main/config.json)). Qwen3-30B-A3B cards: 30.5B total / 3.3B activated, `moe_intermediate_size=768`; routers, norms and `lm_head` are excluded from FP8 ([Qwen3-30B-A3B-FP8 card](https://huggingface.co/Qwen/Qwen3-30B-A3B-FP8)). Qwen3-8B card: 8.2B total, 6.95B non-embedding; 40,960 = 32,768 output + 8,192 prompt reservation ([Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B)).

Recommended vLLM flags and parser names (checked against vLLM docs and registries):

| Repo | Flags from docs | Reasoning parser | Tool-call parser |
|---|---|---|---|
| Qwen3-8B, Qwen3-8B-FP8, Qwen3-1.7B | `vllm serve <repo> --reasoning-parser qwen3`; optional `--max-model-len` (default is config 40,960) | `qwen3` | `hermes` with `--enable-auto-tool-choice` |
| Qwen3-30B-A3B-FP8 (hybrid thinking) | as above | `qwen3` | `hermes` |
| Qwen3-30B-A3B-Instruct-2507-FP8 | card: `--max-model-len 262144`, drop to 32,768 on OOM | none needed, no `<think>` is emitted | `hermes` |
| Qwen3-Embedding-0.6B | `--runner pooling`; endpoint `/v1/embeddings` (also `/pooling`, Cohere `/v2/embed`) | none | none |
| Qwen3-8B-GGUF | card commands are for llama.cpp (`llama-cli -hf Qwen/Qwen3-8B-GGUF:Q8_0 ...`) and Ollama (`ollama run hf.co/Qwen/Qwen3-8B-GGUF:Q8_0`); no vLLM line in notes | n/a | n/a |

Sources: [vLLM reasoning outputs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/reasoning_outputs.md), [Qwen function calling](https://qwen.readthedocs.io/en/latest/framework/function_call.html), [Qwen vLLM deployment](https://qwen.readthedocs.io/en/latest/deployment/vllm.html), [vLLM tool_parsers registry](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/tool_parsers/__init__.py), [vLLM embed docs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/models/pooling_models/embed.md), [Qwen3-8B-GGUF card](https://huggingface.co/Qwen/Qwen3-8B-GGUF).

Behaviour of the pinned Qwen3 models:

- Thinking is on by default. With `enable_thinking=False` the template appends `<think>\n\n</think>\n\n` after `<|im_start|>assistant\n`. `/think` and `/no_think` are model-level soft switches that only work when `enable_thinking=True`. Tool calls use Hermes-style `<tool_call>` JSON blocks ([Qwen3-8B tokenizer_config](https://huggingface.co/Qwen/Qwen3-8B/raw/main/tokenizer_config.json), [Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B)).
- vLLM docs: disable thinking per request with `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` or server-wide with `--default-chat-template-kwargs '{"enable_thinking": false}'`. Reasoning appears in `reasoning`; `reasoning_content` is deprecated. `reasoning_effort` auto-injects `enable_thinking` (low/medium/high -> true, none -> false; explicit `enable_thinking` wins) ([vLLM reasoning outputs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/reasoning_outputs.md)).
- Card sampling: thinking Temperature=0.6, TopP=0.95, TopK=20, MinP=0, "DO NOT use greedy decoding"; non-thinking Temperature=0.7, TopP=0.8, TopK=20, MinP=0. `generation_config.json`: temperature 0.6, top_k 20, top_p 0.95 ([Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B), [generation_config](https://huggingface.co/Qwen/Qwen3-8B/raw/main/generation_config.json)).
- YaRN for 131,072 tokens: `--rope-scaling '{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}' --max-model-len 131072`. The card warns static YaRN can hurt short-text quality ([Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B), [Qwen vLLM deployment](https://qwen.readthedocs.io/en/latest/deployment/vllm.html)). Unverified: that `--rope-scaling` is still accepted by vLLM 0.31 (the Qwen3.5 card uses `--hf-overrides` with `rope_parameters`).
- OOM mitigations in the Qwen docs: lower `--max-model-len`, lower `--gpu-memory-utilization` (default 0.9), `--enforce-eager` ([Qwen vLLM deployment](https://qwen.readthedocs.io/en/latest/deployment/vllm.html)).
- `Qwen3-30B-A3B` has two generations. Original `Qwen3-30B-A3B(-FP8)` is hybrid thinking (32,768 native). `Qwen3-30B-A3B-Instruct-2507(-FP8)` "supports only non-thinking mode" and has 262,144 native context. "Qwen3-30B-A3B-FP8" is therefore not the same behaviour as the 2507 FP8 ([Qwen3-30B-A3B-FP8 card](https://huggingface.co/Qwen/Qwen3-30B-A3B-FP8), [2507-FP8 card](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8)).
- Embedding model: instruction-aware (queries use `Instruct: {task}\nQuery:{query}`, documents none; the card says 1-5% gain), user-defined output dims 32 to 1024 (MRL), last-token pooling, Sentence-Transformers pipeline Transformer -> Pooling -> Normalize, 100+ languages ([Qwen3-Embedding-0.6B card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [pooling config](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/raw/main/1_Pooling/config.json)). vLLM docs list `Qwen3ForCausalLM` (converted) -> `Qwen/Qwen3-Embedding-0.6B` and say to specify `--runner pooling` explicitly ([vLLM supported models](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/models/supported_models.md)).
- Ollama `qwen3:8b` is Q4_K_M, 5.2 GB, digest `500a1f067a9f`, Apache 2.0, 40K context; `qwen3:8b-q8_0` 8.9 GB; `qwen3:8b-fp16` 16 GB ([Ollama qwen3:8b](https://ollama.com/library/qwen3:8b), [tags](https://ollama.com/library/qwen3/tags)).
- Blackwell 4-bit builds of Qwen3-8B (both Apache-2.0, 6.40 GB): `nvidia/Qwen3-8B-NVFP4` (SHA `ccd10a893cbca613259517c3efe08e151ddf2b8e`, ModelOpt, `kv_cache_quant_algo: FP8`, group size 16; card lists TensorRT-LLM as the supported runtime, tested on B200) and `RedHatAI/Qwen3-8B-NVFP4` (SHA `e391349c110709b87bfc2ad2fde3f50dc5839fd8`, compressed-tensors, "ready for inference with vLLM>=0.9.1") ([nvidia card](https://huggingface.co/nvidia/Qwen3-8B-NVFP4), [RedHatAI card](https://huggingface.co/RedHatAI/Qwen3-8B-NVFP4)). vLLM docs say ModelOpt checkpoints are detected via `hf_quant_config.json` (`quant_algo` `NVFP4`, `quantization="modelopt_fp4"`); without native FP4 GEMM it falls back to weight-only W4A16 via Marlin with a warning ([vLLM ModelOpt docs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/quantization/modelopt.md)).
- Other Qwen3-8B builds: `Qwen/Qwen3-8B-AWQ` (SHA `4da05a8edb55c6046cce958586c33b61da07bb79`, 6.10 GB), `RedHatAI/Qwen3-8B-FP8-dynamic` (SHA `05233ce1e0565b5fdc9cfa000ab840152ed30c70`, 9.44 GB) ([Qwen3-8B-AWQ](https://huggingface.co/api/models/Qwen/Qwen3-8B-AWQ), [RedHatAI FP8-dynamic](https://huggingface.co/api/models/RedHatAI/Qwen3-8B-FP8-dynamic)).
- Unverified: tool-call reliability of Qwen3-1.7B; exact `vllm serve ... --runner pooling` startup on 0.31.0; whether `dimensions=` (MRL) works via the OpenAI endpoint without `--hf-overrides '{"is_matryoshka": true}'`; MoE FP8 kernel behaviour on the lab GPU; that `nvidia/Qwen3-8B-NVFP4` loads in vLLM 0.31 on Blackwell. Run each once on the target hardware before the workshop.

**Interpretation** (my inference). Weights of every pinned model are far below the workshop GPU's 96 GB, so the real limit is KV cache and concurrency, not weights (section 5.2). The FP8 8B build cuts weight bytes by about 42% (9.44 GB vs 16.38 GB, DERIVED), which is a throughput and headroom lever, not a quality-neutral guarantee. The notes contain no quality measurement.

**Workshop decision.** `config/models.yaml` pins the table above. Profiles in `config/vllm-profiles/*.yaml` carry `--reasoning-parser qwen3` and `--tool-call-parser hermes` (with `--enable-auto-tool-choice`) for the Qwen3 chat models and `--runner pooling` for the `embedding` profile, never the card lines.

### 5.2 KV cache bytes per token (DERIVED)

**Source facts**

- Formula: bytes per token = 2 (K and V) x layers x KV heads x head_dim x bytes per element (2 for BF16). Inputs are the `config.json` fields in the table above. Excludes vLLM block/page rounding, CUDA-graph memory, activation memory and, for hybrid models, the fixed per-sequence recurrent state (notes, derived).
- Qwen3.5-9B inputs: `layer_types` = 24 `linear_attention` + 8 `full_attention`, `num_key_value_heads=4`, `head_dim=256` ([Qwen3.5-9B config](https://huggingface.co/Qwen/Qwen3.5-9B/raw/main/config.json)).

**DERIVED table** (arithmetic mine, inputs from the facts above):

| Model | Arithmetic | Bytes/token | KiB/token | per sequence at 32,768 | at 40,960 | at long ctx |
|---|---|---|---|---|---|---|
| Qwen3-8B | 2 x 36 x 8 x 128 x 2 | 147,456 | 144 | 4.5 GiB | 5.625 GiB | 18 GiB at 131,072 |
| Qwen3-1.7B | 2 x 28 x 8 x 128 x 2 | 114,688 | 112 | 3.5 GiB | 4.375 GiB | 14 GiB at 131,072 |
| Qwen3-30B-A3B (both generations) | 2 x 48 x 4 x 128 x 2 | 98,304 | 96 | 3.0 GiB | 3.75 GiB | 24 GiB at 262,144 (2507) |
| Qwen3-14B (comparison; 40 layers, 8 KV, 128) | 2 x 40 x 8 x 128 x 2 | 163,840 | 160 | 5.0 GiB (160 KiB x 32,768) | n/a | n/a |
| Qwen3-Embedding-0.6B | 2 x 28 x 8 x 128 x 2 | 114,688 | 112 | n/a | n/a | Unverified how vLLM allocates KV for the pooling runner |
| Qwen3.5-9B (8 full-attention layers only) | 2 x 8 x 4 x 256 x 2 | 32,768 | 32 | 1.0 GiB (32 KiB x 32,768) | n/a | 8 GiB at 262,144 |
| Qwen3.5-35B-A3B (10 full-attention layers) | 2 x 10 x 2 x 256 x 2 | 20,480 | 20 | n/a | n/a | n/a |

- FP8 KV cache stores 1 byte per element instead of 2: Qwen3-8B 73,728 B/token (notes); by the same halving Qwen3-1.7B 57,344 and Qwen3-30B-A3B 49,152 (DERIVED, mine).
- Qwen3.5-9B is 4.5x smaller per token than Qwen3-8B (144 / 32 = 4.5). The 24 Gated-DeltaNet layers add a constant-size state per sequence, size Unverified.

**Interpretation** (my inference). The number to sell in a lab is per-sequence KV at the context you actually allow: concurrency is roughly KV pool divided by (KiB/token x tokens per sequence). The 30B MoE has smaller KV per token (96 KiB) than the dense 8B (144 KiB) because of 4 KV heads versus 8, even though it has more layers. Hybrid attention models (Qwen3.5 and later) change this picture by a factor of about 4 to 5. The `kv-fp8`, `kv-constrained` and `kv-constrained-fp8kv` profiles are where this shows up.

**Workshop decision.** Use the table as the hand-check for `scripts/sizing.py` output, and as the prediction students write down before running the `kv-constrained`, `kv-constrained-fp8kv` and `max-seqs-8` profiles in `config/vllm-profiles/`. Measured values go to `benchmark/results/`.

### 5.3 Alternative families for the model-selection lab

State of 2026-10-14. All SHAs below are `main` at fetch and matched on re-check, except `zai-org/GLM-5.3` (still moving; re-resolve). Licence names are as in section 11.3. "Weights" is the BF16 or stated size from HF metadata; fit against 96 GB is DERIVED (weights size alone, no KV, no overhead).

**Source facts**

| Family | Repo | SHA | Licence | Facts the notes give |
|---|---|---|---|---|
| Qwen | Qwen/Qwen3.5-9B | `c202236235762e1c871ad0ccb60c8ee5ba337b9a` | Apache-2.0 | 9,653,104,368 params BF16, 19.31 GB, 32 layers (8 x (3 Gated DeltaNet + 1 gated attention)), 16 Q / 4 KV heads, head_dim 256, vision encoder, ctx 262,144 (to 1,010,000) |
| Qwen | Qwen/Qwen3.5-4B | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` | Apache-2.0 | 4,659,865,088 params, 9.32 GB, 24 linear + 8 full attention layers, ctx 262,144 |
| Qwen | Qwen/Qwen3.5-35B-A3B | `59d61f3ce65a6d9863b86d2e96597125219dc754` | Apache-2.0 | 35.95B BF16 (71.90 GB), 256 experts / 8, 30 linear + 10 full attention, ctx 262,144; FP8 repo 37.46 GB |
| Qwen | Qwen/Qwen3.5-397B-A17B | `8472618112abcbd45acbcdc58436aff4233c23f7` | Apache-2.0 | 403B params, 806.8 GB BF16 |
| Qwen | Qwen/Qwen3.6-27B | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | Apache-2.0 | dense, 27.78B, 55.56 GB, 64 layers hybrid, ctx 262,144 |
| Qwen | Qwen/Qwen3.6-35B-A3B | `995ad96eacd98c81ed38be0c5b274b04031597b0` | Apache-2.0 | 35.95B, 71.90 GB |
| Qwen | Qwen/Qwen3.8-27B | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | Apache-2.0 | dense 27B, 64 layers (16 x (3 DeltaNet + 1 gated attention)), 24 Q / 4 KV heads, head_dim 256, image + video, ctx 262,144 (1,000,000 with YaRN) |
| Qwen | Qwen/Qwen3.8-2.4T-A95B | `207bd685a7e3696cfaff12ded7c6a7ea0f88c996` | Qwen3.8-Max License | 2.4T total / 95B active, 4.89 TB BF16 |
| Qwen | Qwen/Qwen3.8-Flash-Next | `de4b8e4d43b917e7706784d8bb445c9af86a3540` | Qwen Community License 1.0 | 125B / 6B active (+ 51B n-gram embedding + 4B MTP), 360 GB BF16 |
| Qwen | Qwen/Qwen3-Coder-30B-A3B-Instruct | `b2cff646eb4bb1d68355c01b18ae02e7cf42d120` | Apache-2.0 | 30.5B / 3.3B active, 48 layers, 128 experts / 8, 32 Q / 4 KV, ctx 262,144, non-thinking only |
| Qwen | Qwen/Qwen3-Coder-Next | `a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb` | Apache-2.0 | 80B / 3B active, hybrid, ctx 262,144; card uses `--tensor-parallel-size 2` |
| Qwen | Qwen/Qwen3-VL-8B-Instruct | `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b` | Apache-2.0 | 8,767,123,696 params, 17.53 GB, 36 layers, 32 Q / 8 KV, head_dim 128, ctx 262,144 |
| Meta | meta-llama/Llama-3.1-8B-Instruct | `0e9e39f249a16976918f6564b8830bc894c89659` | Llama 3.1 Community License | gated manual, 8.03B, 16.06 GB, 8 languages incl. German |
| Meta | meta-llama/Llama-3.3-70B-Instruct | `6f6073b423013f6a7d4d9f39144961bfbfbc386b` | Llama 3.3 Community License | gated manual, 70.55B, 141.1 GB |
| Meta | meta-llama/Llama-4-Scout-17B-16E-Instruct | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` | Llama 4 Community License | gated manual, 108.6B (17B active), 217.3 GB, text + image in, 12 languages |
| Meta | meta-llama/Llama-4-Maverick-17B-128E-Instruct | `73d14711bcc77c16df3470856949c3764056b617` | Llama 4 Community License | 401.6B (17B active), 803.2 GB (an FP8 sibling exists) |
| Meta | meta-models/Muse-Glimmer-30B | `a4e59da52a7bc87ae7251dd5545c0dd437c44b68` | Apache-2.0 + Usage Policy | dense ~29.6B, 59.55 GB BF16, 52 layers, 32 Q / 2 KV, head_dim 128, 39 sliding (2048) + 13 full layers, ctx 131,072+, text + image in |
| Google | google/gemma-4-E4B-it | `ee0ef6023621cff504d758262d4e04895a5af4a2` | Apache-2.0 | 4.5B effective / 8B with embeddings, 42 layers, 128K, 15.99 GB |
| Google | google/gemma-4-E2B-it | `3e22461f65e89153144f8adb70e3b8c2cc9845a7` | Apache-2.0 | 2.3B effective / 5.1B with embeddings, 35 layers, 128K, 10.25 GB |
| Google | google/gemma-4-12B-it | `707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7` | Apache-2.0 | 11.95B, 48 layers, hidden 3,840, 16 Q / 8 KV, head_dim 256, 256K, 23.92 GB, text + image + audio |
| Google | google/gemma-4-26B-A4B-it | `4d7ae4984b7db7de8f8457170b3f1a419ee76d52` | Apache-2.0 | 25.2B / 3.8B active, 30 layers, 128 experts, 16 Q / 8 KV, 256K, 51.61 GB |
| Google | google/gemma-4-31B-it | `842da3794eaa0b77d5f08bae87a17459d91ff475` | Apache-2.0 | dense 30.7B, 60 layers (50 sliding 1024 + 10 full), 32 Q / 16 KV, head_dim 256, 256K, 62.55 GB |
| Mistral | mistralai/Ministral-3-8B-Instruct-2512 | `5b26027e7b19eeb4b7352e1fed3926375dd2cb4d` | Apache-2.0 | 8.9B (incl. 0.4B vision), 34 layers, 32 Q / 8 KV, head_dim 128, ctx 262,144, FP8 main checkpoint, "fitting in 12GB of VRAM in FP8" |
| Mistral | mistralai/Ministral-3-14B-Instruct-2512 | `29439f81c2be264d8d393273f99e7db9c0961120` | Apache-2.0 | 13.9B, 40 layers, 32 Q / 8 KV, ctx 262,144 |
| Mistral | mistralai/Mistral-Small-3.2-24B-Instruct-2506 | `95a6d26c4bfb886c58daf9d3f7332c857cb27b43` | Apache-2.0 | 24.0B BF16; repo 96.0 GB (two weight sets) |
| Mistral | mistralai/Devstral-Small-2-24B-Instruct-2512 | `55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128` | Apache-2.0 | 24.0B, ctx 256k, single RTX 4090 / 32 GB Mac class, has `vllm serve` section |
| Mistral | mistralai/Mistral-Small-4-119B-2603 | `a11f36bebf709121056b1dbcc943d1c6afbe494d` | Apache-2.0 | 119B / 6.5B active, 128 experts / 4, FP8, 241.85 GB repo, card serve line uses `--tensor-parallel-size 2` |
| Mistral | mistralai/Devstral-2-123B-Instruct-2512 | `1613bf01adb5e1c6fdc196b46e6b173eae75eb4a` | Modified MIT | 125.0B, 88 layers, FP8, ctx 262,144 |
| Mistral | mistralai/Mistral-Medium-3.5-128B | `22b2b868a15677cfa6061277ed2f653d1349a9ab` | Modified MIT | dense 128B, 256k ctx, 267.2 GB repo |
| Mistral | mistralai/Mistral-Large-3-675B-Instruct-2512 | `383ffea2c7d60dfd44ca960e8e691709d4fdb9cd` | Apache-2.0 | 675B total / 41B active (card later says 673B / 39B), 681.5 GB repo |
| DeepSeek | deepseek-ai/DeepSeek-V4.1-Flash | `5254448103b6254fc646dacbca1cbbf20e9216c1` | MIT | 552B backbone, 1M ctx, 510 GB, no Jinja chat template |
| DeepSeek | deepseek-ai/DeepSeek-V4-Flash-0731 | `7872f01b1d1fe23eabc4c98b48bffcef5a386062` | MIT | 43 layers, 256 experts, 166.9 GB |
| DeepSeek | deepseek-ai/DeepSeek-V4-Pro-0813 | `72e1d3230f6c080a530b0a1d46f8eb4602340597` | MIT | 61 layers, 384 experts, 892.7 GB |
| DeepSeek | deepseek-ai/DeepSeek-V3.2 | `a7e62ac04ecb2c0a54d736dc46601c5606cf10a6` | MIT | (2025-12-01) |
| Moonshot | moonshotai/Kimi-K3 | `f831ab66814297da540d832a5235f8e904f29d06` | Kimi K3 License | 2.8T / 104B active, 1.56 TB, custom code (`auto_map`) |
| Moonshot | moonshotai/Kimi-K2.6 | `7eb5002f6aadc958aed6a9177b7ed26bb94011bb` | Modified MIT | 1T / 32B active, INT4, 595.2 GB, custom code (`auto_map`) |
| Moonshot | moonshotai/Kimi-K2.7-Code | `74797c9c62378b951a1f6fcf5c4631024e9b8bef` | Modified MIT | (2026-06-11) |
| OpenAI | openai/gpt-oss-20b | `6cee5e81ee83917806bbde320786a8fb61efebee` | Apache-2.0 + usage policy | 21B / 3.6B active, MXFP4 MoE weights, 24 layers, 64 Q / 8 KV, head_dim 64, ctx 131,072, "run within 16GB of memory" |
| OpenAI | openai/gpt-oss-120b | `b5c939de8f754692c1647ca79fbf85e8c1e70f8a` | Apache-2.0 + usage policy | 117B / 5.1B active, 36 layers, "single 80GB GPU" |
| IBM | ibm-granite/granite-4.2-8b | `f8de16cdcdbc6c779ca517604e050d82cc119e44` | Apache-2.0 | dense, 40 layers, 32 Q / 8 KV, 17.58 GB, ctx 131,072 (card 128K, to 512K) |
| IBM | ibm-granite/granite-4.2-30b | `9e668ce1c538387ef24d3644e9b0606647762636` | Apache-2.0 | (created 2026-08-07) |
| Zhipu | zai-org/GLM-5.3-Flash | `91b69215804f2d2036a8867f6ce44848e278dcda` | MIT | 320B / 18B active, FP8 328 GB, ctx 1,048,576, multimodal |
| Zhipu | zai-org/GLM-5.3 | `ba32f8c19c8738e2c57c71798c601d477a7bf844` (moving) | GLM-5.3 License | 753.3B FP8, 755.6 GB |
| NVIDIA | nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | `a9904d24bcc1d289a1950fa9d2b978c47cf903b9` | OpenMDW-1.1 | 30B / 3B active, NemotronH hybrid, ctx up to 1M (256K on a single H100) |
| Swiss AI | swiss-ai/Apertus-v1.5-8B | `a411d838600baf0e3635a3daf66fb7c55fc97bb6` | Apache-2.0 (gated auto) | 8.9B, 685,739 downloads |
| EuroLLM | utter-project/EuroLLM-9B-Instruct-2512 | `def82454026b0353f12e48a0de081a9ed380d91e` | Apache-2.0 | Llama architecture, 42 layers, 9.15B, ctx 32,768, all 24 official EU languages |

Sources for the table: HF model API per repo, `https://huggingface.co/api/models/<repo>` (SHA, licence, params), and the cards and `config.json` files linked in the per-family bullets below; family listings: [Qwen](https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=80), [meta-llama](https://huggingface.co/api/models?author=meta-llama&sort=createdAt&direction=-1), [google](https://huggingface.co/api/models?author=google&sort=createdAt&direction=-1&limit=80), [mistralai](https://huggingface.co/api/models?author=mistralai&sort=createdAt&direction=-1&limit=40), [deepseek-ai](https://huggingface.co/api/models?author=deepseek-ai&sort=createdAt&direction=-1&limit=25), [moonshotai](https://huggingface.co/api/models?author=moonshotai&sort=createdAt&direction=-1&limit=25), [openai](https://huggingface.co/api/models?author=openai&sort=createdAt&direction=-1), [ibm-granite](https://huggingface.co/api/models?author=ibm-granite&sort=createdAt&direction=-1).

vLLM serving facts per family:

- **Qwen3.5 / 3.6 / 3.8 (hybrid Gated DeltaNet, 1 in 4 layers full attention).** Thinking is default (template appends `<think>\n`); tool calls are XML (`<function=` / `parameter=`). Card line: `vllm serve Qwen/Qwen3.5-9B --port 8000 --tensor-parallel-size 1 --max-model-len 262144 --reasoning-parser qwen3`; tools add `--enable-auto-tool-choice --tool-call-parser qwen3_coder`; text-only `--language-model-only` ("skips the vision encoder and multimodal profiling to free memory for KV cache"); MTP `--speculative-config '{"method":"qwen3_next_mtp","num_speculative_tokens":2}'`. The vLLM recipe says vLLM `>= 0.17.0` and gives `--speculative-config '{"method": "mtp", "num_speculative_tokens": 1}'`. The card recommends context of at least 128K "to preserve thinking capabilities"; sampling thinking general `temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5`. Languages: "201 languages and dialects" ([Qwen3.5-9B card](https://huggingface.co/Qwen/Qwen3.5-9B), [vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3.5-9B), [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B)). Caution: card and recipe disagree on the MTP method name and token count, and the card says "vLLM from the main branch is required" while the recipe says `>= 0.17.0`.
- **Qwen3-Coder.** Tool parser `qwen3_coder`; the registry also has `qwen3_xml` (same class `Qwen3EngineToolParser`) and the vLLM docs name `qwen3_xml` ([vLLM tool calling](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md)). Coder-Next card sampling: temperature=1.0, top_p=0.95, top_k=40 ([Qwen3-Coder-Next card](https://huggingface.co/Qwen/Qwen3-Coder-Next)).
- **Llama.** Llama 3.1/3.2/4 JSON: `--tool-call-parser llama3_json --chat-template examples/tool_chat_template_llama3.1_json.jinja` (no parallel calls). Llama 4: `--tool-call-parser llama4_pythonic --chat-template examples/tool_chat_template_llama4_pythonic.jinja` ([vLLM tool calling](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md)). Meta has published no new `meta-llama/` model since Llama 4 and the April 2025 guard models; its newest open-weight LLM is Muse Glimmer 30B (2026-08-09) ([meta-llama listing](https://huggingface.co/api/models?author=meta-llama&sort=createdAt&direction=-1)). vLLM has `muse_glimmer` tool and reasoning parsers and lists `MuseGlimmerForConditionalGeneration`; reasoning strength is set in the system prompt (`Reasoning strength: <low|medium|high|xhigh>`) ([Muse Glimmer card](https://huggingface.co/meta-models/Muse-Glimmer-30B), [vLLM supported models](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/models/supported_models.md)).
- **Gemma 4.** Reasoning parser `gemma4`; tool parser `gemma4` in the registry. "Gemma 4 reasoning is disabled by default"; enable with `enable_thinking=True` in `chat_template_kwargs` or `reasoning_effort`. Card: thinking via `<|think|>` at the start of the system prompt, native function calling, "35+ languages" out of the box, pre-trained on 140+, pretraining cutoff Jan 2025 ([vLLM reasoning outputs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/reasoning_outputs.md), [gemma-4-12B-it card](https://huggingface.co/google/gemma-4-12B-it)). Unverified: the exact recommended `vllm serve` line (recipes.vllm.ai returned HTTP 500; `tool_calling.md` has no Gemma 4 section). Expected: `--reasoning-parser gemma4 --tool-call-parser gemma4 --enable-auto-tool-choice`. QAT variants (`-qat-q4_0-gguf`, `-qat-w4a16-ct`) exist for 31B, 26B-A4B, 12B, E4B, E2B ([google listing](https://huggingface.co/api/models?author=google&sort=createdAt&direction=-1&limit=80)).
- **Mistral.** `--tool-call-parser mistral` and, for reasoning-capable models, `--reasoning-parser mistral`. Two weight formats: official (`--tokenizer_mode mistral --config_format mistral --load_format mistral`) or HF (`--tokenizer_mode hf --config_format hf --load_format hf --chat-template examples/tool_chat_template_mistral_parallel.jinja`) ([vLLM tool calling](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md)). Ministral 3 8B card line: `vllm serve mistralai/Ministral-3-8B-Instruct-2512 --tokenizer_mode mistral --config_format mistral --load_format mistral --enable-auto-tool-choice --tool-call-parser mistral`, recommended temperature below 0.1 ([card](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512)). Mistral Small 4 card line: `vllm serve mistralai/Mistral-Small-4-119B-2603 --max-model-len 262144 --tensor-parallel-size 2 --attention-backend FLASH_ATTN_MLA --tool-call-parser mistral --enable-auto-tool-choice --reasoning-parser mistral --max_num_batched_tokens 16384 --max_num_seqs 128 --gpu_memory_utilization 0.8`; per-request `reasoning_effort` none or high ([card](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603)). Caution: Medium 3.5 had a config bug fixed in commit `c4be198050fb5789774a55b92ed697becfbf20ae` ("incorrect entry that caused long-context performance degradation"); GGUFs made earlier need regeneration ([card](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B)). Caution: the Mistral Large 3 card says 675B / 41B active in one place and 673B / 39B in another ([card](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512)).
- **DeepSeek.** Reasoning parser `deepseek_r1` for R1, `deepseek_v3` for V3.1 (reasoning off by default, enable with `thinking=True`); tool calling for V3.1 `--tool-call-parser deepseek_v31 --chat-template examples/tool_chat_template_deepseekv31.jinja`; V3 / R1-0528 `deepseek_v3`; registry also holds `deepseek_v32`, `deepseek_v4`, `deepseek_v41` ([vLLM tool calling](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md), [vLLM reasoning outputs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/reasoning_outputs.md)). A 7 to 14B DeepSeek dense model no longer exists (DERIVED from the listing); only the 284B+ MoEs are current. Draft-model repos `eagle3_qwen3_8b_ttt7`, `dflash_qwen3_8b_block7`, `dspark_qwen3_8b_block7` (2026-06-28) accelerate Qwen3-4B/8B/14B and Gemma 4 12B ([deepseek-ai listing](https://huggingface.co/api/models?author=deepseek-ai&sort=createdAt&direction=-1&limit=25)). V4.1-Flash ships no Jinja chat template ([card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)).
- **Kimi.** `--tool-call-parser kimi_k2` for K2; `kimi_k3` parsers for K3; K2.6 card passes `chat_template_kwargs={"thinking": False}`. K3 has thinking always on and requires passing the complete assistant message including `reasoning_content` back in multi-turn ([Kimi-K3 card](https://huggingface.co/moonshotai/Kimi-K3), [Kimi-K2.6 card](https://huggingface.co/moonshotai/Kimi-K2.6)).
- **gpt-oss.** Tool parser `openai` (`--tool-call-parser openai`); reasoning parser registry name `openai_gptoss` (exists at v0.31.0); the reasoning docs table does not list gpt-oss. Must be used with the harmony response format; reasoning levels via system prompt `Reasoning: high`; native tools; full chain-of-thought is exposed and "not intended to be shown to end users" ([vLLM reasoning registry v0.31.0](https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/reasoning/__init__.py), [gpt-oss-20b card](https://huggingface.co/openai/gpt-oss-20b)).
- **Granite 4.2 8B.** Card line: `--reasoning-parser granite_thinking_parser --reasoning-parser-plugin ./granite_thinking_parser.py --tool-call-parser qwen3_coder` (plugin file needed); vLLM docs list reasoning parser `granite_thinking_parser`, reasoning on by default (`enable_thinking=False` to disable); tool parser `granite4` is documented for Granite 4.0. Tested languages incl. German ([card](https://huggingface.co/ibm-granite/granite-4.2-8b), [vLLM reasoning outputs](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/reasoning_outputs.md)).
- **Nemotron 3.5 Lightning, GLM.** Nemotron: `--reasoning-parser auto` (resolves to `nemotron_3`) and `--tool-call-parser auto` (resolves to `qwen3_coder`); NVFP4 variants exist. GLM: parsers `glm45` / `glm47` ([Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16), [GLM-5.3-Flash card](https://huggingface.co/zai-org/GLM-5.3-Flash)). Caution: the notes' registry list spells the Nemotron reasoning parser `nemotron_v3` while the card resolution says `nemotron_3`; Unverified which is exact.
- **Parser registry cheat-sheet.** Reasoning: `qwen3`, `deepseek_r1`, `deepseek_v3`, `deepseek_v4`, `deepseek_v41`, `gemma4`, `glm45`/`glm47`, `openai_gptoss`, `granite` / `granite_thinking_parser`, `kimi_k2`, `kimi_k3`, `mistral`, `nemotron_v3`, `minimax_m2`, `olmo3`, `step3`, `hunyuan_a13b`, `ernie45`, `mimo`, `seed_oss`, `hf`. Tool: `hermes`, `qwen3_coder`, `qwen3_xml`, `qwen3_json` (alias of hermes, `main` only, not in the `v0.31.0` tag), `openai`, `mistral`, `llama3_json`, `llama4_pythonic`, `llama4_json`, `pythonic`, `deepseek_v3`, `deepseek_v31`, `deepseek_v32`, `deepseek_v4`, `deepseek_v41`, `kimi_k2`, `kimi_k3`, `glm45`, `glm47`, `gemma4`, `functiongemma`, `granite4`, `granite`, `granite-20b-fc`, `muse_glimmer`, `step3p5`, `minimax_m2`, `olmo3`, `xlam`, `hf` ([reasoning registry](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/reasoning/__init__.py), [tool registry](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/tool_parsers/__init__.py)). `--enable-auto-tool-choice` is mandatory together with `--tool-call-parser <name>`; `--tool-strict-level` raises a server-side strictness floor ([vLLM tool calling](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/features/tool_calling.md)). Unverified: the release in which `qwen3_json`, `deepseek_v41` and similar entries landed.
- **German-language claims (vendor wording only).** Qwen3 119 languages with German listed; Qwen3.5 "201 languages and dialects"; Llama 3.1 8 languages incl. German; Llama 4 12 languages incl. German; Gemma 4 "35+ languages out of the box, pre-trained on 140+"; Mistral Small 4 / Ministral 3 / Large 3 / Medium 3.5 list German among "dozens of languages"; Granite 4.2 lists German among 12 tested languages; Nemotron 3.5 among 6; EuroLLM among 35; Muse Glimmer ">100 languages" with no list read. Unverified: gpt-oss, DeepSeek V4, Kimi K2.6/K3 (no list found) ([Qwen3 blog](https://qwenlm.github.io/blog/qwen3/), [Qwen3.5-9B card](https://huggingface.co/Qwen/Qwen3.5-9B), [Llama 3.1 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/MODEL_CARD.md), [Llama 4 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md), [EuroLLM-9B card](https://huggingface.co/utter-project/EuroLLM-9B-Instruct-2512)).
- Ollama library entries that exist for newer models: `qwen3.5:9b` (256K), `qwen3.8:27b` (18 GB, 256K), `gemma4:e4b`, `gemma4:12b`, `gemma4:26b`, `gemma4:31b`, `gpt-oss:20b` (14 GB, 128K), `gpt-oss:120b` (65 GB) ([Ollama library](https://ollama.com/library/qwen3.5), [gemma4](https://ollama.com/library/gemma4), [gpt-oss](https://ollama.com/library/gpt-oss)).

**Interpretation** (my inference).

- DERIVED fit check against one 96 GB card, comparing HF weight sizes only (no KV, no overhead). Ample room: Qwen3.5-4B (9.32 GB) and 9B (19.31 GB), Qwen3-VL-8B (17.53 GB), Gemma 4 E2B / E4B / 12B (10.25 / 15.99 / 23.92 GB), Granite 4.2 8B (17.58 GB), Llama 3.1 8B (16.06 GB), EuroLLM-9B, Ministral 3 8B and 14B, gpt-oss-20b (13.76 GB root set). Tighter KV budget: Qwen3.6-27B (55.56 GB), Gemma 4 31B (62.55 GB), Muse Glimmer 30B (59.55 GB), Gemma 4 26B-A4B (51.61 GB), Mistral-Small-3.2-24B (48 GB per set), Qwen3.5/3.6 35B-A3B BF16 (71.90 GB; the FP8 repo at 37.46 GB is the realistic choice). Weights alone exceed 96 GB: Llama 3.3 70B BF16 (141.1 GB), Llama 4 Scout (217.3 GB) and Maverick (803.2 GB), Mistral Small 4 (~121 GB per set) and Medium 3.5 (~133.6 GB per set), DeepSeek V4 (166.9 GB and up), GLM-5.3-Flash (328 GB), Qwen3.8-Flash-Next (360 GB), Kimi and Qwen3.8-2.4T. The gpt-oss-120b card says it runs on a "single 80GB GPU".
- Hybrid-attention models (Qwen3.5 and later; Nemotron 3.5 is described as a NemotronH hybrid) shrink KV per token, and sliding-window models (Gemma 4, Muse Glimmer, gpt-oss) restrict it differently. Both change the concurrency ranking relative to dense models of the same weight size, which makes "same weight size, different concurrency" a good lab demonstration. The notes do not say how vLLM allocates KV for sliding-window layers; measure it.
- Poor "just run `vllm serve`" candidates: DeepSeek V4.1-Flash (no Jinja template), Kimi K3 (must pass `reasoning_content` back; ships custom code), Granite 4.2 (reasoning parser needs a plugin file). Vendor language claims are not measured quality; a lab that cares about German should run its own eval across the same prompts.

**Workshop decision.** Shortlist for the lab in `docs/MODEL-SELECTION.md`: Qwen3.5-9B, Gemma 4 12B, Ministral 3 8B / 14B, Granite 4.2 8B, gpt-oss-20b and EuroLLM-9B, each run on the same prompts and measured with `benchmark/infbench` (`benchmark/run.sh`) before any choice. Principle: the smallest model that reliably satisfies the task. Each candidate is pinned by full SHA from the table (re-resolve GLM-5.3 first, if used) and its licence is recorded using the checklist in 11.5. Parser flags come from the vLLM docs and registries, never copied from the card.

### 5.4 Caution: model-card vLLM snippets can be stale

**Source facts**

- The Qwen3-8B, Qwen3-8B-FP8, Qwen3-1.7B and Qwen3-30B-A3B-FP8 cards still print `vllm serve ... --enable-reasoning --reasoning-parser deepseek_r1` (card says "vllm>=0.8.5"). `--enable-reasoning` was deprecated in vLLM v0.9.0 (2025-05-15; release note "Reasoning: deprecate `--enable-reasoning`") and no longer exists in `vllm/engine/arg_utils.py` on `main`. The correct parser for Qwen3 is `--reasoning-parser qwen3` ([Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B), [vLLM v0.9.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.9.0), [vLLM arg_utils.py](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/engine/arg_utils.py)).
- The Qwen docs' tool-calling line also pairs `--tool-call-parser hermes` with `--reasoning-parser deepseek_r1`; the `deepseek_r1` part is stale ([Qwen function calling](https://qwen.readthedocs.io/en/latest/framework/function_call.html)).
- The Qwen3-Embedding-0.6B card uses `LLM(model=..., task="embed")`. `--task` was replaced by `--runner` / `--convert` in vLLM v0.10.1 (2025-08-18); use `--runner pooling` ([Qwen3-Embedding-0.6B card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [vLLM v0.10.1 release](https://github.com/vllm-project/vllm/releases/tag/v0.10.1)).
- The gpt-oss card's vLLM line refers to a special wheel `vllm==0.10.1+gptoss` from release time; it is obsolete ([gpt-oss-20b card](https://huggingface.co/openai/gpt-oss-20b)).
- `nvidia/Qwen3-8B-NVFP4` documents TensorRT-LLM only and calls itself `nvidia/Qwen3-8B-FP4` in its usage snippet (old repo name). The RedHatAI card's vLLM test statement is for vLLM 0.9.1, not 0.31 ([nvidia card](https://huggingface.co/nvidia/Qwen3-8B-NVFP4), [RedHatAI card](https://huggingface.co/RedHatAI/Qwen3-8B-NVFP4)).
- Card/recipe disagreements for Qwen3.5 and parser spelling uncertainty for Nemotron are listed in 5.3.

**Interpretation** (my inference). Cards are written at release time and not maintained against vLLM releases. A card line is a hint about the model's template, not an instruction for the pinned engine. Silent failure is possible: an unknown or wrong reasoning parser yields either a startup error or reasoning text leaking into `content`.

**Workshop decision.** The lab handout (`docs/MODEL-SELECTION.md`) tells students to check every card flag against `vllm serve --help` for the pinned image (`vllm/vllm-openai:v0.31.0`, digest in `infra/versions.env`) and the docs for that tag, and to record the working flag set in the profile YAML under `config/vllm-profiles/`.

---

## 6. GPU options and hardware reasoning

Verified 2026-10-14. Legend used in this section: **D** = dense (no 2:4 structured sparsity); **S** = sparse (2:4); **[D]** after a number = DERIVED by the research agent (arithmetic shown where it matters, e.g. dense = sparse / 2 when NVIDIA says so in a footnote); `n/a` = not supported by the hardware; `Unverified:` = not confirmed by a primary source. Peak rates are "at GPU boost clock" per NVIDIA footnotes. BF16 equals the FP16 rate on all parts below unless noted.

### 6.1 Dense versus sparse: how to read NVIDIA headline numbers

**Source facts**

- "Sparse" here means 2:4 structured sparsity. NVIDIA headline numbers are frequently sparse, and the dense rate is half of the sparse rate where NVIDIA says so in a footnote. RTX PRO whitepaper footnote 2 reads "Effective TOPS / TFLOPS using the Sparsity Feature"; footnote 1 reads "Peak rates are based on GPU Boost Clock" ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)).
- L4 page: "Shown with sparsity. Specifications are one-half lower without sparsity." ([NVIDIA L4](https://www.nvidia.com/en-us/data-center/l4/)).
- H100 page: asterisked values are "With sparsity" ([NVIDIA H100](https://www.nvidia.com/en-us/data-center/h100/)). HGX B200: FP16/BF16/FP8/INT8/TF32 are "Specification in Sparse. Dense is 1/2 sparse spec shown." ([NVIDIA HGX](https://www.nvidia.com/en-us/data-center/hgx/)).
- Product-page "AI TOPS" for GeForce (RTX 4090 1321, RTX 5090 3352) are SPARSE numbers at the most favourable precision, not BF16 numbers ([RTX Blackwell whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)). The 4090 figure 1321.2 is FP8 with FP16 accumulate, sparse; DERIVED reading.
- GeForce cards run FP32-accumulate Tensor operations at half the FP16-accumulate rate (RTX 5090 209.5 vs 419 TFLOPS dense). RTX PRO 6000 does not (FP16 with FP16 accumulate = FP16 with FP32 accumulate = 503.8) ([RTX Blackwell whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)). vLLM BF16 uses FP32 accumulate.
- The H100 whitepaper FP16 numbers (1000/2000 SXM) were "preliminary"; shipping datasheets say 989.5 dense / 1,979 sparse ([Hopper whitepaper mirror](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf)).

**Interpretation** (my inference)

- Before any number goes on a slide, label it D or S and name the accumulate type. A missing footnote can mean a 2x error.
- For BF16 inference with FP32 accumulate, the GeForce "AI TOPS" headline is far above the usable rate: RTX 4090 1321 versus 165.2 TFLOPS dense BF16 (8.0x, DERIVED), RTX 5090 3352 versus 209.5 (16.0x, DERIVED). The workshop GPU does not have the FP32-accumulate penalty.

**Workshop decision**

- All slides and `docs/METRICS.md` quote dense BF16 values and say "dense" next to them. Sparse figures appear only to explain why the vendor headline looks 2x larger.

### 6.2 Spec tables

#### Table A: compute and memory

| GPU | Arch / CC | Memory | BW (GB/s) | BF16/FP16 D (TFLOPS) | FP8 D | FP4 D | SMs | L2 |
|---|---|---|---|---|---|---|---|---|
| **RTX PRO 6000 Blackwell Server Edition (workshop GPU)** | Blackwell GB202 / 12.0 | 96 GB GDDR7 ECC, 512-bit | **1597** | ~500 [D] (page: "1 PFLOP", unlabelled) | ~1000 [D] | ~2000 [D] | 188 [D] (24,064 CUDA cores / 128) | 128 MB, Unverified: for Server |
| RTX PRO 6000 Workstation (600 W) | GB202 / 12.0 | 96 GB GDDR7 ECC, 512-bit | 1792 | 503.8 (S 1007.6) | 1007.6 (S 2015.2) | 2015.2 (S 4030.4) | 188 | 128 MB (131072 KB) |
| RTX PRO 6000 Max-Q (300 W) | GB202 / 12.0 | 96 GB GDDR7 ECC | 1792 | 438.9 (S 877.9) | 877.9 (S 1755.7) | 1755.7 (S 3511.4) | 188 | 128 MB |
| L4 | Ada AD104 / 8.9 | 24 GB GDDR6 ECC | 300 | 121 (S 242) | 242 (S 485) | n/a | 58 | 48 MB |
| L40S | Ada AD102 / 8.9 | 48 GB GDDR6 ECC | 864 | 362.05 (S 733) | 733 (S 1,466) | n/a | 142 [D] (18,176 / 128) | 96 MB, Unverified: for L40S (L40 = 98304 KB) |
| A100 80GB PCIe | Ampere GA100 / 8.0 | 80 GB HBM2e | 1,935 | 312 (S 624) | n/a | n/a | 108 | 40 MB |
| A100 80GB SXM | GA100 / 8.0 | 80 GB HBM2e | 2,039 | 312 (S 624) | n/a | n/a | 108 | 40 MB |
| H100 PCIe | Hopper GH100 / 9.0 | 80 GB HBM2e | 2,000 | 756.5 [D] (S 1,513) | 1,513 [D] (S 3,026) | n/a | 114 | 50 MB |
| H100 SXM5 | GH100 / 9.0 | 80 GB HBM3 | 3,350 | 989.5 [D] (S 1,979) | 1,979 [D] (S 3,958) | n/a | 132 | 50 MB |
| H100 NVL | GH100 / 9.0 | 94 GB HBM3 per GPU | 3,900 | 835.5 [D] (S 1,671) | 1,670.5 [D] (S 3,341) | n/a | Unverified | Unverified |
| H200 SXM | Hopper / 9.0 | 141 GB HBM3e | 4,800 | 989.5 [D] | 1,979 [D] | n/a | Unverified | Unverified |
| H200 NVL | Hopper / 9.0 | 141 GB HBM3e | 4,800 | 835.5 [D] | 1,670.5 [D] | n/a | Unverified | Unverified |
| B200 (HGX/DGX B200 GPU) | Blackwell / 10.0 | 180 GB HBM3e ("up to") | ~8,000 [D] (64 TB/s / 8) | 2,250 [D] (36 PFLOPS S / 8 / 2) | 4,500 [D] | 9,000 [D] | 148 | 126 MB, Unverified: stated for "GB200 GPU" |
| RTX 4090 | Ada AD102 / 8.9 | 24 GB GDDR6X, 384-bit | 1,008 | 165.2 FP32-acc (S 330.4); 330.3 FP16-acc | 330.3 FP32-acc / 660.6 FP16-acc | n/a | 128 | 72 MB |
| RTX 5090 | Blackwell GB202 / 12.0 | 32 GB GDDR7, 512-bit | 1,792 | 209.5 FP32-acc (S 419); 419 FP16-acc | 419 FP32-acc / 838 FP16-acc | 1,676 (S 3,352) | 170 | 96 MB |

#### Table B: platform

| GPU | Power | PCIe | NVLink | MIG |
|---|---|---|---|---|
| RTX PRO 6000 Server | "Up to 600 W (configurable)"; family page 400-600 W; passive | Gen5 x16 | No (Lenovo table reprinting NVIDIA specs; not listed by NVIDIA) | up to 4 @ 24 GB |
| RTX PRO 6000 Workstation | 600 W TBP; active | Gen5 x16 | Unverified: none (not listed) | up to 4 x 24 / 2 x 48 / 1 x 96 GB |
| RTX PRO 6000 Max-Q | 300 W TBP | Gen5 x16 | Unverified: none (not listed) | same profiles |
| L4 | 72 W | Gen4 x16, 64 GB/s | not listed | not in MIG list |
| L40S | 350 W | Gen4 x16, 64 GB/s bidirectional | No | No |
| A100 80GB PCIe / SXM | 300 W / 400 W (HGX up to 500 W) | Gen4, 64 GB/s | bridge for 2 GPUs 600 GB/s / NVLink 600 GB/s | up to 7 @ 10 GB |
| H100 PCIe | 300-350 W | Gen5, 128 GB/s | bridge 600 GB/s | up to 7 @ 10 GB |
| H100 SXM5 | up to 700 W | Gen5, 128 GB/s | NVLink 4: 900 GB/s | up to 7 @ 10 GB |
| H100 NVL | 350-400 W | Gen5, 128 GB/s | bridge 600 GB/s | up to 7 @ 12 GB |
| H200 SXM / NVL | up to 700 W / 600 W | Gen5, 128 GB/s | 900 GB/s | up to 7 @ 18 GB / 16.5 GB |
| B200 | Blackwell up to 1,200 W max; HGX B200 SKU Unverified (Lenovo title says 1000 W) | Gen6 (Blackwell Ultra blog table) | NVLink 5: 1.8 TB/s per GPU | up to 7 (180 GB part) |
| RTX 4090 / 5090 | 450 W / 575 W | Gen4 / Gen5 | No / No | not supported |

**Source facts**

- Server Edition datasheet (NVIDIA doc 3850600, Apr25, read from an Akamai-hosted copy because NVIDIA's `resources.nvidia.com` copy is password-protected) ([datasheet copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf)).
- Workstation and Max-Q rows come from the whitepaper Table 4 (boost 2617 MHz at 600 W; 2280 MHz at 300 W) ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)).
- L4 and L40S rows: ([NVIDIA L4](https://www.nvidia.com/en-us/data-center/l4/), [L4 Ada whitepaper v2.1](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf), [NVIDIA L40S](https://www.nvidia.com/en-us/data-center/l40s/)).
- A100 rows (dense | sparse* listed for both PCIe and SXM) ([A100 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf)).
- H100/H200 rows ([NVIDIA H100](https://www.nvidia.com/en-us/data-center/h100/), [NVIDIA H200](https://www.nvidia.com/en-us/data-center/h200/), [H100 PCIe product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/data-center/h100/PB-11133-001_v01.pdf), [PNY-hosted H100 datasheet](https://www.pny.com/file%20library/company/support/product%20brochures/nvidia%20data%20center%20gpus/nvidia-h100-datasheet.pdf)). The H200 page carries the footnote "Preliminary specifications. May be subject to change."
- B200 rows: per-GPU values are my division of the 8-GPU system numbers ([DGX B200](https://www.nvidia.com/en-us/data-center/dgx-b200/), [HGX](https://www.nvidia.com/en-us/data-center/hgx/)). 148 SMs: ([NVIDIA blog on CUDA MPS](https://developer.nvidia.com/blog/boost-gpu-memory-performance-with-no-code-changes-using-nvidia-cuda-mps/)).
- RTX 4090 and 5090 rows ([RTX Blackwell whitepaper Table 3](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf)).
- Compute capability: RTX PRO 6000 Blackwell 12.0, L4 and L40S 8.9, A100 8.0, H100 9.0, B200 10.0, RTX 4090 8.9, RTX 5090 12.0 ([CUDA GPUs](https://developer.nvidia.com/cuda-gpus)).
- Compute capability 12.0 (GB202) and 10.0 (B200) are different instruction targets: Blackwell `sm_100` and `sm_120` are first supported in CUDA 12.8 ([driver and architecture matrix](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html)).

**Caution:** B200 memory is 180 GB per GPU in HGX/DGX B200 (1,440 GB / 8), not 192 GB. 192 GB is the maximum in the Blackwell Ultra blog table, and its "Blackwell" column is the 1.2 kW maximum configuration, so its dense FP8 (5 PFLOPS) is higher than the 4.5 PFLOPS derived from HGX B200 ([DGX B200](https://www.nvidia.com/en-us/data-center/dgx-b200/), [Blackwell Ultra blog](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)).

**Caution:** The H100 PCIe product brief gives the NVLink bridge bandwidth as 600 GB/s in its Table 6 and as "900 GB/s bidirectional" in its overview text. Datasheets say 600 GB/s. Treat 600 GB/s as correct ([H100 PCIe product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/data-center/h100/PB-11133-001_v01.pdf)).

**Caution:** Runpod lists "NVIDIA H200 NVL" as 143 GB while NVIDIA says 141 GB ([Runpod GPU types](https://docs.runpod.io/references/gpu-types)).

**Interpretation** (my inference)

- On bandwidth alone the workshop GPU (1597 GB/s) sits between an A100 PCIe (1,935) and an RTX 4090 (1,008), and well below any HBM3 part. On capacity (96 GB) it exceeds every part in the table except H200 and B200. That combination (large capacity, mid bandwidth, GDDR7) is the reason model choice and quantization matter more on this card than on an H100.
- Unverified specs stay unverified: do not put L2 sizes for Server, L40S or B200, or SM counts for H100 NVL and H200, on a slide.

**Workshop decision**

- The workshop GPU is fixed in `config/workshop.yaml` (`gpu_class: "NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB)"`). Table A is reference material for the slides. `scripts/sizing.py` uses only the capacity, as `--gpu-gib` (default 96).

### 6.3 The workshop GPU in detail: RTX PRO 6000 Blackwell Server Edition

**Source facts**

- Datasheet spec table: 24,064 CUDA cores; 752 fifth-generation Tensor Cores; 188 fourth-generation RT cores; FP32 120 TFLOPS; "Peak FP4 AI PFLOPS 4 PFLOPS"; RT 355 TFLOPS; 96 GB GDDR7 with ECC; 512-bit; memory bandwidth 1597 GB/s; "Up to 600W (Configurable)"; "Up to 4 MIGs @ 24GB"; confidential compute supported; PCI Express 5.0 x16; 4.4" H x 10.5" L dual slot, passive; power connector 1x PCIe CEM5 16-pin ([datasheet copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf)).
- Datasheet prose: "96 GB of GPU memory and 1.6 TB/s bandwidth"; "PCIe Gen 5 ... double the bandwidth of PCIe Gen 4"; 4 NVENC (9th gen) and 4 NVDEC (6th gen) ([datasheet copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf)).
- Product page spec table: FP4 Tensor Core 4 PFLOPS, FP8 2 PFLOPS, FP16/BF16 1 PFLOP, TF32 234 TFLOPS, FP32 120 TFLOPS, RT 355 TFLOPS, memory 1597 GB/s. The page has no footnotes and does not say sparse or dense. Cooling variants: air "Dual-Slot, FHFL"; liquid "Single-Slot, FHXL" ([product page](https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/)).
- Family page: Server Edition power draw 400-600 W; Workstation 600 W; Max-Q 300 W; all PCIe Gen 5 x16; cooling Server passive, Workstation double flow-through, Max-Q active ([family page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/)).
- Lenovo's product guide (reprints NVIDIA specs): memory bandwidth "Up to 1597 GB/s"; TF32 234 (peak); FP16 1 PFLOPS (peak); BF16 1 PFLOPS (peak); FP8 2 PFLOPS (peak); FP4 4 PFLOPS (peak); "NVLink support: No" ([Lenovo LP2263](https://lenovopress.lenovo.com/lp2263.pdf)).
- Workstation Edition, same GB202 die, 28 Gbps GDDR7, 512-bit, 1792 GB/s; dense FP16 503.8, FP8 1007.6, FP4 2015.2 TFLOPS; sparse 1007.6 / 2015.2 / 4030.4; boost 2617 MHz at 600 W ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)). The Workstation datasheet's "4000 AI TOPS" carries the footnote "Theoretical FP4 TOPS using sparsity" ([Workstation datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf)).
- Per-SM and per-die resources for GB202 at 188 SMs: L1/shared 24,064 KB total (= 128 KB per SM), register file 48,128 KB (= 256 KB per SM), L2 131,072 KB (Workstation) ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)).
- Runpod GPU IDs: "NVIDIA RTX PRO 6000 Blackwell Server Edition" (96 GB), "... Server Edition MIG 1g.24gb" (24 GB), "... MIG 2g.48gb" (48 GB), "... Workstation Edition" (96 GB), "... Max-Q Workstation Edition" (96 GB) ([Runpod GPU types](https://docs.runpod.io/references/gpu-types)).

**Derived numbers**

- Pin rate: 1597 GB/s / 64 B (512-bit bus) = 24.95 Gbps per pin (DERIVED), against 1792 / 64 = 28.0 Gbps for the Workstation card (matches the whitepaper's 28 Gbps). The Server card is therefore 1597 / 1792 = 0.891 of the Workstation bandwidth (DERIVED), about 11 % lower.
- SM count: 24,064 / 128 = 188; 752 / 4 = 188 (DERIVED).
- Dense reading of the page numbers: FP16/BF16 about 1 PFLOP / 2 = ~500 TFLOPS; FP8 ~1000; FP4 ~2000 (DERIVED).

**FP16 "sparse" ambiguity (Unverified)**

- The product page lists FP4 4 PFLOPS, FP8 2 PFLOPS, FP16 1 PFLOP without any sparsity footnote. They match the Workstation whitepaper's SPARSE numbers (4030.4, 2015.2, 1007.6). The sparse reading is inferred from that exact match. Unverified: NVIDIA does not label the page's FP4/FP8/FP16 numbers as sparse.
- The page's TF32 234 TFLOPS is closer to a DENSE TF32 value (Workstation dense TF32 251.9; sparse 503.8). The page therefore mixes conventions, which is a second reason not to trust unlabelled numbers.
- NVIDIA states no boost clock for the Server Edition in any retrieved document. The page's RT figure is 355 TFLOPS against 381.8 for the Workstation (ratio 0.93), so the Server card may run lower clocks; dense FP16 may then be nearer 468 TFLOPS (503.8 x 0.93). Treat 468-504 TFLOPS as the plausible dense range (DERIVED, Unverified).

**Caution:** Bandwidth differs between family members. Any blog, benchmark or forum post that quotes "RTX PRO 6000, 96 GB, 1792 GB/s" is describing the Workstation or Max-Q card, not the Server Edition used here (1597 GB/s) ([datasheet copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf), [RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)).

**Caution:** The CUDA programming guide appendix extraction shows 100 KB max shared memory per SM for compute capability 12.x, while the Blackwell tuning guide says 128 KB shared capacity per SM and 99 KB max per block. The difference is probably combined-cache size versus carve-out; Unverified which reading the programming guide intends ([tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html), [compute capabilities appendix](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html)).

**Unverified items**

- Server Edition L2 (128 MB inferred from the identical GB202 configuration).
- NVLink on Workstation and Max-Q (not listed in either datasheet, no explicit "No" found).
- What `nvidia-smi` reports as total MiB for the 96 GB card (ECC reduces the total available memory per NVML text; needs hardware).
- Whether Tensor Memory (TMEM) exists on the CC 12.0 die; NVIDIA describes it only for datacenter Blackwell.
- A `1g.24gb` MIG slice is about 47 SMs (188 / 4) and about 400 GB/s (DERIVED, Unverified); NVIDIA gives no numeric per-profile SM or bandwidth figure for this card.

**Interpretation** (my inference)

- Teach the card as "a Blackwell GB202 with 96 GB, about 1.6 TB/s and roughly 500 TFLOPS dense BF16". It is memory-bandwidth-limited for single-stream decode and has plenty of compute for prefill.
- The 11 % bandwidth gap to the Workstation card is the number to remember when comparing against published RTX PRO 6000 benchmarks: decode throughput scales with bandwidth.

**Workshop decision**

- Participants measure on the Server Edition pods. `benchmark/infbench/sampler.py` records `utilization.gpu`, `memory.used`, `power.draw`, `temperature.gpu` and `clocks.sm` so a lower-than-expected result can be checked against clocks and power instead of being blamed on the datasheet.

### 6.4 Ops:byte (roofline ridge point) per GPU

**Source facts**

- NVIDIA defines the "ops:byte ratio" as the ratio of a processor's math bandwidth to its memory bandwidth. An algorithm whose arithmetic intensity is below it is memory-limited; above it, math-limited ([NVIDIA GPU performance background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html)).
- Total time = max(T_mem, T_math); T_mem = bytes accessed / memory bandwidth; T_math = operations / math bandwidth ([same guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html)).
- V100 reference: ops:byte "between 40 and 139" depending on L2 (3.1 TB/s) versus HBM (~900 GB/s), with 125 FP16 Tensor TFLOPS. Example (V100, FP16): linear layer batch 512 = 315 FLOPS/B (arithmetic-limited); batch 1 = 1 FLOPS/B (memory-limited) ([same guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html)).
- Matrix-vector products "are always memory limited; their arithmetic intensity is less than 1"; the comparison is "a simplified rule of thumb" ([NVIDIA matmul guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html)).

**DERIVED table** (ops:byte = TFLOPS x 1e12 / (GB/s x 1e9), FLOP per byte; dense BF16/FP16, FP32 accumulate unless noted)

| GPU | Dense BF16 (TFLOPS) | BW (GB/s) | Arithmetic | ops:byte |
|---|---|---|---|---|
| **RTX PRO 6000 Server, Workstation-clock case (workshop reference)** | 503.8 | 1597 | 503.8e12 / 1597e9 | **315.5** |
| RTX PRO 6000 Server, "1 PFLOP / 2" case | 500 | 1597 | 500e12 / 1597e9 | 313.1 |
| RTX PRO 6000 Server, lower-clock case (Unverified) | 468 | 1597 | 468e12 / 1597e9 | 293.0 |
| RTX PRO 6000 Workstation | 503.8 | 1792 | 503.8e12 / 1792e9 | 281.1 |
| RTX PRO 6000 Max-Q | 438.9 | 1792 | 438.9e12 / 1792e9 | 244.9 |
| L4 | 121 | 300 | 121e12 / 300e9 | 403.3 |
| L40S | 362.05 | 864 | 362.05e12 / 864e9 | 419.0 |
| A100 80GB PCIe | 312 | 1935 | 312e12 / 1935e9 | 161.2 |
| A100 80GB SXM | 312 | 2039 | 312e12 / 2039e9 | 153.0 |
| H100 PCIe | 756.5 | 2000 | (1513/2)e12 / 2000e9 | 378.2 |
| H100 SXM | 989.5 | 3350 | (1979/2)e12 / 3350e9 | 295.4 |
| H100 NVL | 835.5 | 3900 | (1671/2)e12 / 3900e9 | 214.2 |
| H200 SXM | 989.5 | 4800 | (1979/2)e12 / 4800e9 | 206.1 |
| B200 | 2250 | 8000 | 2250e12 / 8000e9 | 281.2 |
| RTX 4090 (FP32 acc, what BF16 vLLM uses) | 165.2 | 1008 | 165.2e12 / 1008e9 | 163.9 |
| RTX 4090 (FP16 acc, marketing) | 330.3 | 1008 | 330.3e12 / 1008e9 | 327.7 |
| RTX 5090 (FP32 acc) | 209.5 | 1792 | 209.5e12 / 1792e9 | 116.9 |
| RTX 5090 (FP16 acc, marketing) | 419 | 1792 | 419e12 / 1792e9 | 233.8 |
| Rubin GPU (context; NVIDIA labels FP16/BF16 "Dense specification") | 4000 | 19200 | 4000e12 / 19200e9 | 208.3 |

The first row's 315.5 is my arithmetic (503.8 / 1.597) added for the workshop decision; the other rows are the research agent's.

- FP8 ops:byte is 2x the FP16 value and FP4 is 4x on Blackwell parts with 2x/4x dense Tensor rates. Workstation example: FP8 1007.6e12 / 1792e9 = 562; FP4 2015.2e12 / 1792e9 = 1,125 (DERIVED).
- Decode GEMM arithmetic intensity at batch B with b bytes per parameter = 2B / b FLOP/B (DERIVED). BF16 (b = 2) gives B; FP8 (b = 1) gives 2B; NVFP4 (b about 0.5625) gives about 3.6B. BF16 weight-read decode therefore stays memory-bound until B is about the ops:byte value (roughly 150-420 tokens in flight per step depending on GPU), ignoring KV reads, attention and overheads.
- Peak numbers only; achieved numbers are lower. Unverified: typical efficiency (not sourced).

**Interpretation** (my inference)

- A lower ops:byte (A100, H200) means the GPU becomes compute-bound at smaller batches; a high ops:byte (L4, L40S) means memory-bound decode persists to larger batches. For the workshop GPU the crossover for BF16 weights is around 315 tokens in flight per step, far above the 8 sequences of the `max-seqs-8` profile, so by this arithmetic decode at such batch sizes is memory-bound (prefill is a separate, compute-heavy phase).
- FP8 weights halve the bytes per token and so move the memory-bound region, they do not change the ridge point of the hardware.

**Workshop decision**

- Slides use the 315.5 FLOP/B figure (rounded "about 315") for the workshop GPU and show the other GPUs from the table in one comparison slide. `docs/METRICS.md` states that ops:byte is a hardware property and the arithmetic is shown with the batch-size consequence above.

### 6.5 GPU memory hierarchy

**Source facts**

- "The GPU is ... a collection of Streaming Multiprocessors (SMs) which are organized into groups called Graphics Processing Clusters (GPCs). Each SM contains a local register file, a unified data cache, and a number of functional units that perform computations." Threads form warps of 32 and run SIMT; registers hold thread-local values; shared memory is visible to a thread block or cluster; each SM has an L1 as part of the unified data cache; a larger L2 is shared by all SMs; the attached DRAM is "global memory" ([CUDA programming guide](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html)).
- Tensor Cores are "specialized high-performance compute cores for matrix multiply and accumulate (MMA) math operations"; introduced in Tesla V100; the H100 SM has 128 FP32 CUDA cores and 4 fourth-generation Tensor Cores ([Hopper whitepaper mirror](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf)).
- Volta: V100 has 640 Tensor Cores (8 per SM), each 64 FMAs per clock, 125 Tensor TFLOPS, 900 GB/s HBM2 (16 GB) ([Volta whitepaper v1.1](https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf)).
- Occupancy limits (CC 8.0/9.0/10.0): 32 threads/warp, 64 warps/SM, 2048 threads/SM, 32 blocks/SM, 65,536 32-bit registers/SM, max 255 registers/thread, 1024 threads/block; CC 12.0: 48 warps/SM ([Hopper whitepaper](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf), [Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html)).

| Level (H100 SXM5) | Size | Bandwidth | Scope |
|---|---|---|---|
| Registers | 256 KB per SM (65,536 x 32-bit); 33,792 KB total (132 SMs) | not published by NVIDIA | per thread / SM |
| L1 + shared memory (unified) | 256 KB per SM; shared configurable up to 228 KB (227 KB per block) | only per-bank rate: 32 banks x 32 bits/clock = 128 B/clock/SM | per SM |
| L2 | 50 MB (full GH100 60 MB) | not published for H100 | all SMs |
| HBM3 (global memory) | 80 GB | 3.35 TB/s (datasheet); whitepaper "over 3 TB/s" | all SMs |

- H100 SXM5: 5 active HBM3 stacks, ten 512-bit controllers (5,120-bit bus); HBM and L2 "support data compression and decompression technology" ([Hopper whitepaper](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf)). The Hopper tuning guide notes inline compression does not reduce footprint ([Hopper tuning guide](https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html)).
- Supported shared-memory capacities on H100 and B200: 0, 8, 16, 32, 64, 100, 132, 164, 196 and 228 KB per SM; one block can address up to 227 KB; static allocations stay limited to 48 KB ([Hopper tuning guide](https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html), [Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html)).
- Hopper adds the Tensor Memory Accelerator, thread block clusters (up to 16 blocks, non-portable; 8 portable) and distributed shared memory ([Hopper in depth](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)).
- A100 for comparison: shared up to 164 KB/SM, combined L1+shared 192 KB/SM, L2 40 MB ([Hopper whitepaper](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf)). Shared memory has 32 banks of 32 bits per clock ([CUDA C best practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html)).
- B200 (CC 10.0): 64K 32-bit registers per SM (256 KB), 256 KB combined L1/texture/shared, up to 228 KB shared, 128 CUDA cores, 4 fifth-gen Tensor Cores and 256 KB Tensor Memory (TMEM) per SM; L2 126 MB (stated for "GB200 GPU"); HBM3e up to 180 GB ([Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html), [Blackwell Ultra blog](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)).
- GB202 full chip: 192 SMs, 24,576 KB L1, 49,152 KB register file, 131,072 KB L2; the RTX PRO 6000 enables 188 SMs ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf)).
- The Hopper tuning guide says only qualitatively that "the bandwidth of the L2 cache to the SMs is also increased"; it gives no numeric L2 or shared-memory bandwidth ([Hopper tuning guide](https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html)).
- DERIVED: peak shared-memory bandwidth = 128 B/clk/SM x SMs x clock; H100 PCIe (114 SMs, 1,755 MHz boost) = 114 x 128 x 1.755e9 = 25.6 TB/s aggregate (peak, conflict-free, assumes the 32-bank x 4 B rule holds on Hopper).
- Unverified: any NVIDIA-published L2 bandwidth for H100. The only on-chip L2 figure retrieved is V100's 3.1 TB/s.

**Interpretation** (my inference)

- Teach four levels: registers, shared/L1 (per SM, tens to hundreds of KB), L2 (tens to 128 MB, shared), global memory (96 GB here). Decode reads every weight from global memory once per step; the caches are far too small to hold 16 GB of weights, which is why the roofline uses DRAM bytes.
- GB202's L2 (131,072 KB, the Workstation figure) is larger than H100's 50 MB, but both are orders of magnitude below 16 GB of weights, so the weight-read argument does not change.

**Workshop decision**

- The memory hierarchy is taught as a one-slide diagram with the H100 numbers above and the GB202 per-SM numbers (128 KB L1/shared, 256 KB registers). No bandwidth figure for L1 or L2 appears, because NVIDIA does not publish one.

### 6.6 NVLink versus PCIe

**Source facts**

- NVLink generations: 4th gen (Hopper) 900 GB/s per GPU, 18 links, domain 8 GPUs; 5th gen (Blackwell) 1,800 GB/s, 18 links, domain 8 or 72; 6th gen (Vera Rubin) 3,000 GB/s, 36 links. Footnote: "Preliminary specifications; may be subject to change." ([NVLink page](https://www.nvidia.com/en-us/data-center/nvlink/)).
- NVIDIA states NVLink bandwidth as bidirectional: Hopper "900GB/s of bidirectional bandwidth per GPU"; Blackwell "1.8TB/s bidirectional throughput per GPU" ([Hopper page](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/), [Blackwell press release](https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Blackwell-Platform-Arrives-to-Power-a-New-Era-of-Computing/default.aspx)). NVLink 5 is 18 links x 100 GB/s ([Blackwell Ultra blog](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)).
- A100 NVLink 3 = 600 GB/s total (V100 300 GB/s) ([Ampere in depth](https://developer.nvidia.com/blog/nvidia-ampere-architecture-in-depth/)).
- PCIe as listed in NVIDIA datasheets: Gen4 x16 "64 GB/s" (L40S says "64 GB/s bidirectional"); Gen5 "128 GB/s" (H100/H200); Gen6 256 GB/s ([L4](https://www.nvidia.com/en-us/data-center/l4/), [L40S](https://www.nvidia.com/en-us/data-center/l40s/), [H100](https://www.nvidia.com/en-us/data-center/h100/), [Blackwell Ultra blog](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)).
- The RTX PRO 6000 datasheet: "PCIe Gen 5 provides double the bandwidth of PCIe Gen 4" ([datasheet copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf)).
- H100 PCIe: three NVLink bridges link two cards, 600 GB/s; H200 NVL 900 GB/s per GPU with a 2- or 4-way bridge ([H100 PCIe product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/data-center/h100/PB-11133-001_v01.pdf), [H200](https://www.nvidia.com/en-us/data-center/h200/)).
- `nvidia-smi topo -m` "Displays a matrix of connections between all GPUs and NICs ... along with CPU/memory affinities". Legend: `X` = self; `SYS` = PCIe plus the SMP interconnect between NUMA nodes; `NODE` = PCIe plus the interconnect between PCIe host bridges within a NUMA node; `PHB` = PCIe plus a host bridge (typically the CPU); `PXB` = multiple PCIe switches without the host bridge; `PIX` = a single PCIe switch; `NV#` = a bonded set of # NVLinks ([nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html)).

**Derived**

- Per-direction NVLink = half the bidirectional figure: NVLink 4 = 450 GB/s, NVLink 5 = 900 GB/s. PCIe x16 per direction: Gen4 32 GB/s, Gen5 64 GB/s, Gen6 128 GB/s. Raw-rate cross-check: 16 GT/s x 16 lanes x 128/130 / 8 = 31.5 GB/s (Gen4); 32 GT/s gives 63.0 GB/s (Gen5). Unverified against PCI-SIG (pages not reachable); assumes 128b/130b encoding.
- NVLink 4 (900) versus PCIe Gen5 (128) = 7.0x (NVIDIA's zhCN H100 datasheet says "7x PCIe 5.0"); NVLink 5 (1,800) versus PCIe Gen5 = 14.1x; NVIDIA says 6th-gen NVLink is "12x the bandwidth of PCIe Gen6" (3,000 / 256 = 11.7x) ([zhCN H100 datasheet](https://images.nvidia.cn/aem-dam/en-zz/Solutions/data-center/h100/nvidia-h100-datasheet-nvidia-a4-2287922-r7-zhCN.pdf), [NVLink page](https://www.nvidia.com/en-us/data-center/nvlink/)).
- RTX PRO 6000 (Server/Workstation), L4, L40S and RTX 4090/5090 have no NVLink, so tensor-parallel all-reduce traffic between such cards goes over PCIe Gen5 x16 (64 GB/s per direction) or Gen4 (32 GB/s), versus 450 GB/s per direction on H100 NVLink 4. Whether peer-to-peer is enabled depends on platform topology (Unverified for specific servers).
- A fully connected HGX H100 board should show `NV18` between every GPU pair; an RTX PRO 6000 server shows only PIX/PXB/PHB/NODE/SYS. Ordering NV# > PIX > PXB > PHB > NODE > SYS is inferred from the legend wording (Unverified as an NVIDIA statement).

**Caution:** NVIDIA quotes NVLink bidirectionally, but PCIe in the same tables sometimes as per-direction-doubled (Gen5 "128 GB/s") and sometimes labelled "bidirectional" (L40S Gen4 "64 GB/s bidirectional"). Compare like with like: halve both for per-direction numbers.

**Interpretation** (my inference)

- A 7x (Hopper) to 14x (Blackwell datacenter) bandwidth gap is why tensor parallelism across RTX PRO 6000 cards is a trade-off, not a free way to add memory. Tensor parallelism needs all-reduce traffic between the GPUs during every forward pass; over PCIe this can become the bottleneck. This is my inference; the notes give the bandwidth numbers, not a measurement.
- The PCIe placement of GPUs in a multi-GPU RTX PRO 6000 pod is Unverified; `nvidia-smi topo -m` after launch is the way to find out.

**Workshop decision**

- The two-GPU profile `config/vllm-profiles/tp2.yaml` is presented as a measured trade-off, not as a scaling recipe. Run `nvidia-smi topo -m` on the pod before using it and keep the output next to the benchmark result in `benchmark/results/`.

### 6.7 `nvidia-smi`, NVML and what GPU-Util measures

**Source facts**

- `nvidia-smi --query-gpu=<props> --format=csv` takes a comma-separated property list; `--format` is mandatory; add `noheader,nounits`; `-l <sec>` loops; `-f <file>` redirects. NVIDIA's example: `nvidia-smi --query-gpu=index,timestamp,power.draw,clocks.sm,clocks.mem,clocks.gr --format=csv -l 1`. Unverified in the retrieved docs: `nvidia-smi --help-query-gpu` lists valid fields ([NVIDIA support article](https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries), [nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html)).
- `utilization.gpu` = "Percent of time over the past sample period during which one or more kernels was executing on the GPU". `utilization.memory` = "Percent of time over the past sample period during which global (device) memory was being read or written". `memory.used` = "Total memory allocated by active contexts" ([NVIDIA support article](https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries)).
- NVML `nvmlUtilization_t` uses the same two definitions for `gpu` and `memory` ([NVML struct](https://docs.nvidia.com/deploy/nvml-api/api/structnvmlUtilization__t.html)). Unverified wording: "Each sample period may be between 1 second and 1/6 second, depending on the product being queried" (seen in a search excerpt only).
- With ECC enabled, high utilization readings can appear at driver initialization from ECC memory scrubbing; on MIG-enabled GPUs querying utilization is not supported ([NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html)). nvidia-smi says the same for encoder, decoder, jpeg, ofa, gpu and memory utilization ([nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html)).
- DCGM profiling definitions: `PROF_GR_ENGINE_ACTIVE` "fraction of time any portion of the graphics or compute engines were active"; `PROF_SM_ACTIVE` "fraction of time at least one warp was active on a multiprocessor, averaged over all multiprocessors"; `PROF_SM_OCCUPANCY` "fraction of resident warps on a multiprocessor, relative to the maximum number of concurrent warps"; `PROF_PIPE_TENSOR_ACTIVE` "fraction of cycles the tensor (HMMA / IMMA) pipe was active"; `PROF_DRAM_ACTIVE` "fraction of cycles where data was sent to or received from device memory". "Note that 'active' does not necessarily mean a warp is actively computing"; SM_ACTIVE of 0.8 or greater "is necessary, but not sufficient, for effective use of the GPU"; below 0.5 "likely indicates ineffective GPU usage" ([DCGM feature overview](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html)).
- NVML memory: `used` = "Sum of Reserved and Allocated device memory"; "the driver/GPU always sets aside a small amount of memory for bookkeeping"; total = free + used ([NVML memory struct](https://docs.nvidia.com/deploy/nvml-api/api/structnvmlMemory__t.html)). The v2 call accounts reserved memory separately and includes it in used ([NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html)).
- `nvidia-smi dmon` default metrics: power, temperature, SM and memory clocks, and utilization of SM, memory, encoder, decoder, JPEG and OFA; `-s` selects groups (`u` utilization, `e` ECC/PCIe replay errors); `-f`, `-c` available. `nvidia-smi pmon` monitors processes, with `-s u` and `-s m` groups ([nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html)). NVIDIA's TensorRT docs recommend running `nvidia-smi dmon -s pcu -f <FILE> -c <COUNT>` next to every benchmark ([TensorRT benchmarking](https://docs.nvidia.com/deeplearning/tensorrt/11.4.0/performance/benchmarking.html)).
- `nvmlDeviceGetPowerUsage` returns milliwatts for the GPU "and its associated circuitry (e.g. memory)"; on Ampere (except GA100) and newer it is averaged over 1 s ([NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html)).
- `nvidia-ml-py` 13.615.71 (released Sep 25, 2026), module `pynvml`: `nvmlInit`, `nvmlDeviceGetHandleByIndex`, `nvmlDeviceGetUtilizationRates` (`.gpu`, `.memory`), `nvmlDeviceGetMemoryInfo` (`.total/.free/.used`), `nvmlDeviceGetPowerUsage` (milliwatts), `nvmlDeviceGetTemperature` (NVML marks it deprecated in favour of `nvmlDeviceGetTemperatureV`), `nvmlDeviceGetClockInfo(handle, NVML_CLOCK_SM | NVML_CLOCK_MEM | NVML_CLOCK_GRAPHICS)`, `nvmlDeviceGetCurrentClocksEventReasons` (bitmask, e.g. `nvmlClocksEventReasonSwPowerCap = 0x4`, `nvmlClocksEventReasonHwSlowdown = 0x8`, `nvmlClocksEventReasonSwThermalSlowdown = 0x20`, `nvmlClocksEventReasonHwThermalSlowdown = 0x40`) ([PyPI nvidia-ml-py](https://pypi.org/project/nvidia-ml-py/)).

**Interpretation** (my inference)

- `utilization.gpu` is a time fraction ("at least one kernel resident"). It says nothing about how many SMs, warps, tensor pipes or memory channels are busy. A single-block kernel can read 100 %. It is a liveness signal, not an efficiency measure. NVIDIA's own DCGM text (SM_ACTIVE 0.8 is "necessary, but not sufficient") supports this.
- For memory-bound decode the informative pair is `DCGM_FI_PROF_DRAM_ACTIVE` high and `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE` low. `memory.used` is high immediately after vLLM starts because vLLM pre-allocates the KV cache pool; it also includes the CUDA context, the PyTorch caching allocator and driver-reserved memory, so it is much more than the weights.
- The right efficiency numbers come from the engine: tokens per second against the bandwidth bound in section 6.10, and the KV-cache usage metric.

**Workshop decision**

- `monitoring/gpu-exporter/exporter.py` documents `DCGM_FI_DEV_GPU_UTIL` as "percent of time a kernel was running (NOT efficiency)" and exports the NVML-derived set (GPU_UTIL, MEM_COPY_UTIL, FB_USED, FB_FREE, POWER_USAGE, GPU_TEMP, SM_CLOCK, MEM_CLOCK) under DCGM names. `docs/METRICS.md` never presents GPU-Util as efficiency; efficiency is judged from engine metrics and the bandwidth bound in section 6.10.

### 6.8 CUDA, driver compatibility and the container toolkit

**Source facts**

- Latest toolkit on the release-notes page: CUDA 13.4 Update 2. Toolkit to driver branch: 13.4 R615; 13.3 R610; 13.2 R595; 13.1 R590; 13.0 R580. "CUDA 13.4 new features and newly enabled platforms require an R615 or later driver." ([CUDA release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)).
- Minor-version compatibility: 13.x needs driver >= 580 (no upper bound); 12.x >= 525 and < 580; 11.x >= 450 and < 525 ([CUDA release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html), [minor-version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)).
- CUDA 12.9 and earlier minimum drivers (Linux x86_64): 12.9 Update 1 >= 575.57.08; 12.9 GA >= 575.51.03; 12.8 Update 1 >= 570.124.06; 12.8 GA >= 570.26; 12.6 Update 3 >= 560.35.05; 12.4 Update 1 >= 550.54.15 ([CUDA release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)).
- "The NVIDIA driver is no longer bundled with the CUDA Toolkit" (Windows from CUDA 13.1, Linux from CUDA 13.4) ([CUDA release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)).
- Minor-version compatibility limits: features spanning toolkit and driver can fail with `cudaErrorCallRequiresNewerDriver`; "Applications that compile device code to PTX will not work on older drivers"; pass an explicit target architecture to NVCC (e.g. `nvcc -arch=sm_xx`) ([minor-version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)).
- Forward compatibility (since CUDA 10.0): supported products are "NVIDIA Data Center GPUs", "Select NGC Server Ready SKUs of RTX cards" and Jetson; package `cuda-compat-<major>-<minor>` installs to `/usr/local/cuda-13.4/compat/` and requires `LD_LIBRARY_PATH` to include that directory; error codes `CUDA_ERROR_SYSTEM_DRIVER_MISMATCH = 803` and `CUDA_ERROR_COMPAT_NOT_SUPPORTED_ON_DEVICE = 804` ([forward compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html)).
- "when using tools such as `nvidia-smi`, the NVIDIA driver reports a maximum version of CUDA supported" ([driver and architecture matrix](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html)). First CUDA support: Blackwell CC 10.0 and 12.0 CUDA 12.8; Hopper 9.0 CUDA 11.8; Ada 8.9 CUDA 11.8; Ampere 8.0/8.6 CUDA 11.0 (same page).
- Container Toolkit: prerequisite is the host GPU driver; configure Docker with `sudo nvidia-ctk runtime configure --runtime=docker` then restart Docker; verify with `sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi` ([install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), [sample workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html)).
- GPU selection: `--gpus all`, `--gpus 2`, `--gpus '"device=1,2"'`; `NVIDIA_VISIBLE_DEVICES` accepts index/UUID list, `all`, `none`, `void`; `NVIDIA_DRIVER_CAPABILITIES` defaults to `utility,compute` and setting it REPLACES the defaults (`utility` = nvidia-smi and NVML) ([docker specialized configurations](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html)).
- Compose GPU reservation: `deploy.resources.reservations.devices` with `driver: nvidia`, `count` or `device_ids` (mutually exclusive), and mandatory `capabilities: [gpu]` ([Docker Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/)).

**Unverified**

- The exact CUDA 13.0 GA minimum build (the release notes give only "R580 / >= 580"; the compat doc's sample shows driver 580.65.06 with "CUDA Version: 13.0", which is sample output, not a requirement).
- Whether the RTX PRO 6000 Blackwell Server Edition counts as a "Select NGC Server Ready SKU" for forward compatibility.
- The exact mechanism that injects the host's `libcuda.so` and NVML into containers (not stated in the retrieved pages).

**Interpretation** (my inference)

- `nvidia-smi`'s "CUDA Version" is the highest CUDA the installed DRIVER supports, not the installed toolkit. The container's own CUDA libraries are separate; `torch.version.cuda` or `nvcc --version` shows what the framework uses. A CUDA 13 container on a driver below R580 fails unless forward compatibility applies. This is the first thing to check when a vLLM image refuses to start on a fresh pod.
- On a rented pod the driver belongs to the provider, so the host CUDA version is a placement property, not something the participant installs. Runpod exposes this as a `gpu.minCudaVersion` field (see section 7.9).

**Workshop decision**

- The engine image is `vllm/vllm-openai:v0.31.0` pinned by digest in `infra/versions.env`. When creating pods, set the Runpod CUDA floor (`gpu.minCudaVersion`, section 7.9) so the host driver satisfies the image. As a first troubleshooting step in `docs/SETUP.md`, compare the driver ceiling shown by `nvidia-smi` with the CUDA version of the image before debugging anything else.

### 6.9 DCGM exporter

**Source facts**

- Latest GitHub release `4.8.4`, published 2026-09-18 (tested with DCGM 4.6.1, go-dcgm v1.4611.2, Go 1.27.1); previous `4.6.0-4.8.3` (2026-07-15), `4.5.3-4.8.2` (2026-05-07), `4.5.2-4.8.1` (2026-02-09), `4.5.1-4.8.0` (2026-01-28) ([dcgm-exporter 4.8.4](https://github.com/NVIDIA/dcgm-exporter/releases/tag/4.8.4)).
- Image repo `nvcr.io/nvidia/k8s/dcgm-exporter` tags (queried 2026-10-14): `latest`, `4.8.4`, `4.6.1-4.8.4`, `4.6.1-4.8.4-distroless`, `4.6.0-4.8.3-distroless`, and older `<dcgm-version>-<exporter-version>-<variant>` with variants ubuntu22.04 / ubi9 / distroless ([nvcr.io tag list](https://nvcr.io/v2/nvidia/k8s/dcgm-exporter/tags/list)).
- Standalone run from NVIDIA docs: `docker run -d --rm --name dcgm-exporter --gpus all --cap-add SYS_ADMIN -p 9400:9400 nvcr.io/nvidia/k8s/dcgm-exporter:${DCGM_EXPORTER_TAG}`; verify with `curl --fail http://localhost:9400/metrics`. Docs recommend a semantic-version tag for controlled upgrades and the DCGM version paired with that exporter release. `DCGM_FI_PROF_*` fields need GPU support and the `SYS_ADMIN` capability ([install DCGM exporter](https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html)).
- Helm: `helm repo add gpu-helm-charts https://nvidia.github.io/dcgm-exporter/helm-charts`, `helm install dcgm-exporter gpu-helm-charts/dcgm-exporter --namespace gpu-monitoring --create-namespace`; the chart enables a ServiceMonitor by default (`--set serviceMonitor.enabled=false` without Prometheus Operator CRDs); GPU nodes tainted `nvidia.com/gpu:NoSchedule` need a toleration ([install DCGM exporter](https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html), [deployment README](https://github.com/NVIDIA/dcgm-exporter/blob/main/deployment/README.md)). The GPU Operator also deploys the exporter ([GPU Operator overview](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html)).
- Default CSV, enabled fields: `DCGM_FI_DEV_SM_CLOCK`, `DCGM_FI_DEV_MEM_CLOCK`, `DCGM_FI_DEV_MEMORY_TEMP`, `DCGM_FI_DEV_GPU_TEMP`, `DCGM_FI_DEV_POWER_USAGE` (W), `DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION` (mJ counter), `DCGM_FI_DEV_PCIE_REPLAY_COUNTER`, `DCGM_FI_DEV_GPU_UTIL` (%), `DCGM_FI_DEV_MEM_COPY_UTIL` (%), `DCGM_FI_DEV_ENC_UTIL`, `DCGM_FI_DEV_DEC_UTIL`, `DCGM_FI_DEV_XID_ERRORS`, `DCGM_FI_DEV_FB_FREE`, `DCGM_FI_DEV_FB_USED`, `DCGM_FI_DEV_FB_RESERVED` (MiB), `DCGM_FI_DEV_NVLINK_BANDWIDTH_TOTAL`, row-remap fields, and the profiling set `DCGM_FI_PROF_GR_ENGINE_ACTIVE`, `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE`, `DCGM_FI_PROF_DRAM_ACTIVE`, `DCGM_FI_PROF_PCIE_TX_BYTES`, `DCGM_FI_PROF_PCIE_RX_BYTES` ([default-counters.csv](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/etc/default-counters.csv)).
- Commented out (opt-in): `DCGM_FI_PROF_SM_ACTIVE`, `DCGM_FI_PROF_SM_OCCUPANCY`, `DCGM_FI_PROF_PIPE_FP64/FP32/FP16_ACTIVE`, the power/thermal violation counters (`DCGM_FI_DEV_POWER_VIOLATION`, `DCGM_FI_DEV_THERMAL_VIOLATION`), `DCGM_FI_DEV_POWER_MGMT_LIMIT`, `DCGM_FI_DEV_ENFORCED_POWER_LIMIT`, ECC counters. The CSV says DCP metrics are "supported on Nvidia datacenter Volta GPUs and newer" ([default-counters.csv](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/etc/default-counters.csv)).
- Profiling needs privileges: "Profiling of the GPU counters requires administrator privileges starting with Linux drivers 418.43 or later"; DCGM profiling "will conflict with usage of other developer tools from NVIDIA" (`dcgmi profile --pause` / `--resume`) ([DCGM feature overview](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html)). The kernel module option `NVreg_RestrictProfilingToAdminUsers` (1 = admin only, `CAP_SYS_ADMIN` or `CAP_PERFMON`) controls access; containers need `--cap-add=SYS_ADMIN` ([NVIDIA permission doc](https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters)).
- dcgm-exporter 4.8.4 notes: opt-in exporter metrics (`--enable-exporter-metrics`), MIG compute-instance fields with a `GPU_CI_ID` label, restart required after live MIG creation or removal, retired PCIe throughput fields replaced by `DCGM_FI_PROF_PCIE_TX_BYTES` / `RX_BYTES` ([dcgm-exporter 4.8.4](https://github.com/NVIDIA/dcgm-exporter/releases/tag/4.8.4)).
- Unverified: whether `DCGM_FI_PROF_*` metrics are exposed for the RTX PRO 6000 Server Edition and for MIG slices (no support matrix retrieved). Unverified: whether `latest` on nvcr.io points at `4.6.1-4.8.4`. Unverified: a ready-made NVIDIA docker-compose pattern (none found; a Compose equivalent is DERIVED from `docker run` plus the Compose GPU docs, with `count: all` not verified in the retrieved Compose page).

**Caution:** NVIDIA's DCGM release-notes page still lists `4.6.0-4.8.3` as latest while GitHub and nvcr.io show `4.8.4`. The older "GPU telemetry" exporter page is stale (`DCGM_EXPORTER_VERSION=2.1.4-2.3.1`, `--net host`, `-f /etc/dcgm-exporter/dcp-metrics-included.csv`); use the install page for commands ([release notes](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/dcgm-exporter.html), [stale page](https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/latest/dcgm-exporter.html)).

**Interpretation** (my inference)

- The exporter's default profile already contains the two metrics that matter for decode (`PROF_DRAM_ACTIVE`, `PROF_PIPE_TENSOR_ACTIVE`). They require `SYS_ADMIN`, which a rented container may not grant. Unverified: Runpod notes assume Pods are not privileged, so DCP metrics are expected to be unavailable there, while plain NVML reads work.

**Workshop decision**

- `monitoring/docker-compose.yml` is the reference stack with dcgm-exporter (for participants' own hardware or Kubernetes). On pods, Prometheus, Grafana and the NVML exporter in `monitoring/gpu-exporter/exporter.py` run as plain processes and emit the same `DCGM_FI_DEV_*` names, so panels written against those names work on both. Where dcgm-exporter is used, pin a semantic-version tag, never `latest`.

### 6.10 Roofline model and why decode is memory-bound

**Source facts**

- Roofline: Samuel Williams, Andrew Waterman, David Patterson, "Roofline: An Insightful Visual Performance Model for Multicore Architectures", Communications of the ACM 52(4), April 2009 (DOI 10.1145/1498765.1498785); original Berkeley tech report UCB/EECS-2008-134, 17 Oct 2008 ([UCB/EECS-2008-134](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.html)). Unverified: CACM page range (65-76 vs 65-77; the ACM page returned HTTP 403).
- Core equation: "Attainable GFlops/sec = Min(Peak Floating Point Performance, Peak Memory Bandwidth x Operational Intensity)". X axis is operational intensity (flops per DRAM byte); the "ridge point, where the diagonal and horizontal roofs meet" has an x-coordinate equal to "the minimum operational intensity required to achieve maximum performance". The paper says "operational intensity" (flops per byte of DRAM traffic after caches), not "arithmetic intensity" ([tech report PDF](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf)).
- NVIDIA: arithmetic intensity = operations / bytes accessed; a kernel can still be latency-bound if parallelism is low (one thread, 16 bytes, 16,000 ops = 1000 FLOPS/B yet severely under-utilizes the GPU) ([GPU performance background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html)). GEMM intensity = (2MNK) / (2(MK + NK + MN)); compare it with ops:byte ([matmul guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html)).
- Pope et al. (Google), "Efficiently Scaling Transformer Inference", arXiv:2211.05102 (v1, 9 Nov 2022): "An N-parameter decoder-only model requires 2N matmul FLOPs in the forward pass per token seen". Section 2.1 "Memory costs": weights and the KV cache "need to be transferred from HBM to the compute cores of the chip once per forward pass (prefill or decode step) of the model. This takes a certain amount of time, which we call the 'memory time.' At small batch sizes and sequence lengths, the time to load weights dominates. At larger batch sizes and sequence lengths (e.g. 2048+ tokens with batch size 512+), the time to load the KV cache dominates." ([arXiv 2211.05102](https://arxiv.org/abs/2211.05102)).
- Same paper: with batch 512 and context 2048 the KV cache is 3 TB, 3x the model's parameters; int8 weights reach 28.5 ms/token versus 36.9 ms/token with bfloat16 at batch 64 on PaLM 540B; "At low latency targets the cost is improved just over a factor of 2, because low-batch-size cost is dominated by weight loading time" ([arXiv PDF](https://arxiv.org/pdf/2211.05102)).
- NVIDIA, "Mastering LLM Techniques: Inference Optimization": decode transfer speed "of data (weights, keys, values, activations) ... dominates the latency"; decode is "like a matrix-vector operation that underutilizes the GPU compute ability compared to the prefill phase"; "Model execution is frequently memory-bandwidth bound - in particular, bandwidth-bound in the weights"; prefill is "a matrix-matrix operation" that "effectively saturates GPU utilization". KV cache per token in bytes = 2 *(num_layers)* (num_heads *dim_head)* precision_in_bytes ([NVIDIA blog](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)). The blog has no latency equation, no MBU numbers and no worked H100 example.

**Derived** (the practical rule)

- One decode step reads every weight once and the KV cache of every sequence in the batch once:
  `t_step >= (W_bytes + KV_bytes) / BW_mem`, with `W_bytes = N_params x bytes_per_param` and `KV_bytes = sum over the B sequences of context_len x (2 x n_layers x n_kv_heads x head_dim x bytes_per_elem)`.
- One step emits one token per sequence, so per-sequence tokens/s <= BW / (W_bytes + KV_bytes) and aggregate tokens/s <= B x BW / (W_bytes + KV_bytes). With grouped-query attention use n_kv_heads, not NVIDIA's num_heads. For mixture-of-experts only the experts hit by the batch are read (Unverified nuance). The equation restates Pope et al.'s "memory time".
- **Practical rule: per-token decode time lower bound is approximately bytes read per token divided by memory bandwidth.**

**Worked example (DERIVED, theoretical lower bound at batch size 1, ignoring KV reads, attention, kernel launch and scheduler overheads)**

- Qwen3-8B in BF16, weights 16.38 GB (the byte count supplied for this section; the research notes use "about 16 GB" for 8B BF16 and cite no source for the byte count, so check it against `scripts/sizing.py` and `config/models.yaml`).
- Workshop GPU: 16.38e9 B / 1597e9 B/s = 10.26 ms per step, i.e. an upper bound of 1597 / 16.38 = **about 97.5 tokens/s** for one sequence. Real engines reach a fraction of this (Unverified: commonly 60-85 % of peak bandwidth; no primary source retrieved).
- Same arithmetic on the Workstation card: 16.38e9 / 1792e9 = 9.14 ms, about 109 tokens/s (DERIVED).
- With FP8 weights (b = 1 byte per parameter, roughly half the bytes), the bound roughly doubles to about 195 tokens/s (DERIVED, ignores scale tensors and any layers kept in BF16).
- Batch effect: the step time stays near 10 ms while the weight read dominates, so aggregate throughput scales with B until KV reads or compute matter. At B = 64 the weights-bound ceiling is 64 x 97.5 = about 6,240 tokens/s; arithmetic intensity at B = 64 is 64 FLOP/B, well below the ridge point of about 315 (DERIVED). This ceiling ignores KV reads and is not a prediction.
- The research notes give a rounded version with 16 GB: batch-1 upper bounds for other GPUs at 16 GB are 99.8 (Server), 112.0 (Workstation), 18.8 (L4), 54.0 (L40S), 120.9 (A100 PCIe), 127.4 (A100 SXM), 209.4 (H100 SXM), 300.0 (H200), 500.0 (B200), 63.0 (RTX 4090), 112.0 (RTX 5090) tokens/s (weights only).

**Interpretation** (my inference)

- This bound is a sanity check, not a forecast. If a measured batch-1 decode is above it, the byte count or bandwidth used is wrong (for example weights are quantized, or the Workstation figure was used). If it is far below, look at overheads, clocks and power before blaming the engine.
- Batch size is the main lever: weight bytes are shared across the batch, so continuous batching raises aggregate throughput at roughly constant per-step time until KV reads or compute take over. That is the quantitative reason the workshop spends time on `--max-num-seqs`, KV cache size and quantization.

**Workshop decision**

- The roofline derivation is taught with the Qwen3-8B example above and always labelled as a theoretical lower bound. Measured values come from `benchmark/infbench` (workloads in `benchmark/workloads/`, results in `benchmark/results/`). Measured results always override the datasheet and the bound.

### 6.11 Power, clocks and thermals

**Source facts**

- Peak throughput numbers are quoted "based on GPU Boost Clock". Hopper whitepaper: "GPU Peak Clock and GPU Boost Clock are synonymous for NVIDIA Data Center GPUs" ([RTX PRO Blackwell whitepaper](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf), [L40S](https://www.nvidia.com/en-us/data-center/l40s/), [Hopper whitepaper](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf)).
- TensorRT benchmarking guidance: "By default, the GPU clock frequency is floating"; lock with `sudo nvidia-smi -lgc <freq>`; "Power throttling occurs when the average GPU power consumption reaches the power limit" (set with `sudo nvidia-smi -pl <power_cap>`); thermal throttling begins at the device-specific slowdown temperature (`nvidia-smi -q -d TEMPERATURE`); passively cooled GPUs throttle if airflow is insufficient; warm up before timing ([TensorRT benchmarking](https://docs.nvidia.com/deeplearning/tensorrt/11.4.0/performance/benchmarking.html)).
- The RTX PRO 6000 Server Edition is passively cooled with configurable power up to 600 W (400-600 W per the family page), so sustained clocks depend on chassis airflow and the configured power limit ([family page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/), [product page](https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/)).
- `nvmlDeviceGetEnforcedPowerLimit` = "the effective power limit that the driver enforces after taking into account all limiters"; `nvmlDeviceGetCurrentClocksEventReasons` returns a bitmask ([NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html)).

**Interpretation** (my inference)

- A rented pod gives no control over `-lgc` or `-pl` (not stated in the notes; Unverified). Benchmark noise from clocks is therefore recorded, not removed.

**Workshop decision**

- `benchmark/infbench/sampler.py` records `power.draw` and `clocks.sm` per run. Compare runs only within one session on one pod, and report the SM clock and power next to every throughput number.

### 6.12 MIG (Multi-Instance GPU)

**Source facts**

- MIG partitions supported GPUs "into multiple isolated instances, each with dedicated compute and memory resources" ([MIG user guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/index.html)). Concepts: a GPU Instance (GI) is GPU slices plus engines; a Compute Instance (CI) holds a subset of the GI's SM slices; CIs share memory and engines with the parent GI; each slice's dedicated memory limits both capacity and bandwidth; naming example `1g.5gb` ([MIG concepts](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/concepts.html)).
- RTX PRO 6000 Blackwell (Server, Workstation, Max-Q; CC 12.0, 96 GB, up to 4 instances): profiles `1g.24gb` (1/4 memory, 1/4 SMs, 4 instances), `2g.48gb` (1/2, 1/2, 2 instances), `4g.96gb` (full), plus `+me`, `+gfx`, `+me.all`, `-me` variants (`+gfx` is new in GB20X) ([supported MIG profiles](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-mig-profiles.html)).
- MIG needs compute capability >= 8.0. Listed: RTX PRO 6000 Blackwell, B200 (up to 7), H200 (up to 7), H100 (up to 7), A100 (up to 7). Not listed: L40S, L4, RTX 4090, RTX 5090 ([supported GPUs](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html)). The L40S page states "Multi-Instance GPU (MIG): No" ([L40S](https://www.nvidia.com/en-us/data-center/l40s/)).
- H100 80GB profiles: 1g.10gb (1/8 memory, 1/7 SMs, 7 instances), 1g.20gb (1/4, 1/7, 4), 2g.20gb (2/8, 2/7, 3), 3g.40gb (4/8, 3/7, 2), 4g.40gb (4/8, 4/7, 1), 7g.80gb (full) ([supported MIG profiles](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-mig-profiles.html)).
- On MIG-enabled GPUs NVML and nvidia-smi utilization queries (gpu, memory, encoder, decoder) are not supported ([nvidia-smi docs](https://docs.nvidia.com/deploy/nvidia-smi/index.html), [NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html)).

**Interpretation** (my inference)

- A `1g.24gb` slice has about a quarter of the SMs and bandwidth (DERIVED, Unverified). A 24 GB slice could hold the 16.38 GB BF16 weights of Qwen3-8B but leaves little KV space, and with roughly 400 GB/s the single-stream bound would drop to about 400 / 16.38 = 24 tokens/s (DERIVED from an Unverified bandwidth). MIG isolates tenants; it does not add capacity or speed.

**Workshop decision**

- Workshop pods request the full-card GPU id (`NVIDIA RTX PRO 6000 Blackwell Server Edition`, 96 GB, as in `config/workshop.yaml`), not the MIG variants Runpod offers, because NVML utilization queries are unsupported on MIG-enabled GPUs and the benchmarks measure whole-card bandwidth. MIG is a lecture topic only.

### 6.13 GPU generations (NVIDIA sources)

| Generation | Date (source) | Examples | Inference-relevant features |
|---|---|---|---|
| Volta | WP v1.1, Aug 2017 | V100 | First Tensor Cores (640 per V100), 125 Tensor TFLOPS, HBM2 900 GB/s |
| Turing | 2018 (Unverified, from memory) | T4 | 2nd-gen Tensor Cores (INT8/INT4); T4: 320 TCs, 130 INT8 TOPS, 70 W |
| Ampere | May 2020 (blog May 14, 2020) | A100, A10, A30 | 3rd-gen Tensor Cores: TF32, BF16, FP64, INT8/INT4; 2:4 sparsity; MIG (7); NVLink 3 600 GB/s |
| Ada Lovelace | Sept 2022 (Unverified date) | L4, L40S, RTX 4090 | 4th-gen Tensor Cores with FP8; GDDR6/6X; no HBM |
| Hopper | announced Mar 22, 2022; H100 "available starting in the third quarter" | H100, H200 | Transformer Engine (FP8/16-bit), HBM3/HBM3e, NVLink 4 900 GB/s, TMA, clusters |
| Blackwell | announced Mar 18, 2024; RTX PRO datasheets Apr 2025 | B200, GB200, RTX PRO 6000, RTX 5090 | 5th-gen Tensor Cores with FP4/FP6, 2nd-gen Transformer Engine (micro-tensor scaling), NVFP4, NVLink 5 1.8 TB/s, 208 B transistors (datacenter), GDDR7 on RTX parts |
| Blackwell Ultra | 2025 | B300, GB300 | up to 160 SMs, 288 GB HBM3E, NVFP4 dense 15 PFLOPS |
| Rubin | Vera Rubin release May 31, 2026; shipments "starting this fall" | Rubin GPU, Vera Rubin NVL72 | HBM4, NVLink 6 (3 TB/s per GPU), adaptive-compression Transformer Engine for NVFP4 |

**Source facts**

- Volta: "The Tesla V100 GPU contains 640 Tensor Cores: eight (8) per SM"; 64 FMAs per clock per Tensor Core; "up to 125 Tensor TFLOPS" ([Volta whitepaper](https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf)).
- Ampere: TF32 has an 8-bit exponent and 10-bit mantissa; BF16/FP32 mixed precision runs at the FP16/FP32 rate; structured sparsity doubles Tensor throughput ([Ampere in depth](https://developer.nvidia.com/blog/nvidia-ampere-architecture-in-depth/)).
- Ada: the Tensor Core adds "support for a new FP8 tensor format. Compared to FP16, FP8 halves the data storage requirements and doubles throughput" ([Ada whitepaper v2.1](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)).
- Hopper: Transformer Engine "intelligently manages and dynamically chooses between FP8 and 16-bit calculations"; H100 SM Tensor Cores deliver 2x the A100 MMA rate per SM on equivalent types and 4x with FP8 ([Hopper whitepaper](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf), [Hopper in depth](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/), [Hopper press release](https://nvidianews.nvidia.com/news/nvidia-announces-hopper-architecture-the-next-generation-of-accelerated-computing)).
- Blackwell: "new 4-bit floating point AI inference capabilities"; 208 billion transistors, TSMC 4NP ([Blackwell press release](https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Blackwell-Platform-Arrives-to-Power-a-New-Era-of-Computing/default.aspx), [Blackwell architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/)).
- NVFP4 (Jun 24, 2025): 4-bit E2M1 values with an E4M3 scale per 16-value micro-block plus an FP32 per-tensor scale; 4.5 bits per value effective; "reduces the model memory footprint by approximately 3.5x relative to FP16, and approximately 1.8x compared to FP8"; DeepSeek-R1-0528 FP8 to NVFP4 PTQ shows "1% or less accuracy degradation on key language modeling tasks" ([NVFP4 blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)).
- Rubin: Vera Rubin press release May 31, 2026 ("Production shipments of Vera Rubin are set to begin starting this fall"). Per Rubin GPU: NVFP4 inference 50 PFLOPS (footnote "Sparse specification"), FP16/BF16 4 PFLOPS ("Dense specification"), 288 GB HBM4, 19.2 TB/s, NVLink 6 3 TB/s ([press release](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory), [Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)).
- Blackwell Ultra: up to 160 SMs and 288 GB HBM3E; NVFP4 15 PFLOPS dense ([Blackwell Ultra blog](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/)).
- Unverified: Turing 2018 and Ada Sept 2022 launch dates (no dated NVIDIA page retrieved; Ada's launch release: [NVIDIA news](https://nvidianews.nvidia.com/_gallery/download_pdf/6329dad6ed6ae51abfa606f4/)).

**Interpretation** (my inference)

- Each generation adds a lower precision (FP16 to TF32/BF16 to FP8 to FP4) that roughly doubles the Tensor rate and halves the weight bytes. By Table A, FP8 Tensor rates exist from Ada onward (A100: n/a) and FP4 only on Blackwell parts; the workshop GPU has both.

**Workshop decision**

- One generations slide, labelled with the dates above including the Unverified ones. The workshop GPU is Blackwell, so the FP8 profiles (`config/vllm-profiles/fp8.yaml`, `kv-fp8.yaml`) run on hardware with FP8 Tensor support. There is no NVFP4 profile in the profile list; NVFP4 is mentioned, not benchmarked.

### 6.14 Workshop decision: which GPU numbers go into config and dashboards

**Interpretation** (my inference)

- Datasheet numbers are ceilings quoted at boost clock. A passively cooled card with a configurable power limit may not hold them. Only two hardware numbers are needed for the roofline arguments in the course: peak dense BF16 compute and memory bandwidth.

**Workshop decision**

- **Numbers used for the workshop GPU**: memory 96 GB; memory bandwidth **1597 GB/s** (Server Edition datasheet, not the Workstation 1792); peak dense BF16 **about 504 TFLOPS**, derived at Workstation clocks (503.8) because NVIDIA states no Server boost clock; ridge point therefore **about 315 FLOP/B** (503.8e12 / 1597e9). The plausible dense range 468-504 TFLOPS and ridge 293-315 FLOP/B is quoted next to it on the slide.
- Reference lines in dashboards and the roofline arithmetic in `docs/METRICS.md` use exactly these numbers and label them "datasheet / derived". `scripts/sizing.py` uses 96 GiB capacity only.
- **Measured results always override the datasheet.** Where a benchmark in `benchmark/results/` disagrees with the bound in section 6.10, the measurement is reported and the datasheet number is annotated, not edited.
- Sparse numbers, GeForce "AI TOPS" and the Workstation 1792 GB/s figure never appear as workshop-GPU values.

## 7. Infrastructure provider and Runpod capabilities

Verified 2026-10-14. Facts marked MCP-LIVE come from live reads of the Runpod MCP server on 2026-10-14 (account-specific or catalogue state; they can change). This section is not legal advice.

### 7.1 Provider identity: the "Werner" finding

**Source facts**

- The workshop specification mentioned "Werner GPU instances". No GPU provider or product named "Werner" was found in web searches. Plausible EU alternatives surveyed: Verda (formerly DataCrunch, Helsinki), Hetzner GEX, Scaleway ([Verda](https://verda.com/), [Hetzner GPU matrix](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/), [Scaleway GPU pricing](https://www.scaleway.com/en/pricing/gpu/)).
- The notes give no URL for the negative result itself (absence of evidence from searches, not a source).

**Interpretation** (my inference)

- Absence of search results is not proof that a provider does not exist; it may be a regional or private offer. The notes give no explanation for the name and record the decision as Runpod without further rationale. Do not guess a spelling.

**Workshop decision**

- The workshop runs on Runpod, driven through the Runpod MCP server. The "Werner" item stays an open question for the organiser, not a requirement. If the organiser can name the provider, only the Runpod-specific parts (this section, `docs/GPU-POOL.md`, `docs/SETUP.md`) change; the engine image, profiles and benchmark harness do not.

### 7.2 Why Runpod

**Source facts**

- Runpod offers the workshop GPU as a self-serve hourly SKU: "NVIDIA RTX PRO 6000 Blackwell Server Edition" (96 GB), $2.49 per GPU-hour on Secure Cloud in the live read (MCP-LIVE list-gpu-types, 2026-10-14; [Runpod GPU types](https://docs.runpod.io/references/gpu-types)).
- Billing is per second with no egress fees ([Runpod billing](https://docs.runpod.io/references/billing-information)). EU Secure Cloud data centers exist (section 7.8). A hosted MCP server and a v2 REST API exist (section 7.9).
- The notes contain no comparative evaluation of the alternatives beyond the survey above.

**Interpretation** (my inference)

- Reasons that follow from the facts: the exact GPU model is available by the hour, billing granularity matches a 3-day workshop, EU data centers are selectable, and every action can be scripted. Cost and sovereignty are not argued by the notes; the sovereignty case is in section 7.10.

**Workshop decision**

- One pod per group on Secure Cloud in an EU data center, created and deleted by script. The workshop does not use Community Cloud (peer-to-peer hosts; see 7.3).

### 7.3 Product model and what a Pod can and cannot do

**Source facts**

- A Pod is a single container launched by Runpod. The docs state: "You cannot run your own Docker instance or Docker Compose on Pods". Docker-in-Docker works only on CPU Pods in Runpod's tutorial ([Pods overview](https://docs.runpod.io/pods/overview), [Docker-in-Docker tutorial](https://docs.runpod.io/tutorials/pods/run-docker-in-docker)).
- Secure Cloud runs in T3/T4 data centers and always has a public IP; Community Cloud is a peer-to-peer network of individual hosts. Instant Clusters are 2-8 self-serve nodes (still containers). Bare Metal is a reserved product, not hourly self-serve ([Pods overview](https://docs.runpod.io/pods/overview), [Instant Clusters](https://docs.runpod.io/instant-clusters), [Bare Metal](https://www.runpod.io/gpu-bare-metal-server)).
- Billing: per second, no egress fees; default account spend limit $80/hour; you need balance for one hour of a Pod before it deploys; at $0 balance all Pods stop and Pods without a network volume are terminated ([Runpod billing](https://docs.runpod.io/references/billing-information)).
- Unverified: whether Pods are privileged (assume not). `nvidia-smi` and NVML reads are expected to work; DCGM profiling metrics need `CAP_SYS_ADMIN` and likely do not.

**Interpretation** (my inference)

- One container means no Compose, no sidecar containers, no Docker-in-Docker. Anything multi-process (vLLM on 8000, a second vLLM on 8001, Prometheus, Grafana, an NVML exporter) must run as plain processes inside the one container.

**Workshop decision**

- The image is the deployment unit; the containerization block runs on participants' laptops, not on the pods. vLLM profiles are rendered and run on the pod by `infra/pod/render-profile.py` and `infra/pod/wsctl`. Monitoring on pods uses `monitoring/pod/grafana.ini`, `monitoring/prometheus/prometheus.pod.yml` and the NVML exporter as plain processes.

### 7.4 SSH

**Source facts**

- Proxied SSH (`ssh.runpod.io`) works on every Pod but does not support SCP/SFTP. Full SSH needs a public IP, 22/tcp exposed and an sshd in the image; it supports SCP and SFTP ([Runpod SSH docs](https://docs.runpod.io/pods/configuration/use-ssh)).
- Account SSH keys are injected into Pods. Runpod's own `start.sh` reads the `PUBLIC_KEY` environment variable. External TCP port mappings change whenever a Pod resets; requesting a port number above 70000 yields identical internal and external ports readable from `RUNPOD_TCP_PORT_<n>` ([Runpod SSH docs](https://docs.runpod.io/pods/configuration/use-ssh), [start.sh](https://raw.githubusercontent.com/runpod/containers/main/container-template/start.sh), [expose ports](https://docs.runpod.io/pods/configuration/expose-ports)).
- The upstream vLLM image has no sshd; the documented approach is to install openssh-server in the start command, write `$PUBLIC_KEY` into `authorized_keys` and start sshd ([custom templates](https://docs.runpod.io/pods/templates/create-custom-template)).
- MCP-LIVE: the account had exactly one registered SSH key (ed25519), matching the local `~/.ssh/id_ed25519.pub`; no pods and no network volumes existed at the start of the research session. (No URL: live account read.)
- MEASURED on a live pod (S1, RTX PRO 6000 Server Edition, EUR-IS-2): multiple Linux users with separate `authorized_keys` work over the one exposed TCP port (`infra/tests/wsctl-integration.sh` and the live checks cover login, isolation of home directories and revocation: a revoked key is removed, running sessions are killed and the next login is denied). A pod restart destroyed the container disk, kept `/workspace` and changed the public SSH port (22290 to 22235) while the IP stayed the same; sshd answered 11 seconds after the restart.

**Caution:** The Runpod docs mention `SSH_PUBLIC_KEY` while the Runpod `start.sh` reads `PUBLIC_KEY`. The script is the primary source for behaviour; verify on a test pod ([SSH docs](https://docs.runpod.io/pods/configuration/use-ssh), [start.sh](https://raw.githubusercontent.com/runpod/containers/main/container-template/start.sh)).

**Interpretation** (my inference)

- Proxied SSH is enough for shells and port forwarding but not for file transfer; a full sshd on an exposed TCP port is required for scp/rsync. That is a public port, so key-only authentication matters.

**Workshop decision**

- Participants reach the vLLM server over SSH tunnels to 127.0.0.1:8000 (generation) and 127.0.0.1:8001 (embeddings). Per-user keys are managed by `infra/add-participant-key.sh`, `infra/revoke-participant-key.sh` and `infra/sync-participants.sh` (template: `infra/participants.example.yaml`). The source of truth for accounts and keys is `infra/participants.yaml` on the trainer's laptop, not the pod: after a pod restart the container disk is gone and `infra/deploy-to-pod.sh` recreates every account from that file. Nothing identity-related is kept on `/workspace` because that volume does not enforce permissions (7.6). The SSH host key is new after a rebuild, so clients must expect a host-key change and the trainer's scripts use a per-pod `known_hosts` file.

### 7.5 Networking

**Source facts**

- The HTTP proxy `https://{podId}-{port}.proxy.runpod.net` is public with no platform authentication, HTTPS only, and Cloudflare's roughly 100 s connection limit applies (error 524). TCP exposure is public without TLS. UDP is unsupported ([expose ports](https://docs.runpod.io/pods/configuration/expose-ports)).
- Global Networking gives each Pod a private `<podId>.runpod.internal` name at 100 Mbps, NVIDIA GPU Pods only, Secure Cloud, On-Demand, in 17 data centers ([Runpod networking](https://docs.runpod.io/pods/networking)).
- MCP-LIVE Global Networking support in EU data centers is listed in section 7.8.

**Interpretation** (my inference)

- A vLLM server bound to 0.0.0.0 and exposed through the proxy URL is reachable by anyone who learns the pod id. A 100 s limit also breaks long non-streaming completions.

**Workshop decision**

- vLLM binds to 127.0.0.1 and requires `--api-key`; nothing is exposed through the HTTP proxy. Access is by SSH tunnel only. See `docs/SECURITY.md`.

### 7.6 Storage

**Source facts**

- Container disk is lost on stop or restart. Volume disk (`/workspace`) survives stop/restart and is deleted on terminate. Network volumes are independent of Pods, bound to one data center, attach only at creation, and can grow but not shrink. Stopped Pods keep billing for storage only and can restart with zero GPUs if capacity is gone ([storage types](https://docs.runpod.io/pods/storage/types), [network volumes](https://docs.runpod.io/storage/network-volumes), [manage Pods](https://docs.runpod.io/pods/manage-pods)).
- Prices: container disk $0.10/GB/month; volume disk $0.10/GB/month running and $0.20/GB/month stopped; network volume $0.07/GB/month (first TB) ([Runpod billing](https://docs.runpod.io/references/billing-information)).

**Interpretation** (my inference)

- Model weights and participant state belong on the volume disk or a network volume, never on the container disk. "Stop" is not a safe way to save money mid-workshop because the GPU may not come back.

**Workshop decision**

- Models are pinned in `config/models.yaml` and fetched by `infra/pod/fetch-models.py`. MEASURED on a live pod (S1): the volume mounted at `/workspace` is a FUSE network filesystem with **no permission enforcement**: `chmod` is silently ignored, `chown` fails, and another user could read a root-owned `0600` file and list a root-owned `0700` directory. The workshop therefore keeps only the download cache on `/workspace` (seeded back into `/opt/workshop/hf` on the container disk in about 60 seconds after a rebuild) and puts homes, keys, API key, state and caches on the container disk. Model downloads from the Hugging Face hub ran at about 1.3 GB/s (Qwen3-8B, 16 GB, in 12.4 s); `/workspace` wrote at about 500 MB/s and read at about 750 MB/s. A full rebuild after a pod restart took 5 min 41 s (cache seed about 60 s, monitoring 16 s, vLLM 194 s, embedding server 53 s). During a live workshop Pods stay running; `terminate` is used only at the end.

### 7.7 GPU catalogue and prices (MCP-LIVE)

Source: Runpod MCP `list-gpu-types`, product POD, Secure Cloud, 2026-10-14. USD per GPU-hour. Availability level was LOW for every listed GPU/data-center pair at the time of the read.

| GPU id | VRAM GB | Secure $/h | Community $/h | max GPUs per pod (Secure) | EU DCs listed | host CUDA versions reported |
|---|---|---|---|---|---|---|
| NVIDIA RTX PRO 6000 Blackwell Server Edition | 96 | 2.49 | 1.69 | 9 | EU-RO-1, EUR-IS-1 (also EUR-IS-2 per `list-data-centers`) | 13.2 |
| NVIDIA RTX PRO 6000 Blackwell Workstation Edition | 96 | 2.59 | 1.69 | 8 | EU-RO-1, EUR-IS-1 | 13.0 |
| NVIDIA L40S | 48 | 1.09 | 0.79 | 8 | EU-NL-1 (also EUR-IS-2) | 13.0 |
| NVIDIA L4 | 24 | 0.59 | 0.44 | 9 | EU-RO-1 | 13.2 |
| NVIDIA GeForce RTX 4090 | 24 | 0.89 | 0.34 | 8 | EU-RO-1, EUR-IS-1 | 12.8, 13.0 |
| NVIDIA GeForce RTX 5090 | 32 | 1.19 | 0.69 | 8 | EUR-IS-1 | 12.8 |
| NVIDIA A100-SXM4-80GB | 80 | 1.79 | 1.39 | 8 | EUR-IS-1 | 13.0 |
| NVIDIA H100 80GB HBM3 (SXM) | 80 | 3.99 | 2.69 | 8 | EU-NL-1, EUR-IS-3 | 12.8, 13.0 |
| NVIDIA H200 (SXM) | 141 | 5.29 | 3.59 | 8 | EU-FR-1, EUR-IS-4 | 12.8, 13.0, 13.2 |
| NVIDIA B200 | 180 | 7.99 | 5.98 | 8 | EU-RO-1 | 13.0 |
| NVIDIA RTX A6000 / A40 | 48 | 0.59 | 0.33-0.35 | 10 | EU-SE-1 | 12.8, 13.0 (A40 also 13.2) |

- MCP-LIVE: for the RTX PRO 6000 Server Edition the catalogue also lists a "serverless" price of 3.49 and a MIG variant "PRO 6000 MIG 24GB" in EUR-IS-2.
- Unverified: whether a multi-GPU RTX PRO 6000 pod places GPUs on the same PCIe root or NUMA node; check `nvidia-smi topo -m` after launch.

**Caution:** The Runpod notes state "The card has no NVLink" without a URL. The only source in the hardware notes is Lenovo's reprint of NVIDIA specs ("NVLink support: No"); NVIDIA's own pages do not list NVLink for the Server Edition ([Lenovo LP2263](https://lenovopress.lenovo.com/lp2263.pdf)).

**Caution:** The public pricing page shows different per-GPU numbers for some cards than the API catalogue. The API (MCP) read is the source of truth for budgeting ([Runpod pricing](https://www.runpod.io/pricing)).

**Caution:** Runpod lists the Workstation-class cards as separate GPU ids with similar prices (Server Edition $2.49, Workstation Edition $2.59). The Workstation card has 12 % more memory bandwidth (1792 vs 1597 GB/s, DERIVED), so benchmark results from the two ids are not interchangeable.

**Interpretation** (my inference)

- The workshop GPU is cheaper per hour than an H100 ($2.49 vs $3.99) and has more VRAM (96 vs 80 GB) but about half the H100 SXM bandwidth (1597 vs 3350 GB/s, from Table A). At $2.49/hour, one pod for a 3-day, roughly 7 teaching hours per day workshop costs about 3 x 7 x 2.49 = $52.29 per pod before storage and idle time (DERIVED; the real bill depends on how long pods run).
- "Availability LOW" means the pool for this SKU is thin; a four-group workshop needs capacity confirmed before the event.

**Workshop decision**

- Check `list-billing` (Runpod MCP) before and after each session and delete Pods immediately after each scripted session (spend control from the Runpod notes). The API/MCP catalogue above is the price basis for budgeting; availability and fallback belong in `docs/GPU-POOL.md`.

### 7.8 EU data centers and compliance tags

MCP-LIVE (`list-data-centers`, 2026-10-14). "Global networking" = supports Runpod Global Networking.

| Data center | Global networking | Compliance tags reported |
|---|---|---|
| EU-CZ-1 | yes | none reported in the notes |
| EU-FR-1 | yes | none reported in the notes |
| EU-NL-1 | yes | GDPR, ISO_IEC_27001, ISO_14001, HIPAA |
| EU-RO-1 | yes | GDPR, HIPAA |
| EU-SE-1 | yes | ISO_IEC_27001 only |
| EUR-IS-1 | no | none reported in the notes |
| EUR-IS-2 | yes | GDPR, HIPAA |
| EUR-IS-3 | no | none reported in the notes |
| EUR-IS-4 | yes | none reported in the notes |
| EUR-IS-5 | no | none reported in the notes |

**Source facts**

- The table above is a live catalogue read (no URL). Tags are reported only for EU-RO-1, EU-NL-1, EU-SE-1 and EUR-IS-2; for the other data centers the read reported none.
- Company-level certifications: SOC 2 Type II, SOC 3, ISO/IEC 27001:2022 ([Runpod compliance](https://www.runpod.io/legal/compliance), [about Runpod](https://www.runpod.io/about/company)).

**Interpretation** (my inference)

- Compliance tags are per data center and differ: EU-SE-1 carries only ISO_IEC_27001 and no GDPR tag, while EU-RO-1 and EUR-IS-2 carry GDPR and HIPAA. A "GDPR" tag is a provider label, not a legal guarantee. A tag that is absent in the read means "not reported", not "non-compliant".
- The data centers that list the workshop GPU (EU-RO-1, EUR-IS-1, plus EUR-IS-2) differ in Global Networking support and tags.

**Workshop decision**

- Pick one named EU data center per session and write down the tags the live read showed (`docs/GPU-POOL.md` is the place for the pool facts). The workshop claims no compliance status beyond what the live read reports.

### 7.9 Templates, images, APIs and MCP

**Source facts**

- Runpod's official docs cover only Serverless vLLM (`runpod/worker-vllm`); no official vLLM Pod template was found. Runpod's own guide runs the upstream image `vllm/vllm-openai` with a custom start command and port 8000 exposed ([Serverless vLLM](https://docs.runpod.io/serverless/vllm/overview), [Runpod vLLM guide](https://www.runpod.io/articles/guides/deploy-vllm-runpod-docker)).
- REST API v1 is deprecated and scheduled to retire 2026-11-15. The Runpod MCP server is v2-only. v2 create-pod fields include name, image, cloud, `gpu{id,count}`, `dataCenterIds`, `globalNetworking`, `mounts`, `startSsh`, `templateId`, `env`, `ports`, `disk` and entrypoint/cmd/args ([migrate from v1](https://docs.runpod.io/api-reference-v2/migrate-from-v1), [create Pod](https://docs.runpod.io/api-reference/pods/POST/pods)).
- The hosted Runpod MCP server (`https://mcp.getrunpod.io/`) authenticates with OAuth or a Bearer API key, exposes pod, template, network-volume, catalogue, billing and serverless tools, acts with the full permissions of the key and has no read-only mode ([runpod-mcp repository](https://github.com/runpod/runpod-mcp), [MCP servers docs](https://docs.runpod.io/get-started/mcp-servers)).
- The Runpod MCP guide `runpod-mcp` (served by the MCP server via `read-guide`, plugin version 1.7.1; no public URL in the notes) states "pin the CUDA floor on every GPU create": `create-pod` takes `gpu.minCudaVersion` ("12.8" by default, "13.0" only for a CUDA-13 image).

**Caution:** One secondary page gives the v1 retirement date as 2026-12-01; the migration guide says 2026-11-15. Plan for the earlier date ([migrate from v1](https://docs.runpod.io/api-reference-v2/migrate-from-v1)).

**Interpretation** (my inference)

- A key with full permissions and no read-only mode means any agent holding it can create, bill and delete pods. The key is a secret with the blast radius of the account.
- The CUDA floor ties section 6.8 to the provider: a CUDA-13 image pinned in `infra/versions.env` needs a host that reports CUDA 13.x (the Server Edition rows report 13.2).

**Workshop decision**

- Use the v2 surface only (the Runpod MCP server is v2-only), and set `gpu.minCudaVersion` to match the image pinned in `infra/versions.env`. The upstream image is used with a start command that installs sshd (see 7.4); no Runpod-specific vLLM template is relied on. The Runpod API key stays with the trainer and never goes onto pods or into the repository (`docs/SECURITY.md`).

### 7.10 Jurisdiction and the data processing agreement: a sovereignty case study

**Source facts**

- Runpod Inc. is the contracting entity and is a US company. The public DPA uses EU Standard Contractual Clauses (Module 2) under Irish law. Sub-processors include AWS, GCP, Cloudflare, Datadog and Snowflake. For region selection Runpod commits only to "reasonable efforts" to use a nearby server ([Runpod DPA](https://www.runpod.io/legal/data-processing-agreement), [compliance](https://www.runpod.io/legal/compliance), [about](https://www.runpod.io/about/company)).
- Certifications: SOC 2 Type II, SOC 3, ISO/IEC 27001:2022 ([compliance](https://www.runpod.io/legal/compliance)).
- The HTTP proxy path goes through Cloudflare (100 s limit, error 524) ([expose ports](https://docs.runpod.io/pods/configuration/expose-ports)).
- Unverified: the state of incorporation of Runpod Inc. Unverified: applicability of the US CLOUD Act is an inference, not a Runpod statement.

**Interpretation** (my inference; not legal advice)

- **EU region does not equal EU jurisdiction.** A pod in EU-RO-1 or EUR-IS-2 keeps the data physically in that data center, but the contracting party is a US company, the DPA relies on EU SCCs, sub-processors include US cloud and SaaS providers, and Runpod promises only "reasonable efforts" on region placement. Whether US law can reach the data is a legal question the notes do not answer.
- The provider controls the layers a participant cannot see (host and driver, network path, the proxy path via Cloudflare). What it does with them beyond the DPA text is not in the notes.
- Sovereignty is an architecture property with trade-offs. Rented US-operated GPUs are defensible for a workshop only if the data on them is synthetic or public; for production data the same decision needs a different provider or a different data class.

**Implications**

1. Use only non-sensitive, synthetic or public data on the workshop pods.
2. Prefer the data center whose tags match the claim you want to make, and record the tag set you saw.
3. Do not describe a Runpod EU pod as "EU-sovereign" in slides.
4. Treat the DPA, SCC module, sub-processor list and the "reasonable efforts" wording as the contract facts to discuss in the sovereignty block.
5. For stronger guarantees evaluate EU-headquartered providers (the surveyed Verda, Hetzner, Scaleway) against the same checklist: contracting entity, governing law, sub-processors, region commitment, certifications.
6. Provider choice and engine choice are independent: the same vLLM image and profiles run on any NVIDIA host with a suitable driver (section 6.8).

**Workshop decision**

- `docs/DIGITAL-SOVEREIGNTY.md` uses this section as a worked case and states "EU region does not equal EU jurisdiction" plainly; `docs/SECURITY.md` is where the data classes allowed on pods belong. Not legal advice.

### 7.11 Implications for the workshop (compiled)

**Source facts**

- No Docker or Compose inside Pods, so the containerization block runs on participants' laptops; on the pods the image itself is the deployment unit.
- Monitoring is pod-native (Prometheus, Grafana and an NVML exporter as plain processes); dcgm-exporter is used in the reference compose stack only.
- Proxy URLs and exposed TCP ports are public: bind vLLM to 127.0.0.1, require `--api-key`, and reach it over SSH tunnels.
- Port mapping changes on Pod restart (measured: 22290 to 22235), and the container disk is wiped: accounts and keys are recreated from `infra/participants.yaml` on the trainer's laptop by `infra/deploy-to-pod.sh`; participants get the new port and see a new host key. `/workspace` holds only the model download cache (no permission enforcement, 7.6).
- Stopped Pods can return with zero GPUs; during a live workshop keep Pods running and use `terminate` only at the end.
- Spend control: per-second billing, check `list-billing` before and after each session, delete Pods immediately after each scripted session.
- These items are the research notes' own compiled list; each rests on the facts in 7.3 to 7.6 above.

**Workshop decision**

- Files built around these constraints: `infra/pod/wsctl`, `infra/pod/ws-user.sh`, `infra/pod/ws-reset.sh`, `infra/add-participant-key.sh`, `monitoring/pod/grafana.ini` and `monitoring/prometheus/prometheus.pod.yml`. Participants never receive provider credentials.

### 7.12 Security observation about the research process: embedded instructions in a vendor docs page

**Source facts**

- One research agent reported that a Runpod documentation page it fetched contained text addressed to AI agents, asking the reader to perform an action through a Runpod docs MCP server. The agent treated it as page content, not as a user instruction, and did not act on it. The hardware research notes identify that page as the Runpod GPU types reference (`https://docs.runpod.io/references/gpu-types`). The Runpod notes report an agent-addressed instruction on "a Runpod documentation page" without naming it; it is probably the same event (Unverified). The text is deliberately not quoted here.

**Interpretation** (my inference)

- This is a live example of indirect prompt injection: instructions arrive inside data fetched for a legitimate purpose. The page's author may be benign (a feedback prompt), but an agent cannot tell benign from malicious by content alone. Fetched web content is data, not instructions.
- Defences that apply: separate the instruction channel (user, system) from the data channel (fetched pages); give agents least-privilege tools (the Runpod MCP key has full account permissions and no read-only mode, so the blast radius of a successful injection would be the account); require human confirmation for billable or destructive actions.

**Workshop decision**

- The Day 3 security material (`docs/SECURITY.md`) uses this as an anecdote without quoting the page (the notes plan it that way). It supports the same rule as the tool-calling material in `apps/tool-calling-demo`: tool and web results are untrusted input.

## 8. Quantization support

Verified 2026-10-14. Source: vLLM v0.31.0 docs and source unless stated.

### 8.1 What vLLM documents and on which hardware

**Source facts**

- Formats listed in the quantization docs: AutoAWQ, BitsAndBytes, GPTQModel, Intel Neural Compressor, LLM Compressor (FP8 W8A8, INT4 W4A16, INT8 W4A8, INT8 W8A8), NVIDIA Model Optimizer, Online Quantization, AMD Quark, Quantized KV Cache, TorchAO, FP8 ViT encoder attention; plus a `b12x` page for SM120/SM121. ([SRC quantization/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md))
- The hardware compatibility table has columns Volta, Turing, Ampere, Ada, Hopper, AMD GPU, Intel GPU, x86 CPU, Arm CPU. It has NO Blackwell column. Rows: AWQ (Turing..Hopper), GPTQ (Volta..Hopper), Marlin (GPTQ/AWQ/FP8/FP4; Turing*..Hopper), llm-compressor INT8 W8A8, llm-compressor FP8 W8A8 (Ada, Hopper, AMD only), bitsandbytes, DeepSpeedFP, GGUF (Volta..Hopper + AMD). The page says the chart "is subject to change" and points to `vllm/model_executor/layers/quantization`. ([SRC quantization/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md))
- `--quantization` default None means "check `quantization_config` in the model config; if None, assume the weights are not quantized". New in 0.31.0: `--quantization-config` (JSON or dotted keys, e.g. `--quantization-config.moe.activation mxfp8`). Valid method names include `awq`, `auto_awq`, `fp8`, `fbgemm_fp8`, `fp_quant`, `modelopt`, `modelopt_fp4`, `modelopt_mxfp8`, `modelopt_mixed`, `auto_gptq`, `gptq`, `gptq_marlin`, `awq_marlin`, `humming`, `compressed-tensors`, `experts_int8`, `quark`, `moe_wna16`, `torchao`, `inc`, `mxfp4`, `gpt_oss_mxfp4`, `deepseek_v4_fp8`, `online`, `fp8_per_tensor`, `fp8_per_block`, `fp8_per_channel`, `int8_per_channel_weight_only`, `nvfp4_per_token`, `mxfp8`. ([SRC quantization/**init**.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/layers/quantization/__init__.py), [vllm/config/model.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py))
- Pre-quantized FP8 checkpoints (llm-compressor / compressed-tensors, ModelOpt) are auto-detected from `config.json` `quantization_config` or `hf_quant_config.json`; no `--quantization` flag is needed. ModelOpt formats: `FP8`, `FP8_PER_CHANNEL_PER_TOKEN`, `FP8_PB_WO`, `NVFP4` and `W4A16_NVFP4` (`modelopt_fp4`), `MXFP8` (`modelopt_mxfp8`). ([SRC modelopt.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/modelopt.md))

**Interpretation** (inference)

- Teaching caveat: the docs' hardware table has no Blackwell column, so "not listed" must not be read as "not supported". The same docs say FP8 W8A8 is supported on Blackwell (next subsection), and the b12x page covers NVFP4/MXFP8/FP8 on SM120. The table is stale; the source tree and the per-format pages are the evidence.
- The reverse also holds: the table does not prove that a kernel exists for compute capability 12.0 either. That needs a smoke test (Unverified items below).

**Workshop decision**

- `docs/MODEL-SELECTION.md` and the quantization lab must show the table, point out the missing column, and then run `config/vllm-profiles/fp8.yaml` on the real card instead of arguing from the table.

### 8.2 FP8 weights and activations

**Source facts**

- "FP8 computation is supported on NVIDIA GPUs with compute capability >= 8.9 (Ada Lovelace, Hopper, Blackwell). FP8 models will run on compute capability >= 7.5 (Turing) as weight-only W8A16, utilizing FP8 Marlin." "Ada Lovelace, Hopper, and Blackwell GPUs are supported for W8A8. Turing/Ampere GPUs are supported for W8A16". SM120 is compute capability 12.0, which is >= 8.9. ([SRC llm_compressor/fp8.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/llm_compressor/fp8.md))
- The FP8 GEMM kernel is chosen automatically and logged as `Selected <kernel> for <module>`. For block-quantized FP8 the order is FlashInfer/DeepGEMM hybrid (Hopper only), DeepGEMM, CUTLASS, Marlin, Triton, Humming, PyTorch fallback. If inference hangs try `VLLM_USE_DEEP_GEMM=0` or `--linear-backend cutlass`. FP8 E4M3 max is 448, E5M2 max is 57344. ([SRC llm_compressor/fp8.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/llm_compressor/fp8.md))
- Unverified: FP8 W8A8 dense on SM120 uses CUTLASS/FlashInfer kernels automatically. The docs name FP8 W8A8 for "Ada, Hopper, AMD" in the Blackwell-less table; SM120 FP8 linear is implied by the b12x page (per-tensor FP8, 128x128 block FP8) and the SM12x blockwise FP8 release-note item, not by a support-matrix row.

**Interpretation** (inference)

- The publisher's FP8 checkpoint (`Qwen/Qwen3-8B-FP8`) is a pre-quantized checkpoint, so vLLM reads its quantization settings from the model files and needs no flag (inference: that this checkpoint carries such a `quantization_config` was not inspected in the notes). `config/models.yaml` records that its weights are 9.44 GB, not half of 16.38 GB, because embeddings and the output head stay in BF16.

**Workshop decision**

- `config/vllm-profiles/fp8.yaml` serves `Qwen/Qwen3-8B-FP8` under `served-model-name: Qwen/Qwen3-8B`, so clients and dashboards keep one `model_name` label across the BF16 and FP8 runs. The profile does not use online quantization.

### 8.3 Online quantization changes in 0.31.0

**Source facts**

- Online quantization quantizes Linear and MoE weights "at load time, without needing a pre-quantized checkpoint or calibration data". Options: `--quantization fp8_per_tensor` (per-tensor fp8_e4m3 weight scale plus dynamic activation scale; on some GPUs (Ada, Hopper) linear activations use per-token scaling), `fp8_per_block` (128x128 weight blocks, 1x128 activation blocks), `fp8_per_channel`, `mxfp8` (e8m0 per-32 scales; "Requires SM 100+ (Blackwell or newer) for w8a8, other GPUs use a w8a16 fallback"), `mxfp4`, `int8_per_channel_weight_only`, `nvfp4_per_token`, or `--quantization online --quantization-config '{...}'` with `targets`/`ignore`. ([SRC online.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/online.md))
- `--quantization fp8` on a BF16 checkpoint still works in 0.31.0 but is deprecated. The code logs "`--quantization fp8 is deprecated for online quantization; use --quantization fp8_per_tensor instead.`" and redirects. `Fp8Config` itself raises "The `fp8` quantization method no longer supports online quantization. Please use `--quantization fp8_per_tensor` instead." for a non-serialized checkpoint. Listed as a breaking change (#53585). ([SRC weight_utils.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/model_loader/weight_utils.py), [fp8.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/layers/quantization/fp8.py), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))
- Also changed in 0.31.0: Quark silent online MXFP4 removed (use the online quantization API); `fbgemm_fp8` and `fp_quant` are in `DEPRECATED_QUANTIZATION_METHODS`; AllSpark INT8 W8A16 removed. ([SRC quantization/**init**.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/layers/quantization/__init__.py), [release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0))

**Interpretation** (inference)

- Older tutorials that say `--quantization fp8` still run, with a warning, but teach a method name that no longer means what it did. Teach `fp8_per_tensor`.

**Workshop decision**

- `infra/pod/render-profile.py` allows `quantization` as a `--set` override, so a group can try `fp8_per_tensor` on the BF16 profile and compare it with the pre-quantized checkpoint.

### 8.4 NVFP4, MXFP4 and the SM120 notes

**Source facts**

- NVFP4: "vLLM selects a GEMM kernel automatically at load time from the backends available on the current platform (CUTLASS, FlashInfer, Marlin, and others). On GPUs without a supported native FP4 GEMM kernel, vLLM falls back to weight-only (W4A16) execution via Marlin and logs a warning". Override `--linear-backend {cutlass, flashinfer_cutlass, flashinfer_cutedsl, flashinfer_trtllm, flashinfer_cudnn, marlin, b12x, ...}` (replaces deprecated `VLLM_NVFP4_GEMM_BACKEND`). ([SRC modelopt.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/modelopt.md))
- 0.30.0: "W4A4 NVFP4 preferred on SM120/121 (#55170)", also under new defaults "W4A4 NVFP4 over weight-only kernels on SM120/121". ([0.30.0 notes](https://github.com/vllm-project/vllm/releases/tag/v0.30.0))
- b12x backend (SM120/SM121 only, extra pip package): linear for per-tensor FP8, 128x128 block FP8, MXFP8, NVFP4, MXFP4; MoE for NVFP4/MXFP4 only. ([SRC b12x.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/b12x.md))
- Open NVFP4/MoE issues on SM120: vllm #50189 (open), flashinfer #2577 (closed completed 2026-07-23), vllm #32826 (closed not_planned); see section 3.3. ([vllm #50189](https://github.com/vllm-project/vllm/issues/50189), [flashinfer #2577](https://github.com/flashinfer-ai/flashinfer/issues/2577))

**Interpretation** (inference)

- NVFP4 is the Blackwell headline feature, and also where the SM120 bug reports concentrate. It is not a workshop path.

**Workshop decision**

- No profile uses NVFP4, MXFP4 or b12x. `config/models.yaml` lists only BF16 and FP8 workshop models.

### 8.5 AWQ, GPTQ, Marlin

**Source facts**

- "The `AutoAWQ` library is deprecated. This functionality has been adopted by the vLLM project in `llm-compressor`"; AWQ checkpoints still load; AWQ is not supported on Volta. GPTQ is via GPTQModel; Marlin/Machete kernels "for both Ampere (A100+) and Hopper (H100+)". ([SRC auto_awq.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/auto_awq.md), [gptqmodel.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gptqmodel.md))
- Unverified: AWQ/GPTQ (Marlin) kernels on SM120. They are built for the image's arch list (which includes 12.0), but no doc statement confirms compute capability 12.0.

**Interpretation** (inference)

- Treat 4-bit weight-only formats as "test before you promise" on this GPU.

**Workshop decision**

- No AWQ or GPTQ profile exists. If a group wants to try one, it is an unverified experiment and should be labelled so in `docs/MODEL-SELECTION.md`.

### 8.6 KV-cache dtypes

**Source facts**

- `--kv-cache-dtype` default `auto`; allowed values: `auto, float16, bfloat16, fp8, fp8_e4m3, fp8_e5m2, fp8_inc, fp8_ds_mla, nvfp4_ds_mla, turboquant_k8v4, turboquant_4bit_nc, turboquant_k3v4_nc, turboquant_3bit_nc, int4_per_token_head, int8_per_token_head, fp8_per_token_head, nvfp4, nvfp4_4over6`. `fp8` equals `fp8_e4m3`. ([SRC cache.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/cache.py))
- With `fp8` and no calibrated scales "all quantization scales are set to 1.0". Calibration via llm-compressor is "Recommended"; per-attention-head scales only with the Flash Attention backend; with FA3 plus FP8 KV the attention itself runs in FP8. `--kv-cache-dtype-skip-layers sliding_window` leaves chosen layers unquantised. ([SRC quantized_kvcache.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/quantized_kvcache.md))
- The newer dtypes (`nvfp4`, `turboquant_*`, `int4/int8/fp8_per_token_head`) exist in the config but are not documented in detail in the notes.

**Interpretation** (inference)

- FP8 KV doubles the tokens that fit in a given byte budget. Quality cost is model-dependent and unmeasured here (uncalibrated scales of 1.0).

**Workshop decision**

- `config/vllm-profiles/kv-fp8.yaml` (`kv-cache-dtype: fp8`) and `kv-constrained-fp8kv.yaml` (4 GiB with FP8 KV) implement the experiment. The quality caveat belongs in the lab text.

### 8.7 GGUF and bitsandbytes

**Source facts**

- GGUF: "highly experimental and under-optimized ... might be incompatible with other features". In 0.31.0 GGUF support "has migrated to OOT vllm-gguf-plugin" (`uv pip install vllm-gguf-plugin`, PyPI 0.0.5, 2026-08-10); load with `vllm serve unsloth/Qwen3-0.6B-GGUF:Q4_K_M --tokenizer Qwen/Qwen3-0.6B`. ([SRC gguf.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gguf.md), [PyPI](https://pypi.org/pypi/vllm-gguf-plugin/json))
- bitsandbytes is out of tree: `vllm-bnb-plugin` (`uv pip install vllm-bnb-plugin`, PyPI 0.0.3, 2026-08-24). The docs hardware table still lists it as Volta..Hopper. ([SRC bnb.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/bnb.md), [PyPI](https://pypi.org/pypi/vllm-bnb-plugin/json))
- Unverified: whether the stock `vllm/vllm-openai:v0.31.0` image bundles either plugin. The notes give only the install commands.

**Interpretation** (inference)

- Pods run with `HF_HUB_OFFLINE=1`; installing a plugin on a pod needs network access to PyPI. GGUF in vLLM is not a path to teach.

**Workshop decision**

- The `Qwen/Qwen3-8B-GGUF` entry in `config/models.yaml` is for the llama.cpp/Ollama comparison, not for vLLM. No vLLM GGUF profile exists.

---

## 9. vLLM metrics

Verified 2026-10-14. Source of truth: `vllm/v1/metrics/loggers.py` (plus `vllm/v1/spec_decode/metrics.py`, `vllm/v1/metrics/perf.py`) at the v0.31.0 tag. Names below are the names Prometheus scrapes, not the names in the code.

### 9.1 Rules: labels, `_total`, histograms

**Source facts**

- Counters are defined WITHOUT `_total` and exposed WITH it by `prometheus_client`: defined `vllm:prompt_tokens` is scraped as `vllm:prompt_tokens_total`. Histograms expose `_bucket`, `_sum`, `_count`. ([SRC loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py), [grafana.json](https://github.com/vllm-project/vllm/blob/v0.31.0/examples/observability/prometheus_grafana/grafana.json))
- Common labels on engine metrics: `model_name` (the first `--served-model-name`) and `engine` (DP engine index as a string, "0"...). Extra labels: `finished_reason` (`request_success`), `reason` (`num_requests_waiting_by_reason`: `capacity` or `deferred`), `source` (`prompt_tokens_by_source`), `sleep_state` (`engine_sleep_state`: `awake`, `weights_offloaded`, `discard_all`), `position` (spec decode per-position). `vllm:lora_requests_info` has only `max_lora`, `waiting_lora_adapters`, `running_lora_adapters`. ([SRC loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py))
- Caution: `vllm:iteration_tokens_total` is a HISTOGRAM despite its `_total` name ("Histogram of number of tokens per engine_step."). It is scraped as `vllm:iteration_tokens_total_bucket/_sum/_count`; the shipped dashboard uses `rate(vllm:iteration_tokens_total_count[$__interval])`. Buckets 1, 8, 16, 32, ..., 16384. ([SRC loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py))
- Caution: `docs/usage/metrics.md` sample output shows only `model_name`; real series carry `model_name` AND `engine` in 0.31.0. ([SRC loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py))
- `/metrics` also carries `http_requests_total`, `http_request_size_bytes`, `http_response_size_bytes`, `http_request_duration_seconds` (prometheus-fastapi-instrumentator) and default `python_*`/`process_*` metrics (the latter not available with `--api-server-count > 1`). Content type `text/plain; version=0.0.4; charset=utf-8`. ([SRC design/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/metrics.md))
- `--api-server-count > 1` switches `prometheus_client` to multiprocess mode; `vllm:iteration_tokens_total` and `lora_requests_info` "might be incorrect" there (code TODOs). ([SRC loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py))

### 9.2 Metric list by type

**Source facts**

Gauges

| Scraped name | Extra labels | Meaning |
|---|---|---|
| `vllm:num_requests_running` | | "Number of requests in model execution batches." |
| `vllm:num_requests_waiting` | | "Number of requests waiting to be processed." |
| `vllm:num_requests_waiting_by_reason` | `reason` | `capacity` or `deferred`; sum equals `num_requests_waiting` |
| `vllm:kv_cache_usage_perc` | | "KV-cache usage. 1 means 100 percent usage." Fraction 0-1; `vllm:gpu_cache_usage_perc` is gone |
| `vllm:cache_config_info` | all `CacheConfig` fields as labels | constant 1; includes `block_size`, `gpu_memory_utilization`, `num_gpu_blocks`, `cache_dtype` |
| `vllm:engine_sleep_state` | `sleep_state` | sleep mode state |
| `vllm:lora_requests_info` | `max_lora`, `waiting_lora_adapters`, `running_lora_adapters` | only if LoRA enabled |

Counters (names as scraped, with `_total`)

| Scraped name | Extra labels | Meaning |
|---|---|---|
| `vllm:prompt_tokens_total` | | "Number of prefill tokens processed." |
| `vllm:prompt_tokens_by_source_total` | `source` | prompt tokens by source |
| `vllm:prompt_tokens_cached_total` | | "Number of cached prompt tokens (local + external)." |
| `vllm:generation_tokens_total` | | "Number of generation tokens processed." |
| `vllm:request_success_total` | `finished_reason` | "Count of successfully processed requests." |
| `vllm:num_preemptions_total` | | "Cumulative number of preemption from the engine." |
| `vllm:prefix_cache_queries_total` | | "Prefix cache queries, in terms of number of queried tokens." |
| `vllm:prefix_cache_hits_total` | | "Prefix cache hits, in terms of number of cached tokens." No hit-rate gauge exists in V1 |
| `vllm:external_prefix_cache_queries_total`, `vllm:external_prefix_cache_hits_total` | | KV-connector (cross-instance) cache |
| `vllm:mm_cache_queries_total`, `vllm:mm_cache_hits_total` | | multimodal items |
| `vllm:corrupted_requests_total` | | only with `VLLM_COMPUTE_NANS_IN_LOGITS` |
| `vllm:estimated_flops_per_gpu_total`, `vllm:estimated_read_bytes_per_gpu_total`, `vllm:estimated_write_bytes_per_gpu_total` | | MFU group; needs `--enable-mfu-metrics` (`v1/metrics/perf.py`) |
| `vllm:spec_decode_num_drafts_total`, `vllm:spec_decode_num_draft_tokens_total`, `vllm:spec_decode_num_accepted_tokens_total`, `vllm:spec_decode_num_accepted_tokens_per_pos_total` | `position` (last) | only with a speculative config (`v1/spec_decode/metrics.py`) |

Histograms (each exposes `_bucket`, `_sum`, `_count`)

| Scraped base name | Unit | Notes |
|---|---|---|
| `vllm:time_to_first_token_seconds` | s | TTFT |
| `vllm:inter_token_latency_seconds` | s | ITL, one sample per streamed output event |
| `vllm:request_time_per_output_token_seconds` | s | per-request TPOT = (e2e - TTFT)/(n_out - 1); recorded as 0 when <= 1 token |
| `vllm:e2e_request_latency_seconds` | s | end to end |
| `vllm:request_queue_time_seconds` | s | "time spent in WAITING phase" |
| `vllm:request_inference_time_seconds` | s | "RUNNING phase" |
| `vllm:request_prefill_time_seconds`, `vllm:request_decode_time_seconds` | s | per phase |
| `vllm:request_prompt_tokens`, `vllm:request_generation_tokens`, `vllm:request_max_num_generation_tokens`, `vllm:request_params_n`, `vllm:request_params_max_tokens` | tokens | per-request counts |
| `vllm:request_num_preemptions` | count | per-request preemptions |
| `vllm:request_prefill_kv_computed_tokens` | tokens | "new KV tokens computed during prefill (excluding cached tokens)" |
| `vllm:iteration_tokens_total` | tokens | per engine step; see caution in 9.1 |
| `vllm:kv_block_lifetime_seconds`, `vllm:kv_block_idle_before_evict_seconds`, `vllm:kv_block_reuse_gap_seconds` | s | only with `--kv-cache-metrics` (sampled by `--kv-cache-metrics-sample`) |

(sources for the three tables: [loggers.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py), [perf.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/perf.py), [spec_decode/metrics.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/spec_decode/metrics.py), [usage/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/metrics.md))

### 9.3 Histogram buckets

**Source facts** (`vllm/v1/metrics/buckets.py`, in seconds)

| Metric family | Buckets |
|---|---|
| Request-phase latencies (e2e, queue, inference, prefill, decode) | 0.3, 0.5, 0.8, 1, 1.5, 2, 2.5, 5, 10, 15, 20, 30, 40, 50, 60, 120, 240, 480, 960, 1920, 7680 |
| TTFT | 0.001, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10, 20, 40, 80, 160, 640, 2560 |
| ITL and TPOT | 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2.5, 5, 7.5, 10, 20, 40, 80 |
| Request token counts | 1-2-5 series up to `max_model_len` |
| `iteration_tokens_total` | 1, 8, 16, 32, ..., 16384 |

([SRC buckets.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/buckets.py))

### 9.4 Deprecated, removed and docs-vs-source differences

**Source facts**

- Deprecation policy: metrics deprecated in X.Y are hidden in X.Y+1 (re-enable with `--show-hidden-metrics-for-version=X.Y`) and removed in X.Y+2. ([SRC usage/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/metrics.md), [design/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/metrics.md))
- Legacy or removed names: `vllm:num_requests_swapped`, `vllm:cpu_cache_usage_perc` (the docs prose still lists `_swapped` in the Grafana description), `vllm:gpu_cache_usage_perc` (replaced by `vllm:kv_cache_usage_perc`), `vllm:time_per_output_token_seconds` (replaced by `vllm:inter_token_latency_seconds` and `vllm:request_time_per_output_token_seconds`), the prefix-cache hit-rate gauge (replaced by the queries/hits counters). No metric is currently flagged deprecated in `loggers.py`; `show_hidden_metrics` is only stored. ([SRC usage/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/metrics.md))
- Caution: `docs.vllm.ai/en/latest/usage/metrics/` lists 42 General metrics including four NOT in the v0.31.0 source: `vllm:admission_rejections`, `vllm:watermark_requests`, `vllm:prompt_tokens_cached_by_source`, `vllm:num_requests_kv_fetch_by_stage`. It marks no metric as deprecated. ([docs.vllm.ai](https://docs.vllm.ai/en/latest/usage/metrics/))

**Interpretation** (inference)

- Dashboards written for 0.6-0.8 era names (`gpu_cache_usage_perc`, `time_per_output_token_seconds`, `_swapped`) show "no data" on 0.31.0 without an error. Panels that need a rate over a counter must use the `_total` name.
- Standard PromQL on these names: prefix-cache hit rate is `rate(vllm:prefix_cache_hits_total[5m]) / rate(vllm:prefix_cache_queries_total[5m])`; mean TTFT is `rate(vllm:time_to_first_token_seconds_sum[5m]) / rate(vllm:time_to_first_token_seconds_count[5m])`; percentiles use `histogram_quantile` on `_bucket`.
- The smallest request-phase bucket is 0.3 s, so queue and prefill times below 300 ms all land in the first bucket; a quantile of a fast server is just the first bound. The TTFT and ITL buckets are fine-grained and do not have this problem.
- `request_time_per_output_token_seconds` records 0 for requests with <= 1 token, which pulls the Prometheus mean down compared with the benchmark tool's TPOT, which excludes those requests.

### 9.5 Official Grafana and Prometheus examples, and what they lack

**Source facts**

- `examples/observability/prometheus_grafana/` contains exactly `README.md`, `docker-compose.yaml`, `grafana.json`, `prometheus.yaml`. `prometheus.yaml`: `scrape_interval: 5s`, `evaluation_interval: 30s`, one job `vllm` targeting `host.docker.internal:8000`. Compose uses `prom/prometheus:latest` and `grafana/grafana:latest`; login admin/admin; datasource `http://prometheus:9090`. The README drives load with `vllm bench serve --dataset-name sharegpt --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json --request-rate 3.0 --endpoint /v1/completions`. ([SRC prometheus_grafana](https://github.com/vllm-project/vllm/tree/v0.31.0/examples/observability/prometheus_grafana))
- `grafana.json` (title "vLLM", schemaVersion 39, template variable `model_name` from `label_values(model_name)`) has 12 panels: E2E Request Latency, Token Throughput, Inter Token Latency, Time Per Output Token (TPOT), Scheduler State (`num_requests_running`, `num_requests_waiting`), Time To First Token Latency, Cache Utilization (`kv_cache_usage_perc`), Request Prompt Length (heatmap), Request Generation Length (heatmap), Finish Reason, Queue Time, Requests Prefill and Decode Time, Max Generation Token in Sequence Group. It has NO panel for prefix-cache hit rate, preemptions or iteration tokens. ([SRC grafana.json](https://github.com/vllm-project/vllm/blob/v0.31.0/examples/observability/prometheus_grafana/grafana.json))
- A second, newer set: `examples/observability/dashboards/{grafana,perses}/`. `grafana/performance_statistics.json` has E2E latency and TTFT at P50/P90/P99/Avg, ITL, and "TPS (Tokens Per Second) Over Time" including `rate(vllm:iteration_tokens_total_count[...])`; `grafana/query_statistics.json` has request rate, p50/p90/p99 latency, input/output token size and throughput. Also `examples/observability/opentelemetry/` and `metrics/offline.py`. ([SRC dashboards](https://github.com/vllm-project/vllm/tree/v0.31.0/examples/observability/dashboards))

**Interpretation** (inference)

- Neither dashboard shows GPU hardware metrics, KV-cache hit rate, preemptions, per-request MFU or SLO attainment. None of them has an alert. The official files are a starting point for latency distributions only.

**Workshop decision**

- `monitoring/` holds the workshop stack: `monitoring/prometheus/prometheus.pod.yml` scrapes `127.0.0.1:8000` (`vllm`), `127.0.0.1:8001` (`vllm-embedding`), `127.0.0.1:9400` (`gpu`, the NVML exporter in `monitoring/gpu-exporter/exporter.py` with DCGM names) and Prometheus itself, every 5 s. `config/vllm-profiles/base.yaml` sets `enable-mfu-metrics: true` for the roofline panel.
- Open item: `monitoring/grafana/dashboards/` is empty in the repository as of 2026-10-14; the workshop panels (prefix-cache hit rate, preemptions, iteration tokens, MFU, GPU) still have to be written. `docs/METRICS.md` should list the `_total` rule and the histogram-named-`_total` exception.
- `benchmark/infbench/sampler.py` accepts both `vllm:*_total` and the non-`_total` names, and falls back to `vllm:gpu_cache_usage_perc` when `vllm:kv_cache_usage_perc` is absent.

---

## 10. Benchmark tooling

Verified 2026-10-14. vLLM facts come from the v0.31.0 source (`vllm/benchmarks/serve.py`, `vllm/benchmarks/datasets/datasets.py`); methodology facts come from the cited papers and tool documents. Book reference: "Inference Engineering" (Kiely, Baseten Books 2026), benchmarking chapter, cited by chapter only.

### 10.1 `vllm bench serve`: flags

**Source facts**

- Install: "To use benchmark commands, please install with extra dependencies using `pip install vllm[bench]`"; the extra is `pandas, matplotlib, seaborn, datasets, scipy, plotly`. `datasets`, `pandas`, `soundfile` are imported behind `PlaceholderModule`, so `--dataset-name random` needs none of them. Sub-commands `vllm bench {latency, serve, throughput}` (plus `sweep`, `startup`, `mm-processor` in source). `VLLM_USE_RUST_BENCH=1` (default off) would delegate to the `vllm-rs` binary. ([SRC docs/cli/README.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/cli/README.md), [datasets.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/datasets/datasets.py))
- Unverified: whether the official Docker image needs `uv pip install --system datasets pandas` for HF/ShareGPT datasets (the Dockerfile copies `benchmarks/` but does not install `vllm[bench]`). Try it before the workshop.

| Flag | Default | Note |
|---|---|---|
| `--backend` | `openai` | Choices include `vllm`, `openai`, `openai-chat`, `openai-responses` (new), `openai-audio`, `openai-embeddings`, `vllm-pooling`, `vllm-rerank` |
| `--base-url` | None | else `http://{--host}:{--port}` |
| `--host`, `--port` | `127.0.0.1`, 8000 | |
| `--endpoint` | `/v1/completions` | use `/v1/chat/completions` with `--backend openai-chat` |
| `--model` | optional | if omitted, the first model of `/v1/models` |
| `--header KEY=VALUE ...` | none | redacted when args are printed |
| `--api-key` | does NOT exist | auth via env `OPENAI_API_KEY` (sent as `Authorization: Bearer`) or `--header Authorization="Bearer <key>"` |
| `--num-prompts` | 1000 | |
| `--request-rate` | `inf` | all requests at t=0; otherwise Poisson (`--burstiness 1.0`) or gamma |
| `--burstiness` | 1.0 | only effective with a finite rate |
| `--max-concurrency` | None | caps in-flight requests; actual rate can fall below `--request-rate`; `<=0` raises |
| `--num-warmups` | 0 | only warm-up flag; warm-up requests precede timing |
| `--ramp-up-strategy` | none | `linear` or `exponential`, with `--ramp-up-start-rps` / `--ramp-up-end-rps`; incompatible with `--request-rate` |
| `--goodput KEY:VALUE ...` | none | keys `ttft`, `tpot`, `e2el` (ms) |
| `--ignore-eos` | off | sets `ignore_eos` so generation reaches `max_tokens` |
| `--extra-body` | none | e.g. `'{"chat_template_kwargs":{"enable_thinking":false}}'` |
| `--temperature --top-p --top-k --min-p --frequency-penalty --presence-penalty --repetition-penalty` | None | server `--generation-config auto` defaults then apply |
| `--seed` | 0 | |
| `--dataset-name` | `random` | `sharegpt, burstgpt, sonnet, random, random-mm, random-rerank, hf, custom, custom_audio, custom_image, prefix_repetition, spec_bench, speed_bench, timed_trace` |
| `--random-input-len`, `--random-output-len` | 1024, 128 | |
| `--random-range-ratio` | "0.0" | float or JSON dict `{"input":0.3,"output":0.5}`, in [0,1) |
| `--random-prefix-len` | 0 | one fixed random prefix generated once and SHARED by every request, so it creates prefix-cache hits |
| `--percentile-metrics` | None, which means `ttft,tpot,itl` for generative models and `e2el` for pooling | allowed: `ttft, tpot, itl, e2el, client_queue_time, e2el_including_client_queue` |
| `--metric-percentiles` | `"99"` | by default ONLY p99 is reported, plus mean, median, std |
| `--save-result`, `--save-detailed`, `--append-result` | off | JSON output; `--save-detailed` adds per-request arrays |
| `--result-dir`, `--result-filename`, `--metadata KEY=VALUE...`, `--label` | | extra top-level JSON keys via `--metadata` |

([SRC benchmarks/serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py), [datasets.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/datasets/datasets.py), [endpoint_request_func.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/lib/endpoint_request_func.py))

- Random dataset semantics: total input = `random-prefix-len` (shared) plus a context length sampled from `[input_len*(1-ratio), input_len*(1+ratio)]`; tokens drawn from the tokenizer vocab without special ids, seeded by `numpy.default_rng(seed)`; prompts are decoded and re-encoded to hit the length. Without `--ignore-eos` the server may stop before `--random-output-len`. ([SRC datasets.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/datasets/datasets.py))
- Default filename: `{label or backend}-{request_rate}qps[-concurrency{N}]-{model_basename}-{YYYYMMDD-HHMMSS}.json`; `request_rate` renders as `inf`. A `.pytorch.json` file is written only if env `SAVE_TO_PYTORCH_BENCHMARK_FORMAT` is set. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))

### 10.2 `vllm bench serve`: printed and JSON output

**Source facts**

- Printed block, title `Serving Benchmark Result`: `Successful requests:`, `Failed requests:`, `Maximum request concurrency:` (if set), `Request rate configured (RPS):` (if finite), `Benchmark duration (s):`, `Total input tokens:`, `Total generated tokens:`, `Request throughput (req/s):`, `Request goodput (req/s):` (only with `--goodput`), `Output token throughput (tok/s):`, `Peak output token throughput (tok/s):`, `Peak concurrent requests:`, `Total token throughput (tok/s):`. Then sections `Time to First Token`, `Time per Output Token (excl. 1st token)`, `Inter-token Latency`, `End-to-end Latency`, each with `Mean`, `Median`, `P99` lines (percentiles per `--metric-percentiles`). An optional `Speculative Decoding` section (acceptance rate, acceptance length, drafts, draft tokens, accepted tokens, per-position rates) appears when the server exposes spec-decode metrics. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- Gotcha: for generative models the default set is `ttft,tpot,itl`, so the `End-to-end Latency` block and the `mean_e2el_ms`, `median_e2el_ms`, `p99_e2el_ms` keys are NOT printed or saved unless you pass `--percentile-metrics ttft,tpot,itl,e2el`. `e2el` is the default only for pooling models. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- JSON keys with `--save-result` (top level): `date`, `endpoint_type`, `backend`, `label`, `model_id`, `tokenizer_id`, `num_prompts`, any `--metadata` keys, `request_rate` (a number, or the STRING `"inf"`), `burstiness`, `max_concurrency`, then `duration`, `completed`, `failed`, `total_input_tokens`, `total_output_tokens`, `request_throughput`, `request_goodput` (null unless `--goodput`), `output_throughput`, `total_token_throughput`, `max_output_tokens_per_s`, `max_concurrent_requests`, `rtfx`, `latencies`, `queue_times`, and per selected metric `mean_<m>_ms`, `median_<m>_ms`, `std_<m>_ms`, `p<N>_<m>_ms` for `<m>` in `ttft`, `tpot`, `itl`, `e2el`, `client_queue_time`, `e2el_including_client_queue`. Non-integer percentiles keep the decimal (`p99.9_ttft_ms`). Spec decode adds `spec_decode_acceptance_rate`, `spec_decode_acceptance_length`, `spec_decode_num_drafts`, `spec_decode_draft_tokens`, `spec_decode_accepted_tokens`, `spec_decode_per_position_acceptance_rates`. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- Without `--save-detailed` these lists are removed: `input_lens`, `output_lens`, `start_times`, `ttfts`, `itls`, `generated_texts`, `errors`. `latencies` and `queue_times` are NOT removed. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- Definitions in the source: `request_throughput = completed/duration`; `output_throughput = total_output_tokens/duration`; `total_token_throughput = (total_input + total_output)/duration`; TPOT per request = `(latency - ttft)/(output_len - 1)`, requests with <= 1 output token excluded from TPOT stats; ITL pooled over all inter-chunk gaps of all requests. ([SRC serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- The docs have an "Understanding the latency metrics" section, and note that the Prometheus TPOT histogram differs from bench TPOT for requests with <= 1 token. ([SRC benchmarking/cli.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/benchmarking/cli.md), [design/metrics.md](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/metrics.md))

**Interpretation** (inference)

- A default `vllm bench serve` run reports a p99 but no p50 or p95, and no end-to-end latency. Students who copy the README line get a tail number without a median and no E2E column. Always pass `--metric-percentiles 50,90,95,99 --percentile-metrics ttft,tpot,itl,e2el`.
- `--request-rate inf` is a burst test, not a steady-state test: all requests arrive at t=0, so TTFT includes the whole queue.

### 10.3 Other tools

**Source facts**

- GuideLLM (`vllm-project/guidellm`): load generator for OpenAI-compatible servers. Profiles `synchronous` (one at a time), `concurrent` (fixed number of parallel streams), `throughput` (finds maximum throughput), `constant` (fixed rate), `poisson` (Poisson around a target rate, `--seed`), `sweep` (synchronous baseline, then throughput, then `sweep_size - 2` rates in between), and a newer `goodput` profile that searches concurrency (doubles until the attainment target is missed, then bisects; default tolerance 10%). Constraints: `max_duration`, `max_requests`, `max_errors`, `over_saturation`; `warmup`/`cooldown`. The docs track `main`, so flag syntax can change between releases. ([GuideLLM repo](https://github.com/vllm-project/guidellm), [metrics.md](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/metrics.md), [SLO guide](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/service_level_objectives.md))
- AIPerf (`ai-dynamo/aiperf`): `--concurrency` (closed loop, "Number of concurrent requests to maintain"), `--request-rate` with `--request-rate-mode`/`--arrival-pattern` (constant, poisson, gamma; default poisson; can combine with `--concurrency` as a cap), `--user-centric-rate` with `--num-users`, `--benchmark-duration` with `--benchmark-grace-period` (default 30 s), warm-up flags. Its README carries a "Migrating from Genai-Perf" guide. ([AIPerf repo](https://github.com/ai-dynamo/aiperf), [cli-options.md](https://github.com/ai-dynamo/aiperf/blob/main/docs/cli-options.md), [metrics-reference.md](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md))
- GenAI-Perf: the notes contain no primary-source fact about GenAI-Perf itself beyond the AIPerf README's migration guide, which positions AIPerf as its successor. Unverified: GenAI-Perf's own metric definitions and status. ([AIPerf repo](https://github.com/ai-dynamo/aiperf))
- LLMPerf (`ray-project/llmperf`): archived read-only since 2025-12-17 (banner: "This repository was archived by the owner on Dec 17, 2025. It is now read-only."). Its README names only inter-token latency and generation throughput, not TTFT. ([LLMPerf repo](https://github.com/ray-project/llmperf))
- NVIDIA NIM LLM Benchmarking Guide, "Metrics" page: defines TTFT, E2E latency, ITL (explicitly equated with TPOT), TPS (system-level versus per-user) and RPS with formulas; its text refers to AIPerf behaviour. ([NIM metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html))
- MLPerf Inference (Reddi et al., ISCA 2020, arXiv:1911.02549) defines LoadGen scenarios SingleStream, MultiStream, Server, Offline. Server and Interactive scenarios use Poisson arrivals ("LoadGen sends new queries to the SUT according to a Poisson distribution"); the Llama 2 70B benchmark used TTFT <= 2 s and TPOT <= 200 ms, tied to about 240 words/min of reading speed. ([MLPerf paper](https://arxiv.org/abs/1911.02549), [inference_rules.adoc](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc), [MLCommons blog](https://mlcommons.org/2024/03/mlperf-llama2-70b/))
- MLPerf datacenter Server-scenario TTFT/TPOT limits (rules file, master, 2026-10-14): Llama3.1-8B summarization 2000 ms / 100 ms (Conversational), 500 ms / 30 ms (Interactive); Llama2-70b QA 2000 / 200 ms and 450 / 40 ms; Mixtral-8x7B 2000 / 200 ms; DeepSeek-r1 2000 / 80 ms and 1500 / 15 ms; GPT-OSS-120B 3000 / 80 ms and 2000 / 20 ms. ([inference_rules.adoc](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc))
- Unverified: the LLM-specific percentile rule (99th for both TTFT and TPOT); the asterisk text was not visible in the fetch. MLPerf's TPOT normalisation (N versus N - 1) was not stated in the text fetched.

### 10.4 Metric definitions differ between tools

**Source facts** (common timeline: send at t0, first content chunk at t_first, last at t_last, N output tokens)

| Metric | Definition by tool | Source |
|---|---|---|
| TTFT | Request submission to the first generated token; includes network, queueing and the whole prefill. AIPerf: first NON-EMPTY content chunk, `content_responses[0].perf_ns - request.start_perf_ns`; reasoning tokens are NOT excluded (a separate metric, TTFO, skips reasoning). | [AIPerf metrics-reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md), [GuideLLM metrics](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/metrics.md), [DistServe](https://arxiv.org/abs/2401.09670) |
| TPOT (vLLM, DistServe, NIM) | `(E2E - TTFT)/(N - 1)`; undefined for N <= 1. vLLM sets it to 0 for goodput when output_len <= 1. NIM calls the same quantity ITL. | [vLLM serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py), [NIM metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) |
| TPOT (MLPerf) | "the average interval between all the tokens generated"; the blog adds "sometimes also called TBT". Normalisation not stated in the text fetched. | [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc) |
| TPOT (GuideLLM) | "The average time taken to generate each output token, including the first token." A DIFFERENT quantity from vLLM/DistServe TPOT. | [GuideLLM metrics](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/metrics.md) |
| ITL (AIPerf) | Per request `(request_latency - TTFT)/(OSL - 1)`, i.e. what vLLM and NIM call TPOT. OSL includes reasoning tokens; needs OSL >= 2. | [AIPerf metrics-reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md) |
| ITL (vLLM bench) | Gaps between consecutive chunks, POOLED over all requests (`itls += outputs[i].itl`); token-weighted, not request-weighted. | [vLLM serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py) |
| ITL (GuideLLM) | "average time between generating consecutive tokens in the output, excluding the first token". | [GuideLLM metrics](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/metrics.md) |
| Inter-chunk latency | AIPerf: distribution of gaps between streamed chunks (not tokens). | [AIPerf metrics-reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md) |
| E2E / request latency | Request start to last content response (AIPerf excludes the terminal usage-only chunk). DistServe: latency = TTFT + TPOT x tokens in decode. | [AIPerf metrics-reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md), [DistServe](https://arxiv.org/abs/2401.09670) |
| Output token throughput (system) | AIPerf `total_osl / benchmark_duration_seconds` (includes reasoning tokens and queueing). NIM `Total_output_tokens / (Ty - Tx)`. | [AIPerf](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md), [NIM](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) |
| Output throughput per user | AIPerf `1 / inter_token_latency_seconds` (excludes TTFT, so not comparable with system throughput). NIM: OSL / e2e_latency per request. | same |
| Request throughput | completed requests / benchmark duration (AIPerf, NIM, vLLM). | same |

- The notes list three consequences: say which tool's TPOT/ITL you mean; `1000 / TPOT_ms` is per-user tokens/s only for the `(E2E - TTFT)/(N - 1)` definition; vLLM's `--goodput tpot:` and GuideLLM's `tpot_ms` SLO key are NOT the same quantity (GuideLLM compares `tpot_ms` against its ITL, which excludes the first token, and warns about it). ([GuideLLM SLO guide](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/service_level_objectives.md))

**Interpretation** (inference)

- "Time per output token" and "inter-token latency" are not interchangeable names. One tool's ITL is another tool's TPOT, and a third tool's TPOT includes the first token. Comparing numbers across tools without aligning definitions is the commonest benchmarking error in this area.
- vLLM's server-side Prometheus histograms (section 9) have their own variants: `inter_token_latency_seconds` is per streamed event and `request_time_per_output_token_seconds` is the per-request TPOT, with 0 for short outputs.

### 10.5 Closed loop, open loop, coordinated omission, goodput

**Source facts**

- Open versus closed (Schroeder, Wierman, Harchol-Balter, NSDI 2006): closed-loop generators (arrivals triggered by completions plus think time) and open-loop generators (arrivals independent of completions) give very different response times at the same load; partly-open models are proposed. ([USENIX NSDI 2006](https://www.usenix.org/conference/nsdi-06/open-versus-closed-cautionary-tale))
- Coordinated omission (Gil Tene): a test thread that waits for a response before sending the next request falls behind its intended schedule and never records the samples it would have taken during a stall, so percentiles look far better than reality; JMeter, Grinder and LoadRunner are named as affected. `wrk2` takes a constant rate (`-R`) and records latency from the time a request should have been sent, using HdrHistogram. ([Tene, mechanical-sympathy post](https://groups.google.com/g/mechanical-sympathy/c/icNZJejUHfE/m/BfDekfBEs_sJ), [wrk2](https://github.com/giltene/wrk2), [talk replay page](https://spring.io/blog/2014/06/03/springone2gx-2013-replay-how-not-to-measure-latency))
- HdrHistogram's `recordValueWithExpectedInterval` back-fills missed samples (example in the README: a 100 s pause with a 10 ms interval changes "99.99% at <= 1 ms" to about 50%). ([HdrHistogram](https://github.com/HdrHistogram/HdrHistogram))
- Unverified: the talk video and slides were not opened in the research; the content of the talk is attested only by the abstract and the written post, and the notes record the post's wording as a paraphrase. Re-check wording before putting quotes on a slide.
- In `vllm bench serve`, `--request-rate` is open loop; `--max-concurrency` caps in-flight requests through an asyncio semaphore, so if the server cannot keep up the real send rate falls below `--request-rate`. The run is then partly closed loop and reintroduces coordinated omission. GuideLLM `concurrent` and AIPerf `--concurrency` are closed loop. The GuideLLM docs never use the words "open-loop" or "closed-loop" for `constant`/`poisson`; that classification is an inference. ([vLLM serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py), [GuideLLM](https://github.com/vllm-project/guidellm))
- Little's law (Little, Operations Research 9(3), 1961): average number in system = arrival rate x average time in system, regardless of distributions. The research cites only the Crossref record, not the paper text. ([DOI 10.1287/opre.9.3.383](https://doi.org/10.1287/opre.9.3.383))
- Tail at scale (Dean and Barroso, CACM 56(2), 2013): at scale, rare high-latency episodes dominate response time, so services should be tail-tolerant. ([DOI 10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794))
- Goodput, DistServe paper: "maximize per-GPU goodput, defined as the maximum request rate that can be served adhering to the SLO attainment goal (say, 90%) for each GPU". Worked example (13B, A100): colocated serving tops out near 1.6 rps on one GPU; disaggregation with 2 prefill + 1 decode GPUs reaches 10 rps total, 3.3 rps/GPU (2.1x). ([DistServe, arXiv:2401.09670](https://arxiv.org/abs/2401.09670))
- Goodput, vLLM `--goodput ttft:<ms> tpot:<ms> e2el:<ms>`: a completed request is good only if EVERY configured metric is at or below its SLO; `request_goodput = good_completed / dur_s`; `itl` is not accepted; no attainment threshold and no per-GPU normalisation; requests with `output_len <= 1` get `tpot = 0` and trivially pass a TPOT SLO. ([vLLM serve.py](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py))
- Goodput, GuideLLM: `--metrics '{"kind":"generative","slo":{"ttft_ms":200,"tpot_ms":50}}'` (also `e2el_ms`); reports SLO attainment and request goodput; errored requests count against attainment; `--profile kind=goodput,target_attainment=0.99,...` searches concurrency for the highest level meeting the target. ([GuideLLM SLO guide](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/service_level_objectives.md))
- Goodput, AIPerf: `--goodput "time_to_first_token:100 inter_token_latency:3.40"` (also `request_latency`, `output_token_throughput_per_user`); Good Request Fraction = good / (completed + errored); Goodput = `good_request_count / benchmark_duration_seconds`. AIPerf allows a throughput-style SLO; vLLM does not. ([AIPerf metrics-reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md))
- Net (from the notes): "goodput" has two meanings. DistServe means the maximum sustainable rate at a stated attainment target, per GPU. vLLM, AIPerf and GuideLLM mean the measured rate of SLO-conforming requests at one tested load. ([DistServe](https://arxiv.org/abs/2401.09670), [Hao AI Lab blog](https://haoailab.com/blogs/distserve))

**Interpretation** (inference)

- A closed-loop test at concurrency N answers "what happens with N users who wait for answers". An open-loop test at rate R answers "what happens when R requests per second arrive no matter what". Capacity planning needs the second; interactive-user experiments can use the first. Report which one you ran.
- Closed loop under overload hides queueing: the offered load backs off with the server. Open loop measured from the scheduled arrival time shows it.
- A DistServe-style goodput figure needs a sweep over rate or concurrency; a single run only yields "requests per second that met the SLO at this load".

### 10.6 What `benchmark/infbench` defines, and why it cross-checks against `vllm bench serve`

The definitions below were read from the harness source on 2026-10-14 (`benchmark/infbench/client.py`, `runner.py`, `report.py`, `stats.py`, `cli.py`); they are repository facts, not external sources.

**Workshop decision**

- TTFT: from the scheduled arrival (open loop) or the send time (closed loop) to the first stream chunk that carries text. Text includes `reasoning_content` and `reasoning` deltas, so a thinking model's first reasoning chunk counts. (`benchmark/infbench/client.py`)
- Latency (E2E): scheduled arrival to the end of the stream. ITL: gap between consecutive text-carrying chunks, pooled over all requests, so it is a chunk gap, not necessarily a token gap. TPOT: `(latency - TTFT)/(completion_tokens - 1)`, with requests of fewer than 2 tokens excluded. Output token counts come from the server's `usage` block (`stream_options.include_usage`). (`benchmark/infbench/client.py`)
- Per-user rate: `output_tps = 1/TPOT` per request; `aggregate_tps = completion tokens / run duration`; `total_tps` and `input_tps` likewise; `request_throughput_rps = ok requests / duration`. (`benchmark/infbench/report.py`)
- Reported percentiles are always p50, p90, p95, p99 plus mean, min, max and count, computed with linear interpolation (numpy default); tokens-per-second per request also gets p1 and p5. E2E latency is always reported. (`benchmark/infbench/stats.py`, `report.py`)
- Closed loop: N workers each send, wait, send again. Open loop: Poisson arrivals from `random.Random(seed).expovariate(rate)`, latency measured from the scheduled arrival, so client lag is not hidden. `--max-inflight` caps open-loop requests and thereby makes the run partly closed loop (the same caveat as `--max-concurrency` in vLLM). (`benchmark/infbench/runner.py`)
- Goodput: `--slo ttft_ms=...,output_tps=...,latency_ms=...`. A request counts only if it meets every stated target; `attainment = good / all measured requests` (failed requests count against); `goodput_rps = good / duration`. The throughput-style `output_tps` SLO follows AIPerf, not vLLM's `tpot`. It is a one-load goodput, not DistServe's maximum rate, so a concurrency or rate sweep is needed for the latter. (`benchmark/infbench/report.py`)
- Request shape: every prompt differs from the first token on except a declared shared prefix, so accidental prefix-cache hits cannot flatter results; `ignore_eos` and `min_tokens` pin the output length (disable with `--no-engine-extensions` for other engines); chat requests set `enable_thinking: false`; warm-up requests are excluded; `--reset-prefix-cache` calls `POST /reset_prefix_cache`. (`benchmark/infbench/workload.py`, `client.py`, `cli.py`)
- Auth: `--api-key` defaults to `$VLLM_API_KEY` or `$OPENAI_API_KEY`; prompt tokenisation uses the server's open `/tokenize` route. (`benchmark/infbench/cli.py`, `workload.py`)

**Interpretation** (inference)

- The harness is about 1,500 lines of Python written for this workshop. Its definitions agree with `vllm bench serve` for TPOT and throughput but differ in three places: TTFT and latency start at the scheduled arrival, ITL pooling is by text chunk, and percentiles and E2E are always reported where vLLM's defaults omit them.
- The cross-check is therefore a validation of the harness against an independent tool, not a second opinion on the server. With the same shape (same input and output lengths, `--ignore-eos`, same rate or concurrency, percentiles aligned with `--metric-percentiles 50,90,95,99` and `--percentile-metrics ttft,tpot,itl,e2el`), request throughput, output token throughput and median TTFT/TPOT should agree within run-to-run noise. A larger gap points to a harness bug, a client-side bottleneck, a prefix-cache hit pattern (vLLM's `random` dataset shares only a prefix you asked for) or a definition mismatch from the table in 10.4.
- Also compare the harness's `/metrics` scrape against the client-side numbers: server-side `vllm:request_time_per_output_token_seconds` and client-side TPOT differ for requests of one token or less.

**Workshop decision** (continued)

- Run `vllm bench serve` once per baseline configuration with `OPENAI_API_KEY` set (no `--api-key` flag exists) and file the JSON next to the `benchmark/results/` run. Open item: no file in the repository contains a `vllm bench serve` command line as of 2026-10-14 (searched); the cross-check recipe still has to be written into `docs/METRICS.md` or the benchmark README, and `benchmark/run.sh` does not call it.
- Teaching order: state definitions first (TTFT, TPOT, ITL, E2E, goodput), then closed vs open loop, then run `benchmark/run.sh` with a rate sweep and an SLO, and only then compare tools.

## 11. Model licences

Verified 2026-10-14. This section describes licence texts as the notes read them. It is not legal advice, and no counsel reviewed it. Clause wording is quoted only in short phrases; read the linked texts before relying on any row.

### 11.1 Open weights vs open source (OSI Open Source AI Definition 1.0)

**Source facts**

- OSAID is "version 1.0"; OSI's press page announcing it is dated October 28, 2024 ([OSI OSAID](https://opensource.org/ai/open-source-ai-definition), [OSI press](https://opensource.org/press-mentions/osi-officially-releases-its-definition-for-open-source-ai)).
- The definition grants four freedoms: use the system for any purpose without asking permission; study how it works and inspect its components; modify it for any purpose, including to change its output; share it with or without modifications. A precondition is access to "the preferred form to make modifications". The freedoms apply to a whole system and to discrete elements ([OSI OSAID](https://opensource.org/ai/open-source-ai-definition)).
- The preferred form must include all three elements below ([OSI OSAID](https://opensource.org/ai/open-source-ai-definition)):

| OSAID 1.0 element | What it requires |
|---|---|
| Data Information | Sufficiently detailed information about the training data so that a skilled person can build a substantially equivalent system, under OSI-approved terms. Includes a complete description of all data (also unshareable data: provenance, scope, characteristics, how obtained and selected, labelling, processing and filtering), a list of publicly available training data and where to get it, and a list of data obtainable from third parties, including for a fee |
| Code | The complete source code used to train and run the system, under OSI-approved licences: data processing and filtering code, training code with arguments and settings, validation and testing, tokenizers, hyperparameter search, inference code, model architecture |
| Parameters | Model parameters such as weights or other configuration settings, under OSI-approved terms (examples include intermediate checkpoints and final optimizer state) |

- "Open Source models" and "Open Source weights" must include the data information and code used to derive those parameters. The definition does not require a specific legal mechanism for making parameters available and allows copyleft ([OSI OSAID](https://opensource.org/ai/open-source-ai-definition)).
- OSI FAQ: systems, models and weights are treated the same. Models that passed OSI's validation: Pythia (EleutherAI), OLMo (AI2), Amber and CrystalCoder (LLM360), T5 (Google). Analysed and not passing: Llama 2 (Meta), Grok (X), Phi-2 (Microsoft), Mixtral (Mistral). These are "not certifications of any kind". Unshareable data is described, not published ([OSI FAQ](https://opensource.org/ai/faq)).
- Unverified: whether OSI has approved any of the custom licences below as a licence, and whether Apertus or EuroLLM satisfy the OSAID (the Apertus card is gated and was not read).

**Interpretation** (my inference, DERIVED in the notes). "Open weights" means the parameters are published, often with a permissive or custom licence, but not the full Data Information and training code. By the OSAID wording, Qwen, Gemma, Mistral, DeepSeek, gpt-oss and Llama checkpoints are at best open weights even when the licence is Apache-2.0 or MIT, because complete training-data information and training code are not part of what the notes found released (not audited per model; Unverified per model). Apache-2.0 and MIT weights satisfy the licence part of the "Parameters" element. The Llama, Qwen community, Kimi, Mistral Modified-MIT and GLM-5.3 licences impose scale or field-of-use conditions, which is the opposite of "use for any purpose". "Open weights" is a licence-and-availability statement; "open source AI" is a statement about the reproducibility of the whole system.

**Workshop decision.** Course materials say "open-weight" for every model in this repository, and use "open source" only where the OSAID elements are met. `docs/DIGITAL-SOVEREIGNTY.md` states the distinction when it discusses what a team can actually reproduce or audit.

### 11.2 EU AI Act: the open-source exemption for general-purpose AI models

Source labelling. The Regulation (EU) 2024/1689 text below comes from the `artificialintelligenceact.eu` AI Act Explorer, an unofficial mirror; the EUR-Lex HTML fetch returned 0 bytes. The mirror renders an amended consolidated text. Art. 53(2) and recitals 102 to 104 read identically to the quotes in the Commission guidelines (paras 69, 71), which are on the Commission's own site.

**Source facts**

- Art. 53(1): GPAI model providers must (a) keep technical documentation (Annex XI), (b) give downstream providers information (Annex XII), (c) have a copyright-compliance policy including text-and-data-mining opt-outs, (d) publish a training-content summary using the AI Office template ([AI Act Art. 53](https://artificialintelligenceact.eu/article/53/)).
- Art. 53(2): points (a) and (b) "shall not apply" to providers of models released under a free and open-source licence "that allows for the access, usage, modification, and distribution of the model", with parameters, weights, architecture information and usage information publicly available. "This exception shall not apply to general-purpose AI models with systemic risks." ([AI Act Art. 53](https://artificialintelligenceact.eu/article/53/), same wording in [Commission guidelines para 69](https://ec.europa.eu/newsroom/dae/redirection/document/118340)).
- Recital 102: a licence is free and open-source when users can "freely access, use, modify and redistribute" the model; credit to the original provider and identical or comparable distribution terms are allowed ([Recital 102](https://artificialintelligenceact.eu/recital/102/)).
- Recital 103 (monetisation): components "provided against a price or otherwise monetised" do not benefit, including via technical support or a platform, or personal-data use beyond security, compatibility or interoperability. Exception: transactions between microenterprises. "Making AI components available through open repositories" is not in itself monetisation ([Recital 103](https://artificialintelligenceact.eu/recital/103/)).
- Recital 104: no exception for systemic-risk models; the exception does not cover the training-content summary and the copyright policy ([Recital 104](https://artificialintelligenceact.eu/recital/104/)).
- Art. 51(2): a GPAI model is presumed to have high-impact capabilities when cumulative training compute exceeds 10^25 FLOPs; the Commission may also designate ([AI Act Art. 51](https://artificialintelligenceact.eu/article/51/)). Art. 54(6) has the same open-source exception for the authorised-representative duty ([Art. 54](https://artificialintelligenceact.eu/article/54/)).
- Art. 2(12): the Regulation does not apply to AI systems released under free and open-source licences, unless placed on the market as high-risk systems or under Art. 5 or 50. This is separate from the GPAI-model exception ([AI Act Art. 2](https://artificialintelligenceact.eu/article/2/)).
- Application: Chapter V applies from 2 August 2025 (Art. 113(b)). The Commission states that from 2 August 2026 its enforcement powers apply, including fines, and models placed on the market before 2 August 2025 must comply by 2 August 2027 ([Art. 113](https://artificialintelligenceact.eu/article/113/), [Commission GPAI guidelines page](https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers)).
- Commission guidelines on the open-source exception ([guidelines](https://ec.europa.eu/newsroom/dae/redirection/document/118340)):
  - Exempt: Art. 53(1)(a), (b) and Art. 54. Not exempt: copyright policy (c) and training-content summary (d) (paras 70, 72).
  - A licence must allow access, use, modification and distribution; if one right is missing it does not qualify (para 75).
  - Disqualifying (para 80): "limitations to non-commercial or research-only use", "prohibitions on distributing the model", "usage restrictions triggered by user scale thresholds", and "requirements to obtain separate commercial licences for specific use cases" (short quotes, joined).
  - Allowed: attribution, same or comparable distribution terms, and proportionate, non-discriminatory "specific, safety-oriented terms" restricting use where it would pose significant risk to public safety, security or fundamental rights (para 81). Reasonable, non-discriminatory security measures such as user verification are allowed (para 76).
  - Monetisation (paras 83 to 86): includes dual licensing that allows free academic use but requires payment for commercial use or use over a certain scale; paid support indistinguishably linked to the model; mandatory support purchase; provider-exclusive hosting that requires paid access (including ad-funded free access); processing personal data as a condition of access. Not monetisation: purely optional paid services, paid support without purchase obligation.
  - Downstream modification (paras 59 to 62): a modifier becomes the "provider" only if the modification significantly changes generality, capabilities or systemic risk; the indicative criterion is modification training compute above one third of the original model's compute (fallbacks: one third of 10^23 FLOP for GPAI, one third of 10^25 for systemic-risk models if the original is unknowable).
- Caution: the guidelines document header reads "Brussels, 19.11.2025, C(2025) 7719 final", while the Commission library page lists publication on 18 July 2025 and says the guidelines are "not legally binding". Unverified: which of the two is the current adopted version ([guidelines](https://ec.europa.eu/newsroom/dae/redirection/document/118340), [library page](https://digital-strategy.ec.europa.eu/en/library/guidelines-scope-obligations-providers-general-purpose-ai-models-under-ai-act)).

The exemption has four conditions (summary table, mine):

| Condition | Source | Effect on models in this repository |
|---|---|---|
| Licence is free and open-source (access, use, modification, distribution; no scale-threshold restriction) | Art. 53(2); guidelines paras 75, 80 | Apache-2.0 and MIT pass the licence test. Licences with MAU, revenue or MaaS-revenue thresholds fail para 80 (DERIVED, below) |
| Parameters, architecture information and usage information are public | Art. 53(2); guidelines paras 87-89 (para numbers as stated in notes) | not assessed per model in the notes |
| Not monetised | Recital 103; guidelines paras 82-86 | not assessed per model in the notes |
| Not a systemic-risk model (presumed above 10^25 FLOPs) | Art. 51(2), Art. 53(2) | Unverified: Kimi K3 (2.8T), Qwen3.8-2.4T, DeepSeek V4-Pro and Mistral Large 3 are plausibly above 10^25 FLOPs; training compute is not disclosed in the cards read |

**Interpretation** (my inference, DERIVED in the notes). The licence test is about the provider's own obligations, not about whether a participant may run the model. DERIVED: Llama (700M MAU), Kimi K2.x / K3 (100M MAU or US$20M monthly revenue), Qwen3.8 Max and Community licences, Mistral Modified-MIT (US$20M monthly revenue) and GLM-5.3 (MaaS revenue threshold) contain thresholds of the kind that para 80 names, so their providers would not qualify for the exemption on the licence test. Apache-2.0 and MIT releases pass that test but still need non-monetisation, public weights and architecture information, and no systemic risk. Separately, running or LoRA-fine-tuning a downloaded model in a workshop does not make the participant a GPAI "provider" under the Commission's indicative one-third-compute criterion, because workshop compute is far below it. Chapter V enforcement powers (fines) apply since 2 August 2026, so the exemption analysis is current, not future. The guidelines are non-binding and the reading above has not been checked by counsel (Unverified).

**Workshop decision.** `docs/DIGITAL-SOVEREIGNTY.md` carries the distinction (provider exemption vs user rights) and states that the workshop gives no legal advice. The workshop's own pinned models are all Apache-2.0, so the licence element does not block the exemption analysis for any of them.

### 11.3 Licence table per family

Read the table row by row; the "Naming / attribution" and "Policy / territorial" columns are separate from the licence text because they often sit in different files. Quoted phrases are short and attributed; everything else is paraphrase.

| Family / repos | Licence (as named in source) | Licence text | Commercial clauses that matter | Naming / attribution | Policy / territorial |
|---|---|---|---|---|---|
| **Qwen**: Qwen3-8B, -8B-FP8, -1.7B, Embedding-0.6B, 30B-A3B(-FP8), 8B-GGUF, Qwen3.5 (4B, 9B, 35B-A3B, 397B-A17B), Qwen3.6, Qwen3.8-27B, Coder, VL-8B | Apache-2.0 (HF tag; repo LICENSE of Qwen3-8B is the stock text, 11,343 bytes) | [Qwen3-8B LICENSE](https://huggingface.co/Qwen/Qwen3-8B/blob/main/LICENSE), [Qwen3.5-9B LICENSE](https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/LICENSE) | No scale threshold in the text. The notes do not list Apache-2.0 duties; read the text | none beyond Apache-2.0 | none noted |
| **Qwen3.8-2.4T-A95B** | "Qwen3.8-Max License", (c) 2026 Qwen (HF `license: other`) | [LICENSE](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/LICENSE) | MIT-style grant, then: (2) if licensee or affiliates run a "Model as a Service or AI Work Assistant business" and aggregate revenue exceeds US$50,000,000 in any consecutive 12 months, a separate licence from Qwen is needed before using the model or derivatives "for any commercial purpose". Does not apply to internal use that makes the model, outputs or capabilities available to no third party. MaaS and AI Work Assistant are defined terms (MaaS = third-party inference or fine-tuning access with meaningful control over inputs, parameters or training data; AI Work Assistant = independent product primarily for coding or office productivity). Contact <model-business@notice.qwencloud.com> | (1) keep copyright and permission notice; display the model name on the UI of commercial products or services above 100,000,000 monthly active users or US$20,000,000 monthly revenue | none noted |
| **Qwen3.8-Flash-Next** | "Qwen Community License 1.0" (HF `qwen-community-1.0`) | [LICENSE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE) | Same conditions as Max, but without the US$50M threshold: any licensee or affiliate that "conducts a Model as a Service or AI Work Assistant business" needs a separate licence before any commercial use. Internal use exposing nothing to third parties is excepted | Same display rule (100M MAU or US$20M monthly revenue) | none noted |
| **Meta Llama 4** (Scout, Maverick) | "Llama 4 Community License Agreement" (effective April 5, 2025); repos `gated=manual` | [llama.com](https://www.llama.com/llama4/license/), [raw LICENSE](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/LICENSE) | (1.a) non-exclusive, worldwide, royalty-free limited licence. (2) if monthly active users of the licensee's or affiliates' products exceed "700 million" in the preceding calendar month on the Llama 4 release date, a licence request to Meta is required, which Meta may grant "in its sole discretion". (5.c) licence terminates if you sue Meta over IP in the Llama Materials or outputs, and you indemnify Meta. (7) California law and courts | (1.b.i) provide a copy of the Agreement and "prominently display 'Built with Llama'"; any distributed AI model improved with Llama Materials or outputs must start its name with "Llama". (1.b.iii) keep a `Notice` text file with the Meta copyright line. (5.a) no trademark licence beyond "Llama" naming | (1.b.iv) comply with law and the Acceptable Use Policy. EU restriction is in the AUP, not the licence: for multimodal models, rights under Section 1(a) "are not being granted" to an "individual domiciled in, or a company with a principal place of business in, the European Union" (Llama 4 AUP). It does not apply to end users of a product or service that incorporates the model |
| **Meta Llama 3.1 / 3.3** | "Llama 3.1 Community License" / "Llama 3.3 Community License" (HF tags `llama3.1`, `llama3.3`); `gated=manual` | clause text not read in the notes | The notes give no clause text for these two; only the Llama 4 text was read. Do not assume it matches | not read | Llama 3.3 AUP carries the EU multimodal sentence as boilerplate (3.3 has no multimodal model); the Llama 3.1 AUP has no such clause ([3.3 AUP](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_3/USE_POLICY.md), [3.1 AUP](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/USE_POLICY.md)). Llama 3.2 AUP has the sentence for the 3.2 vision models ([3.2 AUP](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_2/USE_POLICY.md)) |
| **Meta Muse Glimmer 30B** | Apache-2.0 plus a separate `USAGE_POLICY.md` | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), [USAGE_POLICY](https://huggingface.co/meta-models/Muse-Glimmer-30B/raw/main/USAGE_POLICY.md) | No scale threshold in Apache-2.0 | none beyond Apache-2.0 | Policy: "not intended for individuals under the age of 18" (policy wording); prohibits illegal activity, harassment, discrimination in employment, credit or housing, unlicensed professional practice, privacy violations, malware, circumventing safety measures; risk-of-harm uses include "Military, warfare, nuclear industries or applications, espionage", ITAR-controlled uses, weapons, "Operation of critical infrastructure"; deception (disinformation, impersonation, presenting outputs as human-generated). Unverified: whether the policy is contractually binding on top of Apache-2.0 (the card says use prohibited by the Apache terms is out of scope; the policy says "should not use"). Get legal review for defence or critical-infrastructure use |
| **Google Gemma 4** (E2B, E4B, 12B, 26B-A4B, 31B) | Apache-2.0 (HF tag; licence page titled "Apache License 2.0") | [Gemma 4 licence page](https://ai.google.dev/gemma/docs/gemma_4_license) | No scale threshold; no "Prohibited Use Policy" found in the text as fetched | none beyond Apache-2.0 | Unverified: the Gemma site navigation still lists a "Prohibited use" page; whether Google asserts it against Gemma 4 users is not established |
| **Mistral (Apache set)**: Ministral 3 (3B, 8B, 14B), Mistral-Small-4-119B-2603, Mistral-Small-3.2, Devstral-Small-2, Mistral-Large-3, Magistral-Small-2509, Leanstral, Shieldstral | Apache-2.0 | [Mistral-Small-4 card](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603), [mistralai listing](https://huggingface.co/api/models?author=mistralai&sort=createdAt&direction=-1&limit=40) | Small 4 card: "Open-source license for both commercial and non-commercial use" | none beyond Apache-2.0 | none noted |
| **Mistral Medium 3.5 128B, Devstral 2 123B** | "Modified MIT License" (HF `other`); Devstral 2 identical except "Attribution notice: 2025 - Mistral AI" | [Medium 3.5 LICENSE](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE), [Devstral 2 LICENSE](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/raw/main/LICENSE) | No rights at all if the "global consolidated monthly revenue of your company (or that of your employer)" exceeds US$20 million (or equivalent) for the preceding month. Applies to the Model and all derivatives, modifications or combined works, "whether provided by Mistral AI or by a third party". A commercial licence from <sales@mistral.ai> "which Mistral AI may grant you at its sole discretion", or Mistral's hosted services. The text refers to "(b)", a drafting error in the file | keep attribution and permission notice; no display carve-out | none noted |
| **Mistral Voxtral-4B-TTS-2603** | `cc-by-nc-4.0` (HF tag only; text not read) | [mistralai listing](https://huggingface.co/api/models?author=mistralai&sort=createdAt&direction=-1&limit=40) | Non-commercial by the licence name (my inference) | n/a | No Mistral Research License model is in the newest-40 listing |
| **DeepSeek V4.1-Flash, V4-Pro(-0813), V4-Flash(-0731), V3.2, V3-0324, R1** | MIT, "Copyright (c) 2023 DeepSeek"; no `LICENSE-MODEL` file | [V4.1-Flash LICENSE](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/LICENSE) | Plain MIT; no threshold | keep MIT notice | none noted |
| **DeepSeek-V3 (Dec 2024)** | "DEEPSEEK LICENSE AGREEMENT Version 1.0, 23 October 2023" in `LICENSE-MODEL` (+ `LICENSE-CODE`) | [LICENSE-MODEL](https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/LICENSE-MODEL) | Use-based restrictions that must be passed on to downstream users; copyright and patent grant; redistribution conditions | per agreement | per agreement (use-based) |
| **Kimi K2.x** (K2.6, K2.7-Code, K2-Instruct-0905, and K2 family generally) | "Modified MIT" | [Kimi-K2.6 LICENSE](https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/LICENSE), [K2.7-Code](https://huggingface.co/moonshotai/Kimi-K2.7-Code/raw/main/LICENSE) | Plain MIT with one modification | If used in commercial products or services with more than 100 million monthly active users or more than US$20 million monthly revenue (an OR, not an AND), display "Kimi K2.6" on the UI; the string is model-specific ("Kimi K2.7 Code", "Kimi K2") | none noted |
| **Kimi K3** | "Kimi K3 License" (2026-06) | [LICENSE](https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE) | If licensee or affiliates operate a Model-as-a-Service business and aggregate revenue exceeds US$20M "in total over any consecutive 12 months", "must enter into a separate agreement with Moonshot AI" before commercial use. MaaS excludes end-user products with the model only embedded in specific features and mere relaying to models hosted by others | Display "Kimi K3" on the UI above 100M MAU or US$20M monthly revenue; the MaaS and display clauses do not apply to internal use or use through Moonshot's official products or certified inference partners | none noted. Model ships custom code (`auto_map`) |
| **GLM-5.3** | "GLM-5.3 License" (custom) | [LICENSE](https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE) | MIT-like grant, but a Model-as-a-Service business with aggregate revenue above US$10 billion over 12 months "must pass Z.AI's security review" before commercial use | not read | none noted |
| **GLM-5.3-Flash, GLM-5.2, 5.1, 4.7-Flash** | MIT | [GLM-5.3-Flash card](https://huggingface.co/zai-org/GLM-5.3-Flash) | Plain MIT | keep MIT notice | none noted |
| **OpenAI gpt-oss-20b / 120b** | Apache-2.0 plus `USAGE_POLICY` | [gpt-oss-20b](https://huggingface.co/api/models/openai/gpt-oss-20b), [USAGE_POLICY](https://huggingface.co/openai/gpt-oss-20b/raw/main/USAGE_POLICY) | Card: "Permissive Apache 2.0 license"; no threshold | none beyond Apache-2.0 | Policy text is short: by using the model "you agree to comply with all applicable law" |
| **IBM Granite 4.2** (3B, 8B, 30B) | Apache-2.0 | [granite-4.2-8b](https://huggingface.co/api/models/ibm-granite/granite-4.2-8b) | No threshold | none beyond Apache-2.0 | none noted |
| **NVIDIA Nemotron 3.5 Lightning 30B-A3B** | OpenMDW-1.1 | [LICENSE](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/raw/main/LICENSE) | Permissive. Redistribution needs the licence copy and notices; has a termination clause for patent or copyright suits. The licence imposes no restrictions or obligations on use, modification or sharing of outputs (paraphrase) | retain notices | none noted |
| **Swiss AI Apertus-v1.5-8B** | Apache-2.0, `gated=auto` | [HF API](https://huggingface.co/api/models/swiss-ai/Apertus-v1.5-8B) | No threshold; access needs HF login and accepting terms | none beyond Apache-2.0 | card not read (gated) |
| **EuroLLM-9B-Instruct-2512** | Apache-2.0 | [HF API](https://huggingface.co/api/models/utter-project/EuroLLM-9B-Instruct-2512) | No threshold | none beyond Apache-2.0 | none noted |
| **Microsoft Phi-4-reasoning-vision-15B** | MIT | [HF listing](https://huggingface.co/api/models?author=microsoft&search=phi&sort=createdAt&direction=-1) | Plain MIT; no Phi-5 found | keep MIT notice | none noted |
| **Third-party quantised builds** (`nvidia/Qwen3-8B-NVFP4`, `RedHatAI/Qwen3-8B-NVFP4`, `-FP8-dynamic`, `Qwen3-8B-AWQ`) | Apache-2.0 on the repos checked (the nvidia card links the Apache 2.0 text) | [nvidia card](https://huggingface.co/nvidia/Qwen3-8B-NVFP4) | Check against the base model's terms (my inference); the nvidia card says the model is "not owned or developed by NVIDIA" | per base | check each repo's own licence field |

**Interpretation** (my inference). Threshold clauses use different metrics, measured on different entities, and have different carve-outs:

| Metric | Where | Measured on |
|---|---|---|
| Monthly active users above 700M | Llama 4 | licensee and affiliates, preceding calendar month at release date |
| Monthly active users above 100M or monthly revenue above US$20M | Kimi K2.x, Kimi K3 display clause, Qwen3.8 display clause | the commercial product or service |
| Global consolidated monthly revenue above US$20M, no rights at all | Mistral Modified MIT | the licensee's company or employer |
| MaaS / AI Work Assistant aggregate revenue above US$50M in 12 months | Qwen3.8-Max | licensee and affiliates |
| Any MaaS / AI Work Assistant business | Qwen3.8-Flash-Next | licensee and affiliates |
| MaaS revenue above US$20M in 12 months | Kimi K3 | licensee and affiliates |
| MaaS revenue above US$10B in 12 months, security review | GLM-5.3 | licensee and affiliates |

The Mistral clause is the strictest for a workshop: the test is the whole employer's monthly revenue and there is no internal-use carve-out in the notes. DERIVED in the notes: any lab participant whose employer is above the threshold cannot use Medium 3.5 or Devstral 2 without a commercial licence. By contrast the Qwen3.8 MaaS clause, the Kimi K3 clauses and the GLM-5.3 clause concern selling model access to third parties; internal use is excepted in the Qwen3.8 and Kimi K3 texts. For the Llama EU sentence, DERIVED: for an EU company, the natively multimodal Llama 4 Scout and Maverick are not licensed to the company directly, while text-only Llama 3.1 and 3.3 are; the legal reading is Unverified (not reviewed by counsel). A usage policy that sits next to Apache-2.0 (Muse Glimmer, gpt-oss) is a separate document, so check whether it binds you.

**Workshop decision.** The workshop's pinned models are all Apache-2.0 (section 5.1). Models used in `docs/MODEL-SELECTION.md` candidate runs get a licence row before any lab uses them. Llama and the Mistral Modified-MIT models are named in the lab only as licence case studies, not as lab defaults.

### 11.4 Licences changed recently

**Source facts**

- "Qwen = Apache-2.0" is no longer universally true: most Qwen repos are Apache-2.0, but `Qwen/Qwen3.8-2.4T-A95B` and `Qwen/Qwen3.8-Flash-Next` use custom licences (both from August 2026) ([Qwen3.8-2.4T LICENSE](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/LICENSE), [Flash-Next LICENSE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE)).
- Licence history by family:

| Family | Earlier | Now | Source |
|---|---|---|---|
| Qwen | Qwen3, 3.5, 3.6, 3.8-27B: Apache-2.0 | 3.8-2.4T-A95B: Qwen3.8-Max License; 3.8-Flash-Next: Qwen Community License 1.0 (2026-08) | [HF Qwen listing](https://huggingface.co/api/models?author=Qwen&sort=createdAt&direction=-1&limit=80) |
| Google Gemma | Older Gemma-family repos keep the `gemma` licence tag (e.g. translategemma, 2026-01-12) | Gemma 4 (2026-03 to 2026-05): Apache-2.0 | [gemma-4-12B-it API](https://huggingface.co/api/models/google/gemma-4-12B-it), [google listing](https://huggingface.co/api/models?author=google&sort=createdAt&direction=-1&limit=80) |
| Meta | Llama 3.x / 4 community licences; no new `meta-llama` model since April 2025 | Muse Glimmer 30B (2026-08-09): Apache-2.0 + Usage Policy | [meta-llama listing](https://huggingface.co/api/models?author=meta-llama&sort=createdAt&direction=-1) |
| Mistral | Most models Apache-2.0 | Medium 3.5 (2026-03-31) and Devstral 2 (2025-11-28): Modified MIT with US$20M monthly revenue ceiling. Not the "Mistral Research License" | [Medium 3.5 LICENSE](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE) |
| DeepSeek | V3 (Dec 2024): DeepSeek License Agreement v1.0 with use-based restrictions | V3-0324 and R1: MIT; V4.x: MIT | [DeepSeek-V3 LICENSE-MODEL](https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/LICENSE-MODEL), [V3-0324 API](https://huggingface.co/api/models/deepseek-ai/DeepSeek-V3-0324) |
| Moonshot | Kimi K2.x: Modified MIT | Kimi K3 (2026-06): "Kimi K3 License", stricter (MaaS agreement clause plus display rule) | [Kimi-K3 LICENSE](https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE) |
| Zhipu | GLM-5.2, 5.1, 4.7-Flash: MIT | GLM-5.3 (2026-08-25): custom licence with security-review clause; GLM-5.3-Flash stays MIT | [GLM-5.3 LICENSE](https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE) |

- Unverified: whether Qwen will keep releasing sub-30B models under Apache-2.0 after Qwen3.8; the evidence is 27B (Apache) vs Flash-Next and Max (custom). The Qwen3.8-27B repo LICENSE is the stock Apache-2.0 text ([Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B)).

**Interpretation** (my inference). The licence is per repo and per version, not per family or publisher. Within one family, adjacent models can differ (Qwen3.8-27B vs Flash-Next; GLM-5.3 vs GLM-5.3-Flash). A licence found in a blog post, a course slide or a model's earlier version can be wrong for the checkpoint you pin. There is no clean size pattern: Mistral Large 3 (675B) is Apache-2.0 while Medium 3.5 (128B) is Modified MIT.

**Workshop decision.** The licence is read from the repo at the pinned SHA on the day of pinning, and re-checked when the pin changes. `docs/MODEL-SELECTION.md` includes the above table as "licence drift" evidence.

### 11.5 Practical checklist: Publisher / Model / Revision / License / Commercial implications / Source

**Source facts.** The record the course teaches is one row per model with six fields. Rows below are filled from the notes for the pinned models and three non-trivial examples.

| Publisher | Model | Revision | License | Commercial implications | Source |
|---|---|---|---|---|---|
| Qwen | Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | Apache-2.0 | No scale threshold or naming duty in the text; notice duties per Apache-2.0 text | [LICENSE](https://huggingface.co/Qwen/Qwen3-8B/blob/main/LICENSE) |
| Qwen | Qwen3-8B-FP8 | `220b46e3b2180893580a4454f21f22d3ebb187d3` | Apache-2.0 | As above | [HF API](https://huggingface.co/api/models/Qwen/Qwen3-8B-FP8) |
| Qwen | Qwen3-1.7B | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | Apache-2.0 | As above | [LICENSE](https://huggingface.co/Qwen/Qwen3-1.7B/blob/main/LICENSE) |
| Qwen | Qwen3-Embedding-0.6B | `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3` | Apache-2.0 (card front-matter; no `license_link` field) | As above | [HF API](https://huggingface.co/api/models/Qwen/Qwen3-Embedding-0.6B) |
| Qwen | Qwen3-30B-A3B-FP8 | `d206ba732169f29bb77fbf80fc2c4b81d4d30782` | Apache-2.0 | As above | [HF API](https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B-FP8) |
| Qwen | Qwen3-8B-GGUF | `7c41481f57cb95916b40956ab2f0b139b296d974` | Apache-2.0 | As above; the repo carries its own `LICENSE` file | [HF API](https://huggingface.co/api/models/Qwen/Qwen3-8B-GGUF) |
| Mistral AI | Mistral-Medium-3.5-128B | `22b2b868a15677cfa6061277ed2f653d1349a9ab` | Modified MIT | No rights if licensee's (or employer's) global consolidated monthly revenue exceeds US$20M; covers derivatives and third-party hosting | [LICENSE](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE) |
| Meta | Llama-4-Scout-17B-16E-Instruct | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` | Llama 4 Community License + AUP | 700M MAU licence request; "Built with Llama"; "Llama" name prefix on derived models; Notice file; EU multimodal clause in AUP; gated manual | [llama.com licence](https://www.llama.com/llama4/license/), [AUP](https://www.llama.com/llama4/use-policy/) |
| Qwen | Qwen3.8-Flash-Next | `de4b8e4d43b917e7706784d8bb445c9af86a3540` | Qwen Community License 1.0 | Any MaaS or AI Work Assistant business needs a separate licence; model-name display above 100M MAU or US$20M monthly revenue | [LICENSE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE) |

**Checklist steps** (the course method; my synthesis of the facts above).

1. Resolve the full 40-hex SHA and write it in the Revision column (4.1). Record the date.
2. Compare three places, because they can differ: the HF licence tag or card front matter, the `LICENSE` file at that SHA, and any separate policy file (AUP, `USAGE_POLICY`). The Llama EU clause is in the AUP, not in the licence text; Muse Glimmer and gpt-oss add a policy next to Apache-2.0.
3. Find every threshold and what it is measured on: users, monthly revenue, trailing-12-month MaaS revenue, or the employer's revenue (11.3 table).
4. Find naming duties: display strings, name prefixes, `Notice` files, notice retention.
5. Find use restrictions and territorial limits.
6. Check gating (`gated` = `False`, `auto`, `manual`) and whether participants need accounts (4.4).
7. For quantised or fine-tuned third-party builds, read that repo's own licence field and the base model's terms.
8. State the commercial implication in one sentence for your own situation, and note what you could not determine. This is not legal advice; for anything beyond internal evaluation, ask counsel.

**Interpretation** (my inference). The Revision column is what makes the row auditable, since a licence can change at a later commit. The Source column should be the licence file URL at that revision, not the model card summary.

**Workshop decision.** `docs/MODEL-SELECTION.md` carries this table as the lab deliverable: each group fills one row per candidate model before recommending it. `config/models.yaml` stores the Revision and License for each pinned model.

## 12. EU regulatory information

Verified 2026-10-14. This section is engineering context, not legal advice. Every legal statement below is a short quote or a paraphrase with its article number. "LEGAL TEXT" means binding text; "GUIDANCE" means non-binding Commission, EDPB or BSI material and is labelled as such.

Source-access note: `eur-lex.europa.eu` returns an HTTP 202 bot challenge to non-browser clients. The notes read the legal acts as XHTML from the Publications Office instead (`curl -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" https://publications.europa.eu/resource/celex/<CELEX>`; CELEX 32024R1689 AI Act, 32026R1744 Omnibus, 32016R0679 GDPR). Permalinks for readers: AI Act `http://data.europa.eu/eli/reg/2024/1689/oj`, Digital Omnibus on AI `http://data.europa.eu/eli/reg/2026/1744/oj`, GDPR `http://data.europa.eu/eli/reg/2016/679/oj`. ([Publications Office, AI Act](https://publications.europa.eu/resource/celex/32024R1689))

### 12.1 AI Act roles: provider, deployer, and when a deployer becomes a provider

**Source facts**

- Art. 3(1): an 'AI system' is "a machine-based system that is designed to operate with varying levels of autonomy" and that "infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(3): a 'provider' "develops an AI system or a general-purpose AI model or that has an AI system or a general-purpose AI model developed" and places it on the market or puts it into service "under its own name or trademark, whether for payment or free of charge". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(4): a 'deployer' is a person or body "using an AI system under its authority except where the AI system is used in the course of a personal non-professional activity". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(11): 'putting into service' is "the supply of an AI system for first use directly to the deployer or for own use in the Union for its intended purpose". An in-house system for own use can therefore make the builder a provider. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(9): 'placing on the market' is "the first making available of an AI system or a general-purpose AI model on the Union market". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(66) 'general-purpose AI system' is an AI system "based on a general-purpose AI model"; Art. 3(68) 'downstream provider' is a provider of an AI system "which integrates an AI model, regardless of whether the AI model is provided by themselves" or by another entity. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 25(1) applies to high-risk AI systems only. A "distributor, importer, deployer or other third-party" is considered a provider if they (a) "put their name or trademark on a high-risk AI system already placed on the market", (b) "make a substantial modification to a high-risk AI system" that remains high-risk, or (c) "modify the intended purpose of an AI system, including a general-purpose AI system" so that it becomes high-risk. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 3(23) 'substantial modification' is a change "not foreseen or planned in the initial conformity assessment" that affects Chapter III Section 2 compliance or the intended purpose. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- The Omnibus replaced Art. 25(2) and (4): the initial provider "shall no longer be considered to be a provider of that specific AI system" and must cooperate with the new provider. The Art. 25(4) written-agreement duty now also names "AI model" suppliers and still exempts free and open-source "tools, services, processes, or components, other than general-purpose AI models". ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Art. 2(8): the Regulation "does not apply to any research, testing or development activity regarding AI systems or AI models prior to their being placed on the market or put into service". Testing in real-world conditions is not covered by that exclusion. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 2(12): the Regulation "does not apply to AI systems released under free and open-source licences, unless" they are placed on the market as high-risk or fall under Art. 5 or Art. 50. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- GUIDANCE, Commission Art. 50 guidelines C(2026) 5054 final, para (11): a company that takes an existing generative AI system, modifies it (for example "with new training data") and puts it into service under its own name "becomes a provider of the new system". ([Art. 50 guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf))

**Interpretation** (my inference): there are two separate role tests. Art. 25 is the high-risk test. The Art. 50 and GPAI role tests follow who develops, names or puts into service the system or model. A team that wraps a vLLM-served open model into its own named chatbot is likely the provider of that AI system, not only a deployer. Open-source licensing of the system does not exempt it from Art. 50 (Art. 2(12)).

**Workshop decision**: `docs/DIGITAL-SOVEREIGNTY.md` should state the role questions as engineering checklist items (who names it, who puts it into service, is it high-risk) and give no legal conclusion. The workshop itself serves third-party models pinned in `config/models.yaml`.

### 12.2 AI literacy (Art. 4)

**Source facts**

- Art. 4 as adopted: providers and deployers "shall take measures to ensure, to their best extent, a sufficient level of AI literacy of their staff and other persons dealing with the operation and use of AI systems on their behalf". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 4(1) as replaced by the Omnibus (in force 27 July 2026): providers and deployers "shall take measures to support the development of AI literacy of their staff". "This obligation does not require providers or deployers to guarantee any specific level of AI literacy of any individual." Art. 4(2): the Commission and Member States "shall support and facilitate" those efforts. ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Chapters I and II (so Art. 4 and the Art. 5 prohibitions) apply from 2 February 2025 (Art. 113(a)). ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))

**Interpretation** (my inference): the duty moved from "ensure a sufficient level" to "support the development of". It is still in force. A hands-on operating workshop is one way to support it, but the notes do not say any training format satisfies Art. 4.

**Workshop decision**: no compliance claim is made for the workshop. `docs/DIGITAL-SOVEREIGNTY.md` should mention Art. 4 only as background and quote the post-Omnibus wording.

### 12.3 Art. 50 transparency: who is obligated and from when

**Source facts**

| Paragraph | Obligated | Duty (paraphrase or short quote) |
|---|---|---|
| Art. 50(1) | providers | AI systems intended to interact directly with natural persons are "designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system", unless obvious to a reasonably well-informed person |
| Art. 50(2) | providers | outputs of systems "including general-purpose AI systems, generating synthetic audio, image, video or text content" are "marked in a machine-readable format and detectable as artificially generated or manipulated"; exception for an "assistive function for standard editing" or no substantial alteration of input |
| Art. 50(3) | deployers | of emotion-recognition or biometric-categorisation systems "shall inform the natural persons exposed thereto of the operation of the system" |
| Art. 50(4) | deployers | deep fakes: "shall disclose that the content has been artificially generated or manipulated"; AI text published "with the purpose of informing the public on matters of public interest" must be disclosed too, unless it "has undergone a process of human review or editorial control" |
| Art. 50(5) | all | information "in a clear and distinguishable manner at the latest at the time of the first interaction or exposure" |

Source for the table: ([AI Act, Art. 50](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)).

- Application: the Regulation "shall apply from 2 August 2026" (Art. 113, first paragraph); Art. 50 is not carved out. Commission guideline para (153): "Article 50 AI Act will apply as from 2 August 2026". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj); [Art. 50 guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf))
- Art. 99(4)(g): non-compliance with Art. 50 transparency obligations is subject to fines up to EUR 15 000 000 or 3 % of total worldwide annual turnover, whichever is higher. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- GUIDANCE: the guidelines are C(2026) 5054 final, Brussels 20.7.2026. A draft was published 8 May 2026 for consultation. ([Commission page](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content))
- GUIDANCE: "Providers must comply with the relevant transparency obligations in Article 50(1) and (2)". An in-house chatbot put into service "for its own use and under its name or trademark" makes the organisation a provider. ([Art. 50 guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf))
- GUIDANCE, paras (23)-(24): open-source AI systems in scope of Art. 50 still need compliance. Providers of open-source components (software, data, models, tools) "that do not constitute in themselves ... an AI system, are not subject to the transparency obligations in Article 50". (same PDF)
- GUIDANCE: obviousness examples where the Art. 50(1) disclosure is not needed include "An internal employee-facing assistant for properly trained staff who is AI literate" and code-assistance chatbots for professional developers. The exception is limited to cases "where there is almost no doubt left". (same PDF)
- GUIDANCE, paras (72)-(73): providers may use "a single marking technique or a combination of techniques". Recital 133 lists "watermarks, metadata identifications, cryptographic methods for proving provenance and authenticity of content, logging methods, fingerprints". Providers need not keep a full provenance chain. (same PDF)
- GUIDANCE: Code of Practice on Transparency of AI-generated Content, final published 10 June 2026. Section 1 covers providers (marking and detection), Section 2 deployers (labelling deepfakes and AI text). Commission and AI Board confirmed it as "an adequate voluntary tool"; about 190 organisations had signed by end of July 2026. ([Commission page](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content))

**Interpretation** (my inference): providers carry 50(1) and 50(2); deployers carry 50(3) and 50(4). Whether a self-hosting team is a provider depends on who puts the system into service under whose name (see 12.1). All Art. 50 duties are in force on the verification date (2026-10-14), except the Art. 50(2) grace described in 12.7. A deployer-side example is an organisation that publishes unreviewed AI text on matters of public interest.

**Workshop decision**: the workshop apps (`apps/inference-client`, `apps/rag-demo`, `apps/tool-calling-demo`) are teaching apps and the notes give no basis to design a labelling feature; `docs/DIGITAL-SOVEREIGNTY.md` should list Art. 50 as a design input for teams that put a system into service.

### 12.4 GPAI obligations, open-source exemption, systemic-risk threshold

**Source facts**

- Art. 3(63): a 'general-purpose AI model' "displays significant generality and is capable of competently performing a wide range of distinct tasks"; models "used for research, development or prototyping activities before they are placed on the market" are excluded. Art. 3(65): 'systemic risk' is "a risk that is specific to the high-impact capabilities of general-purpose AI models". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Systemic-risk threshold, Art. 51(2): a GPAI model "shall be presumed to have high impact capabilities" when "the cumulative amount of computation used for its training measured in floating point operations is greater than 10^25". Art. 51(3): the Commission may amend the threshold by delegated act. Art. 52(1): the provider must notify the Commission "without delay and in any event within two weeks". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 53(1), all GPAI providers: (a) technical documentation (Annex XI); (b) information for downstream AI-system providers (Annex XII); (c) "a policy to comply with Union law on copyright and related rights"; (d) "a sufficiently detailed summary about the content used for training ... according to a template provided by the AI Office". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Open-source exemption, Art. 53(2): obligations 53(1)(a) and (b) "shall not apply to providers of AI models that are released under a free and open-source licence" with publicly available weights, architecture and usage information. "This exception shall not apply to general-purpose AI models with systemic risks." Art. 53(1)(c) and (d) are not exempted. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 54(1) and (6): third-country GPAI providers must appoint an EU authorised representative; the duty does not apply to qualifying open-source providers "unless the general-purpose AI models present systemic risks". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 55(1), systemic-risk providers additionally: model evaluation including "adversarial testing"; assess and mitigate systemic risks; report "serious incidents" to the AI Office; ensure "an adequate level of cybersecurity protection for the general-purpose AI model with systemic risk and the physical infrastructure of the model". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 53(4)/55(2): providers "may rely on codes of practice within the meaning of Article 56 to demonstrate compliance ... until a harmonised standard is published". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Recital 103 (interpretive): components "provided against a price or otherwise monetised, including through the provision of technical support" do not benefit from the open-source exceptions; "making AI components available through open repositories should not, in itself, constitute a monetisation". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Recital 97 (interpretive): model obligations "should in any case not apply when an own model is used for purely internal processes that are not essential for providing a product or a service to third parties and the rights of natural persons are not affected". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Art. 111(3): GPAI providers whose models were placed on the market before 2 August 2025 "shall take the necessary steps in order to comply ... by 2 August 2027". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Fines: Art. 101(1) lets the Commission fine GPAI providers up to 3 % of annual worldwide turnover or EUR 15 000 000, whichever is higher, for intentional or negligent infringement. Art. 113(b) applied Chapter V from 2 August 2025 "with the exception of Article 101", so GPAI fines are enforceable from 2 August 2026. ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- GUIDANCE, Commission GPAI Q&A: "From 2 August 2026 onwards" the Commission enforces full compliance including fines. In the first year the AI Office treats providers not yet fully compliant with their Code commitments "as acting in good faith". ([Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/guidelines-obligations-general-purpose-ai-providers))
- GUIDANCE, GPAI guidelines C(2025) 5045 final (18.7.2025), para (17): the indicative GPAI criterion is training compute "greater than 10^23 FLOP" plus the ability to "generate language (whether in the form of text or audio), text-to-image or text-to-video". ([GPAI guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2025-07/guidelines_on_the_scope_of_the_obligations_for_generalpurpose_ai_models_established_by_regulation_1cx2atxgq79us4n3x8jfgyy1qlm_118340-3.pdf))
- GUIDANCE, guidelines paras (72)-(92): the open-source licence must allow "access, use, modification, and distribution". Disqualifiers: non-commercial-only licences, usage restrictions "triggered by user scale thresholds", separate commercial licences. Monetisation (dual licensing, paid support "indistinguishably linked" to the model, hosting-only behind payment) removes the exemption. Processing personal data as a condition of access counts as monetisation unless "exclusively and strictly limited to the security of the model". The exemption never covers 53(1)(c) or (d). (same PDF)
- GUIDANCE, para (53): placing-on-market examples include "copied onto a customer's own infrastructure". (same PDF)
- GUIDANCE, training-content summary template: applies to "Any provider of general-purpose AI models, including those with systemic risks", open-source models included; public "no later than when a model is placed on the Union market"; for models placed before 2 Aug 2025 by 2 Aug 2027; enforcement from 2 Aug 2026. Three sections: general information, list of data sources, data-processing aspects. ([Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content))
- GUIDANCE, GPAI Code of Practice, published 10 July 2025; chapters Transparency, Copyright (all GPAI providers) and Safety and Security (systemic-risk providers, Art. 55 only). Commission and AI Board confirmed it as an "adequate voluntary tool". Signatories include Amazon, Anthropic, Google, IBM, Microsoft, Mistral AI, OpenAI; xAI signed only Safety and Security. Commission page last updated 7 Oct 2026. ([Commission page](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai))

**Interpretation** (my inference): a licence with usage-scale thresholds or non-commercial limits may disqualify a model from the Art. 53(2) exemption even if its weights are public. Open-weight does not equal open-source in the Act's sense. The systemic-risk presumption is compute-based (10^25 FLOP). The notes found no primary source on whether the Commission has classified any common open-weight family as systemic-risk. Use the model's own licence text, not a family name, when checking.

**Workshop decision**: `config/models.yaml` pins the models; `docs/MODEL-SELECTION.md` should record the licence per model as a selection criterion next to quality and cost, and `docs/DIGITAL-SOVEREIGNTY.md` should refer to this section for the GPAI duties of the upstream provider.

### 12.5 Commission guidelines on modifiers and fine-tuners

**Source facts** (all GUIDANCE, [GPAI guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2025-07/guidelines_on_the_scope_of_the_obligations_for_generalpurpose_ai_models_established_by_regulation_1cx2atxgq79us4n3x8jfgyy1qlm_118340-3.pdf) unless stated)

- Paras (60)-(62): "The Commission considers a downstream modifier to become the provider of the modified general-purpose AI model only if the modification leads to a significant change in the model's generality, capabilities, or systemic risk." Footnote 11: "fine-tuning" is "one way of 'modifying'".
- Para (63): "an indicative criterion for when a downstream modifier is considered to be the provider of a general-purpose AI model is that the training compute used for the modification is greater than a third of the training compute of the original model".
- Para (64) fallback: if the modifier cannot know the original compute, the threshold is one third of 10^25 FLOP for an original systemic-risk model, otherwise one third of the GPAI-presumption threshold (currently 10^23 FLOP).
- Para (67): "currently few modifications may meet the criterion"; the criterion is "primarily forward-looking". Para (68): for such modifiers the Art. 53(1)(a)-(b) documentation "is limited to information on the modification"; copyright policy and training summary "are limited to the data used as part of the modification". Para (69): they must also comply with Art. 54. Paras (70)-(71): modifying a systemic-risk model past the criterion yields a presumed systemic-risk model (notify under Art. 52(1)).
- Footnote 12: whether the original provider or a downstream actor modifies the model is case by case; "An important factor ... may be who has the control over the model's weights, for example, in case of fine-tuning via API".
- Annex A.2: hardware estimate C = N *L* H *U (GPUs, seconds, peak FLOP/s, utilisation); dense-transformer approximation C ~ 6* P * D (parameters times training tokens). Para (118): "training compute" is "the total amount of compute directly contributing to parameter updates".
- Recital 109 (AI Act): "In the case of a modification or fine-tuning of a model, the obligations for providers of general-purpose AI models should be limited to that modification or fine-tuning". ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj))
- Training summary for such modifiers "covers only the training content used for that modification", names the modified model and references the original summary. ([Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content))
- Commission FAQ: modifiers become providers "only in exceptional cases" when the modification uses "more than one-third of the original model's training compute". ([Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/guidelines-obligations-general-purpose-ai-providers))
- Derived arithmetic (computed by the research agent from Annex A.2.2; not stated in the source): fine-tuning a 7B-parameter model on 1B tokens is about 6 x 7e9 x 1e9 = 4.2e19 FLOP, against a fallback threshold of 1e23 / 3 = 3.3e22 FLOP, roughly three orders of magnitude below. A 70B model on 1B tokens is 4.2e20, still about 80x below. ([GPAI guidelines PDF, Annex A.2](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2025-07/guidelines_on_the_scope_of_the_obligations_for_generalpurpose_ai_models_established_by_regulation_1cx2atxgq79us4n3x8jfgyy1qlm_118340-3.pdf))

**Interpretation** (my inference): ordinary LoRA or full fine-tuning on a domain corpus is far below the indicative criterion, so the fine-tuner normally stays a downstream user of the upstream model. This concerns the GPAI model role. It does not remove system-level duties such as Art. 50 or Art. 25.

**Workshop decision**: the workshop serves pinned third-party models (`config/models.yaml`); `docs/DIGITAL-SOVEREIGNTY.md` should carry the criterion and the derived arithmetic for teams that later fine-tune, labelled as guidance and as derived.

### 12.6 Application timeline (after the Omnibus)

**Source facts**

| Date | What applies | Basis |
|---|---|---|
| 2 Feb 2025 | Chapters I-II: definitions, AI literacy (Art. 4), prohibitions (Art. 5) | Art. 113(a) |
| 2 Aug 2025 | Chapter III Section 4, Chapter V (GPAI), Chapter VII (governance), Chapter XII (penalties), Art. 78, "with the exception of Article 101" | Art. 113(b) |
| 2 Aug 2026 | General application incl. Art. 50 transparency, Art. 101 GPAI fines, national enforcement | Art. 113 |
| 2 Dec 2026 | New prohibitions Art. 5(1)(ba),(bb), 1a, 1b (non-consensual intimate imagery, CSAM generation); Art. 50(2) grace end for systems placed on the market before 2 Aug 2026 | Omnibus |
| 2 Aug 2027 | Pre-Aug-2025 GPAI models compliant (Art. 111(3)); national sandboxes operational (Art. 57(1) as amended) | Art. 111(3); Omnibus |
| 2 Dec 2027 | High-risk requirements for Annex III systems (Chapter III Sections 1-3) | Omnibus |
| 2 Aug 2028 | High-risk Art. 6(1) / Annex I product-embedded systems (original 2 Aug 2027 replaced) | Omnibus |

Sources: ([AI Act, Art. 113](https://eur-lex.europa.eu/eli/reg/2024/1689/oj); [Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj)). The Commission AI Act page (last updated 3 Aug 2026) lists the same milestones and says the Omnibus "entered into force on 27 July 2026". ([Commission AI Act page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai))

**Interpretation** (my inference): on 2026-10-14 the 2 Aug 2026 duties are live and the next dated milestone is 2 Dec 2026.

**Workshop decision**: `docs/DIGITAL-SOVEREIGNTY.md` should reproduce this table with the verification date and say to re-check before each workshop run.

### 12.7 The AI Omnibus amendment: Regulation (EU) 2026/1744

**Source facts**

- Identity: Regulation (EU) 2026/1744 of the European Parliament and of the Council of 8 July 2026 "amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 as regards the simplification of the implementation of harmonised rules on artificial intelligence (Digital Omnibus on AI)"; OJ L 24.7.2026; ELI `http://data.europa.eu/eli/reg/2026/1744/oj`. ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Entry into force: "on the third day following that of its publication in the Official Journal" (Art. 4), i.e. 27 July 2026. Trail from OJ footnotes: EP position 16 June 2026, Council decision 29 June 2026, signed at Strasbourg 8 July 2026; EDPS/EDPB joint opinion 20 January 2026. ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Commission press release of the political agreement is dated 7 May 2026 (IP/26/1024); the Commission proposal was adopted 19 Nov 2025. ([Commission news](https://digital-strategy.ec.europa.eu/en/news/eu-agrees-simplify-ai-rules-boost-innovation-and-ban-nudification-apps-protect-citizens); [Commission AI Act page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai))
- Art. 50 changes, only two textual touches. Art. 50(7) replaced: the Commission, not the AI Office, "shall encourage and facilitate" codes of practice and "shall assess whether adherence ... is adequate to ensure compliance with the obligations laid down in paragraphs 2 and 4"; the power to approve codes by implementing act is gone, the power to specify common rules by implementing act remains. New Art. 111(4): providers of systems generating synthetic content "that have been placed on the market before 2 August 2026 shall take the necessary steps in order to comply with Article 50(2) by 2 December 2026"; recital 38 calls it "a transitional period of four months". ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Art. 50(1)-(5) text, the 2 Aug 2026 start for 50(1), 50(3), 50(4), and the Art. 99(4)(g) fine tier were not changed. Recital 41: codes "have limited legal effect, and in particular do not grant a presumption of conformity". ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- GUIDANCE, Art. 50 guidelines paras 153-154: a partly interactive, partly generative system can use the grace period only for marking; "compliance with the disclosure obligation for AI systems directly interacting with natural persons must be ensured as of 2 August 2026". Content generated before 2 Aug 2026 need not be marked retroactively. ([Art. 50 guidelines PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf))
- GPAI changes: no amendment to Art. 51, 52, 53, 54 or 55 (obligations, 10^25 FLOP presumption, open-source exemption unchanged); the Art. 101 fine regime is untouched. Art. 56(6) replaced: "The Commission, taking utmost account of the opinion of the Board, shall assess whether the codes of practice cover the obligations provided for in Articles 53 and 55". ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Art. 75(1) replaced: the AI Office is "exclusively competent" for AI systems "based on general-purpose AI models where the model and the system are developed by the same provider" (with carve-outs for Annex I products, Annex III point 2, certain law-enforcement and financial uses, and justice) and for AI systems integrated into designated VLOPs/VLOSEs. New Arts. 75a-75d give the AI Office market-surveillance powers, inspections, commitments, fines and periodic penalty payments. ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Other changes: new Art. 4a lets providers "exceptionally process special categories of personal data" for bias detection and correction under conditions; Art. 27(4) lets a deployer cross-reference a GDPR Art. 35 DPIA from the Art. 27 fundamental-rights impact assessment; Art. 99(4) gains point (da) for Art. 25(2) and (4); Art. 99(6a) extends the lower-of-two fine cap to small mid-caps; new Annex XIV lists "AIH 0301 generative AI systems, including AI systems based on general-purpose AI models" and "AIH 0401 ... other emerging AI technologies ... including Agentic AI". ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Art. 2(7) as replaced: "Union law on the protection of personal data, privacy and the confidentiality of communications applies to personal data processed in connection with the rights and obligations laid down in this Regulation." ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Caution: the Omnibus also amends Regulation (EU) 2018/1139 Art. 50 (aviation). That is unrelated to AI Act Art. 50. ([Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- Caution: this is the AI Omnibus. The separate Digital Omnibus on GDPR, ePrivacy, Data Act and NIS2 was proposed on 19 Nov 2025; the Commission Digital Rulebook page (updated 27 July 2026) only calls it "proposed". ([Commission Digital Rulebook](https://digital-strategy.ec.europa.eu/en/policies/digital-rulebook))

**Interpretation** (my inference): for inference operators the Omnibus changed dates and enforcement mechanics, not the Art. 50 or GPAI substance. The only relief for Art. 50 is the four-month marking grace for pre-existing generative systems.

**Workshop decision**: `docs/REFERENCES.md` should cite Regulation (EU) 2026/1744 by number and ELI so that readers do not rely on older "Omnibus delays Art. 50" summaries.

### 12.8 GDPR articles relevant to inference

**Source facts** (LEGAL TEXT, [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj))

| Article | What the text says (short quote or paraphrase) |
|---|---|
| Art. 4(1), 4(2) | personal data is "any information relating to an identified or identifiable natural person", including "an online identifier"; processing includes "storage" and "retrieval" |
| Art. 5(1)(b),(c),(e),(f), 5(2) | purpose limitation; minimisation "adequate, relevant and limited to what is necessary"; storage limitation "for no longer than is necessary"; integrity and confidentiality; accountability ("able to demonstrate compliance") |
| Art. 6(1)(a)-(f) | lawful bases: consent, contract, legal obligation, vital interests, public task, legitimate interests; 6(1)(f) does not apply "to processing carried out by public authorities in the performance of their tasks" |
| Art. 9(1) | special categories prohibited unless a 9(2) condition applies (for example explicit consent) |
| Art. 25(1), 25(2) | by design: measures "such as pseudonymisation" to implement principles "such as data minimisation"; by default: "only personal data which are necessary for each specific purpose of the processing are processed", covering "the amount of personal data collected, the extent of their processing, the period of their storage and their accessibility" |
| Art. 28(1), 28(2), 28(3) | controllers "shall use only processors providing sufficient guarantees"; processing "only on documented instructions from the controller, including with regard to transfers of personal data to a third country"; no sub-processor without authorisation |
| Art. 30(1), 30(2) | records of processing activities for controllers and processors |
| Art. 32(1) | "appropriate technical and organisational measures to ensure a level of security appropriate to the risk", including "pseudonymisation and encryption", confidentiality, integrity, availability, resilience, timely restoration, regular testing |
| Art. 35(1), 35(3) | impact assessment "prior to the processing" where processing, "in particular using new technologies", "is likely to result in a high risk"; 35(3)(a)-(c): profiling-based decisions with legal effect, large-scale special categories, large-scale public monitoring |
| Chapter V, Art. 44-49 | Art. 44 general principle; Art. 45 adequacy decisions (periodic review "at least every four years"); Art. 46 safeguards (46(2)(c) standard data protection clauses, 46(2)(b) BCRs); Art. 47 BCRs; Art. 48 foreign judgments; Art. 49 derogations |
| Art. 83(4), 83(5) | up to EUR 10 000 000 / 2 % for Arts. 25 to 39; up to EUR 20 000 000 / 4 % for Arts. 5, 6, 7, 9 and transfers under Arts. 44 to 49 |

**Interpretation** (my inference, from the Art. 4 definitions): prompts, responses and logs that relate to an identifiable person are personal data and their storage is processing. The principles of Art. 5 and 25 therefore apply to prompt/response logs (see 13.12). Self-hosting takes a model-API provider out of the data path and leaves the controller duties in place. A rented GPU pod still involves an infrastructure provider, so the Art. 28 and Chapter V questions move to that provider; they do not disappear. A DPIA question arises when the use case involves new technology and high risk (Art. 35(1)).

**Workshop decision**: `docs/SECURITY.md` should link the logging default (request logging off) to Art. 5(1)(c),(e) and Art. 25(2). `docs/DIGITAL-SOVEREIGNTY.md` should list Art. 28 and Chapter V as the questions to ask about every party in the data path, including the GPU provider.

### 12.9 EDPB Opinion 28/2024

**Source facts** (GUIDANCE, adopted 17 December 2024 on a request from the Irish SA under Art. 64(2) GDPR; [EDPB Opinion 28/2024](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf))

- Anonymity: AI models trained on personal data "cannot, in all cases, be considered anonymous". For anonymity "both (1) the likelihood of direct (including probabilistic) extraction of personal data ... and (2) the likelihood of obtaining, intentionally or not, such personal data from queries, should be insignificant", taking into account "all the means reasonably likely to be used". Supervisory authorities assess case by case.
- Legitimate interest: the opinion "recalls that there is no hierarchy between the legal bases" and applies a three-step test (identify the interest; necessity; balancing). An interest is legitimate if lawful, "clearly and precisely articulated" and "real and present". Examples named: a conversational agent to assist users; "improving threat detection in an information system".
- Unlawful development: for a model that retains personal data and is deployed by another controller, supervisory authorities should consider whether the deployer "conducted an appropriate assessment, as part of its accountability obligations ... to ascertain that the AI model was not developed by unlawfully processing personal data".
- The opinion distinguishes mitigating measures from measures "legally required ... anyway".

**Interpretation** (my inference): a team that downloads open weights and serves them is a deployer in the opinion's sense. Documenting a provenance check of the model (model card, licence, training-data statement) is the accountability step the opinion points at.

**Workshop decision**: `docs/MODEL-SELECTION.md` should note, per model, whether a provenance or training-data statement exists; `docs/DIGITAL-SOVEREIGNTY.md` should cite Opinion 28/2024 for the reason.

### 12.10 Transfers: Schrems II and the EU-US Data Privacy Framework

**Source facts**

- CJEU Grand Chamber C-311/18 (16 July 2020): Art. 46 safeguards "must ensure that data subjects ... are afforded a level of protection essentially equivalent to that guaranteed within the European Union"; the assessment covers the contractual clauses and the third country's legal system including public-authority access; Decision 2010/87/EU (SCCs) remained valid; "Commission Implementing Decision (EU) 2016/1250 ... (EU-US Privacy Shield) is invalid." ([CJEU C-311/18](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62018CJ0311))
- Adequacy decision for the DPF: Commission Implementing Decision (EU) 2023/1795 of 10 July 2023. ([CJEU press release](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf))
- General Court T-553/23 Latombe v Commission, 3 September 2025 (Tenth Chamber, extended composition): "Dismisses the action". The Court found the DPRC independence plea unfounded and that Schrems II does not require prior authorisation of bulk collection by an independent authority, only "at a minimum, ex post judicial review". The Commission must monitor continuously and "may decide, if necessary, to suspend, amend or repeal" the decision if US law changes. ([CJEU press release](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf); [judgment](https://publications.europa.eu/resource/celex/62023TJ0553))
- First periodic review report (9 Oct 2024): "the Commission considers it appropriate to carry out the next periodic review after three years" (about late 2027). ([Commission report](https://commission.europa.eu/document/download/25695177-8073-4ce3-bf81-eb816dc6b468_en?filename=Report+on+the+first+periodic+review+of+the+functioning+of+the+adequacy+decision+on+the+EU-US+Data+Privacy+Framework.pdf))
- Unverified: appeal C-703/25 P (lodged 31 Oct 2025, published as C/2025/6610 on 22 Dec 2025, other parties Ireland and the United States) is reported only by secondary sources; no hearing, Advocate General opinion or judgment was found as of mid-Oct 2026. Check InfoCuria before teaching "DPF is settled". ([InfoCuria](https://infocuria.curia.europa.eu/))

**Interpretation** (my inference): the DPF adequacy decision stands at first instance on 2026-10-14 and the reported appeal is unverified. A US-hosted API sends prompts across the Chapter V boundary; an EU-located pod does not, but the question of who operates it remains (see 12.11 on the CLOUD Act).

**Workshop decision**: the workshop pods run in Runpod Secure Cloud, EU (repository fact). `docs/DIGITAL-SOVEREIGNTY.md` should state the region. The notes do not say where the pod operator is headquartered; that has to be checked before the document makes any CLOUD Act statement about it.

### 12.11 Sovereignty frameworks

**Source facts: EU Cloud Sovereignty Framework (CSF)**

- Original: "Cloud Sovereignty Framework, Version 1.2.1, Oct. 2025", DG DIGIT, tied to the Cloud III Dynamic Purchasing System tender (EUR 180 million over six years, launched October 2025). The copy read is a third-party host of the EC PDF. ([PDF copy](https://ppc.land/content/files/2025/11/Cloud-Sovereignty-Framework.pdf); [Commission news 10 Oct 2025](https://commission.europa.eu/news-and-media/news/commission-moves-forward-cloud-sovereignty-eur-180-million-tender-2025-10-10_en))
- Official later document: "Cloud Sovereignty Framework: Implementation guidance" (13 pp.; award to four providers in April 2026 per Commission press). ([Implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en))
- The Commission's June 2026 explainer says the scoring is based on 48 specific criteria and does not mention EUCS. ([Commission explainer](https://commission.europa.eu/news-and-media/news/sovereign-cloud-framework-explained-2026-06-01_en))

Sovereignty dimensions (objectives, weights from v1.2.1) ([PDF copy](https://ppc.land/content/files/2025/11/Cloud-Sovereignty-Framework.pdf)):

| Objective | Dimension | Weight |
|---|---|---|
| SOV-1 | Strategic Sovereignty | 15 % |
| SOV-2 | Legal & Jurisdictional Sovereignty | 10 % |
| SOV-3 | Data & AI Sovereignty | 10 % |
| SOV-4 | Operational Sovereignty | 15 % |
| SOV-5 | Supply Chain Sovereignty | 20 % |
| SOV-6 | Technology Sovereignty | 15 % |
| SOV-7 | Security & Compliance Sovereignty | 10 % |
| SOV-8 | Environmental Sustainability | 5 % |

- Criteria highlights (implementation guidance): SOV-2 includes "exposure to non-EU laws with cross-border reach (e.g., US CLOUD Act, Chinese Cybersecurity Law)". SOV-3 includes "only the customer, not the provider, has effective control over cryptographic access to their data", "auditability of AI model usage", "Strict confinement of storage and processing to European jurisdictions, with no fallback to third countries", and AI models/pipelines "developed, trained, hosted, and governed under EU control". SOV-4 includes "Ease of migrating workloads ... without vendor lock-in". SOV-5 includes origin of hardware, firmware, software packaging/updates. SOV-6 includes open licences with "rights to audit, modify, and redistribute" and non-proprietary APIs. SOV-7 includes security monitoring/logging oversight by customer or EU authority and "maintenance Autonomy". SOV-8 includes PUE, circularity, emissions disclosure. ([Implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en))
- SEAL (Sovereignty Effective Assurance Level): SEAL-0 No Sovereignty; SEAL-1 Jurisdictional Sovereignty; SEAL-2 Data Sovereignty; SEAL-3 Digital Resilience (v1.2.1) or "Technological Sovereignty" (implementation guidance wording); SEAL-4 Full Digital Sovereignty ("no critical non-EU dependencies"). The contracting authority sets a minimum SEAL per objective; the Sovereignty Score only ranks offers that clear the minimum. Caution: SEAL-3 is named differently in the two documents. ([PDF copy](https://ppc.land/content/files/2025/11/Cloud-Sovereignty-Framework.pdf); [Implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en))
- Lessons learnt (Commission): SEAL-4 "is not today relevant ... considering existing dependence to specific supply chains (chips, hardware)"; self-declaration is a heavy verification burden. ([Implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en))

**Source facts: BSI C5 and C3A**

- BSI published C5:2026 on 7 April 2026: new dedicated treatment of container management, confidential computing and post-quantum cryptography; supply chain and multi-tenant separation treated more specifically. The press release says sovereignty criteria are not part of C5:2026 and will be published separately. ([BSI press release](https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260407_C5_Cloud_Computing.html))
- The BSI C5 page lists both "C5:2026" and "C5:2020" and says the catalogue was "completely revised in 2025/26". ([BSI C5 page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Empfehlungen-nach-Angriffszielen/Cloud-Computing/Kriterienkatalog-C5/kriterienkatalog-c5_node.html))
- BSI published C3A "Criteria enabling Cloud Computing Autonomy" on 27 April 2026. It "follows" the EU CSF in structure and objectives, assumes the provider already meets C5, has no regulatory effect, will get C5-like audits, and allows localisation requirements (data-centre location, origin of operating staff). ([BSI press release](https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260427_C3A.html); [BSI C3A page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Empfehlungen-nach-Angriffszielen/Cloud-Computing/C3A/C3A.html))

**Source facts: EUCS, Gaia-X, CLOUD Act**

- EUCS: ENISA's certification-framework page lists EUCS (cloud services) among "Schemes under development"; EUCC is the only published scheme listed. The only ENISA EUCS document found is the draft candidate scheme dated 22 Dec 2020 ("This publication is a draft version"). ([ENISA framework page](https://www.enisa.europa.eu/topics/product-security-and-certification/cybersecurity-certification-framework); [ENISA EUCS draft](https://www.enisa.europa.eu/publications/eucs-cloud-service-scheme))
- Gaia-X Compliance Document marketing summary (9 July 2025): Standard Compliance plus Label Levels 1-3. Level 1 = "standard data protection and security following European laws" (declaration-based). Level 2 adds cybersecurity criteria verified by third-party Conformity Assessment Bodies and an option for EEA-only processing. Level 3 requires data processed exclusively in the EEA and provider "headquarters and the main establishments" in the EEA. Built on standards "such as ISO/IEC 27001 and BSI C5". Gaia-X goals: transparency, autonomy, data protection, security, interoperability, portability, sustainability, European control. ([Gaia-X summary](https://gaia-x.eu/wp-content/uploads/2024/09/Compliance-Document_Marketing-Summary-2024.pdf))
- CLOUD Act, LEGAL TEXT 18 U.S.C. § 2713 (added by Pub. L. 115-141, 23 Mar 2018): a provider "shall comply with the obligations of this chapter to preserve, backup, or disclose the contents of a wire or electronic communication" and related records "within such provider's possession, custody, or control, regardless of whether such communication, record, or other information is located within or outside of the United States." One line: US-jurisdiction providers can be compelled to disclose data they control even if stored abroad. ([Cornell LII](https://www.law.cornell.edu/uscode/text/18/2713))

**Interpretation** (my inference, editorial mapping from the notes, not a source claim): the workshop's sovereignty formula elements map onto CSF objectives as follows.

| Workshop element | Closest CSF objectives | Gap / note |
|---|---|---|
| DATA | SOV-3, SOV-2 | CSF adds customer-held keys and "no fallback to third countries" |
| MODEL | SOV-3, SOV-6 | AI Act GPAI duties (Art. 53) are a separate legal axis |
| INFRASTRUCTURE | SOV-5, SOV-1, SOV-8 | accelerator provenance is where the CSF says SEAL-4 is unrealistic today |
| OPERATIONAL CONTROL | SOV-4, SOV-7 | includes patch autonomy and EU-controlled logging |
| PORTABILITY | SOV-4, SOV-6 | lock-in, migration, non-proprietary APIs |
| not in formula | SOV-1 Strategic, SOV-8 Environmental | candidate additions or explicit exclusions |

Sovereignty is an architecture property with trade-offs: the Commission's lessons-learnt text calls SEAL-4 "not today relevant" given dependence on chip and hardware supply chains.

**Workshop decision**: `docs/DIGITAL-SOVEREIGNTY.md` should use the CSF objectives as the vocabulary for the comparison, mark SEAL-4 as "not today relevant" per the Commission, and mark EUCS as "listed as under development by ENISA, adoption unverified".

### 12.12 Not verified (section 12)

- Unverified: COM numbers of the November 2025 proposals (secondary sources say COM(2025) 836 for the AI part and COM(2025) 837 for the data/GDPR part); the Publications Office did not serve either document.
- Unverified: status of the separate Digital Omnibus (GDPR, ePrivacy, Data Act, NIS2) proposed 19 Nov 2025. Secondary sources (Sept-Oct 2026) report no Council mandate or Parliament committee vote; the EDPB-EDPS joint opinion (Feb 2026) opposed the narrowed "personal data" definition. Treat GDPR as unchanged.
- Unverified: appeal outcome and any hearing, AG opinion or judgment in C-703/25 P; the reported appeal details (31 Oct 2025, C/2025/6610, 22 Dec 2025); one unverified post that Microsoft was granted leave to intervene; one snippet of an order dated 4 June 2026.
- Unverified: 2026 developments in US oversight bodies (for example PCLOB composition) and any Commission reaction.
- Unverified: chapter-level commitments of the GPAI Code of Practice (for example robots.txt handling, output-infringement mitigation); publication date of the training-summary template (the FAQ shows only "Last update 26 March 2026").
- Unverified: whether the Commission has classified any common open-weight family as GPAI-with-systemic-risk or published the Art. 52(6) list.
- Unverified: BSI C5:2026 transition rule (C5:2026 recommended for audit periods ending on or after 1 June 2027) and criteria counts (168 vs 121); they come from search-result summaries, not an opened BSI page.
- Unverified: any 2026 adoption of EUCS; the date the ENISA framework page was last edited.
- Unverified: whether a Gaia-X compliance document newer than the 2025 releases exists.
- Caution: the CSF v1.2.1 text was read from a third-party host (ppc.land), not from a Commission URL.

---

## 13. Security of self-hosted inference

Verified 2026-10-14. Not legal advice. GUIDANCE labels mark non-binding material.

Source-access note: the GitHub MCP connector was unavailable in the research session (credential expired). GitHub advisory and issue data below was pulled from the public REST API `https://api.github.com/repos/vllm-project/vllm/...`. ([GitHub API](https://api.github.com/repos/vllm-project/vllm/security-advisories))

### 13.1 Two layers: infrastructure security and LLM application security

**Source facts**

- The notes treat the layers separately. Infrastructure (the serving process, its network, images, weights, cache, logs) is covered by the vLLM security guide and CVE advisories. Application (prompts, tools, agents, outputs) is covered by OWASP, NIST and MCP material. ([vLLM security guide](https://docs.vllm.ai/en/latest/usage/security/); [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/))

**Interpretation** (my inference): authenticating the endpoint does not make the model's behaviour safe, and a well-filtered prompt does not help if the control plane is reachable. Both layers need an owner.

**Workshop decision**: `docs/SECURITY.md` should be split into the two layers. Layer 1 is the pod boundary (127.0.0.1 binding, `--api-key`, SSH access, pinned image). Layer 2 is application behaviour (prompt injection, tool permissions in `apps/tool-calling-demo`).

### 13.2 vLLM exposure facts

**Source facts** ([vLLM security guide](https://docs.vllm.ai/en/latest/usage/security/) unless stated)

- Default bind: `--host` default is `None`; in source `sock_addr = (args.host or "", args.port)` and the printed listen address falls back to `"0.0.0.0"`, i.e. all interfaces unless `--host` is set. `--allowed-origins` defaults to `["*"]` (read in `vllm/entrypoints/launchers/cli_args.py` of the installed v0.31.0 package on a live pod; an earlier reading of the CLI documentation as `[]` was wrong), so a browser page can call a reachable server cross-origin. `--disable-fastapi-docs` hides Swagger/ReDoc. ([launcher.py](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/launchers/launcher.py); [vllm serve CLI](https://docs.vllm.ai/en/latest/cli/serve/))
- `--api-key` / `VLLM_API_KEY` authenticates only the `/v1`, `/v2`, `/inference` and `/cohere` prefixes. Unauthenticated endpoints include `/invocations`, `/pooling`, `/classify`, `/score`, `/rerank`, `/metrics`, `/tokenize`, `/detokenize`, `/health`, `/version`, `/load`. Operational controls such as `/pause`, `/abort_requests`, `/update_weights`, `/scale_elastic_ep` are unauthenticated when generation is supported. Recommended: a reverse proxy that allowlists endpoints and adds authentication, rate limiting and logging.
- Caution: the premise "vLLM has no built-in TLS" is wrong. The API server supports `--ssl-keyfile`, `--ssl-certfile`, `--ssl-ca-certs`, `--ssl-cert-reqs` (default 0), `--enable-ssl-refresh`, `--ssl-ciphers` ("TLS 1.2 and below only"). What is missing is mutual TLS between internal nodes (PyTorch Distributed, KV transfer). ([vllm serve CLI](https://docs.vllm.ai/en/latest/cli/serve/))
- Inter-node traffic is "insecure by default and must be protected by placing the nodes on an isolated network". PyTorch Distributed has unencrypted messages, no authorization protocol and accepts connections from anywhere; `TCPStore` "listens on all network interfaces" by default. Set `VLLM_HOST_IP`, `--kv-ip/--kv-port`, `data_parallel_master_ip/port`. Cache contents load without integrity checks, including formats allowing arbitrary code execution. Ray: the whole cluster is one trust domain.
- Multi-tenancy: vLLM does not isolate tenants sharing a process; run one instance per tenant or use an authenticating gateway. For prefix-cache timing attacks (CVE-2025-46570) use `cache_salt` with a random secret of about 256 bits scoped to the tenant.
- Dangerous toggles: `VLLM_SERVER_DEV_MODE=1` (cache reset, sleep, `/collective_rpc`, config disclosure; "never" in production); `VLLM_ALLOW_RUNTIME_LORA_UPDATING=True` (dynamic LoRA "not a secure operation"); `--enable-tokenizer-info-endpoint`; `--trust-request-mm-kwargs`; `--tool-server demo` (Docker Python interpreter with no network isolation by default, may reach LAN and cloud metadata); endpoint plugins via `VLLM_PLUGINS` are trusted code; `--grpc-port` has no authentication, authorization or encryption.
- Resource-limit variables: `VLLM_MAX_N_SEQUENCES` (default 16384; docs suggest 64 or 128 for public deployments), `VLLM_MEDIA_URL_ALLOW_REDIRECTS=0`, `VLLM_MAX_MEDIA_DOWNLOAD_SIZE_MB` and related decode caps (0 disables the cap), `VLLM_P2P_MAX_PEERS`. FIPS: use `--mm-hasher-algorithm sha256`/`sha512` instead of blake3; add mTLS/IPsec for inter-node traffic.
- Security policy: report privately; CVSS bands (Critical >= 9.0 ... Low < 4.0); critical and high are fixed in a private fork with pre-notification, moderate and low via public PRs; "A CVE is requested when a fix is merged." ([SECURITY.md](https://github.com/vllm-project/vllm/blob/main/SECURITY.md))

**Interpretation** (my inference): the workshop's 127.0.0.1 binding makes the unauthenticated endpoints (`/metrics`, `/health`, `/tokenize`, control endpoints) reachable only from the pod itself and from SSH tunnels, which is why a bound loopback address plus `--api-key` is a reasonable pair for a shared pod. `--api-key` alone does not protect the endpoints listed above, and the pod becomes exposed if `--host` is ever changed. Cloud-metadata reach is a concern for `--tool-server demo` and the media-fetching paths.

**Workshop decision**: profiles in `config/vllm-profiles/*.yaml`, rendered by `infra/pod/render-profile.py` and run by `infra/pod/wsctl`, keep the explicit loopback bind (127.0.0.1:8000, embedding on 127.0.0.1:8001) and `--api-key`. `docs/SECURITY.md` should list the dev-mode and toggle variables above as "do not set". Unverified: that the profiles currently set none of them; the notes did not read the profile files.

### 13.3 vLLM CVEs (GitHub security advisories, API pull 2026-10-14)

**Source facts**

- Totals: 104 published advisories (27 in 2025, 77 in 2026). 2025: 3 critical, 10 high, 12 medium, 2 low. 2026: 2 critical, 17 high, 54 medium, 4 low. 78 of the 2025-26 advisories carry a CVE id. Per-advisory URL pattern `https://github.com/vllm-project/vllm/security/advisories/<GHSA id>`. ([vLLM advisories](https://github.com/vllm-project/vllm/security/advisories))
- Caution: several 2026 CVE ids in the API output have six digits (for example CVE-2026-105753); the list below reproduces them as GitHub lists them.

Authentication and network exposure (most relevant for the workshop):

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2026-48746](https://github.com/vllm-project/vllm/security/advisories/GHSA-94f4-hr76-p5j6) | critical 9.1, 2 Jun 2026 | `--api-key` bypass: callers can skip the API-key check on the OpenAI-compatible endpoints by injecting special characters into the `Host` header, which ASGI servers and Starlette do not filter (advisory text, re-read 2026-10-14); affected `>=0.3.0`, patched `>=0.22.0` |
| [CVE-2025-59425](https://github.com/vllm-project/vllm/security/advisories/GHSA-wr9h-g72x-mwhm) | high 7.5, 7 Oct 2025 | API key compared in a timing-attackable way; fixed in 0.11.0 |
| [CVE-2026-73555](https://github.com/vllm-project/vllm/security/advisories) | low, 27 Jul 2026 | unauthenticated internal path and username disclosure via validation errors |

Remote code execution class:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2026-22778](https://github.com/vllm-project/vllm/security/advisories/GHSA-4r2x-xpjr-7cvv) | critical 9.8, 2 Feb 2026 | RCE chain via video processing (PIL error leak plus JPEG2000 heap overflow); default unauthenticated servers; pre-auth via `/invocations`; fixed 0.14.1 |
| [CVE-2026-22807](https://github.com/vllm-project/vllm/security/advisories/GHSA-2pc9-4j83-qjmr) | high 8.8, 21 Jan 2026 | RCE via `auto_map` dynamic module loading during model initialisation |
| [CVE-2025-66448](https://github.com/vllm-project/vllm/security/advisories/GHSA-8fr4-5q9j-m8gm) | high 7.1, 1 Dec 2025 | RCE via `transformers_utils/get_config` |
| [CVE-2026-27893](https://github.com/vllm-project/vllm/security/advisories/GHSA-7972-pg2x-xr59) | high 8.8, 26 Mar 2026 | hard-coded `trust_remote_code=True` in NemotronVL and KimiK25 bypasses the user's opt-out |
| [CVE-2026-90553](https://github.com/vllm-project/vllm/security/advisories/GHSA-3c86-2m5g-59q7) | high 7.8, 28 Aug 2026 | LlavaOnevision2 processor loader executes attacker model code despite `trust_remote_code=False` |
| [GHSA-h3rc-6mm3-gc2m](https://github.com/vllm-project/vllm/security/advisories/GHSA-h3rc-6mm3-gc2m) | high 8.1, 6 Oct 2026, no CVE id yet | request-controlled `mm_processor_kwargs.code_revision` allows RCE when `--trust-remote-code` is enabled; affected `>=0.7.3,<0.31.0` |
| [CVE-2026-41523](https://github.com/vllm-project/vllm/security/advisories/GHSA-q8gq-377p-jq3r) | high 7.5, 14 Jun 2026 | security check implemented with `assert` is skipped under `python -O` / `PYTHONOPTIMIZE=1`, allowing code execution from a malicious Hub model; fixed 0.22.0 |
| [CVE-2025-62164](https://github.com/vllm-project/vllm/security/advisories/GHSA-mrw7-hf4f-83pf) | high 8.8, 20 Nov 2025 | `torch.load()` on user-supplied `prompt_embeds`: memory corruption, DoS, potential RCE; affected `>=0.10.2`, fixed 0.11.1 |
| [CVE-2026-73557](https://github.com/vllm-project/vllm/security/advisories/GHSA-pr7f-p5mw-fc87) | 27 Jul 2026 | bypass of the CVE-2025-62164 remediation via concurrent prompt parts |
| [CVE-2025-24357](https://github.com/vllm-project/vllm/security/advisories/GHSA-rh4j-5rhw-hr54) | high 7.5, 27 Jan 2025 | malicious model RCE via `torch.load` in `hf_model_weights_iterator` |
| [CVE-2025-32434](https://github.com/vllm-project/vllm/security/advisories/GHSA-ggpf-24jw-3fcw) | high 7.5, 22 Apr 2025 | fix bypass with PyTorch < 2.6.0 |
| [CVE-2025-9141](https://github.com/vllm-project/vllm/security/advisories/GHSA-79j6-g2m3-jgfw) | high 8.8, 20 Aug 2025 | RCE in the Qwen3-Coder tool-call parser |

Pickle, ZeroMQ and multi-node:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2025-30165](https://github.com/vllm-project/vllm/security/advisories/GHSA-9pcc-gvx5-r5wm) | high 8.0, 6 May 2025 | V0 multi-node ZMQ RCE; not fixed ("ensure your environment is on a secure network"); V1 not affected |
| [CVE-2025-47277](https://github.com/vllm-project/vllm/security/advisories/GHSA-hjq4-87xh-g4fv) | critical 9.8, 20 May 2025 | PyNcclPipe KV-transfer service accepts malicious serialized data; fixed 0.8.5 |
| [CVE-2025-32444](https://github.com/vllm-project/vllm/security/advisories/GHSA-hj4w-hm2g-p6w5) | critical 10.0, 29 Apr 2025 | pickle over ZeroMQ sockets "set to listen on all network interfaces" in the Mooncake integration |
| [CVE-2025-29783](https://github.com/vllm-project/vllm/security/advisories/GHSA-x3m8-f7g5-qhm7) | critical 9.0, 19 Mar 2025 | same Mooncake pickle-over-ZeroMQ class |
| [CVE-2025-30202](https://github.com/vllm-project/vllm/security/advisories/GHSA-9f8f-2vmf-885j) | high 7.5, 29 Apr 2025 | DoS via ZeroMQ on multi-node |

SSRF:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2025-6242](https://github.com/vllm-project/vllm/security/advisories/GHSA-3f6c-7fw2-ppm4) | high 7.1, 7 Oct 2025 | SSRF in `MediaConnector` |
| [CVE-2026-24779](https://github.com/vllm-project/vllm/security/advisories/GHSA-qh4c-xf7m-gxfc) | high 7.1, 27 Jan 2026 | SSRF |
| [CVE-2026-25960](https://github.com/vllm-project/vllm/security/advisories/GHSA-v359-jj2v-j536) | 9 Mar 2026 | SSRF protection bypass |
| [CVE-2026-34753](https://github.com/vllm-project/vllm/security/advisories/GHSA-pf3h-qjgv-vcpr) | 3 Apr 2026 | SSRF in `download_bytes_from_url` |
| [CVE-2026-73560](https://github.com/vllm-project/vllm/security/advisories/GHSA-4hhp-h66f-j5j7) | 13 Aug 2026 | SSRF plus local file read in the MiMoV2Omni loader |
| [GHSA-vfp2-c8pq-v6h6](https://github.com/vllm-project/vllm/security/advisories/GHSA-vfp2-c8pq-v6h6) | high, 9 Oct 2026 | SSRF via `X-Request-Id` makes a `P2pNcclConnector` prefill worker connect outbound and leak KV-cache tensors; affected `>=0.9.2,<0.24.0` |

Supply chain and build:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2026-54232](https://github.com/vllm-project/vllm/security/advisories/GHSA-jrf6-vqxq-pjv2) | high 8.8, 9 Jun 2026 | dependency confusion in the Dockerfile via `flashinfer-jit-cache` with `--extra-index-url` and `UV_INDEX_STRATEGY="unsafe-best-match"`; could backdoor images ("exfiltration of all user prompts, API credentials, and model data"); `vllm/vllm-openai < 0.22.1`, fixed >= 0.22.1 |
| [CVE-2026-47155](https://github.com/vllm-project/vllm/security/advisories/GHSA-3ww4-5jv9-j5gm) | medium 6.5, 10 Jun 2026 | "Artifact Pin Decay": `--revision` / `--code-revision` pins do not cover all artifacts (dynamic code, GGUF, image processors, side weights). Caution: advisory metadata reads "affected <= 0.22.0, patched 0.22.0"; check the advisory page before quoting a fixed version |

Multi-tenant leakage and cache:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2025-46570](https://github.com/vllm-project/vllm/security/advisories/GHSA-4qjh-9fv9-r85r) | low 2.6, 28 May 2025 | prefix-cache timing side channel |
| [CVE-2025-25183](https://github.com/vllm-project/vllm/security/advisories) | low 2.6, 6 Feb 2025 | Python `hash()` collisions in the prefix cache |
| [CVE-2026-73558](https://github.com/vllm-project/vllm/security/advisories/GHSA-7m6h-x95x-82q5) | medium, 11 Aug 2026 | "Cross-User Data Leak Vulnerability" |
| [CVE-2026-53923](https://github.com/vllm-project/vllm/security/advisories/GHSA-5jv2-g5wq-cmr4) | medium, 11 Jun 2026 | GGUF dequantize kernel exposes uninitialised GPU memory in multi-tenant serving |
| [CVE-2026-105752](https://github.com/vllm-project/vllm/security/advisories/GHSA-935w-9g4m-p28p) | low, 28 Sep 2026 | Harmony tool continuations drop `cache_salt` |
| [GHSA-rh6f-3x46-j33q](https://github.com/vllm-project/vllm/security/advisories/GHSA-rh6f-3x46-j33q) | 6 Oct 2026 | caller-controllable cache keys allow cross-request cache aliasing |
| [CVE-2026-54236](https://github.com/vllm-project/vllm/security/advisories/GHSA-hgg8-fqqc-vfmw) | 11 Jun 2026 | incomplete fix of CVE-2026-22778 leaks PIL repr addresses through the Anthropic-compatible router |

Availability (DoS), representative:

| ID | Severity, date | One line |
|---|---|---|
| [CVE-2025-48956](https://github.com/vllm-project/vllm/security/advisories) | high 7.5, 20 Aug 2025 | HTTP header size limits not enforced |
| [CVE-2026-93592](https://github.com/vllm-project/vllm/security/advisories/GHSA-25q3-v2hm-8vpf) | high 7.5, 3 Sep 2026 | negative token id in `/v1/embeddings` or `/pooling` kills the engine |
| [CVE-2026-34756](https://github.com/vllm-project/vllm/security/advisories) | 3 Apr 2026 | OOM via unbounded `n` |
| [CVE-2026-100647](https://github.com/vllm-project/vllm/security/advisories/GHSA-wpww-v874-ph2p) | 12 Sep 2026 | unbounded `cache_salt` length stalls the scheduler |
| [GHSA-4xqp-c3mv-qff7](https://github.com/vllm-project/vllm/security/advisories/GHSA-4xqp-c3mv-qff7) | 6 Oct 2026 | oversized `min_tokens` hangs the engine "while /health stays green" |
| [GHSA-rhcx-5729-88vg](https://github.com/vllm-project/vllm/security/advisories/GHSA-rhcx-5729-88vg) | 7.7 | cross-tenant DoS |
| [CVE-2026-57173](https://github.com/vllm-project/vllm/security/advisories), [CVE-2026-54233](https://github.com/vllm-project/vllm/security/advisories) | Aug-Oct 2026 | examples of the many multimodal decompression-bomb and EngineCore-crash advisories |

**Interpretation** (my inference): the advisory stream is dominated by four classes: model-loading and remote-code paths, multimodal input handling (SSRF, decompression, parsers), multi-node serialisation, and cache or tenant isolation. A single-model, single-pod, loopback-bound deployment with `trust_remote_code` off and pinned model files is exposed to fewer of them than a multi-node or multi-tenant one. The `--api-key` bypass shows that the key is one control and should not be the only one. `/health` staying green during an engine hang (GHSA-4xqp-c3mv-qff7) is an argument for latency and queue metrics in monitoring, not health checks alone.

The advisory metadata for CVE-2026-48746 lists `>=0.22.0` as patched, and the GHSA-h3rc-6mm3-gc2m range ends below 0.31.0, so the pinned image `v0.31.0` is outside those two ranges. The notes do not state which of the Aug-Oct 2026 advisories are fixed in 0.31.0.

**Workshop decision**: the image is pinned by digest in `infra/versions.env` (engine `vllm/vllm-openai:v0.31.0`), and `docs/SECURITY.md` should record the advisory check date and the rule "do not set `--trust-remote-code` for workshop models" (my recommendation, derived from the RCE rows above; the pinned models are listed in `config/models.yaml`). Dashboards in `monitoring/` should show request latency and queue metrics, not only `/health`; whether they do is not in the notes.

### 13.4 Exposure incidents for local inference servers (Ollama family)

**Source facts**

- SentinelLABS x Censys "Silent Brothers" (29 Jan 2026): 175,108 unique publicly reachable Ollama hosts in 130 countries from 7.23 million observations; about 23,000 persistent hosts generate most activity; at least 201 hosts ran "uncensored" prompt templates. ([SentinelLABS](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/))
- Cisco, "Detecting exposed LLM servers: a Shodan case study on Ollama" (1 Sep 2025): 1,139 exposed instances found by Shodan; 214 (about 18.8 %) responded to a benign unauthenticated prompt; risks listed include unauthenticated API access, model extraction, resource hijacking, and backdoor/poisoning via untrusted models. ([Cisco](https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama))
- Censys "Ollama Drama": 10.6K exposed instances, 1.5K responding to prompts (earlier, narrower study). ([Censys](https://censys.com/blog/ollama-drama-investigating-the-prevalence-of-ollama-open-instances-with-censys/))

**Interpretation** (my inference): the numbers are for Ollama, not vLLM; they show that a default-reachable inference port is found and used within the internet's scanning window. The notes have no equivalent vLLM or llama.cpp measurement.

**Workshop decision**: `docs/SECURITY.md` should use these figures to justify the loopback-only bind and SSH access path, and state that they are about Ollama.

### 13.5 OWASP Top 10 for LLM Applications 2025

**Source facts** ([OWASP GenAI](https://genai.owasp.org/llm-top-10/); the page gives no explicit English release date, translations are dated 12 March 2025 and 22 July 2025)

| ID | Title |
|---|---|
| LLM01:2025 | Prompt Injection |
| LLM02:2025 | Sensitive Information Disclosure |
| LLM03:2025 | Supply Chain |
| LLM04:2025 | Data and Model Poisoning |
| LLM05:2025 | Improper Output Handling |
| LLM06:2025 | Excessive Agency |
| LLM07:2025 | System Prompt Leakage |
| LLM08:2025 | Vector and Embedding Weaknesses |
| LLM09:2025 | Misinformation |
| LLM10:2025 | Unbounded Consumption |

- LLM06 Excessive Agency "enables damaging actions to be performed in response to unexpected, ambiguous or manipulated outputs from an LLM"; root causes are excessive functionality, permissions and autonomy; mitigation: "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed or not." ([OWASP LLM06](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/))

**Interpretation** (my inference): for a self-hosted stack the table maps onto the earlier sections: LLM03 to 13.10, LLM10 to the vLLM resource-limit variables and DoS advisories (13.2, 13.3), LLM08 to `apps/rag-demo` and the embedding instance, LLM06 to `apps/tool-calling-demo`.

**Workshop decision**: `docs/SECURITY.md` should use the ten IDs as checklist headings.

### 13.6 Agentic threats

**Source facts**

- "Agentic AI - Threats and Mitigations" v1.0, published 17 Feb 2025 by the OWASP Agentic Security Initiative (first in a series). ([OWASP](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/))
- "OWASP Top 10 for Agentic Applications for 2026", published 9 Dec 2025: ASI01 Agent Goal Hijack; ASI02 Tool Misuse; ASI03 Identity & Privilege Abuse; ASI04 Agentic Supply Chain Vulnerabilities; ASI05 Unexpected Code Execution; ASI06 Memory & Context Poisoning; ASI07 Insecure Inter-Agent Communication; ASI08 Cascading Failures; ASI09 Human-Agent Trust Exploitation; ASI10 Rogue Agents. ([OWASP](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/))
- OWASP MCP Top 10 (items labelled 2025; the project page says "Phase 3, Beta Release and Pilot Testing"): MCP01 Token Mismanagement & Secret Exposure; MCP02 Privilege Escalation via Scope Creep; MCP03 Tool Poisoning; MCP04 Software Supply Chain Attacks & Dependency Tampering; MCP05 Command Injection & Execution; MCP06 Prompt Injection via Contextual Payloads; MCP07 Insufficient Authentication & Authorization; MCP08 Lack of Audit and Telemetry; MCP09 Shadow MCP Servers; MCP10 Context Injection & Over-Sharing. ([OWASP MCP Top 10](https://owasp.org/projects/mcp-top-10))
- OWASP "MCP Tool Poisoning" is "an indirect prompt injection attack targeting AI agents" via external tool servers. Mitigations: validate tool output against fixed schemas, isolate privileged tools, enforce access controls "server-side", allowlist vetted MCP servers, confirm sensitive actions outside the LLM context. ([OWASP community](https://community.owasp.org/attacks/MCP_Tool_Poisoning))
- BSI/ANSSI joint "Design Principles for LLM-based Systems with Zero Trust" (published 11 August 2025 on the ANSSI site): recommendations include restricting access rights, transparent decision-making and keeping critical decisions under human supervision. ([ANSSI](https://cyber.gouv.fr/en/publications/jointly-led-international-publications/design-principles-for-llm-based-systems-with-zero-trust/))

**Interpretation** (my inference): the agentic lists add identity, memory, inter-agent trust and cascading failure on top of single-prompt threats. The common control across OWASP LLM01, LLM06 and the MCP material is the same: enforce authorisation outside the model and keep a human approval step for high-risk actions.

**Workshop decision**: `apps/tool-calling-demo` should be taught as the place where authorisation lives in code, not in the prompt; `docs/SECURITY.md` should reference ASI01-ASI10 and mark the MCP Top 10 as beta.

### 13.7 Prompt injection: direct versus indirect, and the primary sources

**Source facts**

- OWASP LLM01 definition: "A Prompt Injection Vulnerability occurs when user prompts alter the LLM's behavior or output in unintended ways." Direct: "a user's prompt input directly alters the behavior of the model". Indirect: "occur when an LLM accepts input from external sources, such as websites or files." Listed mitigations: constrain model behaviour; define and validate output formats; input/output filtering; "Enforce privilege control and least privilege access"; "Require human approval for high-risk actions"; segregate and identify external content; adversarial testing. ([OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/))
- Primary paper for indirect injection: Greshake et al., "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", arXiv:2302.12173 (v1 23 Feb 2023; v2 5 May 2023): attackers can target an application remotely by "strategically injecting prompts into data likely to be retrieved". ([arXiv](https://arxiv.org/abs/2302.12173))
- NIST AI 100-2 E2025 (March 2025): direct prompt injection is the subset of direct prompting attacks "in which the main user provides in-context instructions that are appended to higher-trust instructions like those provided by the application designer (such as the model's SYSTEM PROMPT)" [NISTAML.018]. Indirect injection attacks "are enabled by RESOURCE CONTROL that allows an attacker to indirectly (or remotely) inject system prompts without directly interacting with the application" and are mounted "by a third party" [NISTAML.015]. Root cause: "GenAI models combine the data and instruction channels". ([NIST AI 100-2 E2025](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf))
- BSI published an indirect-prompt-injection warning in 2023. ([BSI warning](https://www.bsi.bund.de/SharedDocs/Cybersicherheitswarnungen/EN/2023/2023-249034-1032.pdf))
- BSI "Evasion Attacks on LLMs - Countermeasures in Practice" notes "Current protective mechanisms, such as fine-tuning, often prove insufficient". ([BSI PDF](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/KI/Evasion-Angriffe_auf_LLMs-Gegenmassnahmen.pdf))

**Interpretation** (my inference): cite NIST AI 100-2 E2025 for the direct definition and Greshake et al. for the indirect one; OWASP LLM01 for the practitioner checklist. Because "the data and instruction channels" are combined in the model, filtering reduces risk but does not remove it; the controls that hold are privilege limits and human approval. Any content retrieved by `apps/rag-demo` is an indirect-injection channel.

**Workshop decision**: `docs/SECURITY.md` should show one direct and one indirect example against the demo apps and teach the least-privilege controls from LLM01 and LLM06; the sources above belong in `docs/REFERENCES.md`.

### 13.8 MCP specification and its security considerations

**Source facts**

- Current specification revision is 2026-07-28 ("The **current** protocol version is 2026-07-28"); the previous revision is 2025-11-25. Version identifiers are `YYYY-MM-DD` dates of the last backwards-incompatible change. ([MCP versioning](https://modelcontextprotocol.io/specification/versioning))
- Standard transports: stdio (newline-delimited messages over a client-launched subprocess's standard streams) and Streamable HTTP (each message an HTTP POST to one endpoint; reply as JSON or request-scoped SSE). HTTP+SSE (2024-11-05) is Deprecated. ([MCP transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports))
- 2026-07-28 made MCP stateless: protocol-level sessions and `Mcp-Session-Id` removed, the `initialize` handshake removed (each request carries version and capabilities in `_meta`), server-initiated requests replaced by Multi Round-Trip Requests, SSE resumability removed; Roots, Sampling and Logging deprecated; Dynamic Client Registration deprecated in favour of Client ID Metadata Documents. ([MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog))
- Streamable HTTP security: "Servers MUST validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks" (invalid gives HTTP 403); local servers "SHOULD bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)"; servers "SHOULD implement proper authentication for all connections". ([MCP Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http))
- Authorization is OPTIONAL. For HTTP transports implementations SHOULD follow the spec; stdio implementations "SHOULD NOT" and take credentials from the environment. MCP servers act as OAuth 2.1 resource servers and "MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728)". Clients "MUST" send the RFC 8707 `resource` parameter. Servers "MUST validate that access tokens were issued specifically for them as the intended audience" and "MUST NOT accept or transit any other tokens". Tokens "MUST NOT be included in the URI query string". Clients "MUST" validate a present `iss` (RFC 9207) before redeeming a code. ([MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization))
- Security Best Practices page covers: Confused Deputy (MCP proxy servers with a static client ID, dynamic client registration and a consent cookie; "MCP proxy servers MUST implement per-client consent"); Token Passthrough ("MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server"); SSRF during OAuth discovery (block private ranges, `169.254.0.0/16` metadata, use an egress proxy; "Avoid implementing IP validation manually"); State Handle Hijacking (replaces session hijacking); Local MCP Server Compromise (show the exact startup command before one-click install, sandbox, least privilege); OAuth Authorization URL Validation (reject `javascript:`/`file:` schemes, never open URLs through a shell); stdio proxy escalation; Mix-Up attacks; localhost redirect impersonation; CIMD trust policies; Scope Minimization (avoid wildcard or omnibus scopes). ([MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices))
- Tools security considerations: servers "MUST" validate all tool inputs, implement access controls, rate limit, sanitize outputs. Clients "SHOULD" prompt for confirmation on sensitive operations, "Show tool inputs to the user before calling the server", validate results before passing to the LLM, implement timeouts, "Log tool usage for audit purposes". "there SHOULD always be a human in the loop with the ability to deny tool invocations." Clients "MUST consider tool annotations to be untrusted unless they come from trusted servers." ([MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools))
- Overview principles: user consent and control; data privacy ("Hosts must not transmit resource data elsewhere without user consent"); tool safety ("Tools represent arbitrary code execution"). Servers should not mark sensitive parameters with `x-mcp-header` because header values "are visible to network intermediaries". ([MCP specification](https://modelcontextprotocol.io/specification/latest); [MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools))

**Interpretation** (my inference): the 2026-07-28 revision removed sessions and the handshake, so older MCP tutorials (HTTP+SSE, `Mcp-Session-Id`, `initialize`) are stale. The MCP "human in the loop" rule and OWASP LLM06 say the same thing at two layers.

**Workshop decision**: where `apps/tool-calling-demo` refers to MCP, cite revision 2026-07-28 and treat tool descriptions and annotations as untrusted input; record the version in `docs/REFERENCES.md`.

### 13.9 NIST and BSI frameworks

**Source facts**

- NIST AI RMF 1.0 released 26 January 2023, voluntary; functions Govern, Map, Measure, Manage. The NIST page says "The AI RMF 1.0 is being revised as part of the White House AI Action Plan"; 7 April 2026 concept note for a Trustworthy-AI-in-Critical-Infrastructure profile. ([NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework))
- NIST AI 600-1 "AI RMF: Generative AI Profile", 26 July 2024, a companion to AI RMF 1.0 prepared under EO 14110. Its 12 risks: CBRN Information or Capabilities; Confabulation; Dangerous, Violent, or Hateful Content; Data Privacy; Environmental Impacts; Harmful Bias or Homogenization; Human-AI Configuration; Information Integrity; Information Security; Intellectual Property; Obscene, Degrading, and/or Abusive Content; Value Chain and Component Integration. ([NIST publication page](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence); [AI 600-1 PDF](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf))
- BSI "Generative AI Models: Opportunities and Risks for Industry and Authorities" (page date 21.01.2025, "continuously updated"; arXiv:2406.04734 v2.0 of 17 Jan 2025). ([BSI](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/Generative_AI_Models.html))
- BSI AI page also lists a checklist for LLM hardening, German-French recommendations for AI programming assistants (with ANSSI), a "Criteria catalog for the integration of externally provided generative AI models into own applications", AIC4 (AI Cloud Service Compliance Criteria Catalogue), and "SBOM for AI - Minimum Elements". ([BSI AI page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Kuenstliche-Intelligenz/kuenstliche-intelligenz_node.html))

**Workshop decision**: `docs/REFERENCES.md` should list these documents as further reading and claim no conformance with any of them.

### 13.10 Supply chain

**Source facts**

- Model and code loading: see the RCE rows in 13.3 (`trust_remote_code`, `auto_map`, `torch.load`, `assert` under `python -O`, revision-pin decay) and OWASP LLM03 Supply Chain (13.5). ([vLLM advisories](https://github.com/vllm-project/vllm/security/advisories))
- Image provenance: vLLM docs publish images on Docker Hub as `vllm/vllm-openai` (plus `-rocm`, `-xpu`) with mutable tags (`:latest`, `:nightly`). The Docker page does not mention signing, SBOM, provenance attestations or digest pinning. The CUDA image "runs as root by default" with a non-root option (`--user 2000:0`); examples use `--ipc=host` and `HF_TOKEN` via an environment variable. ([vLLM Docker docs](https://docs.vllm.ai/en/latest/deployment/docker/))
- In the repository, `.buildkite/scripts/docker-build-metadata-args.sh` emits build metadata (commit, pipeline, build URL) and `.buildkite/scripts/publish-release-images.sh` copies per-arch images from ECR to Docker Hub; neither contains `cosign`, `sigstore`, `sbom` or `attest`. ([metadata script](https://github.com/vllm-project/vllm/blob/main/.buildkite/scripts/docker-build-metadata-args.sh); [publish script](https://github.com/vllm-project/vllm/blob/main/.buildkite/scripts/publish-release-images.sh))
- Digest pinning (Docker docs): "A digest takes the place of the tag when pulling an image", for example `docker pull ubuntu@sha256:<digest>`; pinning "pins" an image to a specific version in time. ([Docker docs](https://docs.docker.com/reference/cli/docker/image/pull/))
- CVE-2026-54232 (Dockerfile dependency confusion) shows a build-time attack path into the official image; CVE-2026-47155 shows `--revision` pins do not cover every artifact (13.3). ([vLLM advisories](https://github.com/vllm-project/vllm/security/advisories))

**Interpretation** (my inference): a digest pin freezes what is pulled, but it does not prove the image is the one the project intended. The notes found no signature or attestation to verify against, so the digest records a point in time, not provenance. Pinned model revisions need a check that all artifacts were fetched at that revision.

**Workshop decision**: `infra/versions.env` pins `vllm/vllm-openai:v0.31.0` by digest, `config/models.yaml` pins models, and `docs/SECURITY.md` should state that this gives reproducibility, not provenance. Running as root inside the pod is a known default of the image; whether the workshop overrides it is not in the notes.

### 13.11 Air-gapped operation: environment variables and telemetry switches

**Source facts**

| Variable or setting | Effect (from the docs) | Source |
|---|---|---|
| `HF_HUB_OFFLINE` | "If set, no HTTP calls will be made to the Hugging Face Hub. If you try to download files, only the cached files will be accessed." True values `1`, `ON`, `YES`, `TRUE` (case-insensitive) | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `HF_HUB_DISABLE_TELEMETRY=1` | "globally disable[s] telemetry" | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `DO_NOT_TRACK` | "Equivalent to `HF_HUB_DISABLE_TELEMETRY`" | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `HF_HUB_DISABLE_UPDATE_CHECK=1` | skips the PyPI update check of the `hf` CLI | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` | stops the token being sent on read calls | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `HF_HOME`, `HF_HUB_CACHE` | cache locations; defaults `~/.cache/huggingface` and `$HF_HOME/hub` | [HF env vars](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) |
| `VLLM_NO_USAGE_STATS=1`, `VLLM_DO_NOT_TRACK=1`, `DO_NOT_TRACK=1` | disable vLLM usage stats (default endpoint `VLLM_USAGE_STATS_SERVER = "https://stats.vllm.ai"`); also disabled if `$HOME/.config/vllm/do_not_track` exists; local record at `~/.config/vllm/usage_stats.json` | [usage_lib.py](https://github.com/vllm-project/vllm/blob/main/vllm/usage/usage_lib.py); [vLLM usage stats docs](https://docs.vllm.ai/en/latest/usage/usage_stats/) |
| Grafana `[analytics] reporting_enabled` | "When enabled Grafana sends anonymous usage statistics to `stats.grafana.org`", default `true`; env `GF_ANALYTICS_REPORTING_ENABLED=false` | [Grafana config](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) |
| Grafana `check_for_updates` | set `false` to stop checking GitHub for new versions; env `GF_ANALYTICS_CHECK_FOR_UPDATES=false` | [Grafana config](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) |
| Grafana `check_for_plugin_updates` | set `false` to stop checking grafana.com for plugin updates; env `GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES=false` | [Grafana config](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) |
| Grafana `feedback_links_enabled`, `[news] news_feed_enabled` | also listed; `news_feed_enabled` default `true` | [Grafana config](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) |

- The vLLM docs do not describe `HF_HUB_OFFLINE` or an air-gapped recipe on the pages checked (offline-inference page, FAQ). Local models are loaded by passing the directory path (`vllm serve <MODEL_DIR>`). ([vLLM offline inference](https://docs.vllm.ai/en/latest/serving/offline_inference/))
- Caution, known friction: issue #23684 (`HF_HUB_OFFLINE=1` broke local-path loading; closed completed 28 Aug 2025) and issue #39039 (air-gapped Gemma 4 still tried to fetch HF cache files; closed "not_planned" 4 Oct 2026). Test the exact vLLM version offline; combine `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, an absolute model path and a pre-populated `HF_HOME`/`HF_HUB_CACHE`. ([issue 23684](https://github.com/vllm-project/vllm/issues/23684); [issue 39039](https://github.com/vllm-project/vllm/issues/39039))

**Interpretation** (my inference): "offline" is a property to test per version, not a flag to trust. Telemetry switches are separate from the offline switch: HF offline mode does not disable the vLLM usage-stats endpoint, and vice versa.

**Workshop decision**: pod startup in `infra/pod/wsctl` should set `HF_HUB_DISABLE_TELEMETRY=1` and `VLLM_NO_USAGE_STATS=1`, and `monitoring/docker-compose.yml` should set the three `GF_ANALYTICS_*` variables above. Unverified: whether those files already do; this research pass did not read them. An offline rehearsal on the pinned `v0.31.0` image is a pre-workshop check, not a claim.

### 13.12 Logging, auditability and retention of prompts and responses

**Source facts**

- LEGAL TEXT, GDPR Art. 5(1)(c),(e) and Art. 25(2) apply to any prompt/response log that contains personal data (see 12.8). ([GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj))
- LEGAL TEXT, AI Act Art. 12(1): high-risk AI systems "shall technically allow for the automatic recording of events (logs) over the lifetime of the system". Art. 19(1) (providers) and Art. 26(6) (deployers): keep logs "for a period appropriate to the intended purpose of the high-risk AI system, of at least six months, unless provided otherwise in ... Union law on the protection of personal data". These apply to high-risk systems only, now from 2 Dec 2027 (Annex III) or 2 Aug 2028 (Annex I). ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj); [Omnibus](https://eur-lex.europa.eu/eli/reg/2026/1744/oj))
- GUIDANCE, EDPB Support Pool of Experts report "AI Privacy Risks & Mitigations - Large Language Models (LLMs)" (Isabel Barberá; Feb 2025, updated Mar 2025; the EDPB states these are the author's views, not its official position): risks include "(Un)intended data logging" ("Providers can log user input queries and outputs for debugging or model improvement, potentially storing sensitive data"), "Unauthorized access to logs", "Data aggregation risks" and "Lack of data retention policies". Mitigations: "Minimize data logging, collect only necessary information"; "Enforce strong access controls, encrypt log data, and monitor access logs"; "Clearly define retention policies, align them with legal requirements and where possible provide users with options to delete their data". For agents: "Limit log retention periods by default and provide configurable options to deployers". ([EDPB report](https://www.edpb.europa.eu/system/files/2025-04/ai-privacy-risks-and-mitigations-in-llms.pdf))
- GUIDANCE, CNIL "Q&A on the use of generative AI systems" (18 July 2024): for personal or sensitive data, on-premise deployment "generally seems more appropriate and secure"; where the provider cannot re-use data (on-premise) a prohibition on personal data in prompts is unnecessary; "the recording of history" is a setting for the deployer to secure; the Q&A gives no retention periods. ([CNIL](https://www.cnil.fr/en/cnils-qa-use-generative-ai-systems))
- vLLM defaults: request logging is off (`--enable-log-requests` default `False`). When on, "INFO: Request ID, parameters and LoRA request. DEBUG: Prompt inputs (e.g: text, token IDs)", minimum level set via `VLLM_LOGGING_LEVEL`. `--enable-log-outputs` (default False, requires `--enable-log-requests`) logs generations. `--max-log-len` limits printed prompt characters (default unlimited). ([arg_utils.py](https://github.com/vllm-project/vllm/blob/main/vllm/engine/arg_utils.py); [vllm serve CLI](https://docs.vllm.ai/en/latest/cli/serve/))
- MCP asks clients to "Log tool usage for audit purposes"; the OWASP MCP Top 10 lists "Lack of Audit and Telemetry" (MCP08); the MCP Security Best Practices page lists "Accountability and Audit Trail Issues" among the risks of token passthrough. ([MCP tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools); [OWASP MCP Top 10](https://owasp.org/projects/mcp-top-10); [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices))
- EU CSF SOV-7 lists "control over security monitoring/logging - customer or EU authority ability to oversee logs, alerts, and monitoring functions". ([Implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en))

**Interpretation** (my inference): there is a tension between audit (keep logs) and minimisation (do not keep prompts). Log metadata (request id, token counts, latency, status) by default and treat prompt/response bodies as personal data with an explicit purpose, access list and retention period. DEBUG request logging turns stdout and log files into a prompt store. The notes give no official retention period for LLM logs.

**Workshop decision**: profiles in `config/vllm-profiles/*.yaml` should leave `--enable-log-requests` and `--enable-log-outputs` unset (default off); `docs/SECURITY.md` should carry the metadata-versus-body rule and say what the benchmark outputs in `benchmark/results/` contain. Unverified: whether the current profiles and harness already match this; the notes did not read them.

### 13.13 Not verified (section 13)

- Unverified: llama.cpp `llama-server` exposure statistics (no primary source); Ollama CVE-2026-7482 and CVE-2024-37032 appear only in secondary sources.
- Unverified: the exact six-principle list of the BSI/ANSSI Zero Trust paper (only a secondary summary was seen); read the PDF before quoting.
- Unverified: whether EO 14110 (cited as the origin of NIST AI 600-1) is still in effect in 2026.
- Unverified: that `TRANSFORMERS_OFFLINE=1` is still required next to `HF_HUB_OFFLINE` in current transformers (community recipes only).
- Unverified: that Prometheus has no phone-home setting (none found, docs not exhaustively checked).
- Unverified: whether Docker Hub carries registry-side attestations or signatures for `vllm/vllm-openai`.
- Unverified: CNIL AI-development recommendations on retention for traceability and performance measurement (search-result summary only; verify at <https://www.cnil.fr/en/ai-system-development-cnils-recommendations-to-comply-gdpr>).
- Unverified: ICO guidance on prompt and log retention; any official EDPB retention period for LLM logs (none adopted per the notes).
- Unverified: the fixed version of CVE-2026-47155 (advisory metadata ambiguous) and which Aug-Oct 2026 advisories are fixed in `v0.31.0`.
- Unverified: the OWASP LLM Top 10 2025 English release date (the page gives none); the OWASP MCP Top 10 is beta.

## 14. Decision log

The decisions this research led to, in one place. Each row names the section that justifies it and the file that implements it.

| # | Decision | Why (section) | Implemented in |
|---|---|---|---|
| D1 | GPU provider is Runpod (Secure Cloud, EU data centers), driven through the Runpod MCP server; "Werner" matched no provider | 7 | `docs/GPU-POOL.md`, `infra/provision.md` |
| D2 | Workshop GPU is the NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB); all measured numbers come from it | 6, 7 | `config/workshop.yaml`, `benchmark/results/` |
| D3 | Pods are single containers, so containerization is taught on participants' laptops and monitoring runs as plain processes | 7 | `deploy/`, `infra/pod/wsmon`, `monitoring/` |
| D4 | One shared vLLM server per pod, bound to 127.0.0.1, `--api-key` set, reached through SSH, because `--api-key` protects only `/v1` and the default bind is all interfaces | 3.7, 13.2 | `config/vllm-profiles/base.yaml`, `infra/pod/render-profile.py` |
| D5 | Engine image `vllm/vllm-openai:v0.31.0`, pinned by digest, host driver must be R580 or newer | 3.2 | `infra/versions.env`, `infra/verify-machine.sh` |
| D6 | Primary model Qwen3-8B (dense, GQA, Apache-2.0) so the KV-cache formula can be checked exactly; FP8 build, small model and embedding model from the same family; every revision is a commit SHA | 4, 5, 11 | `config/models.yaml` |
| D7 | Qwen3.5, Gemma 4 and others appear as selection-lab alternatives with licence rows; licences are read per repo at the pinned SHA because they drift | 5.3, 11.4 | `docs/MODEL-SELECTION.md` |
| D8 | Our own benchmark harness defines TTFT, ITL, TPOT and goodput explicitly and is cross-checked against `vllm bench serve`, because tools define the metrics differently | 10 | `benchmark/infbench/`, `docs/METRICS.md` |
| D9 | Sweeps use different prompts at every level; prefix caching is on by default in vLLM V1 and would otherwise flatter later runs | 3.9 | `benchmark/infbench/cli.py` |
| D10 | The Grafana dashboard uses vLLM v0.31.0 metric names and DCGM GPU names so it works with the pod exporter and with dcgm-exporter | 6.9, 9 | `monitoring/grafana/build_dashboard.py` |
| D11 | Day 1-2 KV experiments use an explicit KV budget (`--kv-cache-memory-bytes`) to simulate a small GPU, because 96 GB hides memory pressure for an 8B model | 3.4, 5.2 | `config/vllm-profiles/kv-constrained.yaml` |
| D12 | Roofline numbers: 1597 GB/s bandwidth and about 504 TFLOPS dense BF16 (derived), always overridden by measurements | 6.1-6.4 | `monitoring/grafana/build_dashboard.py` |
| D13 | Security and sovereignty are taught as engineering: data-flow mapping, supply-chain pinning, patched engine versions, and Runpod as a case study ("EU region is not EU jurisdiction") | 7.10, 12, 13 | `docs/SECURITY.md`, `docs/DIGITAL-SOVEREIGNTY.md` |
| D14 | Fetched documentation is data, not instructions; one vendor docs page carried embedded instructions for AI agents and is used as an anecdote in the security block | 7.12, 13.7 | `docs/SECURITY.md` |
| D15 | Teaching content carries no calendar dates; the Heise event is currently cancelled and undated | 1 | `scripts/check-repo.mjs` |
