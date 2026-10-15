---
layout: section
module: 19
heading: "Production architecture"
layer: infrastructure
question: "What sits between a user's request and the GPU once the model is a service?"
can:
  - "Draw a request path from client to GPU with one failure mode per hop"
  - "Explain streaming, time-outs, retries and backpressure"
  - "Say which state lives where when a replica restarts"
---

---
layout: default
heading: "What we have run so far"
---

<Flow :items='[{ "label": "Client", "sub": "curl, SDK, app", "layer": "application" }, { "label": "API", "sub": "OpenAI-compatible", "layer": "runtime" }, { "label": "Inference server", "sub": "vLLM", "layer": "runtime" }, { "label": "GPU", "sub": "one per group", "layer": "runtime" }]' />

That is enough to learn how inference works. It is not yet a service.

- **Who** may call it, and how many calls at once?
- **What happens** when a replica is slow, full or dead?
- **How do we know**, and how do we change it safely?

<!--
**Key:** Everything we have run so far is four boxes in a row. Production adds what protects, multiplies, observes and feeds them.

**Example:** On our pods nothing restarts vLLM when it hangs: `wsctl` starts, stops and checks the server on request, and a person types the command.

**Transition:** The next slide draws the whole stack; then we walk the request path hop by hop and ask what fails at each.

**Question:** "Does this need Kubernetes?" No. The picture is the same under systemd, Compose or Kubernetes; the orchestrator only automates restarts, scaling and rollout.

**Deeper:** vLLM's documentation lists Kubernetes integrations such as production-stack and llm-d; treat them as one way to automate this picture, not as the picture.
-->

---
layout: default
heading: "The production inference stack"
---

<D13ProductionStack />

<!--
**Key:** The request path of the first server gets a gateway and a balancer in front and several replicas behind, and four kinds of supporting service keep it alive: observability, a model registry, secrets and storage.

**Example:** Read the top row left to right: gateway and balancer are where authentication, rate limits and health probes live. Click once for the supporting services, again for what the workshop pods leave out.

**Transition:** Let us take the request path hop by hop and ask what fails at each.

**Question:** "What is the GPU pool?" The capacity behind the replicas: each replica owns one or more GPUs, and the pool is what a scaler grows or shrinks.

**Deeper:** The dashed boxes are the honest part: the pods run one replica per group and no gateway, which is why Lab 5 asks you to design what the pods lack.
-->

---
layout: default
heading: "The request path: one job and one failure per hop"
---

| Hop | Job | How it fails |
| --- | --- | --- |
| API gateway | TLS, authentication, rate limits, path allowlist | open endpoints, one shared key, no limit per client |
| Load balancer | spreads requests, probes health, bounds the queue | sends work to a full replica, hides a dead one |
| Replica (vLLM) | schedules requests, holds weights and KV cache | queue grows, memory fills, process hangs |
| GPU | runs the model | out of memory, throttled, driver mismatch |

<Takeaway>

Each hop adds latency, a failure mode and something to monitor.

</Takeaway>

<!--
**Key:** Every hop has one job and a typical failure, and a failure usually shows up one hop later than where it starts.

**Example:** A full KV cache inside a replica reaches the client as a slow first token, and reaches the operator as waiting requests, long before any error appears.

**Transition:** The replica is the only hop that keeps expensive state in memory, so state comes next.

**Question:** "Do we need a balancer for one replica?" Not to balance, but yes for health probes, draining and an entry point that survives replacing the replica.

**Deeper:** A gateway can also be the balancer; the boxes are roles, not products. Driver mismatch is a real GPU-hop failure: a CUDA 13 image needs a host driver of R580 or newer.
-->

---
layout: default
heading: "State: the API is stateless, the process is not"
---

| State | Where it lives | Gone when the replica restarts? |
| --- | --- | --- |
| Conversation history | the client sends it with every request | no |
| Weights | VRAM, loaded from the model cache | yes: load again |
| KV cache and prefix cache | VRAM of that one replica | yes: recompute |
| Compiled kernels, CUDA graphs | a cache directory | only if the directory is lost |

<Consequence>

A replica is replaceable only once it is warm. Routing, restarts and scaling all inherit that.

</Consequence>

<!--
**Key:** The HTTP API is stateless because the chat history travels in every request, but the replica behind it keeps expensive state in memory: weights, KV cache and prefix cache.

**Example:** Restart one replica and the cached system prompt is gone; the next requests pay full prefill until the cache fills again. Whether the compile cache survives decides how long the restart takes, and the scaling module shows that difference as measured start-up times.

**Transition:** State in memory also changes what a long-lived stream means for failure handling.

**Question:** "Can replicas share a KV cache?" Offloading and disaggregated prefill exist in vLLM v0.31.0, with disaggregation flagged experimental; the default is one cache per replica.

**Deeper:** Each data-parallel engine has its own KV cache, so the benefit of prefix caching depends on routing.
-->

