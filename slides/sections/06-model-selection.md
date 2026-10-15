---
layout: section
module: 6
heading: "Model selection"
layer: runtime
question: "Which model is the smallest one that reliably does my task, and how do I know?"
can:
  - "Turn a task and its constraints into a shortlist, cheap checks first"
  - "Read a license per repository and per revision and name its consequence"
  - "Reject a larger model with arithmetic or a measurement, not a feeling"
---

---
layout: statement
---

# Choose the smallest model that reliably does the task.

<p class="lead">Smallest: counted in VRAM, latency, GPU hours and operational risk. Reliably: counted on your task, at your precision, under your load.</p>

<!--
**Key:** The rule has two halves that pull in opposite directions, and both are measured: "smallest" in what you pay, "reliably" on your own task at the precision you will serve and the load you expect.

**Example:** Ask the room for one task they run today and a model they would pick for it; Lab 1 asks which smaller model you considered and why you rejected it.

**Transition:** A rule needs a procedure, and the procedure is ordered so that cheap checks come first.

**Question:** "Why not take the biggest model that fits?" It costs latency, GPU hours and risk on every request, so the bigger model has to earn its place on your eval, not on a chart.

**Deeper:** Put one candidate on the shortlist that is smaller than you expect to need; it shows how much capability the task really takes.
-->

---
layout: default
heading: "The workflow: cheap checks first"
---

<Flow :items='[{ "label": "TASK + EVAL", "sub": "what must it do" }, { "label": "SHORTLIST", "sub": "three to five" }, { "label": "License", "sub": "may I use it" }, { "label": "FIT", "sub": "weights + KV" }, { "label": "MEASURE", "sub": "eval, latency" }, { "label": "DECIDE", "sub": "write it down" }]' />

<Takeaway>

A license veto costs ten minutes. A measurement costs GPU time. A wrong decision costs a deployment.

</Takeaway>

<!--
**Key:** The six steps are ordered by cost: a license or architecture veto removes a candidate in minutes, whereas a measurement needs a running server and a wrong decision needs a redeployment.

**Example:** Walk one invented candidate through: the architecture is not in the engine at the pinned version, so it is dropped before anyone downloads 60 GB. Task and eval come first because without a pass criterion nothing downstream can decide.

**Transition:** First the shortlist: which families are there, and how do we compare them without declaring a winner?

**Question:** "Where do the benchmarks go?" Into step two, the shortlist; never into step six.

**Deeper:** The workflow is a procedure on purpose: a catalog of models is out of date within weeks, a procedure is not.
-->

---
layout: default
heading: "Model families: compare facts, not rank"
---

| Family | Examples in the research notes |
| --- | --- |
| Qwen | Qwen3, 3.5, 3.6, 3.8; dense and MoE; Coder, VL |
| Llama | 3.1 8B, 3.3 70B, 4 Scout and Maverick; Muse Glimmer 30B |
| Gemma | Gemma 4: E2B, E4B, 12B, 26B-A4B, 31B |
| Mistral | Ministral 3, Small 3.2 and 4, Medium 3.5, Large 3, Devstral |
| DeepSeek | V3, R1, V4: large MoE only |
| Kimi | K2.x, K3: 1 T to 2.8 T MoE |

<Warning title="As researched for this delivery">

Every model fact in this module moves fast. Re-check before use.

</Warning>

<!--
**Key:** Families differ in size range and architecture, and those are comparable facts; "which family is best" is not a question we try to answer. Licenses get their own check later.

**Example:** Read one row across: Gemma 4 comes in sizes from E2B to 31B, while DeepSeek V4 exists only as large mixture-of-experts checkpoints that do not fit one 96 GB card in full precision. Say once that every model fact here is as researched for this delivery, and that the open-model landscape changes within weeks.

**Transition:** Within a family, the question is not size alone but what kind of model it is.

**Question:** "Where are gpt-oss, Granite and EuroLLM?" The notes also cover gpt-oss, Granite, Nemotron, GLM, EuroLLM and Apertus; the table keeps to the curriculum's families.

**Deeper:** The pinned workshop models are all Qwen3: one family gives the cheapest size comparison.
-->

---
layout: default
heading: "Kind of task, kind of model"
---

<div class="ki-grid ki-cols-2">
<div class="ki-card">

