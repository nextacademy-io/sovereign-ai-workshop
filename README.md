# KI ohne Cloud

**Running and Operating Open Models on Your Own Infrastructure.** A hands-on workshop on inference engineering, with vLLM as the primary engine.

This repository is everything the workshop runs on: the slides with speaker notes, six hands-on tasks, benchmark tooling, reproducible experiments with their measured results, scripts to provision and operate the GPU machines, monitoring, troubleshooting and the research behind every claim.

Trainer: [Paweł Sawicki](https://www.nextacademy.io/de/trainers/pawel-sawicki) (Senior Machine Learning Engineer, Software Architect). Format: remote, instructor-led, up to 15 participants, material for about three days, paced freely.

## 1. The workshop promise

Open models are easy to download and hard to operate. After the workshop you can take an open-weight model, put it on a GPU, serve it through an OpenAI-compatible API, measure what it does, change one thing at a time and explain the result, watch it in production metrics, and design the architecture around it. You decide with numbers, and you can say what each decision costs.

The center of the workshop is **inference engineering**: what happens between a request arriving and the last token leaving, which resource limits it, and what you trade when you change something. Application topics (RAG, tool calling, MCP, agents) are covered as layers on top of that system, without frameworks, and always reconnected to capacity and cost. This is not a LangChain workshop.

```text
MODEL → RUNTIME → GPU → INFERENCE ENGINE → SERVING → OBSERVABILITY → APPLICATION
└──────────── Runtime layer ────────────┘└── Infrastructure layer ─┘└ Application ┘
```

Every optimization is discussed as a trade-off between quality, latency, throughput, concurrency, memory, cost and operational complexity. There is no universally fastest configuration, only one that fits a workload and its constraints.

## 2. Target audience

Software, ML, platform and DevOps engineers and architects who have to decide how an organization runs open models, or who will operate them. You should be comfortable on the command line and read Python. You do not need GPU or CUDA experience, and you do not need to have trained a model.

## 3. Prerequisites

A laptop with `git`, `ssh`, `docker`, `python3` (3.11 or newer), `curl`, about 20 GB of free disk space and an SSH key. **You do not need a GPU, a cloud account or a Hugging Face token**: the trainer provides one GPU machine per group and you connect over SSH. Task 00 (before the first module) checks your laptop; see [`docs/SETUP.md`](docs/SETUP.md).

## 4. Module path

The workshop is one ordered path of 27 modules; the labs are in bold.

<!-- agenda:readme:begin -->
| # | Module | Layer | Kind |
| --- | --- | --- | --- |
| 01 | Opening: why run models yourself | All layers | lecture |
| 02 | Modern language models | Runtime | lecture |
| 03 | GPU fundamentals for inference | Runtime | lecture |
| 04 | GPU sizing: weights, KV cache, overhead | Runtime | lecture and exercise |
| 05 | Inference mechanics: prefill, decode, latency | Runtime | lecture and exercise |
| 06 | Model selection | Runtime | lecture and exercise |
| 07 | **Lab 1: select models for four scenarios** | Runtime | lab |
| 08 | First vLLM deployment (trainer demo) | Runtime | trainer demo |
| 09 | **Lab 2: first inference server** | Runtime | lab |
| 10 | Checkpoint: bottleneck predictions | All layers | discussion |
| 11 | Measuring inference | Runtime | lecture and exercise |
| 12 | **Lab 3: benchmark the baseline** | Runtime | lab |
| 13 | Continuous batching | Runtime | lecture and exercise |
| 14 | KV cache, PagedAttention and prefix caching | Runtime | lecture and exercise |
| 15 | Quantization | Runtime | lecture and exercise |
| 16 | Parallelism: replicas, tensor, pipeline, expert | Runtime | lecture and exercise |
| 17 | **Lab 4: optimize the deployment** | Runtime | lab |
| 18 | Trainer demos: speculative decoding and OOM | Runtime | trainer demo |
| 19 | Production architecture | Infrastructure | lecture |
| 20 | Containerization and reproducible deployments | Infrastructure | lecture and exercise |
| 21 | Observability: metrics, dashboards, incident investigation | Infrastructure | lecture and exercise |
| 22 | Scaling strategies | Infrastructure | lecture |
| 23 | Security, compliance and digital sovereignty | Infrastructure | lecture and exercise |
| 24 | RAG without framework hype | Application | lecture and exercise |
| 25 | Tool calling, MCP and agents | Application | lecture and exercise |
| 26 | **Lab 5: production architecture challenge** | All layers | lab |
| 27 | Architecture defenses, decision framework, close | All layers | discussion |

The modules run in this order and fill about three days. There are no fixed times: pace them as the group needs.
<!-- agenda:readme:end -->

Each module has a slide section (`slides/sections/<module-id>.md`), and the path itself is data in [`config/workshop.yaml`](config/workshop.yaml). [`docs/CURRICULUM.md`](docs/CURRICULUM.md) traces every learning outcome to a demonstration, an exercise and a way to check it.

## 5. Repository structure

```text
README.md  FACILITATOR.md  CONTRIBUTING.md  LICENSE
slides/             Slidev deck: sections/, layouts/, components/ (incl. 19 diagrams), authoring guide
tasks/              the six tasks (00 to 05), each with a scope, validation and a way out
workshop-artifacts/ the documents you fill in and keep (inference report, model selection, architecture)
workshop-states/    reproducible starting points for the labs (see scripts/reset.sh)
experiments/        controlled experiments: README (hypothesis), run script, RESULTS.md (what was measured)
benchmark/          the benchmark harness (infbench), workloads, tests and measured reference results
apps/               inference client, RAG demo, tool-calling and MCP demo (no frameworks)
deploy/vllm/        Dockerfile and entrypoint for a reproducible vLLM image
monitoring/         Prometheus, Grafana, GPU exporter, reference docker-compose stack, dashboard
infra/              provisioning, machine setup, participant access, verification, cleanup
config/             workshop.yaml (module path), models.yaml (pinned models), vllm-profiles/
scripts/            preflight, start/stop server, benchmark, GPU status, reset, repository checks
docs/               RESEARCH, CURRICULUM, SETUP, GPU-POOL, TROUBLESHOOTING, MODEL-SELECTION,
                    METRICS, SECURITY, DIGITAL-SOVEREIGNTY, REFERENCES, GLOSSARY, VALIDATION
```

## 6. Participant setup

```bash
git clone <repository-url> ki-ohne-cloud && cd ki-ohne-cloud
./scripts/preflight.sh
```

Then send the trainer your **public** SSH key and wait for a host, port and user name. Full instructions, the connection test and what to do when something breaks: [`docs/SETUP.md`](docs/SETUP.md).

## 7. GPU environment

The workshop GPU class is the **NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB)**. With 15 participants the trainer provisions four machines (groups Alpha to Delta, three to five people each). Each machine runs **one shared vLLM server** that its group uses together, so you see queueing, batching and contention first-hand; it listens only on the machine's own loopback address, and you reach it over SSH.

