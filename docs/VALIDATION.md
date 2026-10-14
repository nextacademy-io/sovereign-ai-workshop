# Validation

What has been verified, how, on which hardware, and what only the trainer can verify. The list follows the Definition of Done of the workshop specification. "Verified" means somebody ran it and the evidence is named; "not verified" is said as plainly. Nothing here is a promise about a room full of people: no human participant took part in the validation.

## The environment of the validation

Two Runpod Secure Cloud pods in EUR-IS-2, each with one NVIDIA RTX PRO 6000 Blackwell Server Edition (94.97 GiB usable), on two different hosts (driver 595.91.07 / CUDA 13.2 and driver 580.159.04 / CUDA 13.0), created from the pinned vLLM v0.31.0 image. The first carried the infrastructure checks and all experiments; the second was built from scratch by `infra/deploy-to-pod.sh` and used for a dry run as a participant. Both were deleted afterwards (`list-pods` returned no pods). Costs and timings: [`GPU-POOL.md`](GPU-POOL.md). The slides, tools and checks were built and run on a MacBook (Node 24, pnpm 10, Python 3.12 through `uv`, system Chrome for rendering).

## Definition of Done

| Item | Status | Evidence |
| --- | --- | --- |
| Slidev builds successfully | **Verified** | `pnpm build`: 335 slides in 27 sections; CI job `slides`. |
| Slides are visually consistent | **Verified** for layout, **not** reviewed slide by slide by a human | One design system (`slides/styles/`, 9 layouts, 24 components), original diagrams `D01` to `D19`. `scripts/check-slides-layout.mjs` renders every slide of the built deck and finds no content outside the slide area. Every slide with a diagram, chart, table or code was looked at in rendered form by its author, and the diagram slides by the lead. A PDF export (`pnpm export`, one slide at a time) of all 335 pages succeeds. |
| Speaker notes exist | **Verified** | `pnpm check` requires, on every slide except cover, dividers and the closing slide, notes of at least 25 words with a **Key** and a **Transition** part. |
| All labs have been executed | **Verified in part** | Tasks 02, 03 and 04 were executed command by command as a non-privileged participant on the freshly built second pod, including all four Lab 4 hypotheses (restarts, benchmarks, the quality probe) and the contention round of Lab 3. Task 01 (model selection) is arithmetic and reading: `scripts/sizing.py` was run for the sizes of the reference answers. Task 00's local checks ran (`./scripts/preflight.sh`: 7 ok); its remote login test was not repeated against the second pod. Task 05 is a design exercise: its starting files and fall-backs (`reset.sh lab-05`) were executed, the exercise itself needs people. |
| Commands have been verified | **Verified** | The commands of tasks 02 to 04, the Day 3 demos (`structured.py`, `batch_extract.py`, `rag.py`, `agent.py`, the MCP variant), the container build and run, the SSH tunnel to the API and to Grafana, `reset.sh` for every lab, `reset-machine.sh`, `revoke-participant-key.sh`, `cleanup.sh`. Three defects were found and fixed this way (`TROUBLESHOOTING.md` incidents 19 and 20, the batch demo, the free-space check on a rerun). |
| GPU setup works from a clean machine | **Verified** | `infra/deploy-to-pod.sh` on a fresh pod: 5 min 29 s, 50 checks passed, 0 warnings, 0 failed (`benchmark/results/2026-10-14-rtxpro6000-s3/deploy-timings.txt`). The second run on the same pod (idempotent) took 1 min 36 s and passed again. |
| Participant SSH access works | **Verified** | Two test users with separate keys: login, own home, isolation checks of `verify-machine.sh`, tunnels from the laptop. |
| No provider credentials exposed | **Verified** | No Runpod API key was ever created (OAuth through the MCP server). `gitleaks` over the history and the working tree: no leaks (CI job `secrets`). One rule allowlists the documented factory login `admin:admin`, which the checks prove does **not** work. |
| No private keys committed | **Verified** | The same scan; `.gitignore` excludes `participants.yaml`, `.env`, keys and `input/`; the test keys lived outside the repository. |
| Model versions pinned | **Verified** | `config/models.yaml`: full 40-character commit SHAs, enforced by `pnpm check`; the pods run offline against the pinned revisions. |
| Important software versions pinned | **Verified** | vLLM image, Prometheus and Grafana by digest and checksum (`infra/versions.env`); Slidev, Vue, UnoCSS and the fonts exactly (`pnpm-lock.yaml`); Python dependencies in `uv.lock` and `apps/inference-client/requirements.txt`; the client image's base by digest. |
| Benchmark scripts are reproducible | **Verified** | 38 tests against a fake streaming server for the metric arithmetic. A second sweep on a different host, driven by a participant account, reproduced the first within 1 % on throughput (84, 308, 547, 893 against 84, 310, 551, 900 tokens/s). |
| Benchmark results identify hardware, model and configuration | **Verified** | `pnpm check` rejects any JSON under `benchmark/results/` without hardware, model revision, engine and CUDA versions, server arguments, workload and date (181 files). |
| Recovery paths exist | **Verified** | Automatic rollback of a failed profile (integration test and live), `wsctl` root-cause output, rebuild after a restart, resets. `FACILITATOR.md` section 7. |
| A participant can recover within about 5 minutes | **Verified** | Fresh repository copy: 1.2 s. Starter files of a lab: under 1 s. Putting the shared server back on `baseline`: 43 s. Rebuilding a whole pod: 5 min 41 s. |
| Monitoring works | **Verified** | Prometheus scrapes vLLM and the GPU exporter; seen through an SSH tunnel from the laptop under load (`monitoring/dashboard-under-load.png`). `verify-machine.sh` checks it (50 checks). |
| The Grafana dashboard works | **Verified** | 18 panels in 3 rows with live data during a benchmark sweep; the factory admin login is rejected and every port is bound to loopback. |
| Reset scripts work | **Verified** | `./scripts/reset.sh lab-01` to `lab-05`, with `--server` and `--hard` (backup made), and `infra/reset-machine.sh user` and `servers`. |
| Participant access can be revoked | **Verified** | After `revoke-participant-key.sh`, the key was refused ("Permission denied (publickey)"), a running session was ended, the audit log recorded it; `cleanup.sh --revoke` removed the remaining account. |
| GPU machines can be destroyed cleanly | **Verified** | `cleanup.sh --collect --revoke --stop-servers`, then `delete-pod`; `list-pods` empty. The collect step lost the participants' files because of a shell-glob bug until the dry run found it. |
| Cost-control checklist exists | **Verified** | `FACILITATOR.md` section 9 (before, during, end of day, after) with the arithmetic of two plans; `GPU-POOL.md`. |
| Links are checked | **Verified** | `lychee` offline on every commit (CI) and online once: 1,560 links in the documents, 12 failures (besides this document, which did not exist yet): one dead Runpod tutorial URL (replaced), registries and a gated model that answer an anonymous request with 401, one site that answers every automated request with 503 (those are excluded in `lychee.toml`), and a transient 503 from GitHub. The weekly CI run repeats the online check. |
| References are documented | **Verified** | `REFERENCES.md`; `RESEARCH.md` separates source fact, interpretation and workshop decision. |
| Model licensing is documented | **Verified** | `config/models.yaml` per model; `MODEL-SELECTION.md` section 5 (read per repository, licences drift). Re-read before delivery. |
| Tasks fit their timeboxes | **Verified in part** | Machine time as a participant: Lab 2 about 20 s of commands, Lab 3 about 2.5 minutes of benchmarks plus a short contention round and the explorations, Lab 4 about 17.5 minutes for **all four** hypotheses (six restarts), against timeboxes of 35, 45 and 40 minutes for one person or hypothesis. The rest of each timebox is reading, predicting, writing the report and discussing: **not measured**; the trainer's dry run with people measures it. |
| The full workshop fits into three days | **Verified** as arithmetic | `config/workshop.yaml`: 415, 420 and 420 teaching minutes, breaks outside; blocks do not overlap; every one of the 23 outcomes is covered; the slide dividers carry the agenda's start time, length and layer (`pnpm check`). Not run in real time. |
| The final capstone is executable | **Verified in part** | Everything it needs exists and was run: the template with the 15 questions, the reference results it cites, the reset. The design and the defences need people. |
| README is complete | **Verified** | The eleven items of the specification, plus "What You Will Have Done by the End"; the agenda is generated from `config/workshop.yaml` and checked. |
| FACILITATOR.md is complete | **Verified** | Minute-by-minute run sheet (generated), per-lab before/during/expected/failure/recovery/debrief, trainer commands, measured start-up timing, discussion prompts, skippable sections, GPU cost controls, shutdown checklist, risk register. |

