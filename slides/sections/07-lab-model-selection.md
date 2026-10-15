---
layout: section
module: 7
heading: "Lab 1: select models for four scenarios"
layer: runtime
question: "Which model, precision, engine and context would you defend for each scenario, and what did you give up?"
can:
  - "Choose model, precision, engine and context for a scenario and defend the choice"
  - "Name what each choice gave up"
  - "Check a choice against the GPU with the sizing script"
---

---
layout: default
heading: "Goal: choose, size and defend a model"
---

<div class="ki-grid ki-cols-2">
<div>

Choose, size and defend an open model for realistic scenarios, using the **smallest model that reliably does the job**.

Work in your group. Each sub-group takes **one scenario first**, finishes it, then takes another or swaps. One document.

</div>
<div class="ki-card">

### You produce

`workshop-artifacts/model-selection.md`

Per scenario: model, precision, hardware, engine, context, reasoning, why, what you gave up. Plus the license table.

</div>
</div>

<!--
**Key:** The deliverable is a document that defends choices, not a model name: every block has a trade-off, and the license table says what each license means for commercial use.

**Example:** Done means the scenario's block has a model, a precision, a context length and a trade-off, and every named model has a license row. The template is workshop-artifacts/model-selection.md in your clone; if it is missing, ./scripts/reset.sh lab-01 creates it.

**Transition:** First the four scenarios, then the steps for each.

**Question:** "Do we have to finish all four?" No: each sub-group takes one scenario first, finishes it, then takes another or swaps with a neighboring sub-group. Two good blocks beat four thin ones, and reduced scope is a legitimate outcome.

**Deeper:** Your best scenario is copied into the Selected Model section of workshop-artifacts/inference-report.md, which grows through the whole path.
-->

---
layout: default
heading: "The four scenarios"
---

| | Scenario | Numbers to design for |
| --- | --- | --- |
| A | Internal German-language assistant for 300 employees, answering from company documents | 20 concurrent users at peak; data must not leave the company; answers within 10 s; 3,000 tokens of retrieved context per question |
| B | Customer-service classification and information extraction | 40,000 tickets per day, peaks of 5 per second; 300 input and 60 output tokens; JSON output; 95 % within 2 s |
| C | Coding assistant for a development team | 100 developers; 16,000 to 32,000 tokens of repository context; first token within 1 s for 95 % of requests |
| D | Document-processing pipeline, run once a month | 2 million documents, 3,000 input and 300 output tokens each; finish within 72 hours; cost per document matters, latency does not |

<!--
**Key:** Turn each requirement into numbers before you name a model: tokens of KV cache for the concurrency, input and output tokens per second at the peak, sequences per pool, documents per second to finish in 72 hours.

**Example:** Scenario B at the peak: five tickets per second at 300 input and 60 output tokens is the load; scenario C at 32,000 tokens of context asks how many such sequences the pool holds. No scenario has a single right answer; the task text deliberately gives no model.

**Transition:** The steps are the same for every scenario.

**Question:** "Where do I start?" Each sub-group takes one scenario first; agree in the group so that different scenarios are covered, and prefer the one closest to your own work.

**Deeper:** The worksheets in docs/MODEL-SELECTION.md section 6 hold questions and trade-offs for each scenario, and no answers.
-->

---
layout: lab
heading: "Steps: the same five for every scenario"
task: 01-model-selection
artifact: workshop-artifacts/model-selection.md
---

<div class="ki-stack">

<div class="ki-stack">
<div class="ki-row"><span class="ki-pill ki-mono">1</span><span>Decide what quality is needed and how you would test it (one sentence).</span></div>
<div class="ki-row"><span class="ki-pill ki-mono">2</span><span>Name model, precision, engine and context. Check the license.</span></div>
<div class="ki-row"><span class="ki-pill ki-mono">3</span><span>Check that it fits the GPU with <code>sizing.py</code>.</span></div>
<div class="ki-row"><span class="ki-pill ki-mono">4</span><span>Decide on thinking mode, and say why.</span></div>
<div class="ki-row"><span class="ki-pill ki-mono">5</span><span>Write down <strong>what you gave up</strong>.</span></div>
</div>

