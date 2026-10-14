---
layout: section
day: 1
heading: "Opening: why run models yourself"
time: "09:00"
minutes: 30
layer: all
question: "Why would an organisation run a model itself, and what does that control cost?"
---

---
layout: default
heading: "Your trainer"
---

<div class="ki-card ki-stack">

## Paweł Sawicki

<div class="ki-row">
<span class="ki-pill">Senior ML Engineer</span>
<span class="ki-pill">AI Engineer</span>
<span class="ki-pill">Software Architect</span>
<span class="ki-pill">Technical Trainer</span>
</div>

<span class="muted">Profile: https://www.nextacademy.io/de/trainers/pawel-sawicki</span>

</div>

<!--
**Key:** Keep this to thirty seconds: who is speaking, and that the three days are about engineering a system, not about downloading a model. **Example:** Say in one sentence why this workshop is about inference engineering rather than prompting, and point to the profile page for the rest. **Transition:** Before the toolbox, the question that decides whether anyone needs it: why run a model yourself at all? **Question:** "Will there be a recording or the slides afterwards?" Answer with whatever the organiser has agreed; your clone of the repository and the artifacts you copy off the machine stay with you. **Deeper:** If the group has not met, a one-line round (role, what you would run yourself) costs five minutes at fifteen people; skip it when the time is tight.
-->

---
layout: default
heading: "Six reasons to run a model yourself"
---

<div class="ki-grid ki-cols-3">
<div class="ki-card">

### Privacy
Who can read prompts and outputs?

</div>
<div class="ki-card">

### Sovereignty
Who controls model, infrastructure and exit?

</div>
<div class="ki-card">

### Cost control
What does one useful workload cost?

</div>
<div class="ki-card">

### Specialisation
Can you pick, pin and adapt the model?

</div>
<div class="ki-card">

### Latency
How far does a request travel?

</div>
<div class="ki-card">

### Regulation
What must you log, document, explain?

</div>
</div>

<p class="muted small">Regulation here is engineering input, not legal advice.</p>

<!--
**Key:** Every reason is a question about control, and every answer has a price, so we do not start with "self-hosting is better" but with what you would be buying and what you would be taking on. **Example:** Privacy is not abstract when the prompts are customer tickets; cost is not the price per GPU hour but the cost per useful workload, which is question 15 on the closing slide of Day 3. **Transition:** The word that bundles several of these is sovereignty, and it is used far too loosely. **Question:** "Is self-hosting cheaper?" Sometimes. It depends on utilisation and on the people you need, and we measure tokens per second on Day 2 to make the arithmetic honest. **Deeper:** Latency is about where the request travels and how long it queues, not only about the speed of the model.
-->

---
layout: default
heading: "Sovereignty is five questions, not one slogan"
---

<Formula :terms='[{ "t": "DATA", "sub": "who reads it" }, { "op": "+" }, { "t": "MODEL", "sub": "which weights" }, { "op": "+" }, { "t": "INFRASTRUCTURE", "sub": "whose hardware" }, { "op": "+" }, { "t": "OPS", "sub": "who patches" }, { "op": "+" }, { "t": "PORTABILITY", "sub": "can you leave" }]' />

<div class="ki-grid ki-cols-2">
<div>

A laptop with a local runner answers **one** question well: the data stays on one machine. Nobody patches, monitors or is on call.

</div>
<div>

The target is not zero dependency. It is dependencies that are **known, bounded and tested**.

</div>
</div>

<!--
**Key:** Sovereignty is an architecture property you inspect per dimension and per workload; the plus signs mean "and", and a system is as sovereign as its weakest dimension that matters for the data it handles. **Example:** "We run an open model on a hyperscaler" fixes the model question and leaves hardware and operations with the operator; "the data centre is in the EU" is a region, not a jurisdiction. **Transition:** More control is real, and it moves work onto your side; the next slide lists that work. **Question:** "Is this a legal framework?" No. It is a set of engineering questions; Day 3 scores the workshop's own setup with them, and it is engineering input, not legal advice. **Deeper:** Even the Commission's own cloud sovereignty text calls full independence not relevant today because of chip supply chains.
-->

---
layout: default
heading: "Control is not free: what you take on"
---

