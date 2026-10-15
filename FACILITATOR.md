# Facilitator guide

The operating manual for the trainer: what to prepare, what to run, what you should see, what goes wrong, how to recover and how to stop paying for GPUs. It is written to be used with the slides (`slides/sections/<module-id>.md`, speaker notes on every slide), the tasks (`tasks/`) and the infrastructure scripts (`infra/`).

Conventions: **T:** is a command on your laptop, **P:** is a command on a GPU pod (as root; participants use `sudo wsctl ...`). `<ip>` and `<port>` are the pod's SSH address; the port changes whenever a pod is rebuilt. The workshop has no clock: you pace the path (section 8). Every measured number comes from `benchmark/results/reference/` and carries its hardware and date there; the experiments' `RESULTS.md` files explain them.

## 1. The workshop on one page

| | |
| --- | --- |
| Promise | Run, measure, optimize and operate an open model on your own infrastructure; inference engineering first, applications on top. |
| Format | One ordered path of 27 modules, material for about three days, paced freely. Remote, up to 15 participants in four groups (alpha, beta, gamma, delta). |
| Machines | One pod per group, each with one NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB class). Participants need no GPU and no account: they connect over SSH. |
| Servers | One shared vLLM server per pod on `127.0.0.1:8000` (Qwen3-8B, profile `baseline`), an embedding server on `:8001`, Prometheus, Grafana and a GPU exporter. Nothing is reachable except through SSH. |
| Work | Six tasks (00 to 05), one growing document `workshop-artifacts/inference-report.md`, trainer demos, five labs with a debrief each, and one incident exercise in the observability module. |
| Pacing | No clock. Natural stopping points are the ends of the labs; section 8 says how to check in, when to break and how to shorten the material. |
| Your rule | Anything risky, expensive or one-off is demonstrated by you: restarts of the server outside the labs, the OOM demo, speculative decoding, a two-GPU comparison if you have the machine, destroying the machines. |

The teaching rhythm in every experiment module: concept, system, experiment, **prediction**, measurement, explanation, production consequence. Ask for the prediction before showing the number; the number never speaks for itself.

## 2. Preparation

Do each step once per pod. `infra/provision.md` has the details and the Runpod MCP calls; `infra/README.md` lists the scripts.

### Well ahead of the first session

- [ ] Re-validate the models: `config/models.yaml` pins revisions; read the license of each repository again (licenses drift) and update `docs/MODEL-SELECTION.md` if one changed.
- [ ] Read the live GPU price and stock (`list-gpu-types`, `get-capacity` for `NVIDIA RTX PRO 6000 Blackwell Server Edition`). Stock was *Low* when this repository was validated: two-GPU stock only existed on CUDA 13.2 hosts. Decide the fallback (another EU data center, or another GPU class: every measured number then changes and the measurement slides need your own run).
- [ ] Decide the data center. EUR-IS-2 (Iceland) is inside the EEA but not the EU; `EU-RO-1` is in the EU. See `docs/DIGITAL-SOVEREIGNTY.md`.
- [ ] Collect each participant's **public** SSH key (task 00); fill `infra/participants.yaml` (public keys only; the file is gitignored).
- [ ] Do a full dry run on one pod: tasks 02 to 04 as a participant, and the three incident tickets of the observability module (section 5). The machine times in this repository were measured that way; the time real participants need is **not** measured, so your dry run with people is the first real number.

### Before the first session

- [ ] Create the pods (state the hourly price first: price × pods = per-hour cost). Create them well ahead of the first session: they cost money from creation, but a pod that cannot be created at the last moment is the larger risk.
- [ ] `T: infra/deploy-to-pod.sh --host <ip> --port <port> --group alpha` for each pod (about 5 minutes plus model download; see section 3), then `T: infra/verify-machine.sh --host <ip> --port <port>`: every line PASS.
- [ ] Send each participant host, port and user name. Ask them to run `./scripts/preflight.sh --host <host> --port <port> --user <user>`.
- [ ] Keep the pods **running** until the workshop ends. A stopped pod can come back without a GPU; `terminate` only at the very end.
- [ ] Open Grafana through a tunnel on your laptop once and look at the dashboard *KI ohne Cloud: inference*.

### Shortly before each session

- [ ] `T: infra/verify-machine.sh` on all pods; `P: wsctl status` shows `main` on `baseline` and `embed` running.
- [ ] From the benchmarking lab on, the server must be on `baseline` at the start of each lab (`P: wsctl start baseline` if not); before the observability and RAG modules, start the embedding server if it is not running (`P: wsctl embed start`).
- [ ] Billing: `list-billing` for the cost of the previous session against your estimate (section 9).
- [ ] Slides open in presenter mode (`pnpm dev`); `slides/dist` built as a fallback (`pnpm build`).

## 3. Infrastructure timing (measured)

From the validation sessions on Runpod Secure Cloud, EUR-IS-2, one RTX PRO 6000 per pod (`docs/GPU-POOL.md` has the log and the costs). The start-up times of vLLM have **one** canonical statement, and every document and slide that quotes them uses it (`benchmark/results/reference/startup/*.json`):

