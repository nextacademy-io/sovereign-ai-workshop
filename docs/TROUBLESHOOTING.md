# Troubleshooting

Symptom, likely cause, fix. Part 1 is for participants. Part 2 is for the trainer and contains every incident met while building and validating the pods.

Where a command runs matters, so each table says "laptop" or "GPU host". `<port>`, `<host>` and `<user>` are the values the trainer gave you. When you ask for help, bring the exact command, the full error text and the output of `sudo wsctl status`.

Measured numbers come from the workshop pods during validation (NVIDIA RTX PRO 6000 Blackwell Server Edition, vLLM 0.31.0, Qwen3-8B).

## Part 1: Participants

### 1.1 Connecting with SSH

Run on your laptop.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Permission denied (publickey)` | Wrong user name or port; your key is not on the machine yet; your key was revoked; ssh offers a different key than the one you sent. | `ssh -v -p <port> <user>@<host>` and look for the line "Offering public key". Pin the key: `ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes -p <port> <user>@<host>`. Then `./scripts/preflight.sh --host <host> --port <port> --user <user>`. Still failing: send the trainer your `.pub` line again. |
| `Too many authentication failures` | The server allows 3 tries. Your ssh agent offers other keys first. | Add `-o IdentitiesOnly=yes -i <your key>`. |
| `Connection refused` or a timeout | The port changed after a rebuild or restart: the IP stays, the port changes (measured: 22290, then 22235). Or the machine is still being rebuilt. | Ask for the current port. A rebuild takes about 5 minutes. Test again with `./scripts/preflight.sh --host <host> --port <port> --user <user>`. |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | The machine was rebuilt and made new host keys. They are not kept on the shared volume on purpose. A changed key is also what an attack looks like. | Ask the trainer whether the machine was rebuilt. If yes: `ssh-keygen -R "[<host>]:<port>"`, then connect again. |
| `bind [127.0.0.1]:8000: Address already in use` when you open a tunnel | Another tunnel or a local server uses port 8000 on your laptop. | Use another local port: `ssh -p <port> -L 18000:127.0.0.1:8000 <user>@<host>`, then `export OPENAI_BASE_URL=http://127.0.0.1:18000/v1`. |
| The session freezes or drops | An idle connection was cut by your network. | Connect with `-o ServerAliveInterval=20`. Run long jobs inside `tmux`, which is installed on the machines. |
| A Docker container cannot reach your tunnel (Day 3) | Inside a container `127.0.0.1` is the container itself. | Docker Desktop: use `http://host.docker.internal:8000/v1`. Linux: add `--add-host host.docker.internal:host-gateway` and bind the tunnel to the bridge: `ssh -L 172.17.0.1:8000:127.0.0.1:8000 ...`. See the comment in `apps/inference-client/Dockerfile`. |
| You can log in, but your files are gone | The machine was rebuilt. The container disk, including `~/ki-ohne-cloud`, is wiped on a restart. | Copy your work to your laptop every day: `scp -P <port> -r <user>@<host>:ki-ohne-cloud/workshop-artifacts ./my-artifacts`. Restore the starter files with `./scripts/reset.sh lab-NN`. |

