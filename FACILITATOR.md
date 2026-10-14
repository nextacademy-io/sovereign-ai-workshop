# Facilitator guide

The operating manual for the trainer: what to prepare, what to run, what you should see, what goes wrong, how to recover and how to stop paying for GPUs. It is written to be used with the slides (`slides/sections/<block>.md`, speaker notes on every slide), the tasks (`tasks/`) and the infrastructure scripts (`infra/`).

Conventions: **T:** is a command on your laptop, **P:** is a command on a GPU pod (as root; participants use `sudo wsctl ...`). `<ip>` and `<port>` are the pod's SSH address; the port changes whenever a pod is rebuilt. Times are relative to the start of each day (09:00). Every measured number comes from `benchmark/results/reference/` and carries its hardware and date there; the experiments' `RESULTS.md` files explain them.

## 1. The workshop on one page

| | |
| --- | --- |
| Promise | Run, measure, optimise and operate an open model on your own infrastructure; inference engineering first, applications on top. |
| Format | 3 days, about 7 teaching hours each, remote, up to 15 participants in four groups (alpha, beta, gamma, delta). |
| Machines | One pod per group, each with one NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB class). Participants need no GPU and no account: they connect over SSH. |
| Servers | One shared vLLM server per pod on `127.0.0.1:8000` (Qwen3-8B, profile `baseline`), an embedding server on `:8001`, Prometheus, Grafana and a GPU exporter. Nothing is reachable except through SSH. |
| Work | Six tasks (00 to 05), one growing document `workshop-artifacts/inference-report.md`, three trainer demos, five debriefs. |
| Your rule | Anything risky, expensive or one-off is demonstrated by you: restarts of the server outside the labs, the OOM demo, speculative decoding, the 2-GPU comparison, destroying the machines. |

The teaching rhythm in every experiment block: concept, system, experiment, **prediction**, measurement, explanation, production consequence. Ask for the prediction before showing the number; the number never speaks for itself.

## 2. Preparation

Do each step once per pod. `infra/provision.md` has the details and the Runpod MCP calls; `infra/README.md` lists the scripts.

### Two weeks before

- [ ] Re-validate the models: `config/models.yaml` pins revisions; read the licence of each repository again (licences drift) and update `docs/MODEL-SELECTION.md` if one changed.
- [ ] Read the live GPU price and stock (`list-gpu-types`, `get-capacity` for `NVIDIA RTX PRO 6000 Blackwell Server Edition`). Stock was *Low* when this repository was validated: two-GPU stock only existed on CUDA 13.2 hosts. Decide the fallback (another EU data center, or another GPU class: every measured number then changes and the Day 2 slides need your own run).
- [ ] Decide the data center. EUR-IS-2 (Iceland) is inside the EEA but not the EU; `EU-RO-1` is in the EU. See `docs/DIGITAL-SOVEREIGNTY.md`.
- [ ] Collect each participant's **public** SSH key (task 00); fill `infra/participants.yaml` (public keys only; the file is gitignored).
- [ ] Do a full dry run on one pod: tasks 02 to 04 as a participant (the timeboxes in this repository were measured that way; yours will differ with your pace).

### The day before

- [ ] Create the pods (state the hourly price first: price × pods = per-hour cost). Create them early: they cost money from creation, but a pod that cannot be created the evening before is the larger risk.
- [ ] `T: infra/deploy-to-pod.sh --host <ip> --port <port> --group alpha` for each pod (about 5 minutes plus model download; see section 3), then `T: infra/verify-machine.sh --host <ip> --port <port>`: every line PASS.
- [ ] Send each participant host, port and user name. Ask them to run `./scripts/preflight.sh --host <host> --port <port> --user <user>`.
- [ ] Keep the pods **running** until the workshop ends. A stopped pod can come back without a GPU; `terminate` only at the very end.
- [ ] Open Grafana through a tunnel on your laptop once and look at the dashboard *KI ohne Cloud: inference*.

### One hour before each day