> A cold start of the baseline profile in a fresh container takes **176 s** to ready in the engine log (about **198 s** as `wsctl start` measures wall time; 188 to 198 s were seen). A start with warm caches takes **55 s** in the log and **67.4 s** as `wsctl` measures it. A restart of the same profile takes **29 s** in the log and **39.3 s** as `wsctl` measures it. The first start of the FP8 profile takes 138 to 143 s.

| Step | Measured |
| --- | --- |
| Pod created, container running | about 2 s |
| sshd answering | about 11 s later (the 9 GB image was cached on the host; a cold host adds the image pull) |
| Model download from the Hugging Face hub (Qwen3-8B, 16 GB) | 12.4 s (about 1.3 GB/s) |
| First vLLM start in a fresh container (empty compile caches) | 176 s in the log; about 198 s as `wsctl` measures it |
| vLLM start with warm caches | 55 s in the log; 67.4 s as `wsctl` measures it |
| Restart of the same profile | 29 s in the log; 39.3 s as `wsctl` measures it |
| First start of the FP8 profile (new checkpoint, first compile) | 138 to 143 s |
| Full rebuild of a restarted pod (`deploy-to-pod.sh`) | 5 min 41 s (model cache seed about 60 s, monitoring 16 s, the first vLLM start and the embedding server (53 s) for the rest) |
| A pod restart changes | the public SSH port (22290 became 22235 in the test), the SSH host key, and wipes the container disk; `/workspace` survives |

Plan the recovery of a broken pod as **five to six minutes** (`infra/deploy-to-pod.sh` again, then tell participants the new port), and never do it while a lab is running if a server restart will do.

## 4. Module guide

The table below is generated from [`config/workshop.yaml`](config/workshop.yaml) (`node scripts/gen-agenda.mjs`); the notes under it say what to do in each module, in path order. Module ids are the file names of the slide sections. How to pace the path, where to stop and how to shorten it: section 8.

<!-- agenda:runsheet:begin -->
| # | Module | Kind | Slides | Task and experiments | Skippable |
| --- | --- | --- | --- | --- | --- |
| 01 | **Opening: why run models yourself** | lecture | `slides/sections/01-opening.md` |  |  |
| 02 | **Modern language models** | lecture | `slides/sections/02-models.md` |  |  |
| 03 | **GPU fundamentals for inference** | lecture | `slides/sections/03-gpu-fundamentals.md` |  |  |
| 04 | **GPU sizing: weights, KV cache, overhead** | lecture and exercise | `slides/sections/04-gpu-sizing.md` | `experiments/baseline` |  |
| 05 | **Inference mechanics: prefill, decode, latency** | lecture and exercise | `slides/sections/05-inference-mechanics.md` |  |  |
| 06 | **Model selection** | lecture and exercise | `slides/sections/06-model-selection.md` |  |  |
| 07 | **Lab 1: select models for four scenarios** | lab | `slides/sections/07-lab-model-selection.md` | Task `01-model-selection` |  |
| 08 | **First vLLM deployment (trainer demo)** | trainer demo | `slides/sections/08-first-vllm.md` |  |  |
| 09 | **Lab 2: first inference server** | lab | `slides/sections/09-lab-first-server.md` | Task `02-first-inference-server` |  |
| 10 | **Checkpoint: bottleneck predictions** | discussion | `slides/sections/10-checkpoint.md` |  |  |
| 11 | **Measuring inference** | lecture and exercise | `slides/sections/11-measuring.md` |  |  |
| 12 | **Lab 3: benchmark the baseline** | lab | `slides/sections/12-lab-benchmark.md` | Task `03-benchmark`<br>`experiments/baseline`<br>`experiments/concurrency` |  |
| 13 | **Continuous batching** | lecture and exercise | `slides/sections/13-continuous-batching.md` | `experiments/concurrency` |  |
| 14 | **KV cache, PagedAttention and prefix caching** | lecture and exercise | `slides/sections/14-kv-cache.md` | `experiments/context-length`<br>`experiments/prefix-cache` |  |
| 15 | **Quantization** | lecture and exercise | `slides/sections/15-quantization.md` | `experiments/quantization` |  |
| 16 | **Parallelism: replicas, tensor, pipeline, expert** | lecture and exercise | `slides/sections/16-parallelism.md` | `experiments/tensor-parallel` |  |
| 17 | **Lab 4: optimize the deployment** | lab | `slides/sections/17-lab-optimize.md` | Task `04-optimization`<br>`experiments/quantization`<br>`experiments/prefix-cache`<br>`experiments/context-length`<br>`experiments/concurrency` |  |
| 18 | **Trainer demos: speculative decoding and OOM** | trainer demo | `slides/sections/18-demos.md` | `experiments/tensor-parallel`<br>`experiments/demos` | yes |
| 19 | **Production architecture** | lecture | `slides/sections/19-production-architecture.md` |  |  |
| 20 | **Containerization and reproducible deployments** | lecture and exercise | `slides/sections/20-containerization.md` |  |  |
| 21 | **Observability: metrics, dashboards, incident investigation** | lecture and exercise | `slides/sections/21-observability.md` |  |  |
| 22 | **Scaling strategies** | lecture | `slides/sections/22-scaling.md` |  |  |
| 23 | **Security, compliance and digital sovereignty** | lecture and exercise | `slides/sections/23-security-sovereignty.md` |  |  |
| 24 | **RAG without framework hype** | lecture and exercise | `slides/sections/24-rag.md` |  |  |
| 25 | **Tool calling, MCP and agents** | lecture and exercise | `slides/sections/25-tools-agents.md` |  |  |
| 26 | **Lab 5: production architecture challenge** | lab | `slides/sections/26-lab-architecture.md` | Task `05-production-design` |  |
| 27 | **Architecture defenses, decision framework, close** | discussion | `slides/sections/27-capstone-close.md` |  |  |
<!-- agenda:runsheet:end -->

