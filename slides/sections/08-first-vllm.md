---
layout: section
module: 8
heading: "First vLLM deployment (trainer demo)"
layer: runtime
question: "What does it take to turn weights into an API, and how do you read what the server tells you?"
can:
  - "Start vLLM from a profile and read its start-up log"
  - "Call the OpenAI-compatible API with curl and from Python, streaming included"
  - "Say what the engine decided at start-up before the first request arrived"
---

---
layout: default
heading: "vllm serve: weights in, API out"
---

<Flow :items='[{ "label": "Model weights", "sub": "pinned Hugging Face revision" }, { "label": "vllm serve", "sub": "scheduler, KV cache, kernels", "layer": "runtime" }, { "label": "HTTP API", "sub": "OpenAI-compatible, port 8000" }, { "label": "Client", "sub": "curl, Python, your application", "layer": "application" }]' />

To the application the model is a **URL, a key and a model name**.

Everything between the weights and the URL is what this workshop is about.

<!--
**Key:** vllm serve loads a pinned set of weights, builds a scheduler and a KV cache around them and exposes the result as an OpenAI-compatible HTTP API, so the application layer sees an endpoint and not an engine.

**Example:** The same chat.py or curl command works against any server that speaks this API; that is also why Ollama or a cloud endpoint can be swapped in, and why we have to measure to tell them apart.

**Transition:** Before we see how our server is started, where does vLLM sit among the other engines?

**Question:** "Is the API identical to OpenAI's?" Largely: the chat completions and models routes behave the same, and extra fields such as chat_template_kwargs are vLLM extensions.

**Deeper:** The API key protects only the /v1 routes; /metrics, /health and /tokenize are open, which is why our servers bind to the loopback address only.
-->

---
layout: default
heading: "Engines: what each one is built for"
---

| Engine | Built for | A typical reason to pick it | Watch out |
| --- | --- | --- | --- |
| vLLM | Serving many requests at once on GPUs | A shared team server, broad model and hardware coverage | Many settings; verify a new GPU or model by running it |
| SGLang | Agentic workloads, large-scale serving, RL rollouts | Many calls that share a long prefix | Not measured here; vLLM also caches prefixes |
| TensorRT-LLM | Optimizing inference on NVIDIA GPUs | A fixed NVIDIA fleet you want to tune hard | NVIDIA GPUs only |
| llama.cpp / Ollama | Local inference with minimal setup, on a CPU, a laptop or a GPU | One user or a laptop, a quick start, GGUF files | Check the concurrency defaults before serving a team |

<span class="muted small">Positioning, not a ranking. This workshop serves with vLLM v0.31.0.</span>

<!--
**Key:** Engines are built for different jobs: ask which fits your workload, hardware and team, not which wins. This workshop uses vLLM; the slide only positions it.

**Example:** Read the "built for" column: vLLM and SGLang are GPU serving engines, TensorRT-LLM is NVIDIA's library, llama.cpp and Ollama are local runners, and Ollama builds on llama.cpp. A later demo runs both under concurrency.

**Transition:** Our server is not started by hand; first a look at how a configuration becomes a running process.

**Question:** "Which engine is fastest?" None in general: it depends on model, GPU, workload and settings. This repository measures vLLM, and Ollama in one demo; SGLang and TensorRT-LLM are not measured.

**Deeper:** Sources: project READMEs, docs/RESEARCH.md 3.13. The book (Inference Engineering, 4.3 inference engines and 3.5 local inference) covers the same landscape; its author works for Baseten and it favors TensorRT-LLM: read its comparison with that caveat.
-->

---
layout: default
class: ki-code-sm
heading: "A profile, not a command line"
---

<Flow :items='[{ "label": "Profile", "sub": "baseline.yaml extends base.yaml" }, { "label": "wsctl start", "sub": "validates and renders it" }, { "label": "vllm serve --config", "sub": "the engine starts", "layer": "runtime" }, { "label": "/health", "sub": "wsctl waits, then records wsctl info" }]' />