- [ ] `T: infra/verify-machine.sh` on all pods; `P: wsctl status` shows `main` on `baseline` and `embed` running.
- [ ] Day 2 and 3: the server must be on `baseline` (`P: wsctl start baseline` if not); start the embedding server on Day 3 (`P: wsctl embed start`).
- [ ] Billing: `list-billing` for yesterday's total against your estimate (section 9).
- [ ] Slides open in presenter mode (`pnpm dev`); `slides/dist` built as a fallback (`pnpm build`).

## 3. Infrastructure timing (measured)

From the validation sessions on Runpod Secure Cloud, EUR-IS-2, one RTX PRO 6000 per pod (`docs/GPU-POOL.md` has the log and the costs):

| Step | Measured |
| --- | --- |
| Pod created, container running | about 2 s |
| sshd answering | about 11 s later (the 9 GB image was cached on the host; a cold host adds the image pull) |
| Model download from the Hugging Face hub (Qwen3-8B, 16 GB) | 12.4 s (about 1.3 GB/s) |
| First vLLM start in a fresh container (empty compile caches) | 176 s from the first log line; 188 to 194 s as `wsctl` measured it in earlier starts |
| vLLM start with warm caches | 55 s in the log; 67.4 s as `wsctl` measured it |
| Restart of the same profile | 29 s in the log; 39.3 s as `wsctl` measured it |
| First start of the FP8 profile (new checkpoint, first compile) | 143 s |
| Full rebuild of a restarted pod (`deploy-to-pod.sh`) | 5 min 41 s (model cache seed about 60 s, monitoring 16 s, vLLM 194 s, embedding server 53 s) |
| A pod restart changes | the public SSH port (22290 became 22235 in the test), the SSH host key, and wipes the container disk; `/workspace` survives |

Plan the recovery of a broken pod as **five to six minutes** (`infra/deploy-to-pod.sh` again, then tell participants the new port), and never do it while a lab is running if a server restart will do.

## 4. Run sheet

The tables below are generated from [`config/workshop.yaml`](config/workshop.yaml) (`node scripts/gen-agenda.mjs`); the notes under them say what to do in each block. Block ids are the file names of the slide sections.

### Day 1: UNDERSTAND & RUN

<!-- agenda:runsheet-1:begin -->
| Time | Min | Block | Kind | Slides | Task and experiments | Skippable |
| --- | --- | --- | --- | --- | --- | --- |
| 09:00-09:30 | 30 | **Opening: why run models yourself** | lecture | `slides/sections/d1-01-opening.md` |  |  |
| 09:30-10:30 | 60 | **Modern language models** | lecture | `slides/sections/d1-02-models.md` |  |  |
| 10:30-10:45 | 15 | *Break* | break |  |  |  |
| 10:45-11:45 | 60 | **Model selection** | lecture and exercise | `slides/sections/d1-03-model-selection.md` |  |  |
| 11:45-12:25 | 40 | **Lab 1: select models for four scenarios** | lab | `slides/sections/d1-04-lab-model-selection.md` | Task `01-model-selection` (30 min) |  |
| 12:25-13:30 | 65 | *Lunch* | break |  |  |  |
| 13:30-14:30 | 60 | **GPU fundamentals for inference** | lecture | `slides/sections/d1-05-gpu-fundamentals.md` |  |  |
| 14:30-15:15 | 45 | **GPU sizing: weights, KV cache, overhead** | lecture and exercise | `slides/sections/d1-06-gpu-sizing.md` | `experiments/baseline` |  |
| 15:15-15:30 | 15 | *Break* | break |  |  |  |
| 15:30-16:15 | 45 | **Inference mechanics: prefill, decode, latency** | lecture and exercise | `slides/sections/d1-07-inference-mechanics.md` |  |  |
| 16:15-16:45 | 30 | **First vLLM deployment (trainer demo)** | trainer demo | `slides/sections/d1-08-first-vllm.md` |  |  |
| 16:45-17:30 | 45 | **Lab 2: first inference server** | lab | `slides/sections/d1-09-lab-first-server.md` | Task `02-first-inference-server` (35 min) |  |
<!-- agenda:runsheet-1:end -->

