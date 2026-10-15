---
layout: section
module: 27
heading: "Architecture defenses, decision framework, close"
layer: all
question: "What would you build, and what would change your mind?"
can:
  - "Defend an architecture and name what would change your mind"
  - "Ask the questions that expose weak evidence"
  - "Walk the 15 decision questions for a new workload"
---

---
layout: two-col
heading: "Defense format: present, question, debrief"
---

- Each group presents: scenario, SLO, design table, diagram.
- Another group questions the design.
- Then the next group presents.

::right::

<Observation title="After the defenses, for the whole room">

What broke first at ten times the load? Which assumption would you check first? What did you trade for your most expensive choice?

</Observation>

<!--
**Key:** Each group presents and another group questions, so every group defends once and questions once. The debrief afterwards compares the reasoning, not the answers.

**Example:** Task 05 asks for a short defense and says another group will question it. Let the next group in the order ask the questions. Start with the scenario, the SLO, the design table and the diagram, and leave the 15 answers in the document. After the last defense ask the three debrief questions on the slide.

**Transition:** What are we listening for?

**Question:** "What if a group did not finish?" They defend what they have and say what is missing; an honest gap with a plan beats a filled-in guess.

**Deeper:** The validation list of task 05 is the instrument: a GPU count from a measured throughput, a *because* on every design row, a stated security boundary and what it leaves unprotected.
-->

---
layout: default
heading: "What makes a good defense"
---

| | Strong | Weak |
| --- | --- | --- |
| Numbers | Labeled measured, estimated or assumed | A GPU count nobody can trace |
| Choices | Each one names what it trades | Each one is a preference |
| Security | A boundary, and what it does not protect | A list of tools |
| Uncertainty | Names the first measurement and what would change the group's mind | Defends the first idea |

<Takeaway>

There is no single correct answer, only the quality of the reasoning.

</Takeaway>

<!--
**Key:** The criteria come straight from the validation list of task 05, and the capstone is judged on the quality of the reasoning, not on the answer.

**Example:** A strong defense points at a throughput measurement and says "this is why four GPUs, and this is the bottleneck we expect". A weak one gives a GPU count and a model name. A strong security section says "the key identifies a group, not a person, so we have no per-user revocation". The strongest designs say what they would measure first and what would change their mind.

**Transition:** The questions that probe these criteria.

**Question:** "Is there a score?" Not in the repository: the questions on the next slide are the instrument, and you adapt them to the room.
-->

---
layout: default
heading: "Questions to ask another group"
---

| Theme | Question |
| --- | --- |
| Capacity | What breaks first at ten times the load? |
| Evidence | Which numbers are measured, and which are assumed? |
| Uncertainty | What would you measure first, and what would change your mind? |
| Security | What does your boundary not protect? |
| Sovereignty | Which dimension is weakest, and do you accept it? |
| Application layers | How many model calls does one request cause? |
| Trade-offs | Which optimization addresses the measured bottleneck, and what does it trade? |
| Operations | How long until a new replica serves traffic? |

<!--
**Key:** The questions probe reasoning, not facts, and each one maps to a line of the validation list or to one of the decision questions.

**Example:** "What breaks first at ten times the load?" is the one question every group must be able to answer. Follow with "which number would you measure first?" and let the group say what it does not know. Use the sovereignty question where the data is sensitive, scenarios A and B. Ask C how many model calls one request causes, and D what happens when interruptible capacity is taken away.

**Transition:** A listening guide per scenario.

**Question:** "What if nobody asks?" Ask one yourself, and rotate who asks.

**Deeper:** They are the 15 decision questions in other words: latency budget (5), concurrency (7), bottleneck (9), optimization (11), monitoring (13), security boundary (14).
-->

---
layout: default
heading: "What to listen for in each scenario"
---

| Scenario | Listen for |
| --- | --- |
| A: sensitive assistant | Data stays in the company; 99.9 % availability needs redundancy; retrieval respects access rights |
| B: customer service | GDPR and an AI notice; a human takeover path; 60 simultaneous chats set the concurrency |
| C: coding assistant | 16k to 32k contexts make the KV cache the limit; agent calls multiply load; interactive latency |
| D: document pipeline | No interactive users: throughput and cost per document; interruptible capacity needs restartable jobs |

<!--
**Key:** Each scenario has a fact that decides the design; listen for whether the group found it.

**Example:** A: the data must stay in the company and availability is 99.9 %, so look for replicas, a stated boundary and retrieval that respects access rights. B: 60 simultaneous chats set the concurrency, and GDPR, a notice that people talk to an AI system and a human takeover path should appear. C: long contexts make the KV cache the limit, and agents multiply the calls. D: with no interactive users, throughput and cost per document decide, and cheap interruptible capacity only works if jobs can restart.

**Transition:** Before the decision framework, the whole path in one picture.

**Question:** "What if two groups choose differently for the same scenario?" Good: compare the trade-offs, not the choices.
-->