### General
Chat, summaries, extraction. Pass your eval with the smallest one.

</div>
<div class="ki-card">

### Reasoning
Thinking per request, paid in output tokens. Qwen3 on, Gemma 4 off.

</div>
<div class="ki-card">

### Coding
Coder variants exist. Test on your repository, with tests that run.

</div>
<div class="ki-card">

### Multilingual
Language lists are vendor claims. Test German items of your own.

</div>
</div>

<!--
**Key:** The task decides which of these axes matters, and for each there is one trap: reasoning evaluated in a different mode than deployed, multilingual taken from a list, coding judged by reading, and "general" assumed to include all three.

**Example:** "Supports 100+ languages" does not say "good German": test formal register, compound words, umlauts and German-English mixes, and count how many tokens a real German document takes on this tokenizer. Dedicated coder models need their own tool-call parser; for some models no language list was found in the research notes.

**Transition:** Two capabilities decide whether a model can sit inside an application: tool calls and structured output.

**Question:** "Is a reasoning model always better?" No: for a classifier thinking pays its tokens on every request, and only your own items show what it buys.

**Deeper:** Every test here is yours, not the vendor's.
-->

---
layout: two-col
heading: "Tool use and structured output"
---

### Tool calling

The model writes calls in the format it was trained on. The engine needs a **parser** for that format and two flags:

- `--enable-auto-tool-choice`
- `--tool-call-parser`

::right::

### Structured output

Constrained decoding enforces **syntax**, not meaning. Name the fields in the prompt too.

<Warning>

One user request can become several model calls. Capacity planning counts them.

</Warning>

<!--
**Key:** A model is only usable for tools if three things match: the format it was trained on, the parser the engine ships for it, and your own multi-turn test; and structured output guarantees valid JSON, not correct fields.

**Example:** Parser names come from the vLLM documentation, not from the model card: cards go stale, and several Qwen3 cards still print a reasoning flag that no longer exists. The tool-call reliability of the small Qwen3-1.7B is unverified in the repository, so test it.

**Transition:** Next, the numbers behind a model's name.

**Question:** "Does a schema make the answer correct?" No: it makes the output parseable; the content still has to be tested.

**Deeper:** The tools and agents module shows how one user request multiplies into several model calls and their token ledger.
-->

---
layout: two-col
heading: "Size and context: read the numbers behind the name"
---

### Size

- **Stored** parameters set the VRAM.
- **Active** parameters set compute per token.
- Names round: Qwen3-1.7B is 1.7 B in `config/models.yaml`, 2.03 B in its checkpoint metadata.

::right::

### Context

- **You need** the longest prompt plus the longest output plus template overhead.
- Workshop servers: `max-model-len: 32768`.

<Warning>

"Supports 262k" is not "answers correctly at 262k".

</Warning>

<!--
**Key:** Two criteria that look like facts on a model card are really inputs to a calculation: the size you size from is the stored count and not the name, and the context you need is the longest prompt plus the longest output plus template overhead, not the maximum.

**Example:** Qwen3-1.7B is listed with 1.7 billion parameters in our configuration while its checkpoint metadata counts 2.03 billion; the sizing tool prints a note when disk size and parameters times bytes differ by more than five percent. Scenario C needs 16,000 to 32,000 tokens of repository context per request.

**Transition:** Whatever fits technically still has to be legal to use, so licenses.

**Question:** "Why not serve the maximum context?" It reserves memory and reduces concurrency; the arithmetic is in the GPU sizing module.

**Deeper:** Static YaRN scaling to 131,072 tokens can hurt short-text quality on Qwen3-8B, according to its card.
-->

---
layout: default
heading: "Open weights are not open source"
---

<div class="ki-grid ki-cols-2">
<div class="ki-card">

### Open weights
The parameters are published, often under a permissive or custom license. Training-data information and training code need not be.

</div>
<div class="ki-card">

### Open source AI
The OSI definition 1.0 needs all three, under OSI-approved terms: **data information**, **complete code**, **parameters**.

</div>
</div>

<Takeaway>

This workshop says "open-weight" for every model it uses.

</Takeaway>

<!--
**Key:** "Open" is two different claims: open weights is a statement about what you may download and run, open source AI in the OSI sense is a statement about whether the whole system can be reproduced and audited, and almost no model we use meets the second.

