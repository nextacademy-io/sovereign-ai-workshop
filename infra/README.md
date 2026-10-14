# Infrastructure

Everything the trainer needs to turn rented GPU machines into workshop environments, check them, reset them and tear them down. Participants never provision anything: they receive an SSH account on their group's machine.

```text
trainer laptop                         GPU pod (one per group, Runpod Secure Cloud)
──────────────                         ─────────────────────────────────────────────
Runpod MCP / console ── create pod ──► sshd (port 22 is the only exposed port)
infra/deploy-to-pod.sh ── git-tracked files over SSH ──►  /opt/workshop/repo   (root-owned)
infra/sync-participants.sh ── public keys ──────────────► accounts, /home/<user>
                                       wsctl ──► vLLM  127.0.0.1:8000   (--api-key, shared by the group)
                                       wsctl ──► vLLM  127.0.0.1:8001   (embeddings for the RAG demo)
                                       wsmon ──► Prometheus 9090, Grafana 3000, GPU exporter 9400  (loopback)
participant laptops ── ssh -L ──────► everything above, through SSH tunnels only
```

## Files

| File | Where it runs | What it does |
| --- | --- | --- |
| [`provision.md`](provision.md) | read | Step-by-step: price check, creating pods through the Runpod MCP, first login |
| [`runpod/pod-start.sh`](runpod/pod-start.sh) | pod, PID 1 | Installs sshd (the vLLM image has none), installs the key, records the container environment |
| [`runpod/pod-spec.example.json`](runpod/pod-spec.example.json) | read | The `create-pod` arguments for one workshop pod |
| [`deploy-to-pod.sh`](deploy-to-pod.sh) | laptop | Copy the repo, run `machine-setup.sh`, create accounts, verify |
| [`machine-setup.sh`](machine-setup.sh) | pod, root | Idempotent bootstrap: tools, SSH policy, API key, models, monitoring, servers |
| [`verify-machine.sh`](verify-machine.sh) | laptop or pod | PASS/WARN/FAIL checks: GPU, accounts, isolation, integrity, models, servers, monitoring |
| [`reset-machine.sh`](reset-machine.sh) | laptop | Restart servers, or give one participant (or everyone) a fresh repo copy |
| [`add-participant-key.sh`](add-participant-key.sh), [`revoke-participant-key.sh`](revoke-participant-key.sh), [`sync-participants.sh`](sync-participants.sh) | laptop | Create, revoke and bulk-sync participant accounts from `participants.yaml` |
| [`cleanup.sh`](cleanup.sh) | laptop | Collect artifacts, revoke all access, stop servers; prints the billing checklist |
| [`participants.example.yaml`](participants.example.yaml) | read | Format of `infra/participants.yaml` (gitignored; public keys only) |
| [`versions.env`](versions.env) | sourced | Pinned versions and checksums of everything the pods download |
| [`pod/`](pod/) | pod | `wsctl` (server supervisor), `wsmon` (monitoring), `ws-user.sh`, `ws-reset.sh`, `render-profile.py`, `fetch-models.py`, `server-info.py`, `paths.sh` |

## Typical day

```bash
# Before the workshop (once per pod, about 5 minutes after the pod is running)
infra/deploy-to-pod.sh --host <ip> --port <port> --group alpha
infra/verify-machine.sh --host <ip> --port <port>

# During the workshop
infra/reset-machine.sh --host <ip> --port <port> user anna      # a participant broke their copy
infra/reset-machine.sh --host <ip> --port <port> servers        # the shared server is stuck
ssh -p <port> root@<ip> 'wsctl status'                          # who started what, stray servers

# End of day
infra/cleanup.sh --host <ip> --port <port> --collect

# End of workshop
infra/cleanup.sh --all --collect --revoke --stop-servers
# ...then delete every pod (Runpod MCP `delete-pod`) and confirm with `list-pods` and `list-billing`
```

## Design decisions that come from measurements

- **The persistent volume does not enforce permissions.** On Runpod, `/workspace` is a network filesystem where `chmod` is ignored, `chown` fails and any user can read or change any file, including files root created with mode `0600`. So `/workspace` is only a download cache for model files. Code, served models, accounts, keys, compile caches, logs and homes live on the container disk, where permissions are real. `infra/pod/paths.sh` defines the layout and `verify-machine.sh` checks it. The consequence: a pod *restart* wipes the container disk, so a rebuild (`deploy-to-pod.sh`) is the recovery path; accounts come back from your `participants.yaml`, models from the cache.
- **Pods are containers and cannot run Docker.** Containerization is taught on participants' laptops; monitoring runs as plain processes on the pod. The same Prometheus config, dashboard and metric names work with `monitoring/docker-compose.yml` on your own server.
- **Only SSH is exposed.** vLLM's `--api-key` protects `/v1` but not `/metrics`, `/health` or `/tokenize`, and the default bind address is all interfaces, so every server binds `127.0.0.1` and is reached through SSH tunnels.
- **What leaves your laptop is decided by git.** `deploy-to-pod.sh` sends tracked files plus untracked files that `.gitignore` does not exclude. Local-only material (`.env`, `infra/participants.yaml`, `input/`) never reaches a rented machine.

See [`docs/GPU-POOL.md`](../docs/GPU-POOL.md) for measured timings and costs, and [`docs/SECURITY.md`](../docs/SECURITY.md) for the threat model.
