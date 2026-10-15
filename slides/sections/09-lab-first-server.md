---
layout: section
module: 9
heading: "Lab 2: first inference server"
layer: runtime
question: "Can you follow one request through the whole chain, and does your arithmetic match what the server reports?"
can:
  - "Follow one request through request, model, GPU, tokens and metrics"
  - "Compare your KV estimate with what the server reports"
  - "Record observations in your own words in the report"
---

---
layout: default
heading: "Goal: follow one request through the chain"
---

<Flow :items='[{ "label": "REQUEST", "sub": "prompt tokens" }, { "label": "MODEL", "sub": "weights, KV cache", "layer": "runtime" }, { "label": "GPU", "sub": "bandwidth, compute", "layer": "runtime" }, { "label": "TOKENS", "sub": "prefill, then decode" }, { "label": "METRICS", "sub": "TTFT, tokens per second" }]' />

<div class="ki-grid ki-cols-2">
<div>

| Link | Where you see it |
| --- | --- |
| REQUEST | prompt tokens in the `usage` block of the reply |
| MODEL | weights memory and KV capacity: `wsctl info`, the log |
| GPU | `nvidia-smi` and `./scripts/gpu-status.sh` |
| TOKENS | the streamed text, the completion tokens |
| METRICS | the last line of `chat.py` |

</div>
<div>

- Work **alone**, on your group's shared server.
- You only **observe and measure**. Do not restart anything.
- You produce the *Hardware* section of `workshop-artifacts/inference-report.md` and three observations in your own words.

</div>
</div>

<!--
**Key:** The lab is not "the API returns text"; it follows one request from the prompt to the numbers and checks that the arithmetic from the sizing module predicts what the server reports.

**Example:** Read the table aloud: tokens in the usage block, the GPU in nvidia-smi, TTFT and speed on the last line of chat.py, memory and cache in the log.

**Transition:** The steps are on the next two slides.

**Question:** "Can I restart if the server hangs?" No, it is shared; check sudo wsctl status and wait: a restart with warm caches takes about 40 seconds, the first start of a profile up to about two and a half minutes. Restarts come in Labs 3 and 4.

**Deeper:** The lab is done when the Hardware section of the report is filled and the KV estimate is checked against the log.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 1 to 5: look, ask, stream, watch"
task: 02-first-inference-server
artifact: workshop-artifacts/inference-report.md
---

Do the steps in order. The full text is in the task file.

<Terminal title="your group's GPU host">

```bash
# 1-2  the GPU and the service
nvidia-smi
sudo wsctl status
sudo wsctl info | python3 -m json.tool | head -40
# 3  the API (the completion is in the demo and in the task file)
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models | python3 -m json.tool
# 4  stream, then read the last line
python3 apps/inference-client/chat.py "Explain batching in one paragraph."
# 5  second terminal: watch while a long request runs in the first
./scripts/gpu-status.sh --watch
python3 apps/inference-client/chat.py --max-tokens 800 "Write a detailed essay about GPUs."
```

</Terminal>

<!--
**Key:** Five steps carry the first half of the lab, and each answers one link of the chain; go through them in order before anyone starts changing things.

**Example:** Circulate and check three things: that people write down GPU name, memory in use and processes before they move on; that the second terminal runs the watcher while the long request runs in the first; that nobody starts a second server.

**Transition:** The second half is where they learn something: change one thing at a time.

**Question:** "Where do I find the full curl for the completion?" In task step 3 and in the demo slide; the task file also has the further-exploration variants, such as streaming with curl and the structured-output script.

**Deeper:** If sudo wsctl info prints nothing useful, the server is stopped or still starting; send people to wsctl status and the troubleshooting table.
-->

---
layout: lab
class: ki-code-sm
heading: "Steps 6 to 9: change, check, write"
task: 02-first-inference-server
artifact: workshop-artifacts/inference-report.md
---

**6** Change one thing at a time: prompt length (paste a long text), `--max-tokens`, `--temperature 1.0`. Record TTFT and tokens per second.

<Prediction title="Before you change anything">

Which change will move TTFT, and which will move tokens per second? Write your guess down.

</Prediction>

<Terminal title="your group's GPU host">