**Example:** Qwen, Gemma, Mistral, DeepSeek, gpt-oss and Llama are at best open weights even under Apache-2.0 or MIT, by the definition's wording; this was not audited model by model. You control the artifact, not its origin.

**Transition:** Within open weights the license terms still differ a lot, and they change.

**Question:** "Does the AI Act exemption mean we may use it freely?" That exemption concerns the provider's obligations, not whether you may run a model; engineering input, not legal advice.

**Deeper:** Running or LoRA-fine-tuning a downloaded model for a workshop does not make you a provider of it.
-->

---
layout: default
heading: "The license belongs to a repository, not a family"
---

| Family | Earlier | Now, as researched |
| --- | --- | --- |
| Qwen | Qwen3, 3.5, 3.6, 3.8-27B: Apache-2.0 | 3.8-2.4T-A95B: Max License; Flash-Next: Community License 1.0 |
| Gemma | older repositories: `gemma` license tag | Gemma 4: Apache-2.0 |
| Meta | Llama 3.x and 4: community licenses | Muse Glimmer 30B: Apache-2.0 plus usage policy |
| Mistral | most models: Apache-2.0 | Medium 3.5, Devstral 2: Modified MIT, US$20M monthly revenue ceiling |
| DeepSeek | V3: license agreement with use-based terms | V3-0324, R1, V4: MIT |
| Kimi | K2.x: Modified MIT | K3: stricter custom license |

<Takeaway>

No size pattern: Mistral Large 3 (675 B) is Apache-2.0, Medium 3.5 (128 B) is not.

</Takeaway>

<!--
**Key:** Adjacent models of one family can carry different licenses, and a license read in a blog post, on a slide like this one, or on an earlier model can be wrong for the checkpoint you pin.

**Example:** "Qwen is Apache" was true for Qwen3 and is not true for the two newest large Qwen3.8 repositories; the same holds for Kimi K3 against K2.x. The rule is procedural: read the LICENSE file of the repository at the commit you pin, on the day you pin it, and again when the pin changes.

**Transition:** What exactly to look for in that file is the next slide.

**Question:** "Can I trust the license tag on the hub?" Compare three places, because they can differ: the tag, the LICENSE file at that revision, and any separate policy file.

**Deeper:** Not legal advice; for anything beyond internal evaluation, ask counsel.
-->

---
layout: default
heading: "Thresholds measure different things"
---

| License | Condition | Measured on |
| --- | --- | --- |
| Llama 4 | above 700 M monthly active users: license request | licensee and affiliates |
| Mistral Medium 3.5, Devstral 2 | monthly revenue above US$20 M: no rights | your company or your employer |
| Kimi K2.x | display the model name above 100 M users or US$20 M monthly revenue | the commercial product |
| Qwen3.8-Flash-Next | a Model-as-a-Service or AI Work Assistant business needs a separate license | licensee and affiliates; internal use excepted |

<p class="muted small">Ask each time: whose users, whose revenue, which period, is internal use excepted? One row per model: Publisher · Model · Revision · License · Commercial implications · Source.</p>

<!--
**Key:** "Commercial use allowed" hides conditions, and each condition counts something different on a different entity, so the checklist row has a Revision column and a Source column that points at the license file at that revision, not at the card.

**Example:** The Mistral clause tests the whole employer's monthly revenue, so a participant whose employer is above it cannot use those two models without a commercial license; the Llama 4 acceptable-use policy also has an EU sentence for multimodal models. For Lab 1 the license table asks for the license and one consequence per model, never just "open".

**Transition:** After the legal veto, the technical one: precision and engine.

**Question:** "Which row applies to us?" That is exactly what the one-sentence consequence is for; write what you could not determine.

**Deeper:** All pinned workshop models are Apache-2.0; the interesting license rows are the other families.
-->

---
layout: two-col
heading: "Quantization and engine compatibility"
---

### Quantization

- Which formats does the publisher ship?
- Which kernels does the engine have for your GPU?
- Re-run your eval at that precision.

FP8 is not half: 16.38 GB becomes 9.44 GB for Qwen3-8B.

::right::

### Engine compatibility

- Is the architecture in the engine's list at the pinned version?
- Which flags and chat template does it need?
- `trust_remote_code`: workshop profiles refuse it.

<Warning>

"It is on Hugging Face" does not mean "it runs".

