# Slides: authoring guide

The deck for "KI ohne Cloud" is a [Slidev](https://sli.dev) presentation. This page is the contract for everyone who writes slides, human or agent. The exemplar to copy from is [`sections/04-gpu-sizing.md`](sections/04-gpu-sizing.md): read it first, and look at the rendered result.

```bash
pnpm --filter slides dev          # live preview at http://localhost:3030
pnpm --filter slides build        # static build into slides/dist
node scripts/check-slides-layout.mjs --range 1-30 --shots /tmp/shots   # render the BUILT deck, report overflow, write PNGs
pnpm check                        # speaker notes, lab slides, sources, section dividers, module-path drift
```

## 1. How the deck is put together

- `slides.md` is a manifest: the cover plus one `src: ./sections/<module-id>.md` entry per module, in path order. Do not edit it. Module ids, titles, order and layers come from [`config/workshop.yaml`](../config/workshop.yaml), and `pnpm check` fails when the manifest or a divider drifts from it. The material has no days, clock times or durations: do not write any.
- One section file per module, `sections/<module-id>.md` (`NN-name`, NN is the position in the path). Slides inside a file are separated by `---` with a frontmatter block, exactly as in the exemplar.
- The first slide of every section is its **divider**: `layout: section` with `heading` (equal to the module's `title` in `workshop.yaml`), `module` (its position), `layer` (copied from `workshop.yaml`), a one-sentence `question`, and `can:` with two or three short statements that complete "After this module you can ...". All later slides inherit layer, module and topic from the divider, which is what drives the bottom rail, the accent color and the kicker above every heading.
- Slide count: lectures 12 to 17 content slides, mixed modules 10 to 16, demos 5 to 10, labs 3 to 5 slides after the divider. Fewer, better slides beat more.

## 2. The rules that make the deck trustworthy

1. **Numbers.** A number that looks measured (latency, throughput, memory reported by a server, start-up time, cost per hour, ratios of measured things) must come from a result file through a sourced component (section 5) or carry `source="illustrative"`, which renders an ILLUSTRATIVE EXAMPLE badge. Arithmetic you show with its formula (bytes per parameter times parameters, KV bytes per token) is fine as plain text. Specifications from a datasheet are fine if the datasheet is in [`docs/REFERENCES.md`](../docs/REFERENCES.md) or [`docs/RESEARCH.md`](../docs/RESEARCH.md). A fact you cannot find in the repository does not go on a slide: leave it out or say what is unknown.
2. **Tested behavior only.** Slides describe what the repository's tools and the measured experiments do. Never describe a command, flag or output you have not seen in `tasks/`, `scripts/`, `experiments/`, `docs/` or a result file.
3. **Trade-offs, not superlatives.** No slide says "X makes inference faster". It says which metric improves, under which workload, which resource becomes the bottleneck, and what is traded (quality, latency, throughput, concurrency, memory, cost, operational complexity). No hype words, no "revolutionary", no "simply".
4. **Layers.** Say which layer a slide is about (the rail does it visually; the divider does it in words). RAG, tools, MCP and agents are application layers on top of inference, never the center. The workshop is not a LangChain workshop.
5. **Teaching rhythm** for any block with an experiment: concept, system, experiment, prediction, measurement, explanation, production consequence. Use `layout: experiment` with `step:` for the prediction, measurement and explanation slides so the rhythm bar shows where we are. Predictions are hypotheses; only measured files are results.
6. **No event dates, days or times.** No dates of the workshop or of a delivery, no "Day 2", no clock times, no "this morning", "tomorrow" or "yesterday", no block lengths and no minute budgets for activities or pacing cues in notes. Refer to other modules by topic ("the sizing module"). Technical durations (start-up time, restart time, latency, retention) are content and stay, and so is the measurement date that the `Provenance` line prints from a result file: it says when a number was measured, not when anything is taught. The check enforces the words.
7. **Sources.** Do not copy passages or figures from the book *Inference Engineering*; cite it by section only if at all. Prefer the primary sources in `docs/REFERENCES.md`. Not legal advice for the EU AI Act or GDPR: say "engineering input, not legal advice" where law appears.
8. **English** everywhere. Only the title "KI ohne Cloud" is German.

## 3. Speaker notes (required on every slide except cover, section dividers and end)

One HTML comment at the end of the slide, in this shape (the check needs the **Key** and **Transition** labels and at least 25 words; 70 to 150 words is right):

```markdown
<!--
**Key:** the one thing to get across.

**Example:** a concrete example or number to say aloud.

**Transition:** how this leads to the next slide.

**Question:** the question a participant is likely to ask, with the answer.

**Deeper:** optional detail for when the room wants more.
-->
```

Each label is its own paragraph, so the presenter view stays readable. Write for delivery, not for maintenance: no "re-check before quoting" remarks or repository history (those belong in `RESULTS.md` files).

Notes are for the trainer: what to say, not a copy of the slide. Include the live action when there is one ("click once, then run the command"). Notes may mention numbers only under the same rules as slides.

## 4. Layouts

Set with `layout:` in the slide's frontmatter. All layouts show the kicker (the module title) above the heading and keep the bottom 64 px free for the rail. Content area: 1136 x 604 px under the kicker.

| Layout | Use | Frontmatter |
| --- | --- | --- |
| `section` | divider, first slide of each section | `heading`, `module`, `layer`, `question`, `can` (two or three statements) |
| `default` | a heading and free content | `heading` |
| `two-col` | text left, something right; `::right::` starts the right column | `heading`, `ratio` (`1:1`, `3:2`, `2:3`, `2:1`, `1:2`) |
| `statement` | the one sentence to remember | none; put `# the sentence` in the body |
| `experiment` | prediction, measurement, explanation of an experiment | `heading`, `step` (`concept`, `system`, `experiment`, `prediction`, `measurement`, `explanation`, `consequence`), `experiment` (directory under `experiments/`) |
| `lab` | one of the six tasks | `heading`, `task` (file name in `tasks/` without `.md`), `artifact` |
| `code` | a code or output block is the content | `heading`, `file` |
| `end` | closing slide | `heading` |
| `cover` | first slide only | set in `slides.md` |

Free-form helpers inside slides: `.ki-grid .ki-cols-2|3|4`, `.ki-stack`, `.ki-row`, `.ki-card`, `.ki-pill`, `.lead`, `.muted`, `.small`, `.ki-mono`. Tables, lists, `code` and fenced code blocks are styled already. Never use inline `style=` for colors; use the tokens in `styles/tokens.css` (`var(--ki-runtime)` and friends) or a component.

Visible text per slide: at most about 45 words outside diagrams, tables and code. Body text is 22 px; do not shrink text below 16 px to make things fit. If a slide does not fit, split it.

## 5. Components

Props with arrays or objects use a bound attribute with JSON in single quotes: `:terms='[{ "t": "WEIGHTS" }]'`. Numbers are bound too (`:digits="1"`).

| Component | What it is | Notes |
| --- | --- | --- |
| `MetricCard` | one number | **`source` required.** `source="measured:benchmark/results/reference/<file>.json"` plus `metric="ttft_ms.p50"`, or `source="illustrative"` plus `value`. Props: `label`, `unit`, `digits`, `note`, `tone` (`good`, `bad`). A slide with measured cards also has one `<Provenance source="..." />`. |
| `ResultTable` | table of results, one row per result file | **`source` required** (a file or a directory), `:columns` (metric paths such as `concurrency`, `ttft_ms.p50`, `aggregate_tps`), optional `match` (a string, or a list: files whose path contains any of them), `:headers`, `:digits`, `label-by="configuration.server_profile"` or `:labels='[...]'` for a first column (with `label-header`). Illustrative: `:headers` and `:rows`. |
| `ResultChart` | line or bar chart | **`source` required**, `x`, `y` (metric paths), `kind`, `title`, `xlabel`, `ylabel`, `match` (string or list), `by="configuration.server_profile"` for one series per profile with a legend. Illustrative: `:points='[{"x":1,"y":10}]'`. |
| `Benchmark` | the numbers of one benchmark run on one card | **`source` required** (one result file). |
| `MemoryBar` | VRAM budget as one stacked bar | **`source` required**, `:segments`, `total`. See the exemplar. |
| `Provenance` | one line: hardware, model, engine version, date | under measured numbers |
| `Formula` | an equation as boxed terms | `:terms='[{"t":"A"},{"op":"+"},{"t":"B","hot":true}]'`, optional `sub` |
| `Flow` | a chain of boxes | `:items='[{"label":"Client"},{"label":"vLLM","sub":"engine","layer":"runtime"}]'` |
| `ArchitectureDiagram` | layered block diagram, application over infrastructure over runtime | `:layers='[...]'`, see the component header |
| `LayerStack` | the seven-stage chain with the current layer lit | `layer`, optional `stage` |
| `TradeoffMatrix` | direction of an effect on the seven trade-off dimensions | `:rows='[{"name":"FP8 weights","effects":{"memory":"up","quality":"risk"}}]'`; direction only, never sizes |
| `ExperimentCard` | what changes, what is held, what is watched | `name`, `variable`, `:profiles`, `workload`, `:metrics`, `hypothesis` |
| `Terminal` | terminal window around a fenced code block | `title` |
| `CodeDiff` | before and after of a configuration | slots `#before`, `#after` with fenced code |
| `Prediction`, `Observation`, `Takeaway`, `Warning`, `Consequence`, `InstructorNote` | labeled asides | optional `title`; one or two sentences |
| `DiagramFrame` | frame for original SVG diagrams | see section 6 |

Use `v-click` sparingly and only where the order of reveal is the teaching point (a diagram built up step by step, a prediction before its answer). The layout checker renders the final click state.

## 6. Diagrams

The deck has 19 original diagrams, `components/D01...` to `D19...`, one Vue single-file component each, named `D<NN><PascalName>.vue` (the exemplar is `D04KvCache.vue`). They are drawn in SVG inside `DiagramFrame`, which defines a coordinate space of **1136 x 460** (exactly the free area under a heading; pass `:height="540"` and use a slide without heading for a bigger one).

- Use the `.dg-*` classes from `styles/base.css` (`dg-box`, `dg-teal`/`dg-violet`/`dg-amber`/`dg-red`/`dg-green`, `dg-text`, `dg-text-muted`, `dg-mono`, `dg-title`, `dg-line`) and the arrow markers `url(#ki-arrow)` plus `-teal`, `-violet`, `-amber`, `-red`. Teal means the runtime layer, violet infrastructure, amber application; red is for failure and green for the result you want.
- Text is 16 to 22 px. About 10 units per character at 20 px; check that labels fit their boxes and the right edge (1136).
- One idea per diagram. Reveal in at most three `v-click` steps. No decoration. Label what each shape is; a diagram that needs the speaker to decode it is not finished.
- Diagram numbers follow the number rules: if a number appears in a diagram, it is arithmetic with a visible formula, a datasheet value, or marked illustrative in the diagram itself ("illustrative").
- Use a diagram on a `layout: default` slide with a heading, and put the explanation in the speaker notes.

## 7. Lab slides

A lab block has 3 to 5 slides after the divider: the goal and the deliverable; the steps in order (three to six short lines, commands in a `Terminal`); what a good result looks like; where help is (`docs/TROUBLESHOOTING.md`, `./scripts/reset.sh lab-NN`, ask the trainer) and the debrief questions. Use `layout: lab` for the steps slide with `task` and `artifact` set. A lab has no timebox: say what counts as done. Tasks are the source of truth: read `tasks/NN-*.md` and do not contradict it.

## 8. Before you hand a section in

1. `pnpm --filter slides build` has no errors or warnings that name your files.
2. `node scripts/check-slides-layout.mjs --range <first>-<last> --shots <dir>` reports no overflow, and you have looked at the PNGs of every slide with a diagram, table, chart or code.
3. `pnpm check` reports no error or warning for your files (dev mode warns about files other authors have not written yet; those are not yours).
4. Every claim is traceable to a file in the repository. Every number follows section 2.
5. Notes exist on every slide, each with Key and Transition.
