---
layout: section
module: 18
heading: "Trainer demos: speculative decoding and OOM"
layer: runtime
question: "Which techniques depend on the workload, and which results do we not have?"
can:
  - "Explain how speculative decoding works and when it pays"
  - "Read the failure of an intentionally impossible profile"
  - "Mark which techniques have measured results here and which do not"
---

---
layout: default
heading: "Speculative decoding: five ways to guess"
---

<Flow :items='[{ "label": "Guess", "sub": "a cheap drafter proposes several tokens", "layer": "runtime" }, { "label": "Check", "sub": "one step of the target model", "layer": "runtime" }, { "label": "Keep", "sub": "the matching tokens, plus one more" }]' />

| Method | How it drafts | What it costs | When it pays | vLLM v0.31.0 |
| --- | --- | --- | --- | --- |
| Draft model | a small second model proposes tokens | a second model in memory | general text the small model predicts well | documented: needs a separate model |
| N-gram, prompt lookup | matches the last tokens against earlier text | nothing: no model, no training | output that copies the input (RAG, code edits) | documented; the demo uses it |
| Medusa-style heads | extra heads on the target guess later positions | heads trained for that model | when such heads exist for your model | not on the v0.31.0 overview page |
| EAGLE-style drafting | a small drafter reads the target's hidden states | a drafter trained for that target | general use | documented: general-purpose method |
| Multi-token prediction | the model was trained to predict several tokens ahead | only models trained that way | when the model has it natively | documented: best with native support |

<!--
**Key:** Every method guesses first and checks in one pass of the target model; who guesses, and what that costs, decides when each pays. All trade spare compute for fewer weight reads per token: they speed up a stream, not the first token.

**Example:** From cheapest to costliest: n-gram needs a copy-heavy output, a draft model memory and its own steps, Medusa-style heads and EAGLE-style drafters training for the target, multi-token prediction a model trained for it. Support is stated only where the v0.31.0 documentation confirms it.

**Transition:** Only n-gram, the cheapest, is tested here: first predict, then measure.

**Question:** "Which should we use?" The one whose cost you can pay on your workload; the vLLM documentation says gains depend on model, traffic, hardware and sampling.

**Deeper:** Inference Engineering, section 5.2; the vLLM overview is in RESEARCH 3.10, which does not describe Medusa.
-->

---
layout: experiment
heading: "Demo 1: speculative decoding, predicted"
step: prediction
experiment: demos
---

<div class="ki-stack">

<ExperimentCard
  name="demos"
  variable="n-gram speculation: the engine guesses the next four tokens by matching earlier text, one step checks them"
  :profiles='["baseline", "spec-ngram"]'
  workload="a copy task (1,000 tokens in) and, as the control, open questions (about 20 tokens in); 1 and 16 clients"
  :metrics='["tokens/s per request", "ITL", "aggregate tokens/s"]'
/>

<Prediction>

Which workload gains, which does not, and what changes at 16 clients, when every step already carries 16 tokens? Commit to gain, no change or loss in four cells.

</Prediction>

</div>

<!--
**Key:** Speculative decoding is the clearest technique that depends on the workload, so we predict before we look: guessing the next tokens from the prompt can only pay when the output repeats the input.

**Example:** The profile spec-ngram guesses four tokens by finding the last two to five tokens earlier in the same prompt and output; no second model is loaded. The copy task asks the model to repeat a passage exactly; the control asks open questions whose answers are new text. Collect a guess per cell; the usual wrong one is that gains vanish at 16 clients.

**Transition:** The measurements.

**Question:** "Why 16 clients?" To test the intuition that a busy GPU has no spare capacity for extra work.

**Deeper:** Live: sudo wsctl start spec-ngram restarts the server for the pod.
-->

---
layout: experiment
heading: "Measured: copy task and control"
step: measurement
experiment: demos
---

<div class="ki-grid ki-cols-2 spec-tables">
<div>

### Copy the text exactly

<ResultTable
  source="measured:benchmark/results/reference/demos"
  :match='["/spec-baseline-c001/c001.json", "/spec-baseline-c016/c016.json", "/spec-spec-ngram-c001/c001.json", "/spec-spec-ngram-c016/c016.json"]'
  :labels='["baseline, 1 client", "baseline, 16 clients", "spec-ngram, 1 client", "spec-ngram, 16 clients"]'
  label-header="Profile and load"
  :columns='["output_tps_per_request.p50", "itl_ms.p50", "aggregate_tps"]'
  :headers='["Tokens/s per request", "ITL p50 (ms)", "Aggregate tokens/s"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>
<div>

### Open questions, the control