</Warning>

<!--
**Key:** A model is only a candidate if the engine at your pinned version can run it on your GPU generation, and a lower precision is a candidate only if its quality holds on your eval.

**Example:** Cards go stale: several Qwen3 cards still print removed flags, so check every flag against the pinned image's help text. Three candidates are poor "just run it" choices in the research notes: one ships no chat template, one needs remote code and passes reasoning content back, and one needs a plugin file for its reasoning parser. vLLM's hardware table has no Blackwell column, so "not listed" does not mean "unsupported": run it.

**Transition:** The last technical veto is memory.

**Question:** "Can I load a third-party 4-bit build?" Unverified for this GPU in our notes; treat it as a smoke-test item.

**Deeper:** The quantization module measures the quality cost with a spot check.
-->

---
layout: default
heading: "Memory fit: reject early with arithmetic"
---

| Weights alone, against one 96 GB card | Examples in the research notes |
| --- | --- |
| Ample room | Qwen3.5-9B 19.31 GB, Gemma 4 12B 23.92 GB, Granite 4.2 8B 17.58 GB |
| Tight KV budget | Gemma 4 31B 62.55 GB, Muse Glimmer 30B 59.55 GB, Qwen3.6-27B 55.56 GB |
| Exceed the card | Llama 3.3 70B BF16 141.1 GB, Llama 4 Scout 217.3 GB, DeepSeek V4 166.9 GB and up |

<span class="muted small">Derived from the weight files in the research notes: no KV cache, no overhead.</span>

```bash
python3 scripts/sizing.py --model primary --precision bf16 --context 8192 --concurrency 16
```

<!--
**Key:** File sizes already sort candidates into three groups before any KV cache is counted; the sizing script then adds the cache for your context and concurrency. Use it to reject early, and confirm against the server's own KV line later.

**Example:** The sizes are weight files without cache or overhead: group one still needs a context and concurrency check, group three needs more than one GPU or a smaller precision. Hybrid and sliding-window models shrink the cache per token; sizing.py assumes full attention and can be wrong for them.

**Transition:** What the arithmetic cannot say is whether the model is any good at your task.

**Question:** "Why not run group three in FP8?" Some would fit, some not; that is a finding with a price, which Lab 1 asks you to write down.

**Deeper:** GB are 10^9 bytes, GiB are 2^30; the vLLM log uses GiB.
-->

---
layout: default
heading: "Leaderboards: shortlist with them, decide without them"
---

- They measure **other tasks**: your data, language and output format are not in them.
- They **average**: a good mean can hide the slice that matters.
- **Settings differ**: thinking, sampling, precision, and the checkpoint you serve is rarely the one scored.
- A score has no latency, memory, license or operability.

<Takeaway>

Use leaderboards to shortlist. Decide on your own eval.

</Takeaway>

<!--
**Key:** A public score answers a question nobody asked you: it measures someone else's task, averaged, under settings you will not use, with no cost attached.

**Example:** Ask the room for a benchmark they have seen quoted and which slice they care about; for scenario A that is German formal text, for B the critical class, for C tool calls and long context. Test sets can also leak into training data and you cannot check. Models also age: new releases and renamed models arrive within weeks.

**Transition:** What replaces the leaderboard is small and cheap: thirty real items.

**Question:** "Isn't an own eval too much work?" About three and a half hours for one person, and it is the only evidence that survives a model change.

**Deeper:** Never tune a prompt on your eval items without holding some out.
-->

---
layout: two-col
heading: "A 30-item eval is a few hours of work"
---

| Step | Effort for one person |
| --- | --- |
| Task in one paragraph, pass criterion | 30 min |
| 30 real items, tagged by slice | 60 min |
| A check per item that a script can run | 45 min |
| A small runner, fixed sampling | 30 min |
| Run every candidate, read every failure | 30 min |
| Freeze and tag | 15 min |

::right::

<Observation title="Keep it comparable">

Same prompt, sampling and thinking mode for every candidate. Store the reply, tokens, latency and revision with each result.

</Observation>

<!--
**Key:** An eval that you can finish in one working session beats a perfect one you never run: 30 real items, a pass criterion set in advance, checks a script can run, and fixed settings for every candidate.