**`01-opening`.** Check that every participant has run task 00; collect those who cannot log in and fix them at the first natural pause, not in front of the room. The opening round is optional: if the group has not met, ask for one sentence from each person (what do you run, or want to run, on your own infrastructure?) and return to these at the close.

**`02-models`.** Live: tokenize a sentence on the shared server (no key needed for `/tokenize`):
`P: curl -s http://127.0.0.1:8000/tokenize -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen3-8B","prompt":"KI ohne Cloud: Hello, tokenizer!"}'` prints `{"count":8,...,"tokens":[80971,28883,14817,25,21927,11,45958,0]}`. A German compound such as "Unabhängigkeit" gives 3 tokens (add `"return_token_strs":true`). Discussion prompt: why does the same text cost different numbers of tokens in different models? Skippable: multimodal and reasoning detail.

**`03-gpu-fundamentals`.** Show `P: nvidia-smi` on your pod and read the GPU name, memory and driver aloud. The point to land: the datasheet bandwidth (1,597 GB/s for this GPU) and the ops-to-byte ratio decide which phase is limited by what (the roofline is taught here and revisited in the mechanics module); `nvidia-smi` utilization is not efficiency (the measured baseline shows 99 % with a single request).

**`04-gpu-sizing`.** Prediction before the server's number: participants estimate the KV capacity with `scripts/sizing.py` (expected 412,893 tokens with the default 4 GiB overhead) and you show the log line (`P: wsctl logs 80 | grep "KV cache"`: 423,328 tokens in the validated run, 426,992 after later restarts). Prompt: why is the result within about 3 % although we guessed the overhead?

**`05-inference-mechanics`.** The experiment sequence uses measured data: bandwidth bound 10.3 ms against a measured inter-token latency of 11.6 ms. Make them predict first (what limits one decode step?). The prediction written down here, to be scored later: prefill scales with prompt length and is compute-heavy; decode is limited by moving weights and KV through memory.

**`06-model-selection`.** The model facts are as researched for this delivery: re-check them (section 2). This module comes after the GPU, sizing and mechanics modules on purpose: Lab 1 uses KV sizing, TTFT and prefill. Push the room away from leaderboard names towards the criteria in `docs/MODEL-SELECTION.md`. Prompt: which smaller model would you try first, and what would make you reject it?

**`07-lab-model-selection`.** Lab 1, see section 5. Sub-groups take one scenario each; reduced scope is a legitimate outcome.

**`08-first-vllm`.** Demo, you drive: `nvidia-smi`; `curl .../v1/models` with the key; one completion; one stream; `wsctl logs`; read the start-up numbers (weights 15.27 GiB, KV cache, graph capture, time to ready). The API is the product; everything else is what makes it behave.

**`09-lab-first-server`.** Lab 2, see section 5.

**`10-checkpoint`.** Collect each group's bottleneck predictions on paper or in the shared report; you score them in the last slides of the demos module. Do not show the measured numbers of the benchmarking lab yet.

**`11-measuring`.** Make the point with the harness: `P: ./scripts/benchmark.sh --concurrency 1,8` once, live, and read each column of the table. The classic trap to demonstrate in words: a repeated seed is answered by the prefix cache (the harness uses a fresh random seed per run and warns above 5 % hit rate). Little's law (concurrency = arrival rate × time in the system) is first explained here.

**`12-lab-benchmark`.** Lab 3, see section 5. This is the lab in which the groups discover contention: only one benchmark at a time per group, apart from the deliberate contention round.

**`13-continuous-batching`.** Show the cap live only on a demo pod: the measured effect of `--max-num-seqs 8` is an aggregate throughput pinned at about 550 tokens/s and a time to first token of 3 s at 16 clients (against 0.6 s). Reproducing it costs a restart for the group (about 40 s each way): do not do it on a pod a group is using, or show the reference results.

**`14-kv-cache`.** Experiments: `context-length` and `prefix-cache` (RESULTS in `experiments/*/RESULTS.md`). The `kv-constrained` profile simulates a small card: a 4 GiB pool and a 16,384-token context limit, about 29,000 tokens, which holds three requests of 8,192 tokens. Say why the context limit is lowered: with the baseline 32,768 the server refuses to start (the pool holds less than one request, a real failure we met).

**`15-quantization`.** Experiment `quantization`: FP8 weights halve the bytes of a decode step for the weight part, the KV cache in FP8 doubles the tokens that fit. Always show the quality check next to the speed-up; the probe is a spot check with a stated resolution (`docs/MODEL-SELECTION.md` section 3).

