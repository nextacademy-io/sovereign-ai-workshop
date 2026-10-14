---
layout: section
heading: "Lab 5: production architecture challenge"
time: "16:00"
minutes: 60
layer: all
question: "Can you design, size and defend an inference platform for a realistic scenario?"
---

---
layout: default
heading: "Lab 5: design a platform for one scenario"
---

<p class="lead">Estimate capacity from measured numbers and defend the design in five minutes. There is no single correct answer.</p>

| | Scenario | Facts you can rely on |
| --- | --- | --- |
| A | Internal assistant handling sensitive enterprise data | 800 employees, 5 % of them active at peak, answers from internal documents (RAG), data must stay in the company, availability 99.9 % |
| B | German customer-service assistant | 2,000 chats a day, peaks of 60 simultaneous chats, short answers, GDPR applies, must not give wrong legal advice, a human can take over |
| C | Coding assistant for 100 developers | Long repository context (16k to 32k tokens), interactive latency matters most, usage clustered at working hours, agents may make many calls per request |
| D | Offline document-processing pipeline | 2 million documents per month, no interactive users, cost per document matters, can use cheap or interruptible capacity |

<!--
**Key:** Four realistic scenarios, one per group, each stressing a different bottleneck. There is no single correct answer; the quality of the engineering reasoning is what counts. **Example:** Assign A to D, one per group (alpha to delta). A is RAG with data that must stay in the company and 99.9 % availability. B is peaks of 60 simultaneous chats under GDPR, with a human takeover. C is 16k to 32k token contexts plus agents. D is two million documents a month with no interactive users, so cost per document decides. **Transition:** First, what the document has to contain. **Question:** "Can we change the facts?" You may add assumptions, labelled as assumptions, and you may not drop the facts you were given. **Deeper:** The timebox is 45 minutes of the 60-minute block; the rest is the debrief.
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
| Estimates | Concurrency, GPUs, bottleneck, scaling, cost | GPU count from measured throughput and the SLO; every number labelled measured, estimated or assumed |
| Diagram | Gateway, auth, replicas, GPU pool, logs, secrets | Data flows marked |
| Risks | Three risks, the first measurement for each | The measurement would reduce the risk |
| 15 questions | One line each | "Do not know yet" says how to find out |

<!--
**Key:** The template is the checklist. A decision table where every row has a choice and a because, estimates with their status, a diagram, three risks with the first measurement for each, and the 15 questions. **Example:** Open the file as participants see it and point at the design table: model, precision, GPU, engine, context, replicas, API and authentication, observability, RAG, scaling, security boundary and SLO. A row without a trade-off in its because column is a preference, not a decision. **Transition:** Now the steps and the clock. **Question:** "How much detail?" Enough for another group to challenge a number. **Deeper:** The security row has to name a boundary and say what is not protected; Lab 5's data-flow map and the sovereignty sheet from this afternoon both belong in that section.
-->

---
layout: lab
heading: "Steps: from the SLO to the defence"
task: 05-production-design
timebox: 45
artifact: workshop-artifacts/production-architecture.md
---

| Step | Do |
| --- | --- |
| 1 | Requirements: workload and SLO as YAML |
| 2 | Capacity: GPUs from measured throughput at the SLO |
| 3 | Design table: every choice gets a *because* |
| 4 | Architecture: gateway, authentication, replicas, scaling, failure |
| 5 | Security: data flows, boundary, one attack per layer |
| 6 | Cost, the 15 questions, five minutes to defend |

<Terminal title="starter files and reference results, without deleting your work">

```bash
./scripts/reset.sh lab-05
```

</Terminal>

<!--
**Key:** Start the 45-minute clock here and leave this slide up. Work from the SLO backwards: tokens per second needed, tokens per second per GPU, number of GPUs, then redundancy. **Example:** Step 1 for scenario A: 800 employees with 5 % active at peak is 40 people at peak, and concurrency is arrival rate times time in the system, so ask how long one answer takes. Step 5 asks for one attack at the infrastructure layer and one at the application layer, and for the extra model calls if RAG or agents are in the design. **Transition:** The numbers you can start from. **Question:** "Do we have to use the reference results?" Use your own Day 2 results first (`benchmark/results/mine/`); the reference results are the fallback that `reset.sh` provides. **Deeper:** Step 4 asks for the three dashboard panels that would page you and the cold-start time you measured.
-->

---
layout: default
heading: "Numbers to start from"
---

<div class="ki-grid ki-cols-4">
<MetricCard label="Output rate, one request at a time" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="output_tps" unit="tok/s" digits="1" />
<MetricCard label="TTFT p50 at 1,200 input tokens" source="measured:benchmark/results/reference/baseline/single-stream/c001.json" metric="ttft_ms.p50" unit="ms" digits="1" />
<MetricCard label="Cold start of one server" source="measured:benchmark/results/reference/startup/cold-start.json" metric="log_seconds_to_ready" unit="s" />
<MetricCard label="Workshop GPU, USD per hour" source="illustrative" value="2.49" unit="USD/h" />
</div>

<Provenance source="measured:benchmark/results/reference/baseline/single-stream/c001.json" />

<Formula :terms='[{ "t": "TOKENS/s NEEDED", "sub": "requests/s × output tokens" }, { "op": "÷" }, { "t": "TOKENS/s PER GPU", "sub": "at the SLO, measured" }, { "op": "=" }, { "t": "GPUs", "sub": "then add redundancy", "hot": true }]' />

<Warning title="Not capacity">

One request at a time is not capacity. Your Day 2 sweep is.

</Warning>

<!--
**Key:** The single-stream numbers are a floor and a proxy, not a capacity: throughput at the SLO comes from your own concurrency sweep. **Example:** Use the cold-start card for the failure and scaling rows: the task says one to three minutes per server, so a replica added during a spike is not serving for that long. The price is the provider catalogue price when it was read, marked illustrative because prices change; state which price you used. Define "useful workload": per ticket, per thousand documents, per developer per month. **Transition:** Last, what good looks like and where help is. **Question:** "What if I have no number for my case?" Take the closest reference result, say that it is a proxy and say how far it is from your case. **Deeper:** The warm-start and restart result files hold the shorter times.
-->

---
layout: two-col
heading: "Stuck? Help, and what the defence looks like"
---

### If you get stuck

- Work backwards from the SLO: tokens per second, GPUs, redundancy.
- No number? Use the closest reference result, labelled a proxy.
- Help: `docs/TROUBLESHOOTING.md`, `./scripts/reset.sh lab-05`, the trainer.

::right::

### The defence

- Five minutes, questioned by another group.
- Say what you would measure first and what would change your mind.

<!--
**Key:** The defence is judged on reasoning: prepare one sentence per row of the design table, the number you trust least, and the answer to "what breaks first at ten times the load?". **Example:** Tell groups the defence order and who questions whom. Circulate: a GPU count with no throughput behind it earns "where does this number come from?". Debrief for the last 15 minutes: what broke first at ten times the load, which assumption would you check first, what did you trade for your most expensive choice? **Transition:** The next block is the defences. **Question:** "Is a wrong estimate penalised?" No; an unlabelled one is. **Deeper:** Further exploration in the task: redo the cost with FP8 and a cheaper GPU, or add a second region or provider.
-->