**`d1-01-opening`.** Check that every participant has run task 00; collect those who cannot log in and fix them during the first break, not now. Ask for one sentence from each person: what do you run, or want to run, on your own infrastructure? Return to these at the close.

**`d1-02-models`.** Live: tokenise a sentence on the shared server (no key needed for `/tokenize`):
`P: curl -s http://127.0.0.1:8000/tokenize -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen3-8B","prompt":"KI ohne Cloud: Hello, tokenizer!"}'` prints `{"count":8,...,"tokens":[80971,28883,14817,25,21927,11,45958,0]}`. A German compound such as "Unabhängigkeit" gives 3 tokens (add `"return_token_strs":true`). Discussion prompt: why does the same text cost different numbers of tokens in different models? Skippable: multimodal and reasoning detail (10 min).

**`d1-03-model-selection`.** The model facts are as researched for this delivery: re-check them (section 2). Push the room away from leaderboard names towards the criteria in `docs/MODEL-SELECTION.md`. Prompt: which smaller model would you try first, and what would make you reject it?

**`d1-04-lab-model-selection`.** Lab 1, see section 5. Cut if short: two scenarios instead of four.

**`d1-05-gpu-fundamentals`.** Show `P: nvidia-smi` on your pod and read the GPU name, memory and driver aloud. The point to land: the datasheet bandwidth (1,597 GB/s for this GPU) and the ops-to-byte ratio decide which phase is limited by what; `nvidia-smi` utilization is not efficiency (the measured baseline shows 99 % with a single request).

**`d1-06-gpu-sizing`.** Prediction before the server's number: participants estimate the KV capacity with `scripts/sizing.py` (expected 412,893 tokens with the default 4 GiB overhead) and you show the log line (`P: wsctl logs 80 | grep "KV cache"`: 423,328 tokens in the validated run, 426,992 after later restarts). Prompt: why is the result within 3 % although we guessed the overhead?

**`d1-07-inference-mechanics`.** The experiment sequence uses measured data: bandwidth bound 10.3 ms against a measured inter-token latency of 11.6 ms. Make them predict first (what limits one decode step?). The Day 2 prediction is written down here: prefill scales with prompt length and is compute-heavy; decode is limited by moving weights and KV through memory.

**`d1-08-first-vllm`.** Demo, you drive: `nvidia-smi`; `curl .../v1/models` with the key; one completion; one stream; `wsctl logs`; read the start-up numbers (weights 15.27 GiB, KV cache, graph capture, time to ready). The API is the product; everything else is what makes it behave.

**`d1-09-lab-first-server`.** Lab 2, see section 5.

### Day 2: MEASURE & OPTIMIZE

<!-- agenda:runsheet-2:begin -->
| Time | Min | Block | Kind | Slides | Task and experiments | Skippable |
| --- | --- | --- | --- | --- | --- | --- |
| 09:00-09:30 | 30 | **Recap and bottleneck predictions** | discussion | `slides/sections/d2-01-recap.md` |  |  |
| 09:30-10:30 | 60 | **Measuring inference** | lecture and exercise | `slides/sections/d2-02-measuring.md` |  |  |
| 10:30-10:45 | 15 | *Break* | break |  |  |  |
| 10:45-11:45 | 60 | **Lab 3: benchmark the baseline** | lab | `slides/sections/d2-03-lab-benchmark.md` | Task `03-benchmark` (45 min)<br>`experiments/baseline`<br>`experiments/concurrency` |  |
| 11:45-12:30 | 45 | **Continuous batching** | lecture and exercise | `slides/sections/d2-04-continuous-batching.md` | `experiments/concurrency` |  |
| 12:30-13:30 | 60 | *Lunch* | break |  |  |  |
| 13:30-14:15 | 45 | **KV cache, PagedAttention and prefix caching** | lecture and exercise | `slides/sections/d2-05-kv-cache.md` | `experiments/context-length`<br>`experiments/prefix-cache` |  |
| 14:15-15:00 | 45 | **Quantization** | lecture and exercise | `slides/sections/d2-06-quantization.md` | `experiments/quantization` |  |
| 15:00-15:15 | 15 | *Break* | break |  |  |  |
| 15:15-16:00 | 45 | **Parallelism: replicas, tensor, pipeline, expert** | lecture and exercise | `slides/sections/d2-07-parallelism.md` | `experiments/tensor-parallel` |  |
| 16:00-17:00 | 60 | **Lab 4: optimize the deployment** | lab | `slides/sections/d2-08-lab-optimize.md` | Task `04-optimization` (40 min)<br>`experiments/quantization`<br>`experiments/prefix-cache`<br>`experiments/context-length`<br>`experiments/concurrency` |  |
| 17:00-17:30 | 30 | **Trainer demos: speculative decoding, OOM, tensor parallelism** | trainer demo | `slides/sections/d2-09-demos.md` | `experiments/tensor-parallel`<br>`experiments/demos` | yes |
<!-- agenda:runsheet-2:end -->

