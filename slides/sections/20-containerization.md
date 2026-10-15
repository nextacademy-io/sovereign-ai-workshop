---
layout: section
module: 20
heading: "Containerization and reproducible deployments"
layer: infrastructure
question: "Does a container image make a deployment reproducible?"
can:
  - "Name the three owners of a deployment: host, image and mounts"
  - "Pin a deployment so it can be reproduced, and say what stays unpinned"
  - "Build a client image and run it against the group endpoint"
---

---
layout: two-col
heading: "docker run does not record the deployment"
ratio: "3:2"
---

<Terminal title="the run line in deploy/vllm/Dockerfile">

```bash
docker run --rm --gpus all --ipc=host \
  -e PROFILE=baseline \
  -e VLLM_API_KEY="$VLLM_API_KEY" \
  -v "$HOME/.cache/huggingface:/models" \
  -p 127.0.0.1:8000:8000 \
  ki-ohne-cloud/vllm:local
```

</Terminal>

It names an image and some inputs, and nothing else.

::right::

### Not in the command

- the **host driver** (CUDA 13 needs R580 or newer)
- the **revision** of the files in `/models`
- the **profile** behind the name
- the **cache state**: compile and kernel caches

<!--
**Key:** A run command names an image and some inputs, but the deployment is also the host driver, the model revision, the configuration and the cache state, and none of those are in the command.

**Example:** Two hosts run the same command: one has a driver below R580 and the CUDA 13 image fails at CUDA initialization, the other mounts a newer model snapshot and answers differently.

**Transition:** First, what is inside the image and what is not.

**Question:** "Isn't the image the reproducible part?" Only if it is pinned by digest, because a tag can be re-pushed.

**Deeper:** This list is almost word for word the comment block at the top of deploy/vllm/Dockerfile, which we read line by line in a few slides.
-->

---
layout: default
heading: "Three owners: host, image, mounts"
---

| Owner | What | Changes when |
| --- | --- | --- |
| **Host** | GPU driver; the NVIDIA container runtime, which injects `nvidia-smi` from the host | the provider or admin updates the machine |
| **Image** | Ubuntu 24.04, Python 3.12, CUDA 13.0.2 user space, PyTorch, vLLM v0.31.0 | you build or pull a different digest |
| **Mounts and environment** | model weights, compile cache, profile name, API key | every run |

<Takeaway>

Reproducible means all three owners are pinned or recorded, not only the image.

</Takeaway>

<!--
**Key:** A GPU container is split across three owners: the host owns the driver, the image owns the CUDA user space and the engine, and the run owns weights, configuration and secrets.

**Example:** `nvidia-smi` is not in the vLLM image at all; the container runtime injects it from the host, which is why the same image reports a different driver on a different machine.

**Transition:** The host-image pair is the first thing that fails on a new machine, so let us look at it with our own numbers.

**Question:** "Is the image really about 9 GB?" About 9 GB compressed for the amd64 image with 40 layers; most of it is PyTorch, CUDA libraries and the compilers vLLM needs at run time.

**Deeper:** The image keeps nvcc and the CUDA development packages because kernels such as FlashInfer compile at run time.
-->

---
layout: default
heading: "The host driver and the image CUDA must agree"
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Host driver" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="configuration.hardware.driver_version" note="reported by the host" />
<MetricCard label="CUDA runtime in the image" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="configuration.cuda_details.runtime" note="what vLLM runs on" />
<MetricCard label="Highest CUDA the driver supports" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="configuration.cuda_details.driver_max" note="the ceiling, not the toolkit" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

- CUDA 13.x images need a host driver of **R580 or newer**.
- Starting the container and initializing CUDA are **different checks**.

<!--
**Key:** The driver belongs to the host and the CUDA user space to the image, and the pair must be compatible before anything else is debugged.

**Example:** Read the cards left to right: the host's driver, the CUDA runtime of the image, and the ceiling the driver supports. The runtime must sit at or below the ceiling, and for CUDA 13 the driver must be R580 or newer.

**Transition:** The other big decision is where the model weights live.

**Question:** "What if I cannot update the driver?" Use the image tag built for CUDA 12.9, which needs 575.57.08 or newer, or ask the provider; on Runpod `gpu.minCudaVersion` sets a CUDA floor for exactly this.

**Deeper:** A container can start and still fail at the first CUDA call; whether forward-compatibility mode covers the RTX PRO 6000 is unverified, so do not plan on it.
-->

---
layout: default
heading: "Where do the weights come from?"
---