<div class="ki-grid ki-cols-2">
<div>

```yaml
# config/vllm-profiles/baseline.yaml (excerpt)
extends: base
model: Qwen/Qwen3-8B
revision: b968826d9c46dd6066d109eabc6255188de91218
served-model-name: Qwen/Qwen3-8B
```

</div>
<div>

```yaml
# config/vllm-profiles/base.yaml (excerpt)
host: 127.0.0.1
port: 8000
dtype: bfloat16
max-model-len: 32768
gpu-memory-utilization: 0.80
```

</div>
</div>

<Takeaway>

A profile is one named, reviewable set of flags. You change the server only through profiles.

</Takeaway>

<!--
**Key:** Every server in this workshop is a profile: a short YAML file that extends a shared base, pins the model revision and says nothing else.

**Example:** Baseline adds only the model and the revision; base sets loopback host, port 8000, BF16, 32,768 tokens of maximum context and 80 percent GPU memory. Later profiles such as max-seqs-8 or kv-fp8 extend baseline and change one setting, which is what makes the experiments controlled.

**Transition:** Now let us look at the machine this profile is running on.

**Question:** "Can I pass any vllm flag?" Participants cannot: wsctl validates the profile and allows only a short list of overrides with --set, such as max-num-seqs or kv-cache-dtype; the trainer controls the rest.

**Deeper:** Restarting with a profile restarts the shared server for the whole group, and a profile that fails to start is rolled back to the previous one automatically.
-->

---
layout: default
heading: "Demo 1: look at the machine"
---

<Terminal title="your SSH session on the group's GPU machine">

```bash
nvidia-smi
sudo wsctl status
sudo wsctl info | python3 -m json.tool | head -40
```

</Terminal>

Run the same three commands in your own session while the trainer talks. They only read. Find three things:

- the **GPU name** and its total memory, and which process holds the memory
- the **engine version**, the profile and the start-up time
- the **weights memory** and the KV-cache capacity in tokens

<!--
**Key:** Before sending any request, the first questions are: what hardware, what process, what configuration, and what did the engine decide at start-up.

**Example:** Trainer: run the three commands while everyone runs them in their own SSH session; they are read-only, and Lab 2 uses the same three. nvidia-smi names the RTX PRO 6000 Blackwell Server Edition and shows memory in use with no request running; wsctl status shows profile and health; wsctl info prints weights memory and KV capacity parsed from the log.

**Transition:** Now talk to it.

**Question:** "Why is memory in use before the first request?" vLLM reserves its budget at start-up, weights plus cache plus graphs; the cache fills as requests arrive.

**Deeper:** wsctl status also lists vLLM processes it did not start; a second copy of a model on the same GPU is the most common cause of a failed start.
-->

---
layout: default
class: ki-code-sm
heading: "Demo 2: ask the API"
---

<Terminal title="gpu host">

```bash
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  $OPENAI_BASE_URL/models | python3 -m json.tool

curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  $OPENAI_BASE_URL/chat/completions -d '{"model":"'"$WORKSHOP_MODEL"'",
  "messages":[{"role":"user","content":"Name three uses of a KV cache."}],
  "max_tokens":120,"chat_template_kwargs":{"enable_thinking":false}}'
```

</Terminal>

<div class="ki-grid ki-cols-2">
<div>

Read in the reply:

- the **model name** the server answers to
- the **usage** block: prompt and completion tokens
- the **finish reason**: stop or length

</div>
<div>

<Observation title="Thinking mode">

`enable_thinking: false` switches off Qwen3's thinking mode for this request.

</Observation>

</div>
</div>

<!--
**Key:** The whole product is two routes: /v1/models tells a client what it can ask for, and /v1/chat/completions turns a message list into tokens, with the token counts in the reply.

**Example:** Trainer: run both commands. Point at the usage block: the prompt tokens include the chat template, and the completion tokens are what we will later divide time by. Change max_tokens to 5 and show finish reason length.

**Transition:** The same request can stream, which is what makes the latency metrics visible.