---
layout: default
heading: "What you can now do, by layer"
---

<ArchitectureDiagram :layers='[
  { "layer": "application", "title": "Application", "items": [{ "label": "Call a model from code", "sub": "JSON-schema output" }, { "label": "Place RAG, tools, MCP, agents", "sub": "and count their model calls" }] },
  { "layer": "infrastructure", "title": "Infrastructure", "items": [{ "label": "Containerize and pin" }, { "label": "Monitor", "sub": "queueing, KV pressure, idle GPU" }, { "label": "Scale and secure", "sub": "boundary, data flows" }, { "label": "Classify sovereignty", "sub": "five dimensions" }] },
  { "layer": "runtime", "title": "Runtime", "items": [{ "label": "Select and size", "sub": "model, precision, KV cache" }, { "label": "Deploy with vLLM", "sub": "read the start-up log" }, { "label": "Measure", "sub": "TTFT, ITL, TPS, percentiles" }, { "label": "Optimize", "sub": "one variable, name the trade" }] }
]' />

<!--
**Key:** Three layers: what participants can now do, not what they heard.

**Example:** Runtime: size memory and predict KV capacity, deploy with vLLM and read the start-up log, benchmark TTFT, ITL and throughput, and change one variable at a time. Infrastructure: containerize and pin, monitor queueing, KV pressure and an idle GPU, scale and secure, and classify a setup by data, model, infrastructure, operations and portability. Application: call a model with a JSON schema, place RAG, tools, MCP and agents on top, and count their model calls.

**Transition:** The closing slide: fifteen questions that tie these together.

**Question:** "Where is fine-tuning?" Covered as a concept, what changes, what it costs and when not to, and not as a hands-on skill.

**Deeper:** In outcome numbers: 1 to 14 are runtime, 15 to 20 infrastructure, 21 and 22 application, and 23 is the architecture itself.
-->

---
layout: two-col
heading: "Before you leave"
ratio: "1:2"
---

### Tell us

- What should we **keep**?
- What should we **change**?

### Next steps

- Run the benchmark harness on your own workload.
- Repeat a lab with one variation.
- Read `docs/METRICS.md` and `docs/TROUBLESHOOTING.md`.

::right::

<Terminal title="your laptop: copy your work, the machines are deleted">

```bash
scp -P <port> -r \
  <your-user>@<host>:ki-ohne-cloud/workshop-artifacts \
  ./my-artifacts
```

</Terminal>

If you did the opening round, read your sentences back: did the course answer them?

<!--
**Key:** The course ends with something to act on: a feedback prompt, three next steps, and your artifacts on your own laptop before the machines are deleted.

**Example:** Ask the two feedback questions: what to keep, what to change. If the opening round was done, read the sentences back and ask whether the course answered them. Then show the `scp` command from the opening slides and ask everyone to run it with their own port and user.

**Transition:** The last slide is the decision framework to take away: the 15 questions.

**Question:** "What if the copy fails?" Check the user name and the port, which changes when a machine is rebuilt (docs/SETUP.md), and ask the trainer while the machine still exists.

**Deeper:** A lab variation needs only your repository copy; the harness on your own workload needs your prompts and a server you may use.
-->

---
layout: end
heading: "The decision framework: 15 questions"
---

<div class="ki-grid ki-cols-2">
<div>
<ol style="list-style-type: decimal; padding-left: 2.2em; font-size: 26px">
<li>What task are we solving?</li>
<li>What quality do we need?</li>
<li>What is the smallest model that satisfies it?</li>
<li>What traffic do we expect?</li>
<li>What is our latency budget?</li>
<li>How large is the context?</li>
<li>What concurrency do we expect?</li>
<li>How much VRAM is required?</li>
</ol>
</div>
<div>
<ol start="9" style="list-style-type: decimal; padding-left: 2.4em; font-size: 26px">
<li>What hardware bottleneck do we expect?</li>
<li>What does the baseline benchmark show?</li>
<li>Which optimization addresses the measured bottleneck?</li>
<li>Does it degrade quality?</li>
<li>What should we monitor?</li>
<li>What security boundary is required?</li>
<li>What does this cost per useful workload?</li>
</ol>
</div>
</div>

<!--
**Key:** The fifteen questions are the decision framework: ask them in order for any new deployment, and write "do not know yet" together with how you would find out when you cannot answer.

**Example:** Take scenario B: question 4 gives 2,000 chats a day, question 7 turns it into concurrency, question 8 sizes the VRAM, question 10 asks what your own baseline shows, and question 15 asks what a useful chat costs.

**Transition:** Leave this slide up and take the last questions.

**Question:** "Which questions need a measurement?" 10, 12 and 15 cannot be answered without one; the rest can be argued from the task and the architecture.

**Deeper:** The same 15 questions end the template of `workshop-artifacts/production-architecture.md`.
-->