| Strategy | Image | A model change means | Risk |
| --- | --- | --- | --- |
| **Baked into the image** | grows by the weights (16.38 GB for Qwen3-8B BF16) | rebuild and push | huge layers, slow pulls, a copy on every host |
| **Downloaded at start** | unchanged | restart | start waits for the network; drift unless the revision is pinned |
| **Mounted cache** (this repository) | unchanged, about 9 GB compressed | change the revision, restart | the cache must be filled and kept intact |

<Takeaway>

The workshop mounts a cache, pins the revision by commit SHA and sets `HF_HUB_OFFLINE=1`: a missing model fails fast instead of fetching something else.

</Takeaway>

<!--
**Key:** Baking weights makes the image self-contained and enormous, downloading at start makes it small and non-reproducible, and a mounted cache pinned by SHA keeps it small and exact.

**Example:** Qwen3-8B in BF16 is 16.38 GB of safetensors; baked in, each model change is a rebuild and a push of that size, mounted it is one changed revision in a profile.

**Transition:** Now the Dockerfile itself.

**Question:** "When would I bake the weights in?" For air-gapped sites or autoscaled nodes where a pull from a local registry is faster and safer than a download; measure both.

**Deeper:** The cache needs the right layout: downloading by commit SHA creates no refs/main, so loading by model name failed offline until fetch-models.py wrote the reference.
-->

---
layout: code
class: ki-code-sm
heading: "The vLLM image, line by line (1 of 2)"
file: deploy/vllm/Dockerfile (excerpt)
---

```dockerfile
ARG VLLM_IMAGE=vllm/vllm-openai@sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3
FROM ${VLLM_IMAGE}

# Telemetry off, models only from the mounted cache.
ENV HF_HOME=/models \
    HF_HUB_OFFLINE=1 \
    VLLM_NO_USAGE_STATS=1 \
    DO_NOT_TRACK=1

COPY config/vllm-profiles/ /opt/workshop/profiles/
COPY infra/pod/render-profile.py /opt/workshop/render-profile.py
COPY deploy/vllm/entrypoint.sh /opt/workshop/entrypoint.sh
```

<!--
**Key:** The base image is pinned by digest, and everything the profile needs is copied in, but the weights are not.

**Example:** Read the first line: a tag such as v0.31.0 can be re-pushed on Docker Hub, a sha256 digest cannot. HF_HUB_OFFLINE and the two telemetry switches are baked in, so a start never contacts the hub or usage statistics.

**Transition:** The second half is the health check and the entrypoint.

**Question:** "Why copy render-profile.py into the image?" The same renderer validates profiles on the pods and in the container; it refuses public binds, remote code and keys in files, so a configuration mistake fails at start.

**Deeper:** The image also carries LABEL metadata for a registry, which is documentation and not behavior; the header comment of the file records that the digest must stay in sync with infra/versions.env.
-->

---
layout: code
class: ki-code-sm
heading: "The vLLM image, line by line (2 of 2)"
file: deploy/vllm/Dockerfile and deploy/vllm/entrypoint.sh (excerpts)
---

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=900s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

EXPOSE 8000
ENTRYPOINT ["/opt/workshop/entrypoint.sh"]
```

```bash
profile="${PROFILE:-baseline}"
python3 /opt/workshop/render-profile.py "$profile" --dir /opt/workshop/profiles --container \
  --out /tmp/active.yaml "$@" >/tmp/active.json
cat /tmp/active.json