| You gain control of | You now own |
| --- | --- |
| **Data**: who reads prompts, logs, embeddings | retention, deletion, access control |
| **Model**: pinned weights under a licence you read | evaluation, selection, licence drift |
| **Infrastructure**: a named operator and region | capacity risk, price |
| **Operations**: patch autonomy, visibility | advisories, monitoring, on-call |
| **Portability**: a credible exit | a second environment, tests |

<Takeaway>

More control costs work. Decide per workload, on purpose, with the dependencies named.

</Takeaway>

<!--
**Key:** Each gain in the left column becomes a duty in the right one, and nobody does that work for you once the model runs on your side. **Example:** Operations is not hypothetical: the research notes counted 104 published security advisories for vLLM so far, so patching is a routine task, not an exception. Licences drift too; a family's licence is not a family property. **Transition:** The same trade-off shows up when you ask where the model should run. **Question:** "Can we outsource the operations part?" Yes, to a managed service or a provider, and then that party owns the dimension and you own the contract; the question moves, it does not disappear. **Deeper:** The count is as researched for this delivery; re-read it from the project's advisory page before quoting it.
-->

---
layout: default
heading: "Where the model can run: a trade-off, not a ranking"
---

| Option | You control | You carry | Ask |
| --- | --- | --- | --- |
| Laptop | Data stays on one machine | One user, one machine's memory, nobody on call | Who operates it later? |
| Dedicated GPU server | Hardware, data path, stack | Buying, housing, patching, fixed capacity | What when it fails or fills up? |
| Private data centre | The same, at team scale | A platform team, the Day 3 topics | Is the GPU pool used well? |
| Dedicated GPU cloud | Software, model, settings | Provider runs host, driver, network | Entity, law, sub-processors? |
| Sovereign cloud | A chosen operator and jurisdiction | Price, capacity, a label to verify | Which criteria, which evidence? |

<p class="muted small">This workshop uses the fourth row: an open model, a European region, a US provider. Day 3 scores it.</p>

<!--
**Key:** Nothing in this table is a ranking; the right row depends on the data class, the load and the team you have, and a team can use more than one row. **Example:** A developer laptop is a fine place to explore a model and a poor place to serve ten colleagues, and the workshop pods are a dedicated GPU cloud with synthetic data, which is acceptable only because of that. **Transition:** Whichever row you pick, the activity is inference, and that word is easily confused with two others. **Question:** "Where does a sovereign cloud label fit?" It is a claim to test: read the contracting entity, the governing law and the sub-processors rather than the badge. **Deeper:** Gaia-X, the EU Cloud Sovereignty Framework and BSI C3A give vocabulary and question lists; none of them is a certificate for model serving.
-->

---
layout: default
heading: "TRAINING ≠ FINE-TUNING ≠ INFERENCE"
---

<D01TrainingFineTuningInference />

<!--
**Key:** The three words answer one question, what happens to the weights: training writes them, fine-tuning changes them, inference only reads them, and this workshop is about the third. **Example:** Walk the columns row by row, then click once: the last row says where the workshop lives. Fine-tuning appears in Lab 1 as a decision, "no fine-tuning needed" or "fine-tune", and you must justify it. **Transition:** Inference is a system, so next the map we use to place every topic. **Question:** "Does fine-tuning make us a model provider?" Ordinary LoRA or full fine-tuning on a domain corpus is, per the Commission's indicative one-third-compute criterion, far below the threshold; this is engineering input, not legal advice. **Deeper:** A fine-tune belongs to one base revision, so a new base model means doing the work again.
-->

---
layout: default
heading: "One chain, three layers"
---

<div class="ki-stack">

<LayerStack layer="all" />

<div class="ki-grid ki-cols-3">
<div class="ki-card">

**Lit chips** show where this slide lives.

</div>
<div class="ki-card">

**Colour** is the layer: teal, violet, amber.

</div>
<div class="ki-card">

**Days 1 and 2** stay in teal. Day 3 moves up the chain.

</div>
</div>

</div>

<!--
**Key:** Every topic belongs to one stage of the chain model, runtime, GPU, engine, serving, observability, application, and the strip at the bottom of every slide lights the stages the slide is about. **Example:** Today's slides light MODEL, RUNTIME, GPU and ENGINE; on Day 3 the strip moves to serving and observability, and RAG, tools, MCP and agents sit at the end as the application layer on top of inference, not at the centre. **Transition:** Here is how the three days walk through this chain. **Question:** "Why is RAG not in the middle?" Because it is an application of a model call, and its cost shows up as extra prompt tokens; we treat it on Day 3 and connect it back to capacity. **Deeper:** On slides about one stage only, the strip highlights just that stage.
-->