## What only the trainer can verify

1. **A dry run with people.** Timeboxes, pacing and the debriefs with real participants, including five people sharing one server in Lab 3 (the dry run simulated contention with two benchmark processes).
2. **Four pods at once.** Two pods existed, never four; stock for four was *Low* when read and for two GPUs later *Out*.
3. **Provisioning outside the MCP server:** the REST API and `runpodctl` scripts are not written or validated.
4. **Two-GPU pods and the tensor-parallel experiment.** No stock; `experiments/tensor-parallel` has never run on hardware (its result-combining arithmetic is unit-tested).
5. **The vLLM against Ollama or llama.cpp comparison and the mixture-of-experts demo.** Not run (the checkpoint needs a 100 GB container disk).
6. **A network volume** instead of the persistent volume.
7. **Billing after the real workshop** (`list-pods` and `list-billing` after `delete-pod`).
8. **Model facts and licences** as of the delivery date, and the vLLM version: re-validate (`FACILITATOR.md` section 2); re-run `baseline` once on the day's hardware.
9. **The event itself:** the Heise page showed no dates when this repository was written; the content holds none.

## Defects the validation found

Twenty-two incidents are recorded with their prevention in [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md), section 2.1. The ones that would have misled a participant if they had reached the room: a profile that could not start (`kv-constrained`), a "cache off" profile that did not switch the cache off, a speculative-decoding control that was not a control (the benchmark's own text is copyable), a quality probe that could not detect a loss, a harness whose prompts shared a cache block, and a collect step that silently skipped the participants' work. Every one was found by running the thing and reading the server's own log, not by review.