**`d2-01-recap`.** Collect each group's bottleneck predictions on paper or in the shared report; you will revisit them in the last block. Do not show Day 2 numbers yet.

**`d2-02-measuring`.** Make the point with the harness: `P: ./scripts/benchmark.sh --concurrency 1,8` once, live, and read each column of the table. The classic trap to demonstrate in words: a repeated seed is answered by the prefix cache (the harness uses a fresh random seed per run and warns above 5 % hit rate).

**`d2-03-lab-benchmark`.** Lab 3, see section 5. This is the block in which the groups discover contention: only one benchmark at a time per group.

**`d2-04-continuous-batching`.** Show the cap live if time allows: the measured effect of `--max-num-seqs 8` is an aggregate throughput pinned at about 550 tokens/s and a time to first token of 3 s at 16 clients (against 0.6 s). Reproducing it costs a restart for the group (40 s each way): only do it on your own demo pod, or show the reference results.

**`d2-05-kv-cache`.** Experiments: `context-length` and `prefix-cache` (RESULTS in `experiments/*/RESULTS.md`). The `kv-constrained` profile simulates a small card: a 4 GiB pool and a 16,384-token context limit, about 29,000 tokens, which holds three requests of 8,192 tokens. Say why the context limit is lowered: with the baseline 32,768 the server refuses to start (the pool holds less than one request, a real failure we met).

**`d2-06-quantization`.** Experiment `quantization`: FP8 weights halve the bytes of a decode step for the weight part, the KV cache in FP8 doubles the tokens that fit. Always show the quality check next to the speed-up; the probe is a spot check with a stated resolution (`docs/MODEL-SELECTION.md` section 3).

**`d2-07-parallelism`.** Replicas against tensor parallelism. The two-GPU comparison is a trainer demonstration on a separate two-GPU pod (`experiments/tensor-parallel`); if you have no results for it, present the hypothesis as a hypothesis.

**`d2-08-lab-optimize`.** Lab 4, see section 5. One hypothesis per group, one restart each: stagger so that only one group restarts at a time on your side if you watch the cost of failures.

**`d2-09-demos`.** Skippable (30 min). Order by value: speculative decoding (`spec-ngram`), the intentional start failure (`oom-demo`), tensor parallelism. Revisit the morning's predictions: which resource was the bottleneck, and who was right?

### Day 3: OPERATE