**`16-parallelism`.** Replicas against tensor parallelism. The two-GPU comparison (`experiments/tensor-parallel`) needs a two-GPU machine and was **never measured** here (no two-GPU stock, `experiments/tensor-parallel/RESULTS.md`): present it as arithmetic and a hypothesis, and show it only if you have run it yourself.

**`17-lab-optimize`.** Lab 4, see section 5. One lever per group, each with a variation the lectures did not show. Collect each group's written prediction before its first run; the reference results anchor only what the lectures showed. Each group restarts its own pod: stagger the restarts if you watch the cost of failures.

**`18-demos`.** Skippable, except its last three slides (predictions scored, the five sentences of the runtime part, the bridge to production). Order by value: speculative decoding (`spec-ngram`), the intentional start failure (`oom-demo`), and tensor parallelism only on a two-GPU machine. The vLLM against Ollama or llama.cpp comparison and the mixture-of-experts demo are prepared but were **not run** in the validation (`experiments/demos/RESULTS.md`): run them once yourself before you show them. Revisit the predictions of the checkpoint: which resource was the bottleneck, and who was right?

**`19-production-architecture`.** Use the workshop's own pods as the worked example: one shared server per group, loopback only, SSH tunnels, an API key that guards `/v1` and nothing else. Name what is a workshop simplification.

**`20-containerization`.** Participants build the CPU-only client image on their laptops and run it against the group endpoint through their tunnel (`docs/SETUP.md` section 3). Docker is not available on the pods, which is itself the lesson: on a managed platform the image is the deployment unit. Read `deploy/vllm/Dockerfile` and `monitoring/docker-compose.yml` together.

**`21-observability`.** Start the embedding server before this module if RAG follows (`P: wsctl embed start`). The incident exercise runs with one ticket per group, in parallel: see "Incident exercise" in section 5.

**`22-scaling`.** Use the measured start-up times as the scaling argument (section 3): a replica takes about 40 seconds with warm caches and about 3 minutes from a cold start to become ready, so autoscaling from zero is a latency event. Skippable: KV-aware routing and prefill/decode disaggregation (one slide).

**`23-security-sovereignty`.** Frame it as engineering input, not legal advice, every time law is mentioned. Case study: this workshop's setup (open model, EU-adjacent region, US provider): classify each component with the sovereignty formula.

**`24-rag`.** Guided run of `apps/rag-demo` on the pod (the embedding server must be running). The handbook corpus contains a superseded policy on purpose: show what the retriever returns when both versions are indexed.

**`25-tools-agents`.** Guided run of the agent loop with the token ledger; the point is `ONE USER REQUEST → MULTIPLE MODEL CALLS → MORE TOKENS → MORE GPU LOAD`.

**`26-lab-architecture`.** Lab 5, see section 5. The lab ends at what the groups produce; the defenses are in the next module.

**`27-capstone-close`.** Each group gives a short defense; another group asks the questions (let the next group in the order ask, so every group defends once and questions once). The defenses are the debrief of Lab 5. Close with the 15 decision questions, and read back the opening sentences if you collected them.

## 5. Labs

For each lab: what you do before, what happens during, what you should observe, what usually goes wrong, how to recover, and how to debrief. All lab files are `tasks/NN-*.md`; participants' recovery is `./scripts/reset.sh lab-NN` (it never deletes their work).

The letters A to D mean different things in Lab 1 (the model-selection scenarios), Lab 4 (the levers) and Lab 5 (the architecture scenarios), and the incident exercise has its own tickets A to C. Say which one you mean.

### Lab 0: preflight (before the first module)

- **Before the lab.** Pods verified; each participant has your host, port and user name (and the public key you added).
- **During the lab.** Nothing: it is homework. Be reachable by chat after you send the access details.
- **Expected observation.** `./scripts/preflight.sh` ends with `0 failed`; the login test prints the GPU name `NVIDIA RTX PRO 6000 Blackwell Server Edition`.
- **Common failure.** Old Python; Docker not running; wrong user name or port; a key line pasted with a line break; the private key sent instead of the `.pub` file (delete the message, tell them to create a new key pair).
- **Recovery.** `T: infra/add-participant-key.sh --host <ip> --port <port> <user>` (see `infra/README.md`); never accept a private key.
- **Debrief.** Collect who is not ready before the first module starts and fix the logins at the first natural pause.

### Lab 1: model selection

- **Before the lab.** Groups formed (3 to 5 people), split into sub-groups. Each sub-group takes **one** scenario first (A to D), finishes it, then takes another or swaps. `docs/MODEL-SELECTION.md` section 6 holds the worksheets. The lab follows the GPU, sizing, mechanics and model-selection modules, so KV sizing, TTFT and prefill are taught before it.
- **During the lab.** Walk the groups. The question to ask everyone: "Which smaller model did you consider, and why did you reject it?" Make them run `scripts/sizing.py`.
- **Expected observation.** Every block names a model, a precision, a context length and a trade-off; license entries name the license and a consequence. Reduced scope (two good blocks instead of four) is a legitimate outcome. See section 11 for what strong answers contain.
- **Common failure.** Picking a model by leaderboard name; counting only weights; a license entry that says only "open"; forgetting the embedding model in the RAG scenario.
- **Recovery.** `./scripts/reset.sh lab-01 --hard` gives a clean template (the old file is saved first).
- **Debrief.** One choice per group, briefly: what did you give up? Then the license differences between families.