**Example:** The mix is 20 typical items, 6 hard or odd ones, and 4 that must be refused or answered with "not in the documents"; German items come from real German text. One item is a single JSON line with an id, a slice, a prompt, a check and a note.

**Transition:** What can 30 items tell you, and what not?

**Question:** "Can we use quality_probe.py as our eval?" It is a pattern for comparing two deployments of one model on synthetic English items; it has no German, no tools, no long context.

**Deeper:** Read at least ten failures yourself: a pass rate says how often, not why.
-->

---
layout: default
heading: "What 30 items can and cannot tell you"
---

| Correct | Rate | 95 % Wilson interval (computed) |
| --- | --- | --- |
| 30 of 30 | 1.00 | 0.886 to 1.000 |
| 27 of 30 | 0.90 | 0.744 to 0.965 |
| 24 of 30 | 0.80 | 0.627 to 0.905 |

<Takeaway>

Thirty items find candidates that fail. They do not rank two good models.

</Takeaway>

<!--
**Key:** With thirty items even a perfect score has a lower bound near 0.89, so the eval finds failing candidates and large differences, and nothing finer.

**Example:** 27 of 30 is 0.90, but the interval runs from 0.74 to 0.97; two models at 27 and 24 out of 30 overlap. Compare candidates on the same items and look at the disagreements: where A is right and B is wrong, and the reverse.

**Transition:** So how do we write the whole decision down? One matrix and one record.

**Question:** "How do we check the 2 percent quality bound in the SLO?" Not with 30 items: it needs hundreds, and then it still resolves only a few points.

**Deeper:** To split smaller differences, add items on which the candidates disagree; adding easy items adds nothing.
-->

---
layout: default
heading: "The selection matrix: hard requirements, then trade-offs"
---

| Candidate | License, engine, fit | Pass rate on my eval | TTFT, ITL at my load | Gives up |
| --- | --- | --- | --- | --- |
| Smaller than expected | each: pass or drop | with interval | measured | written down |
| Candidate A | each: pass or drop | with interval | measured | written down |

<div class="ki-grid ki-cols-2">
<div class="ki-card">

**Hard requirements** remove a candidate without any measurement.

</div>
<div class="ki-card">

**Trade-offs** are weighed on measured values.

</div>
</div>

<!--
**Key:** The matrix separates what vetoes from what trades off: license, engine and fit remove a candidate outright, while quality and latency are weighed on measurements, and the last column is the sentence a choice without a trade-off is missing.

**Example:** For the winner and for the smaller model you rejected, write the decision record: repository and full 40-character revision, precision of weights and cache, engine and flags, context served, thinking on or off, evidence, and what makes you decide again.

**Transition:** Now the four scenarios you will fill this in for.

**Question:** "What if two candidates tie?" Take the smaller one and note what would change the decision: a new release in the family, a license change, traffic that grows.

**Deeper:** The record's last line matters: the open-model ecosystem moves, so every choice needs its re-decision trigger.
-->

---
layout: default
heading: "Lab 1 scenarios: introduced, not solved"
---

| | Scenario | Numbers to design for | First question |
| --- | --- | --- | --- |
| A | German assistant on company documents | 300 employees, 20 concurrent users, 10 s, 3,000 tokens of retrieved context | Which context must the server allow? |
| B | Ticket classification and extraction | 40,000 per day, peaks of 5 per second, 300 in and 60 out tokens, 95 % within 2 s | Does it need thinking at all? |
| C | Coding assistant | 100 developers, 16,000 to 32,000 tokens of context, first token within 1 s | Does the first token survive the prefill? |
| D | Monthly document pipeline | 2 million documents, 3,000 in and 300 out tokens, 72 hours | Which throughput, at what cost per document? |

<!--
**Key:** Each scenario is a requirement that must be turned into numbers before any model is named, and each one pulls on a different trade-off: context against concurrency, thinking against latency, prefill against first token, throughput against cost.

**Example:** Do not solve any of them. Point at A: 20 users times 3,000 tokens of retrieved context already says something about the KV cache; at B: five per second at 300 input tokens is the load the model must absorb at the peak.

**Transition:** Lab 1 follows next: each sub-group takes one scenario first and swaps afterwards.

**Question:** "Do I need a GPU to do the lab?" No, sizing.py runs anywhere with Python.

**Deeper:** Reduced scope is a legitimate outcome: two scenarios done well beat four thin ones.
-->