<!-- agenda:runsheet-3:begin -->
| Time | Min | Block | Kind | Slides | Task and experiments | Skippable |
| --- | --- | --- | --- | --- | --- | --- |
| 09:00-09:45 | 45 | **Production architecture** | lecture | `slides/sections/d3-01-production-architecture.md` |  |  |
| 09:45-10:30 | 45 | **Containerization and reproducible deployments** | lecture and exercise | `slides/sections/d3-02-containerization.md` |  |  |
| 10:30-10:45 | 15 | *Break* | break |  |  |  |
| 10:45-11:45 | 60 | **Observability: metrics, dashboards, incident investigation** | lecture and exercise | `slides/sections/d3-03-observability.md` |  |  |
| 11:45-12:30 | 45 | **Scaling strategies** | lecture | `slides/sections/d3-04-scaling.md` |  |  |
| 12:30-13:30 | 60 | *Lunch* | break |  |  |  |
| 13:30-14:30 | 60 | **Security, compliance and digital sovereignty** | lecture and exercise | `slides/sections/d3-05-security-sovereignty.md` |  |  |
| 14:30-15:15 | 45 | **RAG without framework hype** | lecture and exercise | `slides/sections/d3-06-rag.md` |  |  |
| 15:15-15:30 | 15 | *Break* | break |  |  |  |
| 15:30-16:00 | 30 | **Tool calling, MCP and agents** | lecture and exercise | `slides/sections/d3-07-tools-agents.md` |  |  |
| 16:00-17:00 | 60 | **Lab 5: production architecture challenge** | lab | `slides/sections/d3-08-lab-architecture.md` | Task `05-production-design` (45 min) |  |
| 17:00-17:30 | 30 | **Architecture defenses, decision framework, close** | discussion | `slides/sections/d3-09-capstone-close.md` |  |  |
<!-- agenda:runsheet-3:end -->

**`d3-01-production-architecture`.** Use the workshop's own pods as the worked example: one shared server per group, loopback only, SSH tunnels, an API key that guards `/v1` and nothing else. Name what is a workshop simplification.

**`d3-02-containerization`.** Participants build the CPU-only client image on their laptops and run it against the group endpoint through their tunnel (`docs/SETUP.md` section 3). Docker is not available on the pods, which is itself the lesson: on a managed platform the image is the deployment unit. Read `deploy/vllm/Dockerfile` and `monitoring/docker-compose.yml` together.

**`d3-03-observability`.** Start the embedding server before this block if RAG follows (`P: wsctl embed start`). The incident exercise: you generate a burst (`./benchmark/run.sh --concurrency 32`), then long prompts (`--workload rag-long-context`), then KV pressure on your demo pod (profile `kv-constrained`); each group names the panel that shows it (running and waiting requests, KV usage, TTFT) and the panel that does **not** (GPU utilization).

**`d3-04-scaling`.** Use the measured start-up times as the scaling argument: a replica takes 30 seconds to 3 minutes to become ready, so autoscaling from zero is a latency event. Skippable: KV-aware routing and prefill/decode disaggregation (one slide).

**`d3-05-security-sovereignty`.** Frame it as engineering input, not legal advice, every time law is mentioned. Case study: this workshop's setup (open model, EU-adjacent region, US provider): classify each component with the sovereignty formula.

**`d3-06-rag`.** Guided run of `apps/rag-demo` on the pod (the embedding server must be running). The handbook corpus contains a superseded policy on purpose: show what the retriever returns when both versions are indexed.

**`d3-07-tools-agents`.** Guided run of the agent loop with the token ledger; the point is `ONE USER REQUEST → MULTIPLE MODEL CALLS → MORE TOKENS → MORE GPU LOAD`.

**`d3-08-lab-architecture`.** Lab 5, see section 5.

**`d3-09-capstone-close`.** Five minutes per group; the audience asks the questions. Close with the 15 decision questions and read back the opening sentences from Day 1.

## 5. Labs

For each lab: what you do before, what happens during, what you should observe, what usually goes wrong, how to recover, and how to debrief. All lab files are `tasks/NN-*.md`; participants' recovery is `./scripts/reset.sh lab-NN` (it never deletes their work).

### Lab 0: preflight (before Day 1)