### 1.2 The API

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401 Unauthorized`, or a note "OPENAI_API_KEY is not set; sending a placeholder key" | The key is missing, empty, or from before a rebuild (a rebuilt machine has a new key). | GPU host: log in again, the key is set at login. Laptop: `export OPENAI_API_KEY=$(ssh -p <port> <user>@<host> 'cat /var/lib/workshop/api-key')`. Test: `curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models` must print 200. |
| `Connection refused` on `127.0.0.1:8000` from your laptop | The tunnel is not open, or its terminal was closed. | Open it again: `ssh -p <port> -L 8000:127.0.0.1:8000 <user>@<host>` and keep that terminal open. |
| `Connection refused` on `127.0.0.1:8000` on the GPU host | The server is stopped, still loading, or crashed. | `sudo wsctl status`. If `main` is stopped: `sudo wsctl start baseline` and tell your group. |
| `Connection refused` on port 8001 | The embedding server (used by the RAG demo) is not running, or on your laptop the tunnel lacks port 8001. | GPU host: `sudo wsctl embed start` (about 53 s). Laptop: add `-L 8001:127.0.0.1:8001` to the tunnel. |
| `404`, "model does not exist" | The name you send is not the name the server serves. The `baseline` and `fp8` profiles serve `Qwen/Qwen3-8B`; `small` serves `Qwen/Qwen3-1.7B`; the embedding server serves `Qwen/Qwen3-Embedding-0.6B`. `WORKSHOP_MODEL` is set to `Qwen/Qwen3-8B` at login. | `curl -s -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models` shows the served name. Then `export WORKSHOP_MODEL=<that name>` or pass `--model`. |
| `400`, an error naming the maximum context length | Prompt plus `max_tokens` is larger than `max-model-len` (32768 in the workshop profiles). | Shorten the prompt or lower `max_tokens`. |
| `content` is empty or `null`, `finish_reason` is `length` | Qwen3 thinks by default. The thinking is in `reasoning`, and `max_tokens` ran out before the answer began. | Raise `max_tokens`, or switch thinking off per request: `extra_body={"chat_template_kwargs": {"enable_thinking": False}}`, as the apps do. |
| A long wait before the first token | Other requests queue in front of yours (the server is shared). Or someone restarted the server. Or the first use of a new JSON schema compiles its grammar (several seconds). Or thinking is on. | `./scripts/gpu-status.sh --watch` shows running and waiting requests. `sudo wsctl status` shows whether the server is restarting (up to 3 minutes, see 1.3). |
| Answers or speed changed without you doing anything | A groupmate started another profile. | `sudo wsctl info` shows profile and arguments. `./scripts/reset.sh lab-NN --server` puts the server on the profile your lab expects (this restarts it for your group). |

### 1.3 The server

`sudo wsctl status` is the first command to run. It prints one line per server:

```text
ROLE    STATE     PID      PROFILE                HEALTH
main    running   <pid>    baseline               ok
embed   running   <pid>    embedding              ok
```

(This shows the layout, not a real run.) Below it come the GPU memory line, one `GPU process:` line per process using the GPU, and a WARNING if vLLM processes exist that `wsctl` did not start.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `HEALTH` is `not ready` | The process is alive and still loading. | Wait. Cold starts take about 3 minutes (below). `sudo wsctl logs 30` shows progress. |
| `main` is `stopped` | Someone ran `wsctl stop`, or the machine was rebuilt. | `sudo wsctl start baseline` (or `./scripts/start-vllm.sh baseline`). Tell your group first. |
| A start fails and prints "the server exited during startup", then "rolling back to the previous profile" | The new profile cannot start: it does not fit in memory, a `--set` value is invalid, the GPU memory is held by another process, or the profile needs two GPUs (`tp2`). `oom-demo` fails on purpose. | Read the 25 log lines it printed. `sudo wsctl status` must show the previous profile running again. That is a result, so record it. Do not retry in a loop: each attempt takes the model away from your group. |
| "rollback to ... failed as well" | The previous profile does not start either. | Ask the trainer. Do not keep retrying. |
| "wsctl: not ready after 900s" | The server did not become healthy in 15 minutes. | `sudo wsctl logs 100`, then ask the trainer. |
| "another wsctl operation is in progress; try again in a moment" | A groupmate is starting or stopping the server. A start holds the lock until the server is ready. | Wait until the start finishes (up to 3 minutes). `sudo wsctl status` and `sudo wsctl logs` keep working during a start. If it never clears and nobody is starting anything, tell the trainer (incident 5 in 2.1). |
| "run with sudo: sudo wsctl ..." | You ran `wsctl` without `sudo`. | `sudo wsctl <command>`. |
| "--set ...: allowed keys are ..." | The key is not one of the engine knobs a group may change. | `sudo wsctl profiles` lists the allowed keys. |
| "unknown profile" or "profile ... is abstract" | A typo, or `base`, which is not startable. | `sudo wsctl profiles`. |
| "no running server to restart; use: wsctl start <profile>" | `restart` needs a server that ran under `wsctl`. | `sudo wsctl start baseline`. |

How long things take (measured):

| Event | Time |
| --- | --- |
| Cold start of the baseline profile (first `torch.compile` and FlashInfer autotune) | 188 to 194 s |
| Warm restart (compile cache present) | 67 s |
| First start of the FP8 profile | 136 s |
| Embedding server | 53 s |
| Whole machine rebuilt after a pod restart | 5 min 41 s |

The model is offline for the whole start. Your group sees the requests fail meanwhile.

### 1.4 Benchmarks

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Zero requests succeeded, or the run ended with an error | Wrong model name ("model ... is not served; server lists: ..."), a missing key (`HTTP 401` in the result's `errors`), a wrong endpoint, a restart during the run, a prompt longer than the context, or a groupmate's run in parallel. | `./scripts/benchmark.sh --concurrency 1 --requests 8` is the smallest test. Read `errors` in the JSON and `summary.md`. Check `echo $OPENAI_BASE_URL $WORKSHOP_MODEL`. Only one benchmark at a time per group. |
| TTFT is suspiciously low, or the second run is much faster | The prefix cache. The same prompts were sent before. Measured: TTFT p50 391 ms, then 51 ms. | The harness warns: "the server's prefix cache answered N % ...". Run again without `--seed` (each run draws a new seed) and without `--same-prompts`. The `shared-prefix` workload is the one place where a cache hit is the point. |
| Your numbers differ from the reference by more than 20 % | Someone else uses the server, or the run was too short. | `./scripts/gpu-status.sh` shows running requests. Use `--requests 64` per level. |
| p95 or p99 jumps between identical runs | Percentiles from few samples are noisy: p99 of 48 requests is the slowest request. Measured: two load generators agreed within 0.4 % on throughput and within 0.2 % on mean ITL, yet differed by 29 % on ITL p99. | More requests, more runs. Compare p50 and p95 first. |
| First requests after a start are slow | The server is warming up (caches, kernels). | Wait for `HEALTH ok` in `sudo wsctl status`. The harness excludes warm-up requests by default (`--warmup`). |
| GPU-Util says 100 % but throughput is low | `GPU-Util` is the share of time any kernel ran, not efficiency. Measured: 100 % at concurrency 1 and at 8, with 6.5 times the throughput. | Read power draw, `running` and `waiting`, and KV cache use next to it (`./scripts/gpu-status.sh`). |
| `pnpm check` rejects your result: "configuration is missing: ..." | The result lacks provenance: model revision, server arguments, engine or CUDA version, GPU. This happens when the harness runs away from the GPU host, or the server was not started by `wsctl` (no `/var/lib/workshop/server.json`). | Run on the GPU host. Away from it, pass `--model-revision`, `--server-args="..."` (with `=`), `--gpu-name`, `--engine-version` and `--runtime-cuda`. The harness prints "warning: provenance incomplete (...)". Do not edit the JSON by hand. |
| Your own run failed completely | Any of the above, and little time left. | `./scripts/reset.sh lab-03` copies reference results to `benchmark/results/reference/`. Continue with those and say so in the report. |

### 1.5 The apps

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Structured output returns truncated JSON, `finish_reason` is `length`, the reply is mostly blanks | The prompt did not describe the fields. Constrained decoding enforces syntax, not content. Measured: 300 tokens, 5,469 of them blanks. With the fields named in the prompt: 34 tokens. | Name every required field and its allowed values in the system prompt, as `apps/inference-client/structured.py` does. Use `temperature=0` and thinking off. |
| A tool call arrives as text (`<tool_call>` in `content`) and `tool_calls` is empty, or a `400` says auto tool choice needs `--enable-auto-tool-choice` and `--tool-call-parser` | The server runs a profile without the parser flags, or the model put the call inside its thinking, which the parser does not read. A small model may also produce a malformed call. | `sudo wsctl info`: the arguments must contain `--enable-auto-tool-choice` and `--tool-call-parser hermes`. Use `baseline` or `fp8`. Switch thinking off, as `apps/tool-calling-demo/agent.py` does. The 8B model is the tested one. |
| The agent prints "(stopped after 8 steps without a final answer)" | The model keeps requesting tools. The step limit is a deliberate bound. | Read the tool results it received. A tool error text the model cannot act on is the usual cause. |
| The agent prints "error: arguments were not valid JSON" | The model produced a malformed argument string. | The agent already sends `temperature=0`. If it repeats, look at the raw `content` and tell the trainer: the model or the parser is the problem. |
| The RAG answer comes from the archived policy | The handbook contains a superseded policy on purpose (`03-remote-work-v1-archived.md`). Retrieval returned the old chunk and not the new one, or the model ignored the "prefer the newer version" rule. | Read the `[rank] score= source` lines the demo prints. Raise `--top-k` (for example 6) or change `--chunk-chars`. Better: keep archived files out of the folder you index (`--docs`). The lesson is freshness: the model cannot know which passage is current. |
| The RAG demo fails with a connection error | The embedding server is not running. | `sudo wsctl embed start`. |

### 1.6 Loading a model offline

The GPU hosts run with `HF_HUB_OFFLINE=1`. Nothing is downloaded after the setup. The pinned models are in `/opt/workshop/hf`.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `from_pretrained("Qwen/Qwen3-8B")` or a tool such as `vllm bench serve` cannot find the model or its tokenizer offline | The cache holds the pinned commit under `snapshots/<sha>`. A lookup of the default revision `main` needs `refs/main`. A download by commit SHA does not create it. | `ls /opt/workshop/hf/hub/models--Qwen--Qwen3-8B/refs/main` must exist. If not, tell the trainer (the fetch script writes it). Meanwhile load by the pinned revision from `config/models.yaml`, or by the local snapshot path. |
| Offline error on your laptop | You set `HF_HUB_OFFLINE=1` and the cache there is empty. | You do not need weights on your laptop: the apps call the API. Unset the variable if you want to download. |
| You want to unset `HF_HUB_OFFLINE` on the GPU host to "fix" a load | A download of `main` could fetch a different commit than the pinned one. | Do not. Ask the trainer to fetch the pinned revision. |

### 1.7 GPU memory

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| CUDA out of memory, "No available memory for the cache blocks", or "free memory on device is less than the desired GPU memory utilization" at startup | Another process holds GPU memory: a second server, a Python session with a model loaded, or a stray server. The embedding server permanently holds about 0.08 of the card, so `--set gpu-memory-utilization` above about 0.9 cannot work (derived from 0.80 plus 0.08). | `sudo wsctl status`. Read the `GPU process:` lines and the WARNING. Stop your own processes (`kill <pid>`, only yours). |
| `sudo wsctl status` warns: "vLLM processes not started by wsctl (duplicate model servers waste GPU memory)" | Someone ran `vllm serve` by hand. | Do not start your own copy of a model: the GPU belongs to the shared server. If it is your process, stop it. If it is not, tell the trainer. |
| You are tempted to run `sudo wsctl reap` | It kills every vLLM process that `wsctl` did not start, including a groupmate's. The sudo rule allows it, but it is a trainer action. | Ask the trainer. |
| The memory shown by `nvidia-smi` is far more than the model needs | Correct. vLLM reserves its budget at startup; the KV cache fills as requests arrive. | Nothing to fix. |

## Part 2: Trainer

First five minutes for any report from a group:

```bash
infra/verify-machine.sh --host <ip> --port <port>              # PASS, WARN, FAIL per check
ssh -p <port> root@<ip> 'wsctl status'                         # servers, GPU, stray processes
ssh -p <port> root@<ip> 'wsctl logs 60'                       # the main server log
ssh -p <port> root@<ip> 'tail -n 20 /var/log/workshop/wsctl.log'   # who started or stopped what
```

### 2.1 Incidents from building and validating the pods

Every row is something that happened on a live pod. Each is now covered by a test, a check or a rule; the last column says which. The threat model behind rows 1 to 4 is in [`SECURITY.md`](SECURITY.md).

| # | What you will see | Why | Fix | How it is prevented now |
| --- | --- | --- | --- | --- |
| 1 | On the shared volume `/workspace`, `chmod` is ignored and `chown` fails. A participant can read a root-owned `0600` file or list a `0700` directory there. `verify-machine.sh` may say "the API key was found under /workspace". | The persistent volume is a network filesystem that does not enforce permissions. | Delete the file. Treat any secret there as leaked: remove `/var/lib/workshop/api-key`, then rerun `infra/deploy-to-pod.sh`, which makes a new key and restarts the servers. (Derived from the scripts, not exercised.) | `/workspace` is a download cache only. Code, accounts, keys, compile caches, logs and homes are on the container disk (`infra/pod/paths.sh`). `verify-machine.sh` checks that no secret is on the volume. Copies to the volume use `rsync -rlt`. |
| 2 | `curl` on `/metrics`, `/health`, `/tokenize` or `/version` works without a key. Verify fails with "port 8000 is bound to ALL interfaces". | `--api-key` guards `/v1` only, and the default bind is all interfaces. A critical advisory (CVE-2026-48746, CVSS 9.1, affects 0.3.0 and later, patched in 0.22.0) allowed skipping the key check through special characters in the Host header. | If the server was not started through `wsctl`: `wsctl stop`, then `wsctl start baseline`. If a port other than 22 is exposed: recreate the pod from `infra/runpod/pod-spec.example.json` (only `22/tcp`). | `render-profile.py` refuses any host except `127.0.0.1` (`infra/tests/test_render_profile.py`). The pod spec exposes only `22/tcp`. Verify checks the loopback bind and that `/v1/models` without a key returns 401. Image pinned to vLLM 0.31.0. |
| 3 | Grafana ignores its config file. `admin:admin` is a valid admin login, anonymous access is off, telemetry is on. Later: the admin account is locked after failed logins (see 2.8). | The binary needs `--config`; `GF_PATHS_CONFIG` is not enough. `GF_SECURITY_ADMIN_PASSWORD__FILE` is ignored for the admin user. | `ssh -p <port> root@<ip> 'wsmon restart'`. | `wsmon` passes `--config`, sets the admin password from `/var/lib/workshop/grafana-admin-password` (and resets it on an existing database). `monitoring/pod/grafana.ini` binds loopback, allows anonymous viewers and turns analytics off. The check against an admin-only endpoint is manual: do it once, because wrong credentials count as failed logins. |
| 4 | Participants see an empty `OPENAI_API_KEY` or `Permission denied` on `/var/lib/workshop/api-key`. A check run as root says everything is fine. | The state directory was mode `0700`. | `chmod 755 /var/lib/workshop`. The key file must be `640 root:workshop`; the `keys` directory stays `700`. | `ws-user` sets the modes. `verify-machine.sh` tests what the first participant can read (`api-key`, `group`, `server.json`) instead of what root can. |
| 5 | Every `wsctl` call fails with "another wsctl operation is in progress", although nobody is working. | The vLLM process inherited `wsctl`'s `flock` file descriptor, so the lock stayed held while the server ran. | Update `wsctl` (rerun `infra/deploy-to-pod.sh`). A server started by the old version still holds the lock: stop it by process group, `kill -TERM -- -$(cat /var/lib/workshop/vllm-main.pid)`, then `wsctl start baseline`. | The server is started with `9>&-`, which closes the descriptor in the child. `infra/tests/wsctl-integration.sh` checks that a participant can restart the server while it runs. |
| 6 | On a fresh machine the first `wsctl start` stops early, with no archived log yet. | A failing `ls` in the log-rotation pipeline aborted the start under `set -o pipefail`. | Update `wsctl`. | The pipeline is guarded, so a failing `ls` no longer aborts the start. The integration test runs `machine-setup` and `wsctl` in a clean Ubuntu container (needs Docker). |
| 7 | A repeated benchmark is much faster: TTFT p50 51 ms against 391 ms, aggregate throughput 636 against 550 tokens per second. Server hit rate over the session 36 %. A different seed went back to 357 ms. | With a fixed default seed, the same command sends identical prompts, and the prefix cache serves them. | Run again with a new seed, or after a restart for a cold measurement. | A random seed per run (stored in the result), `--seed` and `--same-prompts` only on purpose, and a warning when the hit rate is above 5 % for a workload without a shared prefix (`benchmark/tests/test_harness.py`). |
| 8 | Offline `from_pretrained("Qwen/Qwen3-8B")` fails; `vllm bench serve` cannot load the tokenizer. | A download by commit SHA creates no `refs/main`. | Rerun `infra/deploy-to-pod.sh`, or on the pod `HF_HOME=/opt/workshop/hf python3 /usr/local/lib/workshop/fetch-models.py --models workshop --config /opt/workshop/repo/config/models.yaml`. | `fetch-models.py` writes `refs/main` with the pinned SHA (`infra/tests/test_fetch_models.py`). |
| 9 | Structured output ends in truncated JSON: `{category, urgency, needs_human}` and then 5,469 whitespace characters up to `max_tokens` (300). | The schema had four required fields and the prompt named none. Constrained decoding enforces syntax, not semantics. | Name the fields in the prompt (34 tokens then). | `config/vllm-profiles/base.yaml` sets `disable_any_whitespace: true` with an explicit `xgrammar` backend (with `auto` the server refuses to start). `apps/inference-client/structured.py` names the fields. Task 02 (Further Exploration) asks participants to reproduce it. |
| 10 | After a failed `wsctl start` the group has no model at all. | The old server was stopped before the new one failed. | `wsctl start baseline`. | `wsctl` rolls back to the previous profile and its overrides, tells the group with `wall`, and logs "rollback to ... after failed start of ..." (`infra/tests/wsctl-integration.sh`, section "rollback"). |
| 11 | `verify-machine.sh --expect-gpu "RTX PRO 6000"` fails with "unknown option". | A GPU name with spaces, passed over SSH, was split into words. | Update the script. | `verify-machine.sh` quotes every forwarded argument with `printf '%q'`. |
| 12 | A research agent reports that a vendor documentation page contains instructions addressed to AI agents. | Web pages are untrusted input. | Ignore the instructions. Note the page. | A rule, not a script: fetched content is data. RESEARCH 7.12 records the case. Check every tool call an assistant proposes for provisioning, because pods bill by the second. |
| 13 | A research agent's claim turns out wrong or unsupported. | Agents summarise and sometimes err. | Read the primary source before it goes on a slide. | A rule: `docs/REFERENCES.md` says "re-read before quoting"; unverified items carry an `Unverified:` label. The CVE advisory, the Omnibus regulation number and dates, and two licence files were re-checked and held. |
| 14 | You run `pkill -f "vllm serve"` through SSH and your own session dies. | The pattern also matches the SSH command line itself. | Reconnect. Use `ssh -p <port> root@<ip> 'wsctl stop'`. | `wsctl stop` signals the process group from a PID file. `wsctl reap` finds strays by process group. Never use `pkill -f` over SSH. |
| 15 | After a pod restart: connection refused, a new port, no accounts, no participant files, the GPU idle. | A restart destroys and recreates the container. The container disk is wiped, `/workspace` is kept. The recorded start command is stored at creation, so changing `pod-start.sh` later does not change a running pod. | Section 2.2. To change the start command, recreate the pod. | The rebuild is one command. Accounts come from `infra/participants.yaml`, models from the cache. `infra/cleanup.sh --collect` each evening saves participants' work. |
| 16 | `docker` does not work on the pod. | A pod is a container. Docker, Compose and Docker-in-Docker are not available on GPU pods. | Do the Day 3 container exercise on the participants' laptops. | The exercise builds `apps/inference-client/Dockerfile` (CPU only, non-root, 72 MB in the test). Monitoring runs as plain processes (`wsmon`). `./scripts/preflight.sh` warns when the laptop's Docker daemon is not running. |

### 2.2 Pod restart and rebuild

What happens: the container is recreated. The container disk is wiped. `/workspace` keeps the model cache. The IP usually stays, the public SSH port changes (measured: 22290, then 22235). `sshd` was listening 11 s after the restart. Servers, accounts, API key, SSH host keys, the Grafana password and participants' homes are gone.

```bash
# 1. Read the new port: Runpod MCP get-pod, fields ssh.direct.host and ssh.direct.port.
# 2. Put host and port of that group into infra/participants.yaml.
# 3. Rebuild (measured: 5 min 41 s in total):
infra/deploy-to-pod.sh --host <ip> --port <new-port> --group <id>
# 4. Check:
infra/verify-machine.sh --host <ip> --port <new-port>
```

Measured recovery: model cache seeded from `/workspace` in about 60 s, monitoring 16 s, vLLM 194 s, embedding server 53 s.

Then tell the group:

- The new port.
- The host key is new (`ssh-keygen -R "[<host>]:<port>"` if the port did not change).
- The API key is new: log in again.
- Files in `~/ki-ohne-cloud` are gone. Only what you collected earlier survives (`infra/cleanup.sh --host <ip> --port <port> --collect`).

Revocations and the file:

- Accounts come back from `infra/participants.yaml`, including every key listed there.
- `infra/revoke-participant-key.sh` acts on the pod only. After a rebuild, a revoked participant is created again.
- So remove the person's entry (or key) from `infra/participants.yaml` when you revoke. Check afterwards: `ssh -p <port> root@<ip> 'ws-user list'`.

The trainer scripts keep their own `known_hosts` file, so recreated pods do not touch yours. If the port did not change but the host key did, remove the stale line: `ssh-keygen -R "[<ip>]:<port>" -f infra/.state/known_hosts`.

### 2.3 Stock shortages and fallbacks

Stock for the workshop GPU was "Low" on the day it was checked. Read before you create (`infra/provision.md`, step 2).

| Situation | Action |
| --- | --- |
| Creating a pod fails or capacity is low | Runpod MCP: `list-gpu-types` with `include: ["AVAILABILITY"]`, `product: ["POD"]`, `cloud: "SECURE"` and EU countries, then `get-capacity` for `NVIDIA RTX PRO 6000 Blackwell Server Edition` with CUDA 13.0 and 13.2. Create the pods well before the workshop. |
| One data center is empty | The pod spec lists `dataCenterIds` `EU-RO-1`, `EUR-IS-1`, `EUR-IS-2`. Try the others. |
| The audience needs the EU, not only the EEA | `EUR-IS-2` (Iceland) is in the EEA but not the EU. Pin `dataCenterIds` to `EU-RO-1` and accept lower availability. |
| Not enough pods for four groups | Three pods carry up to 11 participants in groups of 3 to 4 (`infra/provision.md`, step 1). |
| Only another GPU is available | Every measured number and slide figure is for the Server Edition. The Workstation Edition has 12 % more memory bandwidth (1792 against 1597 GB/s, derived), so results are not interchangeable. An 80 GB card changes the sizing: `scripts/sizing.py --gpu-gib 80`. `verify-machine.sh --expect-gpu "RTX PRO 6000"` matches both RTX PRO 6000 cards; use `--expect-gpu "Server Edition"` to tell them apart. |
| Driver check fails ("older than R580") | The CUDA 13 image needs R580 or newer. Recreate with `gpu.minCudaVersion: "13.0"` as in the pod spec, on another host. |
| Temptation to stop a pod to save money | Do not. A stopped pod can restart with zero GPUs if capacity is gone, and still bills for its volume. Restart also wipes the container disk (2.2). Pods stay running during the workshop and are deleted at the end. |
| Create is refused | Runpod needs balance for at least one hour of every pod. At a zero balance all pods stop, and pods without a network volume are terminated. Keep auto-pay on. |

### 2.4 The 100-second proxy limit

The Runpod HTTP proxy (`https://<podId>-<port>.proxy.runpod.net`) has a connection limit of about 100 s (a Cloudflare error 524) and no authentication. The workshop does not use it: the pod exposes only `22/tcp`, vLLM binds `127.0.0.1`, and participants use SSH tunnels. A tunnel has no such limit; `sshd` keeps connections alive (`ClientAliveInterval 30`).