### Lab 2: first inference server

- **Before the lab.** `P: wsctl status`: `main` is `baseline` and healthy on every pod. Nobody restarts anything in this lab.
- **During the lab.** Everyone is on the same shared server, so the first queueing may already appear when everybody sends long requests at once: point it out, it is the lead-in to the benchmarking lab.
- **Expected observation.** From `wsctl info`: weights about 15.27 GiB, KV cache about 58 GiB and about 420,000 tokens; time to first token grows with prompt length and tokens per second per request hardly changes; temperature does not change speed; GPU utilization shows 100 % even for a single request.
- **Common failure.** A 401 (the key is set at login: log in again); the `sizing.py` check off by 2x or 4x (2x: the cache stores keys **and** values; 4x: the 32 query heads were used instead of the 8 KV heads); starting a second model server (never: the GPU memory belongs to the shared server).
- **Recovery.** `./scripts/reset.sh lab-02`; a stuck server: `T: infra/reset-machine.sh --host <ip> --port <port> servers`.
- **Debrief.** Draw `REQUEST → MODEL → GPU → TOKENS → METRICS` on the board and put one number from the participants' reports at each arrow.

### Lab 3: benchmark the baseline

- **Before the lab.** The server runs `baseline`; Grafana tunnels open. Four roles per group, as on the slides and in the task: the *driver* runs the sweep, the *dashboard reader* watches Grafana (GPU utilization, running and waiting requests), the *recorder* fills the report, the *skeptic* asks which number would change the group's mind. The roles rotate for the contention round.
- **During the lab.** Insist on the prediction first. Remind groups: one benchmark at a time per group, except the contention round. Watch `P: wsctl status` for stray processes.
- **Expected observation** (the reference run in `benchmark/results/reference/concurrency/`): aggregate tokens per second about 84, 310, 551 and 900 at concurrency 1, 4, 8 and 16; time to first token p95 about 73, 210, 416 and 821 ms; tokens per second per request 86, 83, 79 and 69; GPU utilization about 100 % at every level; power 362 W rising to 425 W. Your groups' numbers are within a few percent. In the contention round (two benchmarks at once) each run is slower than the same concurrency alone: in the dry run two benchmarks at concurrency 8 got 447 tokens/s each (894 together, the same as one benchmark at concurrency 16) and a time to first token p50 of 405 and 743 ms against 364 ms alone. Have the groups compare each with the concurrency-8 row of the first run.
- **Common failure.** The prefix-cache warning (an earlier run used the same prompts: run again without `--seed`); two benchmarks at once by accident; numbers 20 % off because someone else used the server.
- **Recovery.** `./scripts/reset.sh lab-03 --server` puts the server on `baseline` and copies the reference results; groups continue with those and say so.
- **Debrief.** Where does a user stop being happy? Use the SLO table: concurrency 8 meets TTFT p95 below 800 ms with 79 tokens/s per request, concurrency 16 misses it by 21 ms. GPU utilization says nothing; waiting requests do.

### Lab 4: optimize the deployment

Lab 4 is not a replication of the lectures. Each group takes one lever (A quantization, B prefix caching, C context length and pool size, D concurrency cap) and a variation of it that the lecture modules did not show (the table in `tasks/04-optimization.md`). The group writes a **prediction** before anything runs, measures, and then compares prediction, result and the lecture's reference.

- **Before the lab.** Assign one lever per group. E (tensor parallelism) is an optional fifth, only if a two-GPU machine is available and you have run it yourself. Each group has the server to itself, because each pod serves one group. Have the reference results of the lecture configurations at hand as the anchor (`benchmark/results/reference/`, explained in `experiments/quantization`, `prefix-cache`, `context-length` and `concurrency`); they are **not** the answers to the variations.
- **During the lab.** Collect each group's written prediction (a number or a direction per metric, with the reason in terms of the resource model) **before** the group starts its runs, and keep them for the debrief. Each restart takes the model offline: about 40 seconds for `baseline` with warm caches, up to about 2.5 minutes for the first `fp8` start (section 3). Tell groups to read the start-up numbers and to prepare the before-run first.
- **Expected observation.** No reference run exists for the variations, so treat what follows as hypotheses from the resource model, to be corrected by your own dry run:
  - **A (FP8 KV cache on the small pool at 16 clients).** FP8 halves the bytes per cached token, so the same pool holds twice the tokens (about 7 requests of 8,192 tokens instead of about 3); both configurations still queue at 16 clients, but FP8 runs more requests together and preempts less. The pool, not the weights, is the lever.
  - **B (shorter shared prefix).** The prefill saved scales with the shared share of the prompt: expect a smaller TTFT gain and a lower hit rate than the lecture's 2,000-token prefix, still in the right direction.
  - **C (a middle pool).** An 8 GiB pool holds about 7 requests of 8,192 tokens (147,456 B per token × about 8,300 tokens ≈ 1.14 GiB per request): at 4 clients nothing waits, at 8 and 16 a queue forms, with fewer preemptions than the 4 GiB pool. Where exactly the knee falls is what the group measures.
  - **D (caps of 4 and 16).** Aggregate throughput is roughly the cap times the per-request speed once clients exceed the cap: cap 4 pins lower than the lecture's cap of 8 (about 550 tokens/s) and queues earlier, cap 16 behaves like the default at 16 clients and pins below it at 32. TTFT p95 grows with the queue.