---
layout: default
heading: "The three days at a glance"
---

<div class="ki-grid ki-cols-3">
<div class="ki-card">

<span class="ki-pill">Day 1</span>

### UNDERSTAND & RUN
*What are we actually running?*

Models, selection, GPU sizing. A first vLLM server.

</div>
<div class="ki-card">

<span class="ki-pill">Day 2</span>

### MEASURE & OPTIMIZE
*How do we make it fast and efficient?*

Benchmarks, batching, KV cache, quantization, parallelism.

</div>
<div class="ki-card">

<span class="ki-pill">Day 3</span>

### OPERATE
*How do we operate this as infrastructure?*

Containers, monitoring, scaling, security. RAG, tools, agents. A design to defend.

</div>
</div>

<!--
**Key:** Each day answers one question, and the questions build on each other: you cannot optimise what you have not measured, and you cannot operate what you have not optimised for a target. **Example:** Day 1 ends with your own request to a running server, Day 2 builds up to a report on one changed setting, Day 3 with an architecture you defend in five minutes. **Transition:** Here is how the machinery of the workshop works, so that nothing about access surprises you. **Question:** "Is the agenda fixed?" The order is, and the demonstrations on Day 2 are the first thing to shorten if we run late; the labs and their debriefs stay. **Deeper:** Day 1 and Day 2 are teal, the runtime layer; Day 3 is mostly violet and amber.
-->

---
layout: default
heading: "How the workshop works"
---

<Flow :items='[{ "label": "Your laptop", "sub": "SSH client" }, { "label": "Group GPU machine", "sub": "Alpha, Beta, Gamma, Delta", "layer": "runtime" }, { "label": "Shared vLLM server", "sub": "one per group", "layer": "runtime" }]' />

<div class="ki-grid ki-cols-2">
<div>

- No GPU and no cloud account needed.
- One GPU machine per group, you connect over SSH.
- The shared server is on purpose: you will see queueing.
- Six tasks; you keep `workshop-artifacts/`.

</div>
<div>

<Terminal title="your laptop">

```bash
ssh -p <port> <your-user>@<host>
```

</Terminal>


<span class="muted small">Setup details: `docs/SETUP.md`</span>

</div>
</div>

<Terminal title="your laptop, at the end of every day">

```bash
scp -P <port> -r <your-user>@<host>:ki-ohne-cloud/workshop-artifacts ./my-artifacts
```

</Terminal>

<!--
**Key:** Nobody needs hardware of their own: the trainer provides one GPU machine per group (an NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB class), and the single shared vLLM server per group is a design decision, because contention is something you only understand by causing it. **Example:** Four groups, one machine each; in Lab 2 you ask the same server at the same time as your neighbours. **Transition:** Last, how we will work during the three days. **Question:** "What if I lose my work?" Copy workshop-artifacts to your laptop at the end of every day with scp; the machines are deleted after the workshop. **Deeper:** The preflight in docs/SETUP.md checks tools and key before Day 1; everything else is on the machine at login.
-->

---
layout: default
heading: "How we work: predict, measure, explain"
---

<RhythmBar />

<div class="ki-grid ki-cols-2">
<div class="ki-card">

### Predict first
Write your prediction **before** the measurement. A result that contradicts the explanation is investigated, not hidden.

</div>
<div class="ki-card">

### SLO first
*There is no universally fastest configuration.*

Running example, a target: 1,200 input and 180 output tokens, 20 concurrent users, TTFT p95 800 ms, 25 output tokens/s per request, at most 2 % quality regression.

</div>
</div>

<!--
**Key:** Every experiment follows the same seven steps, and optimisation always needs a target, because the fastest configuration for one workload is the wrong one for another. **Example:** The running example is a workload plus a service level objective: 1,200 tokens in, 180 out, twenty concurrent users, first token within 800 ms at p95, 25 tokens per second per request, quality within two percent. These are targets, not measurements. **Transition:** With that, the first technical block: what a language model does between the prompt and the next token. **Question:** "Do I have to guess?" Yes, a wrong guess teaches more than a right one; we revisit the Day 2 predictions at the end of the day. **Deeper:** Availability is the fourth target of the example SLO (99.9 percent); Day 3 returns to it.
-->