| Symptom | Cause | Fix |
| --- | --- | --- |
| A 524 error, or a long non-streaming request cut after about 100 s | Someone reached the server through the proxy URL, which means a port other than 22 was exposed. | Do not use the proxy. Recreate the pod from `infra/runpod/pod-spec.example.json` (`ports: ["22/tcp"]`). An exposed vLLM port also leaks `/metrics`, `/health` and `/tokenize` (incident 2). |

### 2.5 Billing checks

Billing is per second. A pod bills until it is deleted. Use the Runpod MCP tools.

| When | Check | Expect |
| --- | --- | --- |
| Before the session | `list-pods` | Only the pods you expect. Read the live price: the price on the day of validation was $2.49 per pod-hour, so four pods cost about $10 per hour. |
| During the day | `list-billing` (hourly buckets) | Spend matches pods times price. |
| After each scripted session | `delete-pod` for pods you no longer need, then `list-pods` | No pods. |
| End of the workshop | `infra/cleanup.sh --all --collect --revoke --stop-servers`, then `delete-pod` for every pod | `list-pods` returns no pods. |
| Final | `list-network-volumes` | Nothing you still pay for. Stopped pods keep billing for storage. |
| Final | `list-billing` for the last day | Zero hourly spend after deletion. |

`infra/cleanup.sh` never deletes pods. It prints this checklist at the end.