- **Common failure.** A prediction written after the run; comparing different workloads or concurrency levels; "after" numbers that are too good because of the prefix cache; a variation that does not start (an over-small pool or a context longer than the pool: the previous profile is restored, that is a result, record it).
- **Recovery.** `./scripts/reset.sh lab-04 --server`; `./scripts/start-vllm.sh baseline`; the reference results can fill in the baseline side where the workload matches, and the group says so.
- **Debrief.** A short report per group that leads with the trade-off and with the wrong prediction. Questions to ask: "What did your prediction get wrong?" "Which assumption of the resource model failed?" "Under which condition would you not use this?" "What would you measure next?" A wrong prediction with the failed assumption named is a good result; a right prediction with no reason is not.

### Incident exercise (observability module)

The exercise is part of the observability module, not a lab with a task file. Each group gets **one** ticket, and all groups work in parallel on their own pods. With four groups the tickets are A, B, C and A again, or your choice.

- **Before the exercise.** Everyone has Grafana open through a tunnel. Groups do not see what you start.
- **During the exercise.** You start the load on each group's server, with the profiles and harness options named on the slides: for ticket A the profile `max-seqs-8` and open-loop load above capacity (`./scripts/benchmark.sh --request-rate`); for B the `baseline` profile with long prompts (`--workload rag-long-context` or a long `--input-tokens`); for C the profile `kv-constrained` with several concurrent long contexts. There is no dedicated incident script. Switching a profile restarts that group's server: about 40 seconds with warm caches, up to about 2.5 minutes the first time (section 3). Groups fill the diagnosis worksheet for their ticket: first panel that moved, panels that stayed flat, what is full, one change, the metric that would warn.
- **Expected observation.** The answer key is in the speaker notes of the worksheet slide. **Its expected readings are hypotheses until you have run a dry run**: no measured result file exists for these conditions. Correct the key after your dry run.
- **Common failure.** Groups name GPU utilization as the symptom (it is 100 % in all three tickets); tickets A and C both queue, so groups mix them up: the difference is KV usage and preemptions.
- **Recovery.** `P: wsctl start baseline` on the pod; `P: wsctl reap` for stray load processes.
- **Debrief.** Compare the groups' readings with the reading table on the last slide of the module; a shared answer after the attempt is fine.

### Lab 5: production architecture

- **Before the lab.** Scenarios assigned (A to D in `tasks/05-production-design.md`). The template has the 15 decision questions at the end.
- **During the lab.** Ask for the arithmetic: concurrency = arrival rate × time in the system; GPUs = required throughput ÷ measured throughput at the SLO; cost per useful workload.
- **Expected observation.** Every number labeled measured, estimated or assumed; a named security boundary and what it does not protect; the first thing that breaks at ten times the load.
- **Common failure.** A GPU count from nowhere; "use Kubernetes" without a bottleneck; security as a list of products; forgetting that agents multiply model calls.
- **Recovery.** `./scripts/reset.sh lab-05`.
- **Debrief.** None of its own: the lab ends at what the groups produce, and the defenses in module `27-capstone-close` are its debrief (the other groups ask the questions). Do not book a second debrief here.

## 6. Trainer commands

```bash
# per pod, from your laptop
infra/deploy-to-pod.sh   --host <ip> --port <port> --group alpha     # build or rebuild a pod
infra/verify-machine.sh  --host <ip> --port <port>                    # PASS / WARN / FAIL checks
infra/reset-machine.sh   --host <ip> --port <port> servers            # restart the shared servers
infra/reset-machine.sh   --host <ip> --port <port> user <name>        # fresh repo copy for one person
infra/sync-participants.sh --group alpha                              # late joiner: add to participants.yaml first
infra/cleanup.sh         --host <ip> --port <port> --collect          # end of each session: collect artifacts

# on a pod (root)
wsctl status | profiles | info | logs 80
wsctl start <profile> [--set max-num-seqs=16]       # restarts the model for the whole group
wsctl embed start | stop                            # embeddings for the RAG demo (port 8001)
wsctl reap                                          # kill vLLM processes wsctl did not start
nvidia-smi ; ./scripts/gpu-status.sh --watch
```

Experiments (only on a pod that no group is using): `T: experiments/run-session.sh --host <ip> --port <port> --label <label> <experiment ...>`. It copies the repository, runs `experiments/runner.py` detached, follows its log and copies the results to `benchmark/results/<date>-rtxpro6000-<label>/` (about 3 to 10 minutes per experiment, 37 minutes for the five single-GPU experiments of the validation).

## 7. Failures and recovery

`docs/TROUBLESHOOTING.md` has the symptom tables for participants and trainer; the ones that cost most time:

| Failure | Cause | What you do |
| --- | --- | --- |
| The shared server is stuck or the model does not answer | A crashed engine, or a participant started something else | `P: wsctl status`; `wsctl reap` for strays; `T: infra/reset-machine.sh ... servers` (about 40 s) |
| A profile does not start | Memory, an invalid `--set`, GPU memory held elsewhere | The previous profile comes back automatically (look for "rolling back"); `wsctl logs 60` shows why |
| A pod restarted (new port, empty container disk) | Provider event or someone restarted it | `T: infra/deploy-to-pod.sh ...` again (5 min 41 s measured), send the **new port**; participants will see a new SSH host key |
| A participant cannot log in | Wrong user or port, key not added | `T: infra/add-participant-key.sh`; check `ws-user list` on the pod (as root) |
| Grafana shows nothing | Prometheus target down, or the tunnel is missing | `P: wsmon status`; reconnect with `-L 3000:127.0.0.1:3000` |
| Benchmark numbers differ wildly between members | Two benchmarks at the same time | One benchmark at a time per group (except the contention round); `wsctl status` |
| No GPU in a new pod | Stock | Create in another listed data center; keep a spare pod ready from before the first session |

The recovery path for a broken pod takes five to six minutes: `deploy-to-pod.sh` (rebuilds users, servers and monitoring from `infra/participants.yaml` and the model cache), `verify-machine.sh`, new port to the group, group continues from `./scripts/reset.sh lab-NN --server`.

## 8. Pacing without a clock

The material is free-form: there are no times in the slides, the tasks or this guide, and you decide how long each module takes. What replaces the clock:

- **Natural stopping points** are the ends of the labs. `./scripts/reset.sh lab-NN` restores the starter state of a lab without deleting anyone's work, so a group can leave after any lab and pick up at the next module without losing anything.
- **A check-in question** at the start of each work session and after each lab, for example: "What is one thing from the last stretch you could now explain to a colleague, and one you could not?" and, after a lab, "Which number surprised you?". The answers tell you whether to slow down or to move on.
- **Short energizers or breaks** whenever a group has listened for a long stretch: stand up, have a pair compare a prediction, or hand a question to the groups instead of answering it yourself. Do not wait for the group to ask.
- **Shortening the material** when the group needs the room elsewhere: see below.
- **No minutes anywhere.** Measured durations such as server start-up times are technical facts and stay; they are not a schedule.

### Shortening the material

Cut in this order, and keep every lab's debrief (details in `docs/CURRICULUM.md` section 7; the only module marked `skippable` in `config/workshop.yaml` is the demos module):

1. The demos of `18-demos`; show one demo inside `16-parallelism` if you like. Keep the last three slides of the module (predictions scored, the five sentences of the runtime part, the bridge to production).
2. In `02-models`, skip multimodal and reasoning detail.
3. In Lab 1, two scenarios instead of four.
4. In Lab 3, concurrency 1, 8 and 16 only.
5. In `22-scaling`, one slide for KV-aware routing and disaggregation.
6. Lab 5: one scenario defended per group, shorter defenses.

## 9. GPU cost control

Price used in this repository: **$2.49 per GPU-hour** (Secure Cloud, one RTX PRO 6000, read from the live catalog at validation time; read it again). Per-second billing; a running pod costs the same idle or busy. Four pods cost 4 × $2.49 = $9.96 per hour together, so the bill is that figure times the hours the pods exist: every 10 hours with all four pods running cost $99.60. The pacing you choose sets the total (`docs/GPU-POOL.md` has the same arithmetic).

| Plan | Cost |
| --- | --- |
| Keep every pod running from the first setup until the last session ends | $9.96 per hour for the whole span, breaks included |
| Stop the pods during a long break and rebuild each one before the next session | $9.96 per hour only while the pods run, plus one rebuild per pod after every stop |

A stopped pod saves $9.96 per hour for the four of them, but each stop wipes the container disk and may return the pod without a GPU. A rebuild takes five to six minutes per pod, about $0.24 of GPU time (341 s ÷ 3,600 × $2.49). Keeping the pods running is the safe default; stop them only for a long break, and only when stock is not *Low*. A network volume (about $0.07 per GB-month) would keep models between rebuilds; this repository did not validate that path.

### Before the workshop