- **Before the lab.** Pods verified; each participant has your host, port and user name (and the public key you added).
- **During the lab.** Nothing: it is homework. Be reachable by chat for 30 minutes after you send the access details.
- **Expected observation.** `./scripts/preflight.sh` ends with `0 failed`; the login test prints the GPU name `NVIDIA RTX PRO 6000 Blackwell Server Edition`.
- **Common failure.** Old Python; Docker not running; wrong user name or port; a key line pasted with a line break; the private key sent instead of the `.pub` file (delete the message, tell them to create a new key pair).
- **Recovery.** `T: infra/add-participant-key.sh --host <ip> --port <port> <user>` (see `infra/README.md`); never accept a private key.
- **Debrief.** Collect who is not ready before Day 1 starts and fix the logins in the first break.

### Lab 1: model selection (30 minutes)

- **Before the lab.** Groups formed (3 to 5 people), one scenario per sub-group first (A to D). `docs/MODEL-SELECTION.md` section 6 holds the worksheets.
- **During the lab.** Walk the groups. The question to ask everyone: "Which smaller model did you consider, and why did you reject it?" Make them run `scripts/sizing.py`.
- **Expected observation.** Every block names a model, a precision, a context length and a trade-off; licence entries name the licence and a consequence. See section 11 for what strong answers contain.
- **Common failure.** Picking a model by leaderboard name; counting only weights; a licence entry that says only "open"; forgetting the embedding model in the RAG scenario.
- **Recovery.** `./scripts/reset.sh lab-01 --hard` gives a clean template (the old file is saved first).
- **Debrief.** One scenario per group, three minutes: what did you give up? Then the licence differences between families.

### Lab 2: first inference server (35 minutes)

- **Before the lab.** `P: wsctl status`: `main` is `baseline` and healthy on every pod. Nobody restarts anything today.
- **During the lab.** Everyone is on the same shared server, so the first queueing may already appear when everybody sends long requests at once: point it out, it is the lead-in to Day 2.
- **Expected observation.** From `wsctl info`: weights about 15.27 GiB, KV cache about 58 GiB and about 420,000 tokens; time to first token grows with prompt length and tokens per second per request hardly changes; temperature does not change speed; GPU utilization shows 100 % even for a single request.
- **Common failure.** A 401 (the key is set at login: log in again); the `sizing.py` check off by 40 % (keys **and** values, wrong head count); starting a second model server (never: the GPU memory belongs to the shared server).
- **Recovery.** `./scripts/reset.sh lab-02`; a stuck server: `T: infra/reset-machine.sh --host <ip> --port <port> servers`.
- **Debrief.** Draw `REQUEST → MODEL → GPU → TOKENS → METRICS` on the board and put one number from the participants' reports at each arrow.

### Lab 3: benchmark the baseline (45 minutes)

- **Before the lab.** The server runs `baseline`; Grafana tunnels open. One driver per group.
- **During the lab.** Insist on the prediction first. Remind groups: one benchmark at a time per group. Watch `P: wsctl status` for stray processes.
- **Expected observation** (the reference run in `benchmark/results/reference/concurrency/`): aggregate tokens per second about 84, 310, 551 and 900 at concurrency 1, 4, 8 and 16; time to first token p95 about 73, 210, 416 and 821 ms; tokens per second per request 86, 83, 79 and 69; GPU utilization about 100 % at every level; power 362 W rising to 425 W. Your groups' numbers are within a few percent. In the contention round (two benchmarks at once) each run is slower than the same concurrency alone: in the dry run two benchmarks at concurrency 8 got 447 tokens/s each (894 together, the same as one benchmark at concurrency 16) and a time to first token p50 of 405 and 743 ms against 364 ms alone. Have the groups compare each with the concurrency-8 row of the first run.
- **Common failure.** The prefix-cache warning (an earlier run used the same prompts: run again without `--seed`); two benchmarks at once by accident; numbers 20 % off because someone else used the server.
- **Recovery.** `./scripts/reset.sh lab-03 --server` puts the server on `baseline` and copies the reference results; groups continue with those and say so.
- **Debrief.** Where does a user stop being happy? Use the SLO table: concurrency 8 meets TTFT p95 below 800 ms with 79 tokens/s per request, concurrency 16 misses it by 21 ms. GPU utilization says nothing; waiting requests do.