### 2.6 Reading `verify-machine.sh`

```bash
infra/verify-machine.sh --host <ip> --port <port>              # all checks
infra/verify-machine.sh --host <ip> --port <port> --no-gpu     # accounts, SSH and permissions only
infra/verify-machine.sh --host <ip> --port <port> --quiet      # print only WARN and FAIL
```

Each line starts with `PASS`, `WARN` or `FAIL`. The script exits non-zero on any `FAIL`. The last line reads "N passed, N warnings, N failed". Aim for PASS on every line. A WARN explains itself, and some are expected (for example, no accounts yet before you sync participants). The script never prints the API key and sends only a few 8-token requests, so it is safe during the workshop.

| Section and message | Meaning | Fix |
| --- | --- | --- |
| Host: "container disk has only N GB free" | Less than 5 GB free on the container disk. | Remove old logs, or recreate the pod with a larger `disk` (the spec uses 50). |
| GPU: "expected N GPU(s), found M" | Wrong pod type. | `get-pod`; recreate. |
| GPU: WARN "GPU model is ..., expected ..." | Numbers will not be comparable with the slides. | See 2.3. |
| GPU: "driver ... is older than R580" | The CUDA 13 image cannot run. | Recreate on another host (2.3). |
| SSH: "sshd configuration valid", "key-only login enforced", "AllowGroups restricts logins", "group 'workshop' exists" | `machine-setup.sh` did not run or was altered. | Rerun `infra/deploy-to-pod.sh --host <ip> --port <port> --group <id>` (idempotent). |
| Accounts: "account X is missing (run: ws-user restore)" | The registry knows the user, the account is gone. | Same container: `ssh -p <port> root@<ip> 'ws-user restore'`. After a restart: rebuild (2.2). |
| Accounts: WARN "X: account exists but has no key (revoked?)" | Expected after a revocation. | Otherwise `infra/sync-participants.sh --group <id>`. |
| Accounts: "X: home mode is N, expected 700", or WARN "no repository copy" | The home was altered, or never populated. | `infra/reset-machine.sh --host <ip> --port <port> user <name>`. |
| "isolation: A can read B's home" | Participants can read each other's files. | Serious. Rerun the deployment and check the modes of `/home/*`. |
| "participant cannot run 'sudo wsctl'", "participant has unrestricted sudo" | `/etc/sudoers.d/workshop` is wrong. | Rerun `infra/deploy-to-pod.sh`. |
| "integrity: A can write to <path>" | A participant can change something root runs. | Serious. Rerun `infra/deploy-to-pod.sh`, which sets `root:root` and `go-w`. |
| "participants can list /var/lib/workshop/keys" | Public keys are readable. | The `keys` directory must be `700`. |
| "participants cannot read /var/lib/workshop/api-key" (or `group`, `server.json`) | Incident 4. | `chmod 755 /var/lib/workshop`; the key file `640 root:workshop`. |
| "the API key was found under /workspace" | Incident 1. | Rotate the key as described there. |
| "API key file is '...'" | Wrong owner or mode. | `chown root:workshop /var/lib/workshop/api-key; chmod 640 /var/lib/workshop/api-key`. |
| Models: "role: repo @ rev is not in the cache" | A pinned model is missing. | Rerun `deploy-to-pod.sh` (seeds from `/workspace`, then downloads). |
| Servers: "main server is not healthy (sudo wsctl status; sudo wsctl logs)" | The main server is down or loading. | `ssh -p <port> root@<ip> 'wsctl status; wsctl logs 60'`, or `infra/reset-machine.sh --host <ip> --port <port> servers`. |
| Servers: "/v1/models without a key returned N (expected 401)" | The server runs without a key. Serious. | Check `/var/lib/workshop/api-key` exists, then `wsctl restart`. |
| Servers: "port 8000 is bound to ALL interfaces" | The server was not started through `wsctl`. Serious. | `wsctl stop`, then `wsctl start baseline`. |
| Servers: "completion request failed" | The server is up but errors. | `wsctl logs 60`. |
| Servers: WARN "embedding server (port 8001) is not running" | The RAG demo will fail. | `ssh -p <port> root@<ip> 'wsctl embed start'` (53 s). |
| Servers: WARN "no /var/lib/workshop/server.json" | The server was not started by `wsctl`. Benchmarks lack provenance. | `wsctl start baseline`. |
| Servers: WARN "N vLLM-related processes" | Probably a stray server. | `wsctl status`, then `wsctl reap` (it kills every vLLM process `wsctl` did not start). |
| Monitoring: GPU exporter, Prometheus, "Prometheus scrapes vLLM", Grafana, "dashboard provisioned" | A monitoring process is down, or the main server is not scraped. | `ssh -p <port> root@<ip> 'wsmon status'`, then `wsmon restart`. |