<Terminal title="your group's GPU machine or your laptop">

```bash
python3 scripts/sizing.py --model primary --precision bf16 --context 8192 --concurrency 16
python3 scripts/sizing.py --model quantized --precision fp8 \
    --kv-dtype fp8 --context 32768 --concurrency 8
```

</Terminal>

</div>

<!--
**Key:** The five steps are the whole method: quality bar, candidate with license, fit, thinking mode, and the sentence about what you gave up; a choice without a trade-off has not been thought through.

**Example:** You ran sizing.py in the sizing module; now change --model, --precision, --context and --concurrency to your scenario. Its numbers give the concurrency and the context, and the prefill material tells you what a long prompt does to the first token. Read the LICENSE file, not a blog post, and fill the document as you go.

**Transition:** Before you start, what does good look like?

**Question:** "My model is not in config/models.yaml." Pass the numbers by hand with --params-b, --layers, --kv-heads and --head-dim; sizing.py --help shows an example.

**Deeper:** The commands run anywhere with Python; no GPU access is needed for the sizing part.
-->

---
layout: default
heading: "What a good result looks like"
---

All four blocks are filled in. Each names a model, a precision, a context length and a trade-off. Every named model has a license row.

<div class="ki-card">

### Validation

- A `sizing.py` run that says it fits, or the reason it needs more than one GPU
- An answer to: "which smaller model did you consider, and why did you reject it?"
- No license entry says only "open": each names the license and one consequence

</div>

<!--
**Key:** The validation is three checks you can do yourself without the trainer: the fit evidence, the rejected smaller model, and license rows with a consequence.

**Example:** A good license row: "Apache-2.0, no scale threshold, notice duties per the text". A good rejection names the arithmetic or measurement behind it, not a feeling. If nothing fits scenario C or D, that is a finding: say what you would need, a bigger GPU, quantization or several GPUs, and what it would cost.

**Transition:** If you get stuck, the next slide lists where to go.

**Question:** "What is a good trade-off sentence?" One that names what got worse: quality, latency, memory, cost or operational complexity.

**Deeper:** When your scenario is done, take another or swap with a neighboring sub-group, or repeat scenario A with FP8 weights and KV cache and see how many more users fit.
-->

---
layout: two-col
heading: "Help and debrief"
---

### If you get stuck

- Sizing: `python3 scripts/sizing.py --help`, weights first, then add the KV cache.
- License: read the `LICENSE` file of the repository.
- Nothing fits? That is a finding.
- Template missing: `./scripts/reset.sh lab-01`
- Unknown term: `docs/GLOSSARY.md`
- Machine or login: `docs/TROUBLESHOOTING.md`

::right::

### Debrief questions

- Which smaller model did you consider, and why did you reject it?
- Which scenario needed more than one GPU, and what would it cost?
- Where would you fine-tune, and where is a better prompt enough?
- Which trade-off did your group argue about?

<!--
**Key:** The debrief is where the lab pays off: every group defends one choice briefly, and the rejected smaller model is the question that separates a choice from a default.

**Example:** Pick two groups with different answers for the same scenario and ask what each gave up; ask who needed more than one GPU and what the bigger setup would cost. Question three comes from the learning outcome on fine-tuning: justify either "no fine-tuning needed" or "fine-tune" for at least one scenario.

**Transition:** Next the first real server: the trainer starts vLLM from a profile and shows how to read what it reports.

**Question:** "Can we keep editing the document?" Yes, it stays in your workshop-artifacts directory; copy it to your laptop before the machines go away.

**Deeper:** Sub-groups that took different scenarios first make the best comparison in the debrief.
-->