---
layout: default
heading: "Streaming, time-outs and retries"
---

| Concern | Rule of thumb |
| --- | --- |
| Streaming | a response lives for seconds; every proxy must pass chunks on, not buffer them |
| Time-outs | separate limits for connect, first token, gap between tokens and total |
| Retries | only before the first token, with back-off: afterwards a retry repeats the whole generation |
| Cancel | a client that leaves ends as finish reason `abort`; check that the disconnect reaches the engine |

<Warning title="A proxy limit is a deployment fact">

Runpod's HTTP proxy cuts a request at about 100 s (error 524). Streaming keeps bytes flowing; it does not make a request fast.

</Warning>

<!--
**Key:** Streaming turns a request into a long-lived connection, so time-outs, retries and cancellation each need a rule that fits a response that is half delivered.

**Example:** A client gives up after 30 s on a 40-second generation and retries; the GPU now runs the same work twice while the first answer is produced for nobody.

**Transition:** When many such requests arrive together they queue, and what we do with the queue is the next slide.

**Question:** "What time-out do I set?" Derive it from the SLO: 0.8 s to first token plus 180 tokens at 25 tokens per second is 8 s in total (METRICS section 14); set limits above that with headroom and alert before clients hit them.

**Deeper:** The workshop pods never use the proxy, because only SSH is exposed.
-->

---
layout: two-col
heading: "Queues and backpressure"
ratio: "1:1"
---

A queue turns overload into waiting. Without a limit, the waiting has no ceiling.

- **Bound** the queue
- **Reject early** with 429 or 503 and a retry hint
- **Reject at the gateway**, where it is cheap

::right::

<ResultTable
  source="illustrative"
  :headers='["Arrivals (req/s)", "Capacity (req/s)", "Waiting after 60 s", "Last one waits"]'
  :rows='[[8, 10, 0, "none"], [12, 10, 120, "12 s"], [20, 10, 600, "60 s"]]'
/>

Last one waits = backlog ÷ capacity.

<!--
**Key:** Overload does not make a server gracefully slower; it builds a queue, and time in the queue is latency that the SLO counts.

**Example:** At 12 requests per second against a capacity of 10, the backlog grows by 2 per second, so after a minute the last request waits 12 seconds; at 20 requests per second it waits a full minute. These figures are illustrative arithmetic, not a measurement.

**Transition:** On the dashboard this queue is the waiting-requests panel, which is why health and metrics come next.

**Question:** "Where does vLLM bound its queue?" The scheduler configuration has limits on queued requests and tokens with HTTP 503 beyond them, but I could not verify which are exposed as flags in v0.31.0, so enforce the limit at the gateway.

**Deeper:** Ollama defaults to a queue of 512 and answers 503 beyond it: a concrete bounded queue in a local runner.
-->

---
layout: default
heading: "Health checks that tell the truth"
---

| Question | Check | In this repository |
| --- | --- | --- |
| Is the process alive? | liveness: `/health` answers | `wsctl status` |
| Can it take traffic? | readiness: model loaded | `wsctl start` polls `/health` until it answers |
| Does it meet the SLO? | latency and queue depth from metrics | Grafana panels, no probe |

<Warning title="Green is not healthy">

An engine can hang while `/health` stays green (advisory GHSA-4xqp-c3mv-qff7). Watch queue depth and latency as well.

</Warning>

<!--
**Key:** A health check answers one narrow question, so production needs three: alive, ready for traffic, and healthy enough for the SLO.

**Example:** `/health` returns 200 with an empty body and 503 only when the engine is dead; `wsctl start` polls it until the model is loaded, and the Dockerfile we read next allows a 900-second start period before it counts a failure.

**Transition:** The three checks, the keys and the weights need a home outside the replicas, the control plane.

**Question:** "Why not probe with a real completion?" You can, as a rare one-token canary; it uses the GPU and a key, so keep it out of the metrics you alert on.

**Deeper:** The advisory is a request with an oversized min_tokens that hangs the engine; the lesson is that liveness alone cannot see it.
-->

---
layout: default
heading: "Registry, secrets, storage: what the replicas are built from"
---

| Component | In production | On the workshop pods |
| --- | --- | --- |
| Model registry | approved revisions in one place, pulled by commit SHA | `config/models.yaml` pins every model by SHA; `infra/pod/fetch-models.py` downloads it |
| Secrets | per-client keys from a secret store, rotated | one group key in a root-owned file that every participant can read, on purpose |
| Storage | read-only model cache, persistent compile cache | model files cached on `/workspace`, which enforces no permissions; compile caches on the container disk |

<!--
**Key:** Replicas must be disposable, so what they are built from lives outside them: which model revision, which keys, which cached files.

**Example:** Our pods pin the model by commit SHA and run offline afterwards, so a missing model fails fast instead of fetching something else; the shared key identifies a group, not a person, which is fine for public data and wrong for production.