### 2.7 Everyday trainer actions

| Situation | Command or cause |
| --- | --- |
| The shared server is stuck | `infra/reset-machine.sh --host <ip> --port <port> servers` |
| A participant broke their repository copy | `infra/reset-machine.sh --host <ip> --port <port> user <name>` (artifacts kept; `--hard` discards them) |
| Everybody needs a fresh copy | `infra/reset-machine.sh --host <ip> --port <port> participants` |
| Late joiner | Add the entry to `infra/participants.yaml`, then `infra/sync-participants.sh --group <id>` |
| Revoke one participant | `infra/revoke-participant-key.sh --host <ip> --port <port> --user <name>`, then remove the entry from `infra/participants.yaml` |
| Who did what | `ssh -p <port> root@<ip> 'tail -n 50 /var/log/workshop/wsctl.log /var/log/workshop/access.log'` |
| Stray vLLM process | `ssh -p <port> root@<ip> 'wsctl status'`, then `wsctl reap` |
| Server provenance | `ssh -p <port> root@<ip> 'wsctl info'` |
| Monitoring down | `ssh -p <port> root@<ip> 'wsmon status'`, `wsmon restart` |
| `deploy-to-pod.sh` says it cannot log in as root | The key is not registered with Runpod, or `sshd` is not up yet (about 11 s after start). |
| `deploy-to-pod.sh` says the directory is not a git checkout | The script uses git to decide what may leave your laptop. Run it from a clone. |
| End of day | `infra/cleanup.sh --host <ip> --port <port> --collect` |

### 2.8 Grafana lockout

Symptom: you cannot log in to Grafana as `admin`, even with the right password.

Cause: Grafana's brute-force protection locks the account after several failed attempts. It happened during the Grafana fixes (incident 3), when the admin account was locked after several failed logins.

Fix:

- Stop trying: each wrong attempt counts toward the lockout.
- Participants do not need a login: the dashboard is open to anonymous viewers (`monitoring/pod/grafana.ini`), through `ssh -L 3000:127.0.0.1:3000`.
- You do not need to guess the admin password: it is stored on the pod. `ssh -p <port> root@<ip> 'cat /var/lib/workshop/grafana-admin-password'`.
- Wait for the lockout to expire, then log in once with that password. `wsmon restart` re-applies the stored password to the database with Grafana's own CLI. Not verified: the length of the lockout, and whether a restart clears it.
