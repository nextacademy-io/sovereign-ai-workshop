# GPU pool: what was measured, what it costs, what can go wrong

The facts about the machines the workshop runs on, as measured while building it. Where a number comes from a file, the file is named; where it comes from a live read of the provider's catalogue it says so, and a live read goes stale: read it again before you provision. How to create the pods: [`infra/provision.md`](../infra/provision.md). How they are secured: [`SECURITY.md`](SECURITY.md).

## 1. The pool the workshop needs

| | |
| --- | --- |
| GPU class | NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB (94.97 GiB usable as vLLM reports it), 1,597 GB/s memory bandwidth (datasheet), no NVLink |
| Pods | one per group: 4 for up to 15 participants (3 to 5 per group), 3 for up to 11 |
| Provider | Runpod, Secure Cloud, driven through the Runpod MCP server (OAuth; no API key was created) |
| Image | `vllm/vllm-openai@sha256:c1c9f6fd...` (v0.31.0, pinned by digest in `infra/versions.env`), 9 GB |
| Per pod | 50 GB container disk, 150 GB persistent volume on `/workspace` (a download cache only: it enforces no permissions), one exposed port: `22/tcp` |
| Price (live read) | $2.49 per GPU-hour on Secure Cloud; two-GPU pods $4.98 |
| Data center used | EUR-IS-2 (Iceland: inside the EEA, not the EU). `EU-RO-1` and `EUR-IS-1` were the other EU-region candidates |

Both validation pods were created in EUR-IS-2 on different hosts (host drivers 595 and 580, CUDA 13.2 and 13.0), and the results agreed within 1 % on throughput (the Lab 3 sweep of the dry run in `benchmark/results/2026-10-14-rtxpro6000-s3/participant-anna/` against `benchmark/results/reference/concurrency/`: 84, 308, 547 and 893 tokens/s against 84, 310, 551 and 900 at concurrency 1, 4, 8 and 16).

## 2. Stock

| Read | Result |
| --- | --- |
| Start of the validation, one GPU | *Low* on CUDA 13.0 and 13.2 |
| Start of the validation, two GPUs | *Low*, CUDA 13.2 hosts only, $4.98 per hour |
| Creating a pod at the start | succeeded within seconds, twice |
| Late the same day, two GPUs | `create-pod` was refused ("There are no longer any instances available with the requested specifications"); a capacity read showed *Out* on both CUDA versions |

Consequences. Stock is the largest operational risk of the workshop (see `FACILITATOR.md`, risk register): four pods at once is a larger ask than one, and a pod that is stopped can come back without its GPU. Provision the evening before, not the morning of, keep every pod running until the end, keep a spare in a second data center, and have a plan for sharing a pod between two groups (the labs tolerate five people per server). The two-GPU tensor-parallel experiment could not be run for exactly this reason: [`experiments/tensor-parallel/RESULTS.md`](../experiments/tensor-parallel/RESULTS.md).

## 3. Timings

Measured on live pods. Source files: `benchmark/results/reference/startup/*.json` (start-up timelines), `benchmark/results/2026-10-14-rtxpro6000-s3/deploy-timings.txt` (step timings of a deployment to a fresh pod).

| Step | Measured |
| --- | --- |
| `create-pod` to the container running | 1 to 2 s (image already cached on the host) |
| ... to sshd answering | 19 s on a fresh host (the start command installs `openssh-server`); 11 s after a restart |
| `infra/deploy-to-pod.sh` on a fresh pod, whole run | 5 min 29 s |
| ...of which model download (four models, 29 GB) | 42 s; a single 16 GB model took 12.4 s on the other host (about 1.3 GB/s) |
| ...of which monitoring (Prometheus, Grafana, GPU exporter) | 17 s |
| ...of which first vLLM start, cold, plus the embedding server | 198 s (176 s in the server's own log) plus 53 s |
| `infra/deploy-to-pod.sh` rerun on a populated pod (idempotent) | 1 min 36 s (the server restarts) |
| Rebuild of a pod after a restart (container disk wiped, `/workspace` kept) | 5 min 41 s |
| vLLM start, warm caches / restart of the same profile | 55 to 67 s / 29 to 41 s |
| First start of the FP8 checkpoint | 138 to 143 s |
| `./scripts/reset.sh lab-NN` | under 1 s; `--server` adds a restart of the model (43 s) |
| `infra/reset-machine.sh user <name>` / `servers` | 1.2 s / 96 s |
| Revoking a participant | 1 s; the key is removed, sessions are killed, the next login is refused |

**A pod restart changes the public SSH port** (22290 became 22235 in the test; the IP stayed), changes the SSH host key and wipes the container disk, so a restart is a rebuild. The recovery path is `infra/deploy-to-pod.sh` again with the new port in `infra/participants.yaml`.

## 4. What the validation cost

Prices at $2.49 per GPU-hour, per-second billing. The provider's billing read lags by up to an hour; the figures below are the runtime of each pod times the price, cross-checked against `list-billing` for the hours that were final when read.

| Pod | Created | Deleted | Used for | Cost |
| --- | --- | --- | --- | --- |
| First pod, one GPU | first session | after the last experiment | infrastructure validation, all experiments (including four reruns that fixed profile and harness defects) | about $8.7, of which about $1.9 was an idle tail |
| Second pod, one GPU, a different host | during the experiments | after the dry run | build from scratch, tasks 02 to 04 and the Day 3 demos as a participant, resets, revocation, cleanup | about $4.1 |
| Two-GPU pod | never created (no stock) | | | $0 |
| Total | | | | about $12.8 of the $20 budget (the account already showed $0.06 before the work) |

Lessons about spending, learnt the expensive way:

- **A pod that is not running a scripted step is wasted money.** The first pod sat idle for about 45 minutes while results were being analysed. Delete the pod when the last experiment has finished and its results are copied; recreate it (a few minutes) if analysis needs more.
- **Create a second pod before deleting the first** when stock is *Low*: the overlap costs a few minutes of a second GPU and saves the risk of not getting one.
- **Reruns cost little and found defects that no review would have**: a profile that could not start, a flag that did nothing, a control that was not a control. Every profile and every experiment should be run once on the workshop GPU before it is taught (`docs/TROUBLESHOOTING.md` section 2.1, incidents 17 to 22).

### Estimate for the workshop itself (arithmetic)

Four pods, $2.49 per pod-hour:

| Plan | Hours per pod | Cost |
| --- | --- | --- |
| Running from two hours before Day 1 to one hour after Day 3, overnight included | 59 | about $588 |
| Running only during teaching hours (stopped overnight, rebuilt every morning) | 33 | about $329 |

Stopping overnight saves about $260 but each stop wipes the container disk and may return the pod without a GPU; the rebuild is five to six minutes per pod. For a fixed schedule the first plan is the safe default. A network volume (priced per GB-month, billed while idle) would keep the models between rebuilds; the path was not validated here.

## 5. Not validated here

- The REST API and `runpodctl` provisioning scripts (the validation used the MCP server only).
- Four pods created and managed in parallel (two were).
- A network volume instead of the persistent volume.
- Two-GPU pods (no stock), the llama.cpp or Ollama comparison and the mixture-of-experts demo (the 31 GB checkpoint needs the 100 GB container disk of `infra/provision.md`).
- That billing stops after `delete-pod` for a four-pod, three-day workshop: verify with `list-pods` and `list-billing` after the real one (see the shutdown checklist in `FACILITATOR.md`).
