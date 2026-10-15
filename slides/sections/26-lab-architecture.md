---
layout: section
module: 26
heading: "Lab 5: production architecture challenge"
layer: all
question: "Can you design, size and defend an inference platform for a realistic scenario?"
can:
  - "Design a platform for a scenario starting from an SLO"
  - "Estimate capacity from measured numbers and label every assumption"
  - "Defend the design against another group's questions"
---

---
layout: default
heading: "Lab 5: design a platform for one scenario"
---

<p class="lead">Estimate capacity from measured numbers and defend the design in a short defense. There is no single correct answer.</p>

| | Scenario | Facts you can rely on |
| --- | --- | --- |
| A | Internal assistant handling sensitive enterprise data | 800 employees, 5 % of them active at peak, answers from internal documents (RAG), data must stay in the company, availability 99.9 % |
| B | German customer-service assistant | 2,000 chats a day, peaks of 60 simultaneous chats, short answers, GDPR applies, must not give wrong legal advice, a human can take over |
| C | Coding assistant for 100 developers | Long repository context (16k to 32k tokens), interactive latency matters most, usage clustered at working hours, agents may make many calls per request |
| D | Offline document-processing pipeline | 2 million documents per month, no interactive users, cost per document matters, can use cheap or interruptible capacity |

<div class="small muted">Scenarios A to D here are different from the Lab 1 scenarios.</div>

<!--
**Key:** Four realistic scenarios, one per group, each stressing a different bottleneck. There is no single correct answer; the quality of the engineering reasoning is what counts.

**Example:** Assign one scenario per group. A is RAG with data that must stay in the company and 99.9 % availability. B is peaks of 60 simultaneous chats under GDPR, with a human takeover. C is 16k to 32k token contexts plus agents. D is two million documents a month with no interactive users, so cost per document decides.

**Transition:** First, what the document has to contain.

**Question:** "Can we change the facts?" You may add assumptions, labeled as assumptions, and you may not drop the facts you were given.

**Deeper:** The letters mean different scenarios in Lab 1 and in this lab; say so when you assign them. The defenses are in the next module.
-->

---
layout: default
heading: "The document: what goes in, and when it is good"
---

| Section | What goes in | Good when |
| --- | --- | --- |
| Scenario | Who uses it, how often, with what data | Specific enough to size |
| Requirements | Workload and SLO as YAML | Concurrency follows from the facts |
| Design | One row per decision, from model to security boundary | Each *because* names a trade-off; security says what is not protected |
| Estimates | Concurrency, GPUs, bottleneck, scaling, cost | GPU count from measured throughput and the SLO; every number labeled measured, estimated or assumed |
| Diagram | Gateway, auth, replicas, GPU pool, logs, secrets | Data flows marked |
| Risks | Three risks, the first measurement for each | The measurement would reduce the risk |
| 15 questions | One line each | "Do not know yet" says how to find out |

<!--
**Key:** The template is the checklist. A decision table where every row has a choice and a because, estimates with their status, a diagram, three risks with the first measurement for each, and the 15 questions.

**Example:** Open the file as participants see it and point at the design table: model, precision, GPU, engine, context, replicas, API and authentication, observability, RAG, scaling, security boundary and SLO. A row without a trade-off in its because column is a preference, not a decision.

**Transition:** Now the steps.

**Question:** "How much detail?" Enough for another group to challenge a number.

**Deeper:** The security row has to name a boundary and say what is not protected; Lab 5's data-flow map and the sovereignty sheet from the security module both belong in that section.
-->

---
layout: lab
heading: "Steps: from the SLO to the defense"
task: 05-production-design
artifact: workshop-artifacts/production-architecture.md
---

| Step | Do |
| --- | --- |
| 1 | Requirements: workload and SLO as YAML |
| 2 | Capacity: GPUs from measured throughput at the SLO |
| 3 | Design table: every choice gets a *because* |
| 4 | Architecture: gateway, authentication, replicas, scaling, failure |
| 5 | Security: data flows, boundary, one attack per layer |
| 6 | Cost, the 15 questions, a short defense prepared |

<Terminal title="starter files and reference results, without deleting your work">

```bash
./scripts/reset.sh lab-05
```

</Terminal>

<!--
**Key:** Leave this slide up while the groups work. Work from the SLO backwards: tokens per second needed, tokens per second per GPU, number of GPUs, then redundancy.

**Example:** Step 1 for scenario A: 800 employees with 5 % active at peak is 40 people at peak, and concurrency is arrival rate times time in the system, so ask how long one answer takes. Step 5 asks for one attack at the infrastructure layer and one at the application layer, and for the extra model calls if RAG or agents are in the design.

**Transition:** The numbers you can start from.

**Question:** "Do we have to use the reference results?" Use your own results first (`benchmark/results/mine/`); the reference results are the fallback that `reset.sh` provides.

**Deeper:** Step 4 asks for the three dashboard panels that would page you and the cold-start time you measured.
-->

---
layout: default
heading: "Numbers to start from"
---

<div class="ki-grid ki-cols-3">
<MetricCard label="Output rate, one request at a time" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="output_tps" unit="tok/s" digits="1" />
<MetricCard label="TTFT p50 at 1,200 input tokens" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="ttft_ms.p50" unit="ms" digits="1" />
<MetricCard label="Cold start of one server" source="measured:benchmark/results/reference/startup/cold-start.json" metric="log_seconds_to_ready" unit="s" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

Price: **2.49 USD** per GPU-hour (one Runpod catalog read; check the current price).

<Formula :terms='[{ "t": "TOKENS/s NEEDED", "sub": "requests/s × output tokens" }, { "op": "÷" }, { "t": "TOKENS/s PER GPU", "sub": "at the SLO, measured" }, { "op": "=" }, { "t": "GPUs", "sub": "then add redundancy", "hot": true }]' />

<Warning title="Not capacity">

One request at a time is not capacity. Your Lab 3 sweep is.

</Warning>

<!--
**Key:** The single-stream numbers are a floor and a proxy, not a capacity: throughput at the SLO comes from your own concurrency sweep.

**Example:** Use the cold-start card for the failure and scaling rows: a replica added during a spike is not serving until it has started, about three minutes for a first start. The price is one Runpod catalog read, so say which price you used and that your own prices differ. Define "useful workload": per ticket, per thousand documents, per developer per month.

**Transition:** Last, what good looks like and where help is.

**Question:** "What if I have no number for my case?" Take the closest reference result, say that it is a proxy and say how far it is from your case.

**Deeper:** The warm-start and restart result files hold the shorter times.
-->

---
layout: two-col
heading: "Stuck? Help, and what you hand in"
---

### If you get stuck

- Work backwards from the SLO: tokens per second, GPUs, redundancy.
- No number? Use the closest reference result, labeled a proxy.
- Help: `docs/TROUBLESHOOTING.md`, `./scripts/reset.sh lab-05`, the trainer.

::right::

### Good when

- the GPU count follows from a measured throughput and a stated SLO
- every design row has a *because* that names a trade-off
- the security section says what is **not** protected

<!--
**Key:** The deliverable is judged on reasoning: one sentence per row of the design table, the number you trust least, and the answer to "what breaks first at ten times the load?". The defenses happen in the next module.

**Example:** Circulate: a GPU count with no throughput behind it earns "where does this number come from?". A group that has finished early adds the cost estimate with FP8 or a second region, as the task suggests.

**Transition:** The defenses come next: each group presents and another group questions.

**Question:** "Is a wrong estimate penalized?" No; an unlabeled one is.

**Deeper:** Further exploration in the task: redo the cost with FP8 and a cheaper GPU, or add a second region or provider.
-->