<ResultTable
  source="measured:benchmark/results/reference/demos"
  :match='["/spec-baseline-open-questions-c001/c001.json", "/spec-baseline-open-questions-c016/c016.json", "/spec-spec-ngram-open-questions-c001/c001.json", "/spec-spec-ngram-open-questions-c016/c016.json"]'
  :labels='["baseline, 1 client", "baseline, 16 clients", "spec-ngram, 1 client", "spec-ngram, 16 clients"]'
  label-header="Profile and load"
  :columns='["output_tps_per_request.p50", "itl_ms.p50", "aggregate_tps"]'
  :headers='["Tokens/s per request", "ITL p50 (ms)", "Aggregate tokens/s"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>
</div>

<p class="small muted">TTFT is left out on purpose: the copy prompts were answered mostly from the prefix cache.</p>

<style>
.spec-tables :deep(td.first) {
  white-space: nowrap;
}
</style>

<!--
**Key:** The same technique gains on one workload and loses on another, and the loss shows at high load. Each row is one run: read the pairs, not the digits.

**Example:** Copy task: speed per request roughly doubles at one client and at 16. Open questions: no change at one client, and at 16 the aggregate falls by about a seventh. Our hypothesis that speculation stops helping under load was wrong for the copy task: the GPU is still memory-bound, so checking extra tokens is cheap. TTFT is left out: the prefix cache answered most copy-prompt tokens.

**Transition:** Why does the loss appear, and why did our first control fail?

**Question:** "Is the copy task fair?" It is the best case, chosen on purpose; the control shows the other end.

**Deeper:** One session, 16 to 32 requests per row.
-->

---
layout: experiment
heading: "Why it pays on copies, and costs on new text"
step: explanation
experiment: demos
---

<div class="ki-grid ki-cols-2">
<MetricCard label="Draft tokens checked (all runs)" source="measured:benchmark/results/reference/demos/spec-spec-ngram-metrics.json" metric="vllm:spec_decode_num_draft_tokens_total" />
<MetricCard label="Draft tokens accepted (all runs)" source="measured:benchmark/results/reference/demos/spec-spec-ngram-metrics.json" metric="vllm:spec_decode_num_accepted_tokens_total" />
</div>

<Provenance source="measured:benchmark/results/reference/demos/spec-spec-ngram-metrics.json" />

- A step carries several tokens because the check shares the weight read.
- On new text more guesses fail: wasted work, and at 16 clients it is no longer free.
- The first control, the harness's own synthetic prompts, also won: the model copies them.

<Consequence>

A workload decision, not a switch. If the control behaves like the treatment, suspect the benchmark.

</Consequence>

<!--
**Key:** Speculation changes the work per step, not the bytes read per step: a step that verifies several guessed tokens costs a little more and can emit several, but only matching guesses count.

**Example:** The two counters cover all speculative runs, copy and open together, so they are no acceptance rate per workload; the RESULTS file gives 43.5 percent overall. On the copy task the step rose from 11.5 to 12.8 ms at one client. The lesson in method: the first run used the harness's synthetic prompts as the unrelated workload and speculation won there too, because the model copies them; benchmark/workloads/open-questions.jsonl is the control we use.

**Transition:** From a technique that can disappoint to a configuration that cannot work.

**Question:** "Do draft models change this?" They have different costs; we did not measure them.

**Deeper:** N-gram is the cheapest variant.
-->

---
layout: default
class: ki-code-sm
heading: "Demo 2: two starts that must fail"
---

<div class="ki-grid ki-cols-2 fails">
<div>

<Terminal title="oom-demo: 40,960 tokens, 4 GiB KV pool">

```text
$ sudo wsctl start oom-demo
RuntimeError: Engine core initialization failed.
wsctl: startup failed (full log: /var/log/…)
wsctl: rolling back to the previous profile…
ready in 39 s. vLLM 0.31.0, profile 'baseline'.
```

</Terminal>

40,960 × 147,456 B = 5.6 GiB needed, 4 GiB reserved.

</div>
<div>

<Terminal title="a context beyond the model's own limit">

```text
$ sudo wsctl start oom-demo \
    --set max-model-len=1048576
ValidationError: … User-specified
  max_model_len (1048576) is greater than
  the derived max_model_len (…=40960.0 …)
wsctl: rolling back to the previous profile…
```

</Terminal>

The model's own limit is checked before memory.

</div>
</div>

<Takeaway>

The cause is in `sudo wsctl logs 100`. The supervisor restored `baseline` by itself both times.

</Takeaway>