**Question:** "Why is thinking switched off?" A thinking model emits a long reasoning sequence first; that changes TTFT, output length and cost, so the benchmarks and the labs switch it off and the trainer shows it separately.

**Deeper:** The environment variables are set at login; a 401 means the key is old, and logging in again fixes it.
-->

---
layout: default
class: ki-code-sm
heading: "Demo 3: stream it"
---

<Terminal title="gpu host">

```bash
python3 apps/inference-client/chat.py "Explain batching in one paragraph."

curl -N -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  $OPENAI_BASE_URL/chat/completions -d '{"model":"'"$WORKSHOP_MODEL"'",
  "messages":[{"role":"user","content":"Name three uses of a KV cache."}],
  "max_tokens":120,"stream":true,
  "chat_template_kwargs":{"enable_thinking":false}}'
```

</Terminal>

With `"stream": true` one reply becomes a **sequence of chunks**. `curl -N` turns off buffering, so you see them arrive. The gap between chunks is the **ITL** from the mechanics module.

<!--
**Key:** Streaming does not make the model faster; it lets the user see the first token after TTFT instead of waiting for the last one, and it exposes the decode loop to the client.

**Example:** Trainer: run chat.py and read the final line: prompt tokens, TTFT, completion tokens, decode speed, total. Then run the curl version with the same message and let the room count the chunks: why is the count close to the completion tokens?

**Transition:** The server knew all of this before the first request: it is in the start-up log.

**Question:** "Is a chunk always one token?" By default yes, vLLM's stream interval is 1; if it is larger, chunk gaps are no longer token gaps, and TPOT is the safer metric.

**Deeper:** Reasoning models stream their thinking in a separate field, which chat.py counts as text when it computes TTFT.
-->

---
layout: code
class: ki-code-sm
heading: "Demo 4: read the start-up log"
file: benchmark/results/reference/baseline/startup-log-excerpt.txt
---

<Flow :items='[{ "label": "Weights", "sub": "load into VRAM" }, { "label": "Compile", "sub": "kernels and graphs" }, { "label": "KV cache", "sub": "gets the rest of the budget" }, { "label": "CUDA graphs", "sub": "captured for decode" }, { "label": "Ready", "sub": "/health answers" }]' />

```text
… Loading weights took 1.97 seconds
… Model loading took 15.27 GiB memory and 3.782364 seconds
… Compiling a graph for compile range (1, 8192) takes 14.76 s
… Available KV cache memory: 58.14 GiB
… GPU KV cache size: 423,328 tokens, Maximum concurrency for 32,768 tokens per request: 12.92x
… Graph capturing finished in 6 secs, took 0.21 GiB
… init engine (profile, create kv cache, warmup model) took 41.56 s (compilation: 24.14 s)
```

<!--
**Key:** The start-up log is the engine's own account of where memory and time went, the first thing to read when a server is slow to start, has less cache than expected or refuses to start.

**Example:** Trainer: run sudo wsctl logs 60 and find these lines; the slide elides timestamps. Weights are 15.27 GiB and take seconds, compilation takes 14.76 s, the cache gets 58.14 GiB which is 423,328 tokens, graph capture takes 6 s and 0.21 GiB.

**Transition:** The same start can take very different times, and that is a measured fact.

**Question:** "Why two graph-capture lines in the log?" The first, 4 s and 0.36 GiB, belongs to vLLM's graph-memory profiling; the second is the capture the accounting uses, 0.21 GiB.

**Deeper:** The memory arithmetic behind these lines is in the sizing module; the full excerpt is in the file named above.
-->