### Lab 4: optimise the deployment (40 minutes)

- **Before the lab.** Assign hypotheses (A quantization, B prefix caching, C context length, D concurrency or batching). Each group has the server to itself, because each pod serves one group.
- **During the lab.** Each restart takes the model offline: about 40 seconds for `baseline`, about 2.5 minutes for the first `fp8` start. Tell groups to read the start-up numbers and to prepare the before-run first.
- **Expected observation** (reference results in `benchmark/results/reference/`): see `experiments/quantization`, `prefix-cache` and `context-length` (RESULTS.md in each) and `experiments/concurrency` for D.
- **Common failure.** Comparing different workloads or concurrency levels; "after" numbers that are too good because of the prefix cache; a profile that does not start (the previous profile is restored: that is a result, record it).
- **Recovery.** `./scripts/reset.sh lab-04 --server`; `./scripts/start-vllm.sh baseline`; reference results for the missing side.
- **Debrief.** Five minutes per group, trade-off first: what improved, what got worse, what it costs to operate, under which condition you would not use it.

### Lab 5: production architecture (45 minutes)

- **Before the lab.** Scenarios assigned (A to D in `tasks/05-production-design.md`). The template has the 15 decision questions at the end.
- **During the lab.** Ask for the arithmetic: concurrency = arrival rate × time in the system; GPUs = required throughput ÷ measured throughput at the SLO; cost per useful workload.
- **Expected observation.** Every number labelled measured, estimated or assumed; a named security boundary and what it does not protect; the first thing that breaks at ten times the load.
- **Common failure.** A GPU count from nowhere; "use Kubernetes" without a bottleneck; security as a list of products; forgetting that agents multiply model calls.
- **Recovery.** `./scripts/reset.sh lab-05`.
- **Debrief.** The defences are the debrief: the other groups ask the questions.

## 6. Trainer commands