: "${VLLM_API_KEY:?set VLLM_API_KEY: the server refuses to start without an API key}"
exec vllm serve --config /tmp/active.yaml
```

<!--
**Key:** The health check allows 900 seconds before failures count, because loading and graph capture take minutes; the entrypoint renders the chosen profile, refuses to start without an API key and then replaces itself with vllm serve.

**Example:** `exec` means the engine, not a shell, is the main process, so it receives the stop signal directly. The `--container` flag makes the renderer bind all container interfaces, because the host side publishes the port on 127.0.0.1 only.

**Transition:** Together these lines separate code, configuration and secret.

**Question:** "Does the health check prove the server is healthy?" It proves `/health` answers; it says nothing about queue depth or latency, which is why the observability module exists.

**Deeper:** Failing fast without a key is a design choice: a server that starts without authentication is worse than one that does not start.
-->

---
layout: default
heading: "Configuration: what changes without a rebuild"
---

| What | Where it is set | Changing it means |
| --- | --- | --- |
| Engine flags | profile YAML in `config/vllm-profiles/`, copied into the image | a rebuild, or `--set key=value` for allowlisted keys |
| Which profile | environment variable `PROFILE` | a restart |
| API key | environment variable `VLLM_API_KEY`; the entrypoint refuses to start without it | a restart; never baked in |
| Model revision | pinned in the profile; files come from the mounted cache | new cache content and a restart |

<!--
**Key:** Keep three things apart: what is code, what is configuration and what is secret. Profiles ship with the image, the profile name arrives as an environment variable, and the key arrives only at run time.

**Example:** `docker run -e PROFILE=fp8 ...` starts the FP8 profile from the same image digest, and `--set max-num-seqs=8` changes one allowlisted knob without a rebuild.

**Transition:** Compose adds the host side: GPUs, ports and restart behavior.

**Question:** "Why not put the key into the profile?" The renderer rejects the api-key setting outright: a profile lives in git and in image layers. On the pods wsctl reads the key from a root-owned file instead.

**Deeper:** Environment variables are visible through docker inspect, so for production use a secret store or Docker secrets rather than a plain -e.
-->

---
layout: code
class: ki-code-sm
heading: "Compose states the host side"
file: monitoring/docker-compose.yml (body of the vllm service)
---

```yaml
environment:
  PROFILE: ${PROFILE:-baseline}
  VLLM_API_KEY: ${VLLM_API_KEY:?set VLLM_API_KEY in .env}
volumes:
  - ${HF_HOME:-${HOME}/.cache/huggingface}:/models
ipc: host
ports:
  - "127.0.0.1:8000:8000"
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
restart: unless-stopped
```

<!--
**Key:** The compose service states what the Dockerfile cannot: reserve the GPU, share IPC for PyTorch, publish on loopback only, restart on failure and take the key from the environment.

**Example:** `127.0.0.1:8000:8000` is the container version of binding vLLM to loopback: inside, the server listens on all container interfaces; outside, only the host's loopback sees the port.

**Transition:** The other three services in this file, Prometheus, Grafana and dcgm-exporter, are the observability stack of the next module.

**Question:** "Why ipc: host?" PyTorch uses shared memory between processes, and the vLLM docs ask for host IPC or a larger shm size; the security checklist notes that it relaxes isolation.

**Deeper:** dcgm-exporter needs the SYS_ADMIN capability for its profiling fields, which a rented container does not grant; that is one reason the pods use an NVML exporter instead.
-->

---
layout: two-col
heading: "Pinning trades freshness for reproducibility"
---

### Pin

- image by **digest**, not tag
- model by **commit SHA**
- Python packages by **version**
- all in `infra/versions.env`

::right::

### Record

- host driver version
- server arguments, profile name
- model revision, engine version

<Consequence>

A pin is a promise to re-check it, on a schedule.

</Consequence>

<!--
**Key:** Pinning gives you a deployment you can rebuild and compare, and it costs you the fixes you did not pick up, so a pin needs a schedule for re-checking.

**Example:** Our benchmark JSON stores hardware, driver, model revision, engine version and server arguments next to every number; without them a result is an anecdote.

**Transition:** Time to do it yourself, on your laptop.

**Question:** "Isn't latest simpler?" Until two hosts disagree; then nobody can say which image either one ran.

**Deeper:** The repository re-verifies its pins before every workshop, and the security notes count more than a hundred vLLM advisories at the time of writing, so a pinned old version is not automatically a safe one.
-->

---
layout: default
heading: "Your turn: build and run the client image"
---

<Terminal title="your laptop">

```bash
docker build -f apps/inference-client/Dockerfile -t ki-ohne-cloud/client:local .
ssh -p <port> -L 8000:127.0.0.1:8000 <your-user>@<host>    # leave open
export OPENAI_API_KEY=$(ssh -p <port> <your-user>@<host> 'cat /var/lib/workshop/api-key')
docker run --rm -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  ki-ohne-cloud/client:local "Say hello in German."
```

</Terminal>

<Warning title="Inside a container, 127.0.0.1 is the container">

The image calls `host.docker.internal:8000`. Docker Desktop (macOS, Windows) maps that name to your laptop. On Linux add `--add-host host.docker.internal:host-gateway` to `docker run` and bind the tunnel to the bridge: `ssh -L 172.17.0.1:8000:127.0.0.1:8000 ...`.

</Warning>

<!--
**Key:** The client image is CPU-only and talks to the group's server through your SSH tunnel; the model stays on the GPU host, and the container needs only a network path to the tunnel.

**Example:** Build, open the tunnel in a second terminal, then run. The answer streams, then `chat.py` prints one stats line (prompt tokens, time to first token, completion tokens, decode speed, total time), as in Lab 2. On Docker Desktop the host name just works; on Linux the tunnel must listen on the bridge address.

**Transition:** Check the result against the validation on the next slide; if it fails, use the fallback there.

**Question:** "It cannot connect." Check the tunnel and the key variable, then the bind: 127.0.0.1 inside a container is the container itself.

**Deeper:** The pods cannot run this, because they are containers; that is why the exercise runs on your laptop.
-->

---
layout: two-col
heading: "Did it work? Check it, or fall back"
ratio: "1:1"
---

### Done when

<Terminal title="your laptop">

```bash
docker run --rm \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  ki-ohne-cloud/client:local \
  "Say hello in German."