- [ ] Machines provisioned (price stated and noted)
- [ ] GPUs verified (`nvidia-smi` shows the RTX PRO 6000 on every pod)
- [ ] Models cached (`verify-machine.sh` lists them at the pinned revisions)
- [ ] Containers cached (the vLLM image digest is in `infra/versions.env`; participants' client image builds on their laptops)
- [ ] SSH access tested for every participant (`preflight.sh --host ...`)
- [ ] Monitoring tested (dashboard through a tunnel shows live panels)

### During the workshop

- [ ] Idle machines checked: a pod nobody uses is still billed; spare pods are deleted
- [ ] GPU utilization monitored on Grafana (remember: it reads 100 % when busy and when merely waiting for memory; look at running and waiting requests)
- [ ] Unexpected duplicate model servers stopped (`wsctl status`, `wsctl reap`)

### End of each session

- [ ] Persist required results: `T: infra/cleanup.sh --host <ip> --port <port> --collect`
- [ ] Stop unnecessary workloads (the embedding server after the RAG modules, demo profiles)
- [ ] Verify machine state: `infra/verify-machine.sh`; servers on `baseline`

### After the workshop (shutdown checklist)

- [ ] Revoke participant access: `T: infra/cleanup.sh --all --collect --revoke --stop-servers`
- [ ] Remove temporary credentials: the group API keys live on the pods and die with them; delete `infra/participants.yaml` and any local copies of participants' keys
- [ ] Terminate GPU instances: `delete-pod` for every pod (Runpod MCP) or terminate in the console
- [ ] Verify instances are terminated: `list-pods` is empty
- [ ] Verify billing has stopped: `list-billing` hourly buckets show no further pod cost, and the account balance stops falling

## 10. Risk register

| Risk | Likelihood | Effect | Mitigation |
| --- | --- | --- | --- |
| GPU stock: four pods not available together (stock was *Low*) | medium | no machine for a group | create early, spare pod, fallback data center, groups of 5 on fewer pods |
| Pod restarted by the provider | low | 5 to 6 minute outage, new port | rebuild path rehearsed; participants warned that the port may change |
| A participant leaks the group API key or exposes a port | low | misuse of one pod | keys only for the group; vLLM binds loopback; `docs/SECURITY.md` |
| Cost overrun: pods left running | medium | hundreds of dollars | shutdown checklist; `list-billing` after the workshop |
| Slow participant laptops or links | medium | labs take longer than planned | everything heavy runs on the pod; `reset.sh` fall-backs; the debrief is the protected part |
| A lab variation crashes the server | medium | group loses time on a restart | automatic rollback; reference results for the lecture configurations; `reset.sh lab-04 --server` |
| Model license or availability changed | low | slides out of date | re-check well ahead of the first session; pinned revisions are kept on the pods |
| Heise date or format changes | n/a | the material needs another pacing | the content holds no dates, days or clock times; the module path is free-form |

## 11. What strong answers look like

Labs 1 and 5 have no single right answer. These are the checks and the arithmetic to expect, derived from the measured reference results (a proxy for other workloads, not a promise).

### Lab 1 (model selection)

Little's law (concurrency = arrival rate × time in the system) is first explained in the measuring module, after this lab, and prefill rate and TTFT come from the mechanics module before it. Where a strong answer below uses Little's law, it is **optional** here: a group that has not met it can reason with "requests in flight = arrival rate × time each one stays".

- **A, German internal assistant, 20 users, 3,000 tokens of context.** KV per request about 3,400 tokens × 147,456 B = 0.47 GiB, so 20 requests need about 9 GiB of cache: memory is not the constraint; time is. A prefill of 3,000 tokens takes about 0.2 s alone (the baseline prefills about 17,000 tokens/s) and a 300-token answer about 4 s at 68 to 79 tokens/s. "Within 10 seconds" therefore fits without thinking mode and fails with a long thinking trace. Strong answers state the output length they assume and test German on their own documents.
- **B, ticket classification, 5 per second at peak.** About 300 output tokens/s and 1,500 prompt tokens/s; by Little's law about 5 requests in flight, a regime where one 8B model on one GPU meets TTFT p95 of 416 ms. The real question is whether a smaller model (the 1.7B in `config/models.yaml`) is accurate enough: a strong answer proposes the eval, not the answer.
- **C, coding assistant with 16,000 to 32,000 tokens of context.** A 32,768-token request holds 4.5 GiB of KV: about 13 such requests fill the 58 GiB pool (the server reports 12.92×), and 100 developers will exceed that at busy moments. The measured single-request TTFT is 0.95 s for 16,384 and 2.0 s for 28,672 prompt tokens on this GPU, so "first token within 1 s" cannot be met with uncached prefill of the whole repository; the answer is a shared prefix (prefix caching), a smaller context, or a faster GPU. Strong answers find this.
- **D, 2 million documents in 72 hours.** 7.7 documents/s, about 2,300 output and 23,000 input tokens/s. One GPU decodes about 1,700 tokens/s at concurrency 64 for a shorter workload and prefills about 17,000 tokens/s, so plan for at least two GPUs or a longer window; at three GPUs for 72 hours the GPU cost is about $540, or about $0.27 per thousand documents at $2.49 per GPU-hour. The restart cost (about 1 minute warm, 3 minutes cold) matters for a resumable batch.

### Lab 2 (first inference server)

- The formula check against the server's own KV memory lands within 2 % (in the reference run within 0.01 %): it validates the per-token arithmetic, not the budget.
- The sizing script's own estimate of the KV capacity, with its default 4 GiB overhead, lands about 3 % from the server's log line: 412,893 tokens against 423,328 in the validated run (2.5 %) and 426,992 after later restarts (3.3 %).
- A larger gap is an arithmetic error: off by 2x means the cache was counted as keys only (it stores keys **and** values); off by 4x means the 32 query heads were used instead of the 8 KV heads.

### Lab 5 (production architecture)

- Concurrency is arrival rate times time in the system; GPUs follow from measured throughput at the SLO (this GPU: 8 concurrent requests meet the course SLO, about 550 tokens/s; 16 miss it by a few percent).
- Cold start of a replica: about 40 seconds restart, about 3 minutes on a fresh machine: autoscaling from zero is a latency event.
- The security boundary names what it does **not** protect (for example the unauthenticated `/metrics`, the Grafana viewer access, a shared API key per group).
- A cost per useful workload with the word "useful" defined.
- The first thing that breaks at ten times the load: usually the waiting queue and TTFT, before GPU memory.