---
layout: default
heading: "Cold, warm, restart: the same server, three start-up times"
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Cold start: time to ready" source="measured:benchmark/results/reference/startup/cold-start.json" metric="log_seconds_to_ready" unit="s" note="fresh container, no caches" />
<MetricCard label="Warm start: time to ready" source="measured:benchmark/results/reference/startup/warm-start.json" metric="log_seconds_to_ready" unit="s" note="compile and kernel caches exist" />
<MetricCard label="Restart: time to ready" source="measured:benchmark/results/reference/startup/restart.json" metric="log_seconds_to_ready" unit="s" note="wsctl restart, warm caches" />
<MetricCard label="Cold start: graph capture" source="measured:benchmark/results/reference/startup/cold-start.json" metric="startup_log.graph_capture_seconds" unit="s" />
<MetricCard label="Warm start: graph capture" source="measured:benchmark/results/reference/startup/warm-start.json" metric="startup_log.graph_capture_seconds" unit="s" />
<MetricCard label="Restart: graph capture" source="measured:benchmark/results/reference/startup/restart.json" metric="startup_log.graph_capture_seconds" unit="s" />
</div>

<Provenance source="measured:benchmark/results/reference/startup/cold-start.json" />

<Consequence>

Same GPU, same weights on local disk. What differs is whether compile and kernel caches from an earlier start exist. A restart takes the model offline for everyone in the group.

</Consequence>

<!--
**Key:** Start-up time is not a constant of the model: it depends on warm caches, and a rebuilt container pays the cold start again, so plan restarts and scaling with the right number.

**Example:** Time to ready from the log: cold 176 seconds, warm 55, restart 29; the wall time that wsctl prints is longer, 67.4 and 39.3 seconds, because it counts from process launch until the API answers. Loading the weights took a few seconds in all three starts; graph capture is one place where they diverge.

**Transition:** One more thing the trainer shows before the lab: what the machine does while a request runs.

**Question:** "How often will we see a cold start?" On a freshly rebuilt container, as in the measured cold start; the scaling module uses these numbers.

**Deeper:** Three single start-ups, not a distribution: treat them as orders of magnitude.
-->

---
layout: default
class: ki-code-sm
heading: "Demo 5: watch the GPU while a request runs"
---

<Terminal title="second terminal">

```bash
./scripts/gpu-status.sh --watch
```

</Terminal>

<Terminal title="first terminal">

```bash
python3 apps/inference-client/chat.py --max-tokens 800 "Write a detailed essay about GPUs."
```

</Terminal>

<div class="ki-grid ki-cols-2">
<div>

Watch four things:

- **GPU-Util** and **power**
- **running requests**
- **KV cache used**

</div>
<div>

<MetricCard label="Memory in use during the reference run" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="gpu.memory_used_mib.max" unit="MiB" note="reserved at start-up, not load" />

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

</div>
</div>

<!--
**Key:** The status screen puts the GPU gauges and the server's own gauges side by side, so the room can see what moves with load and what does not.

**Example:** Trainer: start the watcher, then the long request. GPU-Util jumps to 100 percent even with one request, as in the GPU fundamentals module; running requests becomes 1; KV cache use stays tiny; memory in use does not change.

**Transition:** That was the demonstration. In the lab you do the same on your group's machine, alone, with the same server.

**Question:** "Why is memory in use that high with no load?" It is the engine's reservation plus anything else on the card; the result file does not record the split, so do not over-explain.

**Deeper:** The status script prints prefix-cache hit rate and preemptions too; both stay at zero or near zero in this workload.
-->

---
layout: statement
---

# The API is the product. Everything else is what makes it behave.

<!--
**Key:** From the application's side the model is an endpoint; everything we measure and tune, memory, batching, caching, precision, parallelism, is there to make that endpoint fast, predictable and affordable.

**Example:** The same chat.py works with any OpenAI-compatible URL, and this is exactly why you can benchmark and swap engines without touching application code. The production modules return to it: what must wrap this API before it is production.

**Transition:** Lab 2: you follow one request through the chain on your own machine, and check that your arithmetic matches what the server reports.

**Question:** "Can I restart the server in the lab?" Not in Lab 2: you only observe and measure, restarts are for Lab 3 and 4 and only through profiles, after telling your group.

**Deeper:** Recovery for a broken lab state is ./scripts/reset.sh lab-02; it keeps your own files and saves the replaced ones.
-->
