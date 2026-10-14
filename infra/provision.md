# Provisioning GPU machines

How to create the Runpod pods for a workshop, bring them to workshop-ready state, and tear them down. The steps are written for an AI assistant or a human using the **Runpod MCP server** (OAuth, `https://mcp.getrunpod.io/`); the console does the same with clicks.

> Validated through the MCP server only. The REST API v1 is being retired and v2 has not been scripted here; treat any REST-based automation as unvalidated.

## 0. What you need

- A Runpod account with balance for **at least one hour of every pod** (Runpod refuses to deploy otherwise), and auto-pay enabled: at a zero balance all pods are stopped and pods without a network volume are terminated.
- Your SSH public key registered with Runpod (account settings, or the MCP `update-ssh-keys`). `startSsh: true` injects it as `PUBLIC_KEY`.
- The Runpod MCP server connected (in Claude Code: `/mcp`, status *Connected*).
- This repository checked out with git (the deploy script uses git to decide what may leave your laptop), and `infra/participants.yaml` filled in (copy `participants.example.yaml`; public keys only).

## 1. Plan the pods

| Participants | Pods | Group size |
| --- | --- | --- |
| up to 15 | 4 (one per group: alpha, beta, gamma, delta) | 3 to 5 |
| up to 11 | 3 | 3 to 4 |

One pod hosts one shared vLLM server for its group. The workshop GPU is the **NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB)**; every measured number in the slides comes from it, so use the same GPU.

Per-hour cost is `pods × price`. At the price read on 2026-10-14 (Secure Cloud, $2.49 per GPU-hour) four pods cost about $10 per hour; a three-day workshop with 8 hours a day is about $240 plus preparation. **Read the live price**, do not trust this number.

## 2. Check stock and price (read before you create)

With the MCP: `list-gpu-types` with `include: ["AVAILABILITY"]`, `product: ["POD"]`, `cloud: "SECURE"` and EU countries, then `get-capacity` for the exact GPU id `NVIDIA RTX PRO 6000 Blackwell Server Edition` and CUDA 13.0 and 13.2. Stock was "Low" on the day of validation, so create the pods well before the workshop and keep fallbacks (EU-RO-1, EUR-IS-1, EUR-IS-2).

Pods created in **EUR-IS-2 (Iceland)** are inside the EEA but not the EU; if that matters to your audience, pin `dataCenterIds` to `EU-RO-1` and accept lower availability. See `docs/DIGITAL-SOVEREIGNTY.md`.

## 3. Create a pod

Use `infra/runpod/pod-spec.example.json` as the template for the `create-pod` arguments:

- `image`: the vLLM image **by digest** (from `infra/versions.env`). Tags are mutable.
- `entrypoint: ["/bin/bash", "-c"]` and `cmd: ["<contents of infra/runpod/pod-start.sh>"]`: the image's own entrypoint is `vllm serve` and it has no SSH daemon.
- `gpu.minCudaVersion: "13.0"`: the CUDA 13 image needs a host driver of R580 or newer.
- `ports: ["22/tcp"]` only. Do **not** expose 8000 or the HTTP proxy: `--api-key` does not protect `/metrics`, `/health` or `/tokenize`.
- `disk`: 50 GB holds the four lab models (about 29 GB); use 100 GB if you also want the demo models (`--models demo`, 30B MoE and GGUF).
- `mounts.persistent`: 100 to 150 GB at `/workspace`. This volume is a **download cache only**; see below.
- `startSsh: true`.

State the hourly price before creating, create, then read the pod back (`get-pod`). The response contains `ssh.direct.host` and `ssh.direct.port`: that is what you give the scripts. The public port changes whenever a pod is recreated; the IP usually does not.

Typical timings measured on 2026-10-14: the container was running 2 s after the call and sshd was listening about 11 s later (the 9 GB image was cached on that host; a cold host adds the image pull).

## 4. Deploy

```bash
infra/deploy-to-pod.sh --host <ip> --port <port> --group alpha
```

Copies the repository (what git tracks plus untracked, un-ignored files) to `/opt/workshop/repo` on the pod, runs `machine-setup.sh` (tools, SSH policy, API key, models, monitoring, vLLM servers), creates the accounts of that group from `infra/participants.yaml`, and runs `verify-machine.sh`. Rerunning is safe and is also how you rebuild a pod after a restart.

Useful flags: `--no-participants` (no accounts yet), `--models demo` (the trainer-demo models), `--skip-servers`, `--skip-models`.

## 5. Verify

```bash
infra/verify-machine.sh --host <ip> --port <port>
```

Every line must be PASS; WARN lines explain themselves. The checks cover the GPU and driver, SSH policy, each account, isolation between participants, integrity of everything root runs (participants cannot write to it), cached models at the pinned revisions, the API (a key is required, a completion works, the port is bound to loopback only), the embedding server and the monitoring stack.

Then give each participant their connection line:

```text
ssh -p <port> <user>@<ip>
# API and Grafana through tunnels, from the participant's laptop:
ssh -p <port> -L 8000:127.0.0.1:8000 -L 3000:127.0.0.1:3000 <user>@<ip>
```

## 6. During the workshop

- Watch spend: `list-billing` (hourly buckets), and `wsctl status` on each pod for stray model servers (duplicates waste VRAM).
- A participant broke their repo copy: `infra/reset-machine.sh --host <ip> --port <port> user <name>` (their artifacts are kept unless `--hard`).
- The shared server is stuck: `infra/reset-machine.sh ... servers`.
- Late joiner: add the entry to `participants.yaml` and run `infra/sync-participants.sh --group <id>`.

## 7. If a pod restarts or is recreated

A restart wipes the container disk; the persistent volume keeps only the model download cache. Run `deploy-to-pod.sh` again with the new host and port: models come from the cache (a minute or two instead of the download), accounts come from `participants.yaml`. Participants' own work in `~/ki-ohne-cloud` is lost, which is why `infra/cleanup.sh --collect` is part of every end of day. SSH host keys are regenerated (not persisted, because the volume does not enforce permissions), so participants see a new host key after a rebuild.

## 8. Tear down

```bash
infra/cleanup.sh --all --collect --revoke --stop-servers
```

Then delete every pod (`delete-pod`), and **verify**: `list-pods` returns no pods, `list-network-volumes` shows nothing you still pay for, and `list-billing` shows zero hourly spend afterwards. Stopping a pod is not enough: a stopped pod keeps billing for its volume.
