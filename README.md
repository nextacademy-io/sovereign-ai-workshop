# KI ohne Cloud

**Running and Operating Open Models on Your Own Infrastructure.** A three-day, hands-on workshop on inference engineering, with vLLM as the primary engine.

This repository is everything the workshop runs on: the slides with speaker notes, six hands-on tasks, benchmark tooling, reproducible experiments with their measured results, scripts to provision and operate the GPU machines, monitoring, troubleshooting and the research behind every claim.

Trainer: [Paweł Sawicki](https://www.nextacademy.io/de/trainers/pawel-sawicki) (Senior ML Engineer, AI Engineer, Software Architect, Technical Trainer). Format: remote, instructor-led, up to 15 participants, three days of about seven teaching hours each.

## 1. The workshop promise

Open models are easy to download and hard to operate. After three days you can take an open-weight model, put it on a GPU, serve it through an OpenAI-compatible API, measure what it does, change one thing at a time and explain the result, watch it in production metrics, and design the architecture around it. You decide with numbers, and you can say what each decision costs.

The centre of the workshop is **inference engineering**: what happens between a request arriving and the last token leaving, which resource limits it, and what you trade when you change something. Application topics (RAG, tool calling, MCP, agents) are covered as layers on top of that system, without frameworks, and always reconnected to capacity and cost. This is not a LangChain workshop.

```text
MODEL → RUNTIME → GPU → INFERENCE ENGINE → SERVING → OBSERVABILITY → APPLICATION
└──────────── Runtime layer ────────────┘└── Infrastructure layer ─┘└ Application ┘
```

Every optimisation is discussed as a trade-off between quality, latency, throughput, concurrency, memory, cost and operational complexity. There is no universally fastest configuration, only one that fits a workload and its constraints.

## 2. Target audience

Software, ML, platform and DevOps engineers and architects who have to decide how an organisation runs open models, or who will operate them. You should be comfortable on the command line and read Python. You do not need GPU or CUDA experience, and you do not need to have trained a model.

## 3. Prerequisites

A laptop with `git`, `ssh`, `docker`, `python3` (3.11 or newer), `curl`, about 20 GB of free disk space and an SSH key. **You do not need a GPU, a cloud account or a Hugging Face token**: the trainer provides one GPU machine per group and you connect over SSH. Task 00 (15 minutes, before Day 1) checks your laptop; see [`docs/SETUP.md`](docs/SETUP.md).

## 4. Three-day agenda

<!-- agenda:readme:begin -->
### Day 1: UNDERSTAND & RUN

*What are we actually running?*

| Time | Min | Block | Layer |
| --- | --- | --- | --- |
| 09:00 | 30 | Opening: why run models yourself | All layers |
| 09:30 | 60 | Modern language models | Runtime |
| 10:30 | 15 | *Break* |  |
| 10:45 | 60 | Model selection | Runtime |
| 11:45 | 40 | **Lab 1: select models for four scenarios** | Runtime |
| 12:25 | 65 | *Lunch* |  |
| 13:30 | 60 | GPU fundamentals for inference | Runtime |
| 14:30 | 45 | GPU sizing: weights, KV cache, overhead | Runtime |
| 15:15 | 15 | *Break* |  |
| 15:30 | 45 | Inference mechanics: prefill, decode, latency | Runtime |
| 16:15 | 30 | First vLLM deployment (trainer demo) | Runtime |
| 16:45 | 45 | **Lab 2: first inference server** | Runtime |

### Day 2: MEASURE & OPTIMIZE

*How do we make it fast and efficient?*

| Time | Min | Block | Layer |
| --- | --- | --- | --- |
| 09:00 | 30 | Recap and bottleneck predictions | All layers |
| 09:30 | 60 | Measuring inference | Runtime |
| 10:30 | 15 | *Break* |  |
| 10:45 | 60 | **Lab 3: benchmark the baseline** | Runtime |
| 11:45 | 45 | Continuous batching | Runtime |
| 12:30 | 60 | *Lunch* |  |
| 13:30 | 45 | KV cache, PagedAttention and prefix caching | Runtime |
| 14:15 | 45 | Quantization | Runtime |
| 15:00 | 15 | *Break* |  |
| 15:15 | 45 | Parallelism: replicas, tensor, pipeline, expert | Runtime |
| 16:00 | 60 | **Lab 4: optimize the deployment** | Runtime |
| 17:00 | 30 | Trainer demos: speculative decoding, OOM, tensor parallelism | Runtime |

### Day 3: OPERATE

*How do we operate this as infrastructure?*

| Time | Min | Block | Layer |
| --- | --- | --- | --- |
| 09:00 | 45 | Production architecture | Infrastructure |
| 09:45 | 45 | Containerization and reproducible deployments | Infrastructure |
| 10:30 | 15 | *Break* |  |
| 10:45 | 60 | Observability: metrics, dashboards, incident investigation | Infrastructure |
| 11:45 | 45 | Scaling strategies | Infrastructure |
| 12:30 | 60 | *Lunch* |  |
| 13:30 | 60 | Security, compliance and digital sovereignty | Infrastructure |
| 14:30 | 45 | RAG without framework hype | Application |
| 15:15 | 15 | *Break* |  |
| 15:30 | 30 | Tool calling, MCP and agents | Application |
| 16:00 | 60 | **Lab 5: production architecture challenge** | All layers |
| 17:00 | 30 | Architecture defenses, decision framework, close | All layers |

Times are relative to the start of each day (09:00 in the trainer's time zone). Breaks are included; teaching time is about seven hours per day.
<!-- agenda:readme:end -->

Each block has a slide section (`slides/sections/<block>.md`), and the schedule itself is data in [`config/workshop.yaml`](config/workshop.yaml). [`docs/CURRICULUM.md`](docs/CURRICULUM.md) traces every learning outcome to a demonstration, an exercise and a way to check it.

## 5. Repository structure

```text
README.md  FACILITATOR.md  CONTRIBUTING.md  LICENSE  LICENSE-CODE
slides/             Slidev deck: sections/, layouts/, components/ (incl. 18 diagrams), authoring guide
tasks/              the six tasks (00 to 05), each with timebox, validation and a way out
workshop-artifacts/ the documents you fill in and keep (inference report, model selection, architecture)
workshop-states/    reproducible starting points for the labs (see scripts/reset.sh)
experiments/        controlled experiments: README (hypothesis), run script, RESULTS.md (what was measured)
benchmark/          the benchmark harness (infbench), workloads, tests and measured reference results
apps/               inference client, RAG demo, tool-calling and MCP demo (no frameworks)
deploy/vllm/        Dockerfile and entrypoint for a reproducible vLLM image
monitoring/         Prometheus, Grafana, GPU exporter, reference docker-compose stack, dashboard
infra/              provisioning, machine setup, participant access, verification, cleanup
config/             workshop.yaml (agenda), models.yaml (pinned models), vllm-profiles/
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

Node 22.12 or newer (Node 24 is what CI uses; `.nvmrc`) and pnpm. Every slide has speaker notes, and numbers on slides come from `benchmark/results/` or are labelled as illustrative. Authoring rules: [`slides/README.md`](slides/README.md).

## 9. Tasks

| # | Task | Timebox |
| --- | --- | --- |
| 00 | [Preflight](tasks/00-preflight.md) | 15 min |
| 01 | [Model selection](tasks/01-model-selection.md) | 30 min |
| 02 | [First inference server](tasks/02-first-inference-server.md) | 35 min |
| 03 | [Benchmark the baseline](tasks/03-benchmark.md) | 45 min |
| 04 | [Optimize the deployment](tasks/04-optimization.md) | 40 min |
| 05 | [Production architecture](tasks/05-production-design.md) | 45 min |

You keep one running document, `workshop-artifacts/inference-report.md`, through all of them. [`tasks/README.md`](tasks/README.md) explains resets and fall-backs.

## 10. Troubleshooting

[`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) lists symptoms, causes and fixes, including the incidents met while building this workshop on real hardware. Glossary: [`docs/GLOSSARY.md`](docs/GLOSSARY.md). Metric definitions: [`docs/METRICS.md`](docs/METRICS.md).

## 11. Licensing

- Text, slides and diagrams: [CC BY 4.0](LICENSE).
- Code, scripts and configuration: [MIT](LICENSE-CODE).
- The models the workshop runs have their own licences, listed per model in [`config/models.yaml`](config/models.yaml) and discussed in [`docs/MODEL-SELECTION.md`](docs/MODEL-SELECTION.md). Third-party software (vLLM, Prometheus, Grafana and the rest) is used under its own licence and is pinned by version and digest in [`infra/versions.env`](infra/versions.env).
- The book *Inference Engineering* is cited by chapter only; no text or figures are reproduced.

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

[`FACILITATOR.md`](FACILITATOR.md) is the run sheet: minute-by-minute agenda, commands, expected outputs, recovery procedures and the GPU cost checklists. [`docs/VALIDATION.md`](docs/VALIDATION.md) records what has been verified, on which hardware, and what only the trainer can verify.