echo "exit code: $?"
```

</Terminal>

- a German greeting streams from your group's server
- then one line: `prompt_tokens=… ttft=… ms … decode=… tok/s total=… s`
- `exit code: 0`

::right::

### No Docker, or no route?

Run the same client on your group's server, where the environment is already set:

<Terminal title="the GPU host">

```bash
ssh -p <port> <your-user>@<host>
cd ki-ohne-cloud
python3 apps/inference-client/chat.py \
  "Say hello in German."
```

</Terminal>

Same reply, same stats line: model, key and client code work. What is left is the container: its image or its route to your tunnel.

<!--
**Key:** A finished exercise has an observable result: the container prints a German reply from the group's server and exits with code 0. When it does not, the fallback separates what works from what does not.

**Example:** Success is a few words of German, a blank line, the stats line on stderr and `exit code: 0`. A failed connection ends in a traceback naming `APIConnectionError` and a non-zero exit code. The run on the pod uses the same `chat.py` with the environment already set: if it answers, server, key and code are fine.

**Transition:** Whichever path you took, ask what the image pinned and what it did not.

**Question:** "Docker will not start on my laptop." Use the fallback and read along; the next slide shows the image's pins.

**Deeper:** The reply wording varies; check the language and the exit code, not the text.
-->

---
layout: default
heading: "What did the container pin, and what did it not?"
---

<div class="ki-grid ki-cols-2">
<div>

### Pinned by the client image

- base image by digest
- `openai` and `numpy` by version
- a non-root user

</div>
<div>

### Left open

- the server, its model and its profile
- the key, set at run time
- your tunnel and your Docker

</div>
</div>

<Terminal title="check it">

```bash
docker images ki-ohne-cloud/client
docker run --rm --entrypoint id ki-ohne-cloud/client:local
```

</Terminal>

<!--
**Key:** An image pins what it contains, and a client image contains very little of the system it depends on; reproducibility belongs to the whole deployment.

**Example:** Ask the room to read their image size from docker images and compare it with the many-gigabyte vLLM image; then ask who can say which model revision answered their request. Only the server's provenance file can, not the client.

**Transition:** The vLLM image is not non-root either, which leads to what managed platforms take away.

**Question:** "Why is our vLLM image not non-root?" The upstream image runs as root by default and offers a non-root option; the workshop engine runs as root on the pods, an accepted risk for public data, and the client image shows the better habit.

**Deeper:** Pass --user 2000:0 to the upstream image to try the non-root route.
-->

---
layout: default
heading: "On a managed pod the image is the deployment unit"
---

| | Workshop pod (managed) | Your own host |
| --- | --- | --- |
| Runtime | one container: no Docker, no Compose, no sidecars | Docker and the NVIDIA Container Toolkit, or Kubernetes |
| Driver | the provider's host; you set a CUDA floor | yours to install and patch |
| You hand over | image digest, start command, ports, disks | the whole Compose or cluster definition |
| After a restart | container disk wiped, `/workspace` kept, SSH port changes | `restart: unless-stopped`, volumes kept |
| Monitoring | plain processes in the same container | separate containers |

<!--
**Key:** On a managed GPU platform you give up the runtime and keep the image: you choose what to start, the provider owns the Docker layer and the driver. On your own host you own all of it.

**Example:** Our pods run the upstream vLLM image by digest with a start command that installs sshd, and monitoring runs as plain processes in the same container; the same Prometheus configuration and dashboard run as containers via the compose file on your own server.

**Transition:** Next module: once it runs, how do we know it runs well?

**Question:** "Why no Docker on the pods?" A Runpod pod is itself a container, and the platform documents that Docker and Compose cannot run inside it.

**Deeper:** After a pod restart the container disk is wiped and the SSH port changes, so the rebuild script, not a restart policy, is the recovery path.
-->