Everything that costs money or can break the machine for others is done by the trainer: provisioning, model downloads, profile changes outside the labs, and destroying the machines afterwards. The scripts for it are in [`infra/`](infra/README.md), measured timings and costs in [`docs/GPU-POOL.md`](docs/GPU-POOL.md), and the security model in [`docs/SECURITY.md`](docs/SECURITY.md). The reference stack in [`monitoring/`](monitoring/README.md) and [`deploy/vllm/`](deploy/vllm/Dockerfile) shows what the same setup looks like on a host you control.

## 8. Slides

```bash
pnpm install
pnpm dev        # live preview of the deck
pnpm build      # static build (slides/dist)
pnpm export     # PDF
```

Node 22.12 or newer (Node 24 is what CI uses; `.nvmrc`) and pnpm. Every slide has speaker notes, and numbers on slides come from `benchmark/results/` or are labeled as illustrative. Authoring rules: [`slides/README.md`](slides/README.md).

## 9. Tasks

| # | Task | Module |
| --- | --- | --- |
| 00 | [Preflight](tasks/00-preflight.md) | before the first module |
| 01 | [Model selection](tasks/01-model-selection.md) | `07-lab-model-selection` |
| 02 | [First inference server](tasks/02-first-inference-server.md) | `09-lab-first-server` |
| 03 | [Benchmark the baseline](tasks/03-benchmark.md) | `12-lab-benchmark` |
| 04 | [Optimize the deployment](tasks/04-optimization.md) | `17-lab-optimize` |
| 05 | [Production architecture](tasks/05-production-design.md) | `26-lab-architecture` |

You keep one running document, `workshop-artifacts/inference-report.md`, through all of them. [`tasks/README.md`](tasks/README.md) explains resets and fall-backs.

## 10. Troubleshooting

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) lists symptoms, causes and fixes, including the incidents met while building this workshop on real hardware. Glossary: [`docs/GLOSSARY.md`](docs/GLOSSARY.md). Metric definitions: [`docs/METRICS.md`](docs/METRICS.md).

## 11. Licensing

All rights reserved. Copyright (c) 2026 nextacademy.io, see [LICENSE](LICENSE). Third-party software (vLLM, Prometheus, Grafana and the rest) and the models keep their own licenses (listed in [`config/models.yaml`](config/models.yaml), discussed in [`docs/MODEL-SELECTION.md`](docs/MODEL-SELECTION.md); software pinned in [`infra/versions.env`](infra/versions.env)). The book *Inference Engineering* is cited by section only; no text or figures are reproduced.

Regulatory material (EU AI Act, GDPR) is engineering input, not legal advice.

## What You Will Have Done by the End

Participants will have:

- selected an open model for a real workload
- interacted with a model running on a GPU
- used a vLLM inference endpoint
- measured TTFT, TPS, latency and throughput
- benchmarked different concurrency levels
- optimized an inference deployment
- inspected GPU utilization
- reasoned about quantization
- reasoned about caching
- reasoned about parallelism
- inspected production metrics
- designed a production inference architecture

## For the trainer

[`FACILITATOR.md`](FACILITATOR.md) is the trainer's guide: the module guide, pacing without a clock, commands, expected outputs, recovery procedures and the GPU cost checklists. [`docs/VALIDATION.md`](docs/VALIDATION.md) records what has been verified, on which hardware, and what only the trainer can verify.