**Transition:** Let us see all of this on the pods themselves.

**Question:** "Why is /workspace only a cache?" Measured during the build: on that volume chmod is ignored and any user can read any file, so nothing secret and nothing root executes lives there.

**Deeper:** The container disk is wiped on a pod restart, so the rebuild script recreates accounts and code, and the weights come back from the cache.
-->

---
layout: code
class: ki-code-sm
heading: "The pods: SSH is the only door"
file: docs/SECURITY.md
---

```text
participant laptop ── ssh -L ──►  pod (container on a rented host)
                                  ├─ sshd on 22/tcp         the only exposed port
                                  ├─ vLLM 127.0.0.1:8000    shared by the group, --api-key
                                  ├─ vLLM 127.0.0.1:8001    embeddings for the RAG demo
                                  ├─ Prometheus 9090, Grafana 3000, GPU exporter 9400   loopback
                                  └─ /workspace             network volume: download cache only
trainer laptop ── ssh as root ──► deployment, verification, revocation (infra/)
```

<!--
**Key:** The pods are a real, small system: one container per group, one shared vLLM bound to loopback, monitoring as plain processes, and SSH as the only exposed port, so the tunnel is the gateway.

**Example:** From your laptop `ssh -L 8000:127.0.0.1:8000` makes the group's server look local; nothing else on the pod answers from the internet.

**Transition:** The key on that server protects less than people assume.

**Question:** "Why one server per group?" On purpose: shared use shows queueing and contention first-hand; production would give each tenant or workload its own routing.

**Deeper:** The pod specification asks the provider for 22/tcp only, and the profile renderer refuses any bind address except 127.0.0.1, two independent layers.
-->

---
layout: default
heading: "The API key does not protect every endpoint"
---

| Path | With `--api-key` set |
| --- | --- |
| `/v1/*` (chat, completions, embeddings, models) | needs `Authorization: Bearer <key>` |
| `/health`, `/metrics`, `/version`, `/load`, `/ping` | open |
| `/tokenize`, `/detokenize`, `/pooling` | open |

<Warning title="The default bind is all interfaces">

Without `--host`, vLLM listens everywhere. On the pods every server binds `127.0.0.1`, and only SSH is exposed.

</Warning>

<!--
**Key:** The API key guards only the OpenAI-compatible routes; metrics, health and tokenizer routes stay open, so the network boundary is the real control and the key is one layer.

**Example:** During pod validation `curl` on `/metrics`, `/health` and `/tokenize` worked without any key, which is why the verify script checks the loopback bind and that `/v1/models` without a key returns 401.

**Transition:** So what did the workshop simplify, and what would production have to add?

**Question:** "Would a gateway fix this?" Yes, if it allowlists paths and keeps `/metrics` on an internal network for Prometheus only; the vLLM flag help itself says not to rely on the key alone.

**Deeper:** The key check had two advisories of its own, a timing attack and a Host-header bypass, which the security module returns to.
-->

---
layout: default
heading: "What the pods simplify, and what production adds"
---

| Production element | Workshop pods | What the simplification hides |
| --- | --- | --- |
| Gateway, TLS, per-client keys | SSH tunnel, one key per group | no per-person audit, no rate limit |
| Balancer, replicas | one shared server, one GPU | no failover: every restart is downtime |
| Health, restart, rollout | `wsctl status`, restart by hand | nothing replaces a failed server |
| Autoscaling | pods run for the whole session | an idle GPU still bills per second |
| Traces and alerts | dashboards only | someone has to be looking |

<!--
**Key:** Each simplification on the pods is a deliberate trade for a classroom, and each one is a line item you must design back in for production.

**Example:** One shared server makes queueing visible and teaches contention, but a single restart takes the model offline for the whole group; a second replica and a rolling restart remove that outage.

**Transition:** Lab 5 asks you to make exactly these decisions.

**Question:** "Is the pod setup a reference architecture?" No. It is a teaching rig built around what a rented container allows: no Docker, one exposed port, no Compose.

**Deeper:** Billing is per second with no egress fees, so an idle pod costs the same as a busy one; the scaling module turns that into cost per useful workload.
-->

---
layout: statement
---

# At ten times the load, what breaks first?

Name the hop, the metric that shows it, and the change you would make.

<!--
**Key:** This is the validation question of Lab 5: a design is defended by saying which hop saturates first and which signal tells you.

**Example:** For a coding assistant with long contexts the answer is probably KV memory in the replica, visible as waiting requests and KV usage; for a document pipeline it is throughput per GPU and the bill.

**Transition:** Before we scale anything, we have to package it reproducibly, so the next module is containers.

**Question:** "Is there one right answer?" No; the capstone is judged on the quality of the reasoning and on whether each recommendation names what it trades.

**Deeper:** Keep this question visible during the observability and scaling modules; both give you vocabulary for the answer.
-->