```bash
# 7  find the KV cache line
sudo wsctl logs 40
# 8  check your arithmetic against it
python3 scripts/sizing.py --model primary --precision bf16 --context 32768 --concurrency 1
```

</Terminal>

**9** Fill *Hardware* in the report and add three observations.

<!--
**Key:** One variable at a time is the habit that the measuring modules build on, and a guess written down first is what turns a click-through into an experiment.

**Example:** Expected, from the task file: TTFT grows with prompt length because prefill has more tokens; tokens per second per request hardly moves with prompt length; temperature changes no speed, because the same weights are read either way.

**Transition:** Let us see what a good result looks like, so people can tell when they are done.

**Question:** "My tokens per second dropped with a very long prompt, is something wrong?" No: each decode step also reads the longer KV cache, which is one of the changes the later modules test.

**Deeper:** The report section asks for GPU, VRAM and bandwidth, weights in GiB, KV capacity and how it was computed, and the maximum concurrency at the context you need.
-->

---
layout: default
heading: "What a good result looks like"
---

<div class="ki-grid ki-cols-4">
<MetricCard label="Weights" source="measured:benchmark/results/reference/baseline/kv-formula-check.json" metric="model_memory_gib" unit="GiB" digits="2" />
<MetricCard label="KV capacity" source="measured:benchmark/results/reference/baseline/kv-formula-check.json" metric="reported_tokens" unit="tokens" />
<MetricCard label="TTFT p50" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="ttft_ms.p50" unit="ms" digits="1" />
<MetricCard label="Tokens/s per request" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="output_tps" unit="tok/s" digits="1" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

- Reference run for **comparison**, not the answer.
- TTFT grows with prompt length; tokens per second does not, except at very long context.
- The formula check: your `sizing.py` bytes per token, applied to the server's available KV memory, give the log's token count within **2 %**.

<Warning title="Off by 2x or 4x?">

2x: you forgot that the cache stores keys **and** values. 4x: you used the 32 query heads instead of the 8 KV heads.

</Warning>

<!--
**Key:** The reference numbers tell people whether their machine behaves like the trainer's, and the validation rule tells them whether their arithmetic is right: within two percent of the server's KV token count.

**Example:** Off by a factor of two: they forgot that the cache stores keys and values. By four: they used the 32 query heads of Qwen3-8B instead of its 8 KV heads. A single request also shows 100 percent GPU-Util: write it down, then explain it.

**Transition:** The last slide is where to get help, and the questions for the debrief.

**Question:** "Why does my KV capacity differ from 423,328?" The available cache memory varies by about one percent between starts, so capacity moves a little; the formula stays.

**Deeper:** These are read-only reference results; reset.sh copies them to your machine, so a failed run does not block the report.
-->

---
layout: two-col
heading: "If you get stuck, and the debrief"
---

| Symptom | Do this |
| --- | --- |
| `401` from the API | log in again: the key is set at login |
| No answer for a long time | `sudo wsctl status`; a restart with warm caches takes about 40 seconds, the first start of a profile up to about two and a half minutes; start nothing else |
| More memory in use than the model needs | correct: vLLM reserves its budget at start-up |
| You broke something | `./scripts/reset.sh lab-02` |

More: `docs/TROUBLESHOOTING.md`, terms in `docs/GLOSSARY.md`, or ask the trainer.

::right::

### Debrief

- **Draw** the chain and mark where TTFT and ITL come from.
- **Compare** your KV estimate with the log: which input was off?
- **Explain** why GPU-Util read 100 % for one request.
- **Classify** what moved TTFT and what moved tokens per second: prefill or decode?

<!--
**Key:** The debrief checks the two outcomes of the lab: they can draw the chain and label prefill and decode, and they can tell a busy GPU from an efficiently used one.

**Example:** Pick two participants to draw the chain on the shared screen; ask a third which of their observations was a surprise. The GPU-Util question is the bridge: the gauge says a kernel was running, while the token rate says how well the card was used.

**Transition:** Next the checkpoint: predicting bottlenecks before we measure anything.

**Question:** "What if two people streamed at once?" Good guess to keep: the shared server will batch them, and Lab 3 measures what that does to speed and latency.

**Deeper:** Copy workshop-artifacts to your laptop after the lab; the machines are deleted after the workshop.
-->