```bash
# per pod, from your laptop
infra/deploy-to-pod.sh   --host <ip> --port <port> --group alpha     # build or rebuild a pod
infra/verify-machine.sh  --host <ip> --port <port>                    # PASS / WARN / FAIL checks
infra/reset-machine.sh   --host <ip> --port <port> servers            # restart the shared servers
infra/reset-machine.sh   --host <ip> --port <port> user <name>        # fresh repo copy for one person
infra/sync-participants.sh --group alpha                              # late joiner: add to participants.yaml first
infra/cleanup.sh         --host <ip> --port <port> --collect          # end of day: collect artifacts

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
| Benchmark numbers differ wildly between members | Two benchmarks at the same time | One driver per group; `wsctl status` |
| No GPU in a new pod | Stock | Create in another listed data center; keep a spare pod from the day before |

The 5-minute recovery path for a broken pod: `deploy-to-pod.sh` (rebuilds users, servers and monitoring from `infra/participants.yaml` and the model cache), `verify-machine.sh`, new port to the group, group continues from `./scripts/reset.sh lab-NN --server`.

## 8. If you run late

Cut in this order and keep every lab's debrief (details in `docs/CURRICULUM.md` section 7):

1. The demos of `d2-09-demos` (about 20 of its 30 min); show one demo inside `d2-07-parallelism`. Keep the last three slides of the block (predictions scored, the five sentences of Day 2, the bridge to Day 3).
2. In `d1-02-models`, skip multimodal and reasoning detail (10 min).
3. In Lab 1, two scenarios instead of four (10 min).
4. In Lab 3, concurrency 1, 8 and 16 only (10 min).
5. In `d3-04-scaling`, one slide for KV-aware routing and disaggregation (10 min).
6. Lab 5: one scenario defended per group, shorter defences (15 min).

## 9. GPU cost control

Price used in this repository: **$2.49 per GPU-hour** (Secure Cloud, one RTX PRO 6000, read from the live catalogue at validation time; read it again). Per-second billing; a running pod costs the same idle or busy.

| Plan (4 pods) | Hours per pod | Cost at $2.49 |
| --- | --- | --- |
| Running from two hours before Day 1 to one hour after Day 3, overnight included | 59 | about $588 |
| Running only during teaching hours (stop overnight, rebuild each morning) | 33 | about $329 |

The second plan is cheaper but each stop wipes the container disk and may return the pod with no GPU; the rebuild is 5 to 6 minutes per pod. For a workshop with a fixed schedule the first plan is the safe default; the saving of about $260 is the price of a possible lost morning. A network volume (about $0.07 per GB-month) would keep models between rebuilds; this repository did not validate that path.

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

### End of day

- [ ] Persist required results: `T: infra/cleanup.sh --host <ip> --port <port> --collect`
- [ ] Stop unnecessary workloads (the embedding server after Day 3, demo profiles)
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
| Slow participant laptops or links | medium | labs overrun | everything heavy runs on the pod; `reset.sh` fall-backs; the debrief is the protected part |
| A lab hypothesis crashes the server | medium | group loses minutes | automatic rollback; reference results; `reset.sh lab-04 --server` |
| Model licence or availability changed | low | slides out of date | re-check two weeks before; pinned revisions are kept on the pods |
| Heise date or format changes | n/a | schedule | the content holds no dates: only the agenda times relative to each day |

## 11. What strong answers look like

Both labs have no single right answer. These are the checks and the arithmetic to expect, derived from the measured reference results (a proxy for other workloads, not a promise).

### Lab 1 (model selection)

- **A, German internal assistant, 20 users, 3,000 tokens of context.** KV per request about 3,400 tokens × 147,456 B = 0.47 GiB, so 20 requests need about 9 GiB of cache: memory is not the constraint; time is. A prefill of 3,000 tokens takes about 0.2 s alone (the baseline prefills about 17,000 tokens/s) and a 300-token answer about 4 s at 68 to 79 tokens/s. "Within 10 seconds" therefore fits without thinking mode and fails with a long thinking trace. Strong answers state the output length they assume and test German on their own documents.
- **B, ticket classification, 5 per second at peak.** About 300 output tokens/s and 1,500 prompt tokens/s; by Little's law about 5 requests in flight, a regime where one 8B model on one GPU meets TTFT p95 of 416 ms. The real question is whether a smaller model (the 1.7B in `config/models.yaml`) is accurate enough: a strong answer proposes the eval, not the answer.
- **C, coding assistant with 16,000 to 32,000 tokens of context.** A 32,768-token request holds 4.5 GiB of KV: about 13 such requests fill the 58 GiB pool (the server reports 12.92×), and 100 developers will exceed that at busy moments. The measured single-request TTFT is 0.95 s for 16,384 and 2.0 s for 28,672 prompt tokens on this GPU, so "first token within 1 s" cannot be met with uncached prefill of the whole repository; the answer is a shared prefix (prefix caching), a smaller context, or a faster GPU. Strong answers find this.
- **D, 2 million documents in 72 hours.** 7.7 documents/s, about 2,300 output and 23,000 input tokens/s. One GPU decodes about 1,700 tokens/s at concurrency 64 for a shorter workload and prefills about 17,000 tokens/s, so plan for at least two GPUs or a longer window; at three GPUs for 72 hours the GPU cost is about $540, or about $0.27 per thousand documents at $2.49 per GPU-hour. The restart cost (about 1 minute warm, 3 minutes cold) matters for a resumable batch.

### Lab 5 (production architecture)

- Concurrency is arrival rate times time in the system; GPUs follow from measured throughput at the SLO (this GPU: 8 concurrent requests meet the course SLO, about 550 tokens/s; 16 miss it by a few percent).
- Cold start of a replica: about 40 seconds restart, about 3 minutes on a fresh machine: autoscaling from zero is a latency event.
- The security boundary names what it does **not** protect (for example the unauthenticated `/metrics`, the Grafana viewer access, a shared API key per group).
- A cost per useful workload with the word "useful" defined.
- The first thing that breaks at ten times the load: usually the waiting queue and TTFT, before GPU memory.