<style>
.fails {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}
.fails :deep(pre),
.fails :deep(code) {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>

<!--
**Key:** A configuration that cannot work should fail at start, say why and leave the group with a model; the two starts show two different checks.

**Example:** Type sudo wsctl start oom-demo while baseline serves, and tell the room the model is offline for about 40 seconds: every pod serves one group. Read the cause in the log: the 4 GiB pool is smaller than one request of the configured length needs. Then run the second command, beyond the model's own limit, and read which check fires first. Excerpts are shortened from the two oom-demo files in benchmark/results/reference/demos.

**Transition:** Next: demos that need more hardware, none of them measured here.

**Question:** "Why not just retry?" Each attempt takes the model away from the group; read the log.

**Deeper:** 5.6 GiB is 40,960 tokens times the 147,456 bytes per token from the sizing module.
-->

---
layout: default
heading: "If you have more hardware: three more demos"
---

<div class="optional-demos">

| Demo | Question | What the trainer prepares | Careful |
| --- | --- | --- | --- |
| Tensor parallelism | Does the all-reduce eat the gain over PCIe? | a two-GPU pod; `experiments/run-session.sh`, experiment `tensor-parallel`; read `nvidia-smi topo -m` first | no run has worked on hardware yet: expect to debug the start |
| vLLM against Ollama or llama.cpp | How do a serving engine and a local runner behave when ten users arrive? | the same workload against each engine: `--endpoint`, `--engine`, `--no-engine-extensions` | engine and precision change together (GGUF 8-bit against BF16); check each default concurrency |
| Mixture of experts | What does a model with many stored and few active parameters cost? | `Qwen/Qwen3-30B-A3B-FP8`: 30B stored, about 3B active per token; `infra/provision.md` | no profile in the repository; architecture and size change together |

</div>

<Warning title="None of the three has a measured result in this repository">

Any number shown is the trainer's own. Say so, and say what was held constant.

</Warning>

<style>
.optional-demos :deep(code) {
  white-space: nowrap;
}
</style>

<!--
**Key:** These three demos belong to the curriculum but nobody measured them, so they are offered, not presented: the trainer may prepare one and must mark its numbers as the trainer's own.

**Example:** Two GPUs: the runner restarts baseline, then tp2, then two servers, one per GPU, and saves the topology. Engines: point the same harness at the other server with --endpoint and label it with --engine; --no-engine-extensions stops it sending ignore_eos and min_tokens, which other engines do not know. Ollama's defaults for parallel requests differ from vLLM's batching (RESEARCH 3.13: check the current values).

**Transition:** Next: the measured rows behind the answers to the checkpoint predictions.

**Question:** "Can we claim vLLM beats Ollama?" Not from this repository: the comparison was never run here.

**Deeper:** The tensor-parallel design, its break-even arithmetic and why it has no result are in experiments/tensor-parallel/RESULTS.md.
-->

---
layout: default
heading: "The measured rows behind the answers"
---

<div class="evidence">

<ResultTable
  source="measured:benchmark/results/reference"
  :match='["concurrency/baseline-c001/c001.json", "concurrency/baseline-c064/c064.json", "context-length/baseline-in00256/c001.json", "context-length/baseline-in28672/c001.json", "prefix-cache/baseline-shared-c001/c001.json", "prefix-cache/no-prefix-cache-shared-c001/c001.json", "quantization/baseline-c001/c001.json", "quantization/fp8-c001/c001.json"]'
  :labels='["Users: 1 client", "Users: 64 clients", "Prompt: 256 tokens", "Prompt: 28,672 tokens", "Shared prefix: cache on", "Shared prefix: cache off", "Weights: BF16", "Weights: FP8"]'
  label-header="Change"
  :columns='["ttft_ms.p50", "itl_ms.p50", "output_tps_per_request.p50", "aggregate_tps"]'
  :headers='["TTFT p50 (ms)", "ITL p50 (ms)", "Tokens/s per request", "Aggregate tokens/s"]'
  :digits='{ "itl_ms.p50": 1 }'
/>

</div>

<!--
**Key:** Each pair shows one change and the metric it moved; the workloads differ between pairs, so compare within a pair, never across.

**Example:** Users: aggregate tokens/s grows twentyfold while the speed per user falls from 86 to 32. Prompt: TTFT grows faster than linearly with the prompt, and ITL creeps up because the step reads more KV. Prefix: TTFT drops with the cache on, decode speed is unchanged. Weights: ITL falls from 11.6 to 7.3 ms with FP8. The prefix and weights pairs are at one client; the load tests at higher concurrency are on earlier slides.

**Transition:** Now the predictions from the checkpoint, scored against these rows.

**Question:** "Where is the second GPU?" Missing, on purpose: it was never measured.

**Deeper:** Four sessions on the same card and engine version, one run per row; the line under the table names the provenance of the first file.
-->

---
layout: default
heading: "The predictions from the checkpoint, scored"
---

| Change | Limited by | What moved | Answer |
| --- | --- | --- | --- |
| More users | memory bandwidth, then the queue | aggregate tokens/s up, speed per user down, TTFT up | measured |
| Longer prompts | prefill compute; small KV pool: capacity | TTFT; waiting requests | measured |
| Longer outputs | decode steps, growing KV | end-to-end latency | reasoned |
| A smaller model | bytes read per step | ITL; quality is the hidden cost | reasoned |
| FP8 weights | memory bandwidth (weight bytes) | ITL; KV capacity only a little; quality risk | measured |
| A second GPU | interconnect (hypothesis) | untested | not measured |
| A shared prefix | prefill compute | TTFT | measured |

<p class="small muted">The last row was not in the checkpoint table. The measured rows are on the previous slide.</p>

<!--
**Key:** Close the loop on the predictions the groups wrote at the checkpoint: every row now has a limiting resource and a status, and the status is the honest part: measured, reasoned or untested.

**Example:** Open the tables collected at the checkpoint and mark each group's cells with the room. Usual surprises: throughput did not flatten up to 64 clients, so the SLO set the limit; GPU utilization read 100 percent everywhere; FP8 weights added little KV capacity on a 96 GB card; the small KV pool was faster per request. Longer outputs and the smaller model were reasoned, never run.

**Transition:** Five sentences to keep from the optimization modules.

**Question:** "Whose prediction counts as right?" The measurement decides; a wrong cell is a finding about our model.

**Deeper:** The extra row, a shared prefix, answers a question the checkpoint table did not ask.
-->

---
layout: default
heading: "Five sentences to be able to say after the optimization modules"
---

<div class="five">

1. **Batching** shares one weight read per step: throughput grows, each user slows a little.
2. **Overload** shows as queueing and TTFT, not as GPU utilization.
3. **Long prompts** cost compute and KV memory; a shared prefix is paid for once.
4. **FP8** weights buy decode speed, an FP8 KV cache buys capacity; both change outputs.
5. **Every change** has a price: name the metric, the workload and the bottleneck, and keep a control.

</div>

<style>
.five :deep(li) {
  font-size: 26px;
  line-height: 1.35;
  margin-bottom: 22px;
}
</style>

<!--
**Key:** If participants can say these five sentences, the optimization modules worked: each one pairs a mechanism with the metric that shows it and the price it carries.

**Example:** Ask five people to say one each in their own words and name where it came from: batching (Lab 3, continuous batching), queueing and the alert on waiting requests, KV memory and the shared prefix, quantization and the quality check, and the rule behind every experiment. Tie sentence 5 to Lab 4: the report that named a condition under which the change should not be used.

**Transition:** Next: the same server becomes a service.

**Question:** "Is the fourth sentence general?" For this card and this model: other GPUs, models and checkpoints may land differently, so measure.

**Deeper:** The five sentences are the checklist behind outcomes 12 to 14 and 18 of the curriculum.
-->

---
layout: default
heading: "Next: from one server to a service"
---

<div class="ki-stack">
<div>

**So far: one server.** One GPU, one model, one engine, measured.

<Flow :items='[{ "label": "Client", "layer": "application" }, { "label": "API", "layer": "runtime" }, { "label": "vLLM", "layer": "runtime" }, { "label": "GPU", "layer": "runtime" }]' />

</div>
<div>

**Next: a service.** What protects, multiplies and observes it.

<Flow :items='[{ "label": "Gateway", "sub": "who may call", "layer": "infrastructure" }, { "label": "Balancer", "sub": "health, queue", "layer": "infrastructure" }, { "label": "Replicas", "sub": "slow, full or dead", "layer": "runtime" }, { "label": "Observability", "sub": "how we know", "layer": "infrastructure" }]' />

</div>
</div>

<p class="muted">Your report keeps growing: Baseline and Experiments are filled in, the architecture comes next.</p>

<!--
**Key:** Everything so far was one replica on one GPU; the questions of the next modules start where that stops: who may call it, what happens when a replica is slow, full or dead, how we know, and how we change it safely.

**Example:** Point at the two rows: the first is what the groups have measured, the second adds a gateway, a balancer, several replicas and observability. The queueing and the KV gauges from the optimization modules become the alerts of the service, and the second-GPU question returns as replicas against tensor parallelism in the scaling module.

**Transition:** Next: the production architecture.

**Question:** "Do we need Kubernetes?" No: the picture is the same under systemd, Compose or Kubernetes; the production-architecture module starts there.

**Deeper:** The production-architecture module draws the full stack and walks the request path hop by hop.
-->
