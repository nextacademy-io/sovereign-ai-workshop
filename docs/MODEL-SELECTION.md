# Model selection

How to choose a model for a task. This is a procedure, not a catalogue: a catalogue of models is out of date within weeks, a procedure is not.

One rule drives everything: **choose the smallest model that reliably satisfies the task.** "Smallest" is counted in what you pay for: VRAM, latency, GPU hours, operational risk. "Reliably" is counted on your own task, at the precision you will serve, under the load you expect.

The document supports Lab 1 ([`tasks/01-model-selection.md`](../tasks/01-model-selection.md)); your answers go into `workshop-artifacts/model-selection.md`. Evidence for the statements about models, engines and licences is in [`RESEARCH.md`](RESEARCH.md), sections 4, 5, 8 and 11. Numbers marked "measured" come from the workshop GPU (NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB) with vLLM 0.31.0. Numbers marked "computed" come from `scripts/sizing.py` or from simple arithmetic on repository values. Nothing here is legal advice.

## 1. The workflow

```text
TASK + EVAL → SHORTLIST → LICENCE → FIT → MEASURE → DECIDE
```

The order is deliberate: cheap checks come first. A licence veto costs ten minutes. A measurement costs GPU time. A wrong decision costs a deployment.

| Step | Question | Tool in this repository | Output |
| --- | --- | --- | --- |
| 1. Task and eval | What must the model do, and how will I know that it did? | Section 3; `experiments/quality_probe.py` as a pattern | A one-paragraph task description, a pass criterion, 30 items with checks |
| 2. Shortlist | Which three to five models could plausibly do it? | Model cards, `config/models.yaml`, RESEARCH 5.3 | A list with size, active parameters, context, modalities |
| 3. Licence | May I use each one for this purpose, at my scale? | Section 5; the `LICENSE` file at the pinned revision | One row of the six-column table per candidate |
| 4. Fit | Do weights and KV cache for my context and concurrency fit, with headroom? | `python3 scripts/sizing.py` | Fits or does not; KV capacity in tokens |
| 5. Measure | Does it pass my eval? Does it meet latency and throughput at my load? | Your eval runner; `benchmark/run.sh` (`./scripts/benchmark.sh` on the pods) | Pass rate per slice with an interval; TTFT, ITL and tokens per second at the expected concurrency |
| 6. Decide | Which is the smallest that passes, and what did I give up? | The decision record below | Model, revision, precision, flags, context, evidence, trade-offs |

### Shortlisting

- Use leaderboards and model cards to build the list. Never use them to decide.
- Put one model on the list that is smaller than you expect to need. Lab 1 asks "which smaller model did you consider, and why did you reject it?" The answer must be a measurement.
- Several sizes of one family give the cheapest size curve. The workshop has `small` (Qwen3-1.7B) and `primary` (Qwen3-8B) for that reason.
- Drop a candidate at once if: its architecture is not in the engine at the pinned version; it needs `trust_remote_code` (workshop profiles refuse it, see section 7); it lacks a modality you need; its language list does not name German when you need German.
- A model that is not in `config/models.yaml` has no pinned revision here. Check its current licence text before you recommend it (`alternatives_discussed` says so).

### The decision record

Write this down for the model you choose, and for the smaller one you rejected:

- Task, eval version and the date it was run.
- Repository, full 40-character revision, licence row.
- Precision of weights and of the KV cache, engine and version, the profile or flags.
- Context length served; thinking on or off.
- Eval result per slice with an interval; latency and throughput at the expected load, with the benchmark provenance.
- The rejected smaller model and the measurement that rejected it.
- What you gave up.
- What makes you decide again: a new release of the family, a licence change, traffic that grows, a quality bound that moves.

The last item matters. The open-model ecosystem moves fast. The header of `config/models.yaml` asks for a re-check, a re-pin and a re-run of the baseline experiment before each delivery. Section 4 and section 5 of this document must then be updated with the new numbers.

## 2. The criteria checklist

Use the tables at steps 2 to 5. Each row says what to look at and the mistake people make most often. First separate **hard requirements** from **trade-offs**. A missing hard requirement (the licence forbids the use, the architecture is unsupported, German is not covered, the model does not fit) removes the candidate without any measurement. Trade-offs (quality, latency, cost) are weighed on measured values.

### Task fit

| Criterion | What to look at | Common mistake |
| --- | --- | --- |
| Task quality | Pass rate on your own eval, split by slice (language, document type, difficulty), with an interval. Compare with the threshold you set in step 1. | Choosing by public benchmark rank, or by an average that hides the slice that matters to you. |
| Reasoning behaviour | Whether thinking is on by default (Qwen3: on; Gemma 4: off), how to switch it per request (`chat_template_kwargs`, `enable_thinking`), which reasoning parser the engine needs, and how many extra output tokens thinking costs on your items. | Evaluating with thinking on and deploying with it off, or the reverse. Leaving thinking on for a classification task and paying its tokens on every request. |
| Multilingual, including German | The vendor's language list (a claim, not a measurement). Then German items of your own: formal register, compound words, umlauts, German-English mixes, your domain terms. The token count of a real German document on this tokenizer (`/tokenize` on the live server). | Reading "supports 100+ languages" as "good German". Testing in English only. Ignoring that the same content can cost more tokens in German, which costs context and latency. For some models no language list was found (RESEARCH 5.3). |
| Coding | Your languages and frameworks, the kind of task (completion, chat, edit, agent), tests that run from your own code base, the context the repository needs. Whether a dedicated coder variant exists and which tool-call parser it needs. | Using a generic coding benchmark as a proxy for your repository. Judging code by reading it instead of running tests. |
| Structured output | Whether the engine constrains decoding to a JSON schema (vLLM: `response_format` or `structured_outputs`; the workshop profiles use the xgrammar backend). Whether the model fills the fields correctly when constrained. The first-use grammar compile time. | Believing that constrained decoding makes the content right. It enforces syntax only. Measured: a schema with four required fields and a prompt that named none ended in 5,469 blank characters and truncated JSON; with the fields named, the reply took 34 tokens. |
| Tool calling | The tool-call format the model was trained on and the vLLM parser for it. The server needs both `--enable-auto-tool-choice` and `--tool-call-parser`. A smoke test with your own tools, over several turns, with wrong arguments. How many model calls one user request causes. | Copying the parser name from a model card. Testing one successful call. Forgetting that agents multiply load: the demo agent needed 3 model calls and 1,519 prompt tokens, where the first call alone had 454 (3.3 times). The tool-call reliability of Qwen3-1.7B is unverified. |
| Multimodality | The input types you need (image, audio, video) and what they cost: encoder weights, profiling memory. Whether the engine can run the model text-only (Qwen3.5 has `--language-model-only`). Whether the licence differs for the multimodal variant. | Choosing a multimodal model for a text task. Missing a licence clause: the Llama 4 acceptable-use policy withholds rights for multimodal models from EU-domiciled individuals and companies (RESEARCH 11.3). |

### Size and architecture

| Criterion | What to look at | Common mistake |
| --- | --- | --- |
| Parameters | Stored parameters (all of them must be in VRAM), the checkpoint size on disk (`weights_gb` in `config/models.yaml`), the precision of each tensor. | Sizing from the name ("8B"). The headline and the stored tensors can differ: `config/models.yaml` records 1.7 B for Qwen3-1.7B, the checkpoint metadata lists 2,031,739,904 parameters (RESEARCH 5.1). `sizing.py` prints a note when disk size and parameters times bytes differ by more than 5 %. |
| Active parameters | For a mixture-of-experts model: the parameters used per token (Qwen3-30B-A3B: 30.5 B stored, 3.3 B active). Active parameters set the compute per token. Stored parameters set the VRAM. | Sizing VRAM from the active parameters. Expecting the quality or the speed of a dense model of the active size: both must be measured. |
| Dense or MoE | `architecture.type`, `experts` and `experts_per_token` in `config/models.yaml`. All experts stay in VRAM. The KV cache depends on the attention layout, not on the experts. Kernel and engine support for MoE on your GPU. | Reading "A3B" as "needs the memory of a 3B model". Assuming that MoE is as well-trodden as dense on every GPU: the open SM120 issues in RESEARCH 3.3 all concern MoE, MLA, NVFP4 or forced FlashInfer paths, and the MoE demo model needs its own smoke test. |
| Context | The native maximum (`context_native`, `max_position_embeddings`), the length you need (longest prompt plus longest output plus template overhead), the KV cost at that length (section 4), the quality at that length on your items. The workshop servers run with `max-model-len: 32768`. | Treating the maximum as what you can serve at your concurrency. Treating "supports 262k" as "answers correctly at 262k". Static YaRN scaling to 131,072 tokens can hurt short-text quality (the Qwen3-8B card warns about it). |

### Adaptation and engine

| Criterion | What to look at | Common mistake |
| --- | --- | --- |
| Fine-tuning support | Whether you need it at all: try the prompt, few-shot examples, retrieval, a longer context and constrained output first. If you do: base and instruct checkpoints, adapter support in the engine, a licence that allows derivatives, the effort to repeat it when the base model changes. | Fine-tuning to fix what a better prompt or retrieval fixes. Forgetting that a fine-tune belongs to one base revision. Curriculum outcome 2: justify either "no fine-tuning needed" or "fine-tune". |
| Quantization support | Which formats the publisher ships (Qwen3-8B-FP8 comes from Qwen itself), which formats the engine has kernels for on your GPU generation, the quality on your eval, and what really shrinks (the weights; the KV cache only with `kv-cache-dtype`). | Expecting half the memory from FP8: the 8B checkpoint goes from 16.38 GB to 9.44 GB, because embeddings and the output head stay in BF16. Trusting vLLM's hardware table: it has no Blackwell column, so "not listed" does not mean "unsupported"; run the model. Assuming a third-party 4-bit build loads on this GPU: unverified (RESEARCH 8.4, 8.5). |
| Engine compatibility | The architecture is in the engine's supported list at the pinned version (vLLM v0.31.0). Required flags, parsers and chat template. Whether it needs `trust_remote_code`. Notes for your GPU generation. Every flag from a model card checked against `vllm serve --help` of the pinned image. | "It is on Hugging Face, so it runs." Copying card flags: several Qwen3 cards still print `--enable-reasoning` (removed) and `--task` (replaced by `--runner`), see RESEARCH 5.4. |

### Resources and speed

| Criterion | What to look at | Common mistake |
| --- | --- | --- |
| VRAM | Weights plus KV cache (context times concurrency) plus overhead, against the budget: 94.97 GiB (usable) times 0.80 is 75.98 GiB here. Run `scripts/sizing.py`, then compare with the server's `GPU KV cache size` line. | Counting only the weights. Forgetting a second model on the same GPU (the embedding server takes 0.08 of it). Using the maximum context for every request. |
| Throughput | Aggregate output tokens per second at the concurrency you expect, measured with the shape of your workload (`benchmark/run.sh`, workloads in `benchmark/workloads/`). | Quoting single-request tokens per second. Using a vendor figure from other hardware. Repeating identical prompts so that the prefix cache flatters the result (measured: TTFT p50 391 ms, then 51 ms). |
| Latency | TTFT and inter-token latency at p95, at the expected concurrency, including queueing and the tokens spent on thinking. The curriculum's example SLO: TTFT p95 800 ms and 25 output tokens per second per request. | Using averages. Testing at concurrency 1 only. Not counting thinking tokens as time. |

### Legal

| Criterion | What to look at | Common mistake |
| --- | --- | --- |
| Licence and commercial restrictions | The `LICENSE` file at the pinned revision, the licence tag on the card, and any separate policy file. Thresholds and what they are measured on, naming duties, territorial limits, gating. Section 5. | Trusting the family name ("Qwen is Apache"). The licence belongs to a repository and a version, not to a family. Reading the card summary instead of the file. |

## 3. Why leaderboards are not enough, and a 30-item eval

### Why leaderboards are not enough

- They measure other tasks. Your task has your data, your language, your output format and your cost of failure.
- They average. A good mean can hide a bad slice: German, long documents, tool calls.
- The settings differ: thinking on or off, sampling, prompt format, precision. The checkpoint you serve (FP8, a third-party quantization) is rarely the checkpoint that was scored.
- Public test sets can leak into training data. You cannot check.
- A score contains no latency, memory, throughput, licence or operability. A model can top a chart and still not fit your GPU or your legal position.
- They age. New releases and renamed models arrive within weeks.

Use leaderboards to shortlist. Decide on your own eval.

### A 30-item task eval in an afternoon

About three and a half hours, one person, no framework.

| Time | Step | Result |
| --- | --- | --- |
| 30 min | Write the task in one paragraph: input, output, what a good answer is, what a wrong answer costs. Set the pass criterion, for example "at least 90 % of items, no failure in the critical slice". | `task.md` |
| 60 min | Collect 30 real items from tickets, documents, code or chats: 20 typical, 6 hard or odd, 4 that must be refused or answered with "not in the documents". Anonymise them. Take German items from real German text. Tag each item with a slice. | `items.jsonl` |
| 45 min | Write the check for each item. Prefer checks a script can run: exact match, regular expression, JSON field equality, "contains all of", unit tests for code. For free text, use at most three yes-or-no rubric questions. | the `check` field |
| 30 min | Write the runner. Send each item to the endpoint with fixed sampling (temperature 0 unless you test sampling), write down the thinking mode, and store reply, tokens, latency, model revision and profile (`sudo wsctl info`). Adapt `_chat()` and `is_correct()` from `experiments/quality_probe.py`. | `run.py`, `results.json` |
| 30 min | Run each candidate. Read every failure in full. Sort failures: wrong content, wrong format, refusal, too long, wrong language. | Results per slice, failure notes |
| 15 min | Freeze the file and tag it. Edit an item afterwards only to repair a wrong check, and then re-run all candidates. | A version tag |

One item as a JSON line:

```json
{"id": "q07", "slice": "german-formal", "prompt": "Wie viele Tage pro Woche darf ich im Homeoffice arbeiten?", "check": {"type": "regex", "pattern": "\\b(3|drei)\\b"}, "note": "current policy says 3 days, the archived one says 2"}
```

Hygiene:

- Same prompt, same sampling, same thinking mode for every candidate.
- Serve each candidate through a profile, so that `sudo wsctl info` records revision and arguments next to the result.
- Keep eval items out of your prompts. If you tune a prompt on the items, hold out 10 of them and do not look at them.
- Read at least ten failures yourself. A pass rate says how often, not why.

### What 30 items can and cannot tell you

Thirty items give wide intervals. These are 95 % Wilson intervals, computed with `wilson()` from `experiments/quality_probe.py`:

| Correct | Rate | 95 % interval |
| --- | --- | --- |
| 30 of 30 | 1.00 | 0.886 to 1.000 |
| 27 of 30 | 0.90 | 0.744 to 0.965 |
| 24 of 30 | 0.80 | 0.627 to 0.905 |

Consequences:

- Thirty items find candidates that fail, and large differences between candidates. They do not rank two good models.
- Compare candidates on the same items and look at the disagreements: where A is right and B is wrong, and the reverse. This pairing is much sharper than comparing two totals. `quality_probe.py compare` does it.
- To resolve smaller differences, add items on which candidates disagree. Adding more easy items adds nothing.
- The 2 % regression bound in the workshop's example SLO cannot be measured with 30 items. It needs hundreds, and still only gives a resolution of a few points.

### `experiments/quality_probe.py`: a self-generated spot check, and its limits

What it does:

- It generates items from templates with a fixed seed: a pallet arithmetic word problem, a number to extract from a policy text, and a message to classify into one of four classes. Every item has a known answer. No external dataset is involved.
- It asks greedily with thinking switched off (`temperature: 0`, `enable_thinking: false`).
- It makes two measurements per deployment: accuracy with a Wilson interval, and agreement of 32 open-ended completions with those of a reference deployment, including how far they match before diverging.
- `compare` pairs the items of two runs.

```bash
python3 experiments/quality_probe.py run --label bf16 --out bf16.json
python3 experiments/quality_probe.py compare bf16.json fp8.json
```

It exists so that the quantization experiment has a quality number (curriculum block `d2-06-quantization`).

Its limits, read from the code:

- The items are synthetic, English, short and single-turn. It has no German, no domain text, no long context, no tools, no JSON schema.
- Three narrow task kinds. The answer is "the value only" within 16 tokens, which rewards format discipline.
- Thinking is off. The Qwen3 card says not to use greedy decoding in thinking mode, so the probe measures a different regime from a deployment that thinks.
- It compares two deployments of one model well, and it can flag a large drop. It cannot prove that two models are equal, and it cannot choose between models. If every candidate scores near the ceiling, it separates none of them.

What to copy is the pattern: items with known answers, a fixed seed, a strict but format-tolerant checker, an interval, a paired comparison, and the label and settings stored with every run.

## 4. The memory arithmetic, worked

```text
WEIGHTS + KV CACHE + RUNTIME OVERHEAD = VRAM REQUIREMENT
KV bytes per token = 2 (K and V) x layers x KV heads x head_dim x bytes per element
```

The architecture fields come from `config/models.yaml`. The tool is `scripts/sizing.py`. Its overhead term (4 GiB) is an assumption. The vLLM budget is `gpu-memory-utilization` times the usable GPU memory, which vLLM reports as 94.97 GiB on the workshop GPU (the nominal 96 GB card): 0.80 times 94.97 GiB is 75.98 GiB.

### The workshop's models

| Config role | Model and precision | Checkpoint on disk (GB) | Parameters stored (B) | Active (B) | Layers | KV heads | head_dim | KV bytes per token (BF16 KV) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `primary` | Qwen/Qwen3-8B, BF16 | 16.38 | 8.2 | 8.2 | 36 | 8 | 128 | 147,456 |
| `quantized` | Qwen/Qwen3-8B-FP8, FP8 | 9.44 | 8.2 | 8.2 | 36 | 8 | 128 | 147,456 |
| `small` | Qwen/Qwen3-1.7B, BF16 | 4.06 | 1.7 | 1.7 | 28 | 8 | 128 | 114,688 |
| `moe_demo` | Qwen/Qwen3-30B-A3B-FP8, FP8 | 32.45 | 30.5 | 3.3 | 48 | 4 | 128 | 98,304 |
| `embedding` | Qwen/Qwen3-Embedding-0.6B, BF16 | 1.19 | 0.6 | 0.6 | 28 | 8 | 128 | not used (pooling runner) |
| `gguf_demo` | Qwen/Qwen3-8B-GGUF (llama.cpp, Ollama) | not in config | 8.2 | 8.2 | 36 | 8 | 128 | not served by vLLM |

For one sequence of 32,768 tokens the KV cache takes (computed): Qwen3-8B 4.5 GiB, Qwen3-1.7B 3.5 GiB, Qwen3-30B-A3B 3.0 GiB. FP8 weights do not change KV bytes per token. An FP8 KV cache halves it (73,728 bytes for Qwen3-8B).

### Example 1: Qwen3-8B in BF16 on the baseline profile

```bash
python3 scripts/sizing.py --model primary --precision bf16 --context 32768 --concurrency 8
```

| Step | Value | Source |
| --- | --- | --- |
| Budget | 94.97 GiB usable x 0.80 = 75.98 GiB | server log: "Desired GPU memory utilization is (0.8, 75.98 GiB)" |
| Weights | 8.2 B x 2 bytes = 15.27 GiB | `sizing.py`; measured in memory: 15.27 GiB |
| Overhead | assumed 4.00 GiB; measured 75.98 - 15.27 - 58.14 = 2.57 GiB (0.87 GiB outside PyTorch's allocator, 1.70 GiB peak activations, CUDA graphs 0.21 GiB, minus a 0.24 GiB over-estimate that vLLM gives back) | `sizing.py` default; server log |
| KV bytes per token | 2 x 36 x 8 x 128 x 2 = 147,456 | `config/models.yaml` |
| KV pool, estimated | 75.98 - 15.27 - 4.00 = 56.71 GiB, so 412,893 tokens | `sizing.py` (computed) |
| KV pool, server | "Available KV cache memory: 58.14 GiB" | measured |
| Capacity from the server's own number | 58.14 GiB / 147,456 bytes = 423,363 tokens | computed |
| Capacity reported by the server | `GPU KV cache size: 423,328 tokens` | measured |
| Requests at the full 32,768 tokens | 423,328 / 32,768 = 12.92 | "Maximum concurrency 12.92x", measured |

Reading the result:

- The hand formula and the server agree: 423,363 predicted against 423,328 reported (ratio 0.9999).
- The `sizing.py` estimate is 2.5 % low (412,893 against 423,328). The whole gap is the assumed overhead: 4.00 GiB assumed against 2.57 GiB measured, and 1.43 GiB is about 10,400 tokens. That is inside the 10 % bound of curriculum outcome 4, and it errs on the safe side.
- A pool of this size holds about 51 requests of 8,192 tokens (computed from the `sizing.py` pool) or 12.9 requests of 32,768 tokens. Context and concurrency trade against each other one for one.

### Example 2: FP8 weights

| Quantity | BF16 | FP8 | Source |
| --- | --- | --- | --- |
| Checkpoint on disk | 16.38 GB | 9.44 GB | `config/models.yaml` |
| Weights in memory | 15.27 GiB | 8.85 GiB | measured |
| Available KV memory | 58.14 GiB | 64.56 GiB | measured |
| KV capacity | 423,328 tokens | 470,096 tokens | measured |

- What FP8 frees (15.27 - 8.85 = 6.42 GiB) goes into the KV pool one for one (58.14 + 6.42 = 64.56 GiB). Capacity rises by 46,768 tokens, 11 %.
- Weights are a minor part of a 96 GiB card. FP8 weights buy decode speed, not capacity. Indicative smoke runs at concurrency 1 gave an ITL p50 of 11.6 ms (BF16) and 7.3 ms (FP8). Aggregate throughput at concurrency 8 was 549 and 838 tokens per second.
- The `sizing.py` estimate for FP8 takes 8.2 B times 1 byte (7.64 GiB) and is therefore slightly optimistic. The tool prints a note: the checkpoint is 8.79 GiB. Use the checkpoint size as the weights term.

### Example 3: FP8 KV cache and a constrained budget

- With `kv-cache-dtype: fp8` a token costs 73,728 bytes instead of 147,456. In the same bytes, twice the tokens fit. This is the formula's prediction; the `kv-fp8` and `kv-constrained-fp8kv` profiles exist to measure it, and quality must be checked as well.
- The `kv-constrained` profile caps the pool at 4 GiB (`kv-cache-memory-bytes`). That is 1,820 blocks of 16 tokens, about 29,120 tokens, or 0.89 requests of 32,768 tokens (computed, RESEARCH 3.8). With an FP8 KV cache: 58,240 tokens, 1.78 requests. Because the pool holds less than one 32,768-token request, vLLM refuses to start with the default `max-model-len` (measured: "4.5 GiB KV cache is needed, which is larger than the available KV cache memory (4.0 GiB)... the estimated maximum model length is 29104"); the profile therefore also sets `max-model-len: 16384`.
- `oom-demo` keeps the model's full 40,960-token context in the same 4 GiB and fails on purpose with that message (5.6 GiB needed, computed). Asking for 1,048,576 tokens (the KV for one such sequence would be 144 GiB, computed) is rejected earlier, by the model's own limit (`--set max-model-len=1048576`, measured).

### Example 4: the small model

```bash
python3 scripts/sizing.py --model small --precision bf16 --context 32768 --concurrency 8
```

- Weights are 4.06 GB on disk, a quarter of the 8B model's 16.38 GB.
- KV per token is 114,688 bytes, 78 % of the 8B model's. Fewer layers help, the same eight KV heads do not. So the pool holds only about 1.3 times more tokens per byte (computed), although the weights are four times smaller.
- `sizing.py` reports a pool of about 651,928 tokens (19.9 requests of 32,768). It is slightly optimistic for the same reason as in example 2: the checkpoint is 3.78 GiB, the tool computes 3.17 GiB.

### Example 5: the mixture-of-experts demo model

```bash
python3 scripts/sizing.py --model moe_demo --precision fp8 --context 32768 --concurrency 8
```

- All 30.5 B parameters are stored, so the FP8 checkpoint is 32.45 GB (30.22 GiB) although only 3.3 B parameters are active for a token. VRAM follows the stored count.
- KV per token is 98,304 bytes: lower than the dense 8B model because it has 4 KV heads, not 8, despite 48 layers.
- `sizing.py` says it fits and shows a pool of about 484,908 tokens. It is optimistic by the gap between 28.41 GiB and the 30.22 GiB checkpoint.
- No measurement of this model on the workshop GPU is in the repository. Smoke-test it before relying on it.

### The speed twin of the memory arithmetic

Decoding one token reads all weights once. The lower bound for one decode step is weights divided by memory bandwidth. The workshop GPU has 1,597 GB/s.

| Model | Bound | Measured ITL p50, concurrency 1 |
| --- | --- | --- |
| Qwen3-8B BF16 | 16.38 GB / 1,597 GB/s = 10.3 ms | 11.6 ms (13 % above the bound) |
| Qwen3-8B-FP8 | 9.44 GB / 1,597 GB/s = 5.9 ms (computed) | 7.3 ms |

Weights that are half the size decode faster. That is why precision belongs in a model-selection decision, next to quality.

### What the formula leaves out

- Block rounding, CUDA graph memory and activations (they sit inside the overhead term).
- Hybrid and sliding-window attention. For Qwen3.5-9B the KV per token is 32,768 bytes, 4.5 times smaller than Qwen3-8B's (RESEARCH 5.2). `sizing.py` assumes full attention in every layer and is wrong for such models. Take the layer layout from the model's `config.json` and trust the server log.
- A second model on the same GPU. The embedding server takes about 0.08 of the memory in this workshop.

Use `sizing.py` to reject candidates early. Use the server's `GPU KV cache size` line to confirm.

## 5. Licences

Read this section with RESEARCH 11. It records what the licence texts said when they were read (October 2026). The research notes state: this is not legal advice and no counsel reviewed it. For anything beyond internal evaluation, ask counsel.

### How to read a licence

1. Resolve the full 40-character commit SHA and write it down. A licence can change in a later commit.
2. Compare three places, because they can differ: the licence tag or card front matter, the `LICENSE` file at that revision, and any separate policy file (acceptable-use policy, `USAGE_POLICY`).
3. Find the grant: use, modify, distribute, derivatives, outputs.
4. Find every threshold and what it is measured on: users, monthly revenue, trailing-twelve-month revenue, or the revenue of your employer.
5. Find naming duties: display strings, name prefixes, `Notice` files, notice retention.
6. Find use restrictions and territorial limits.
7. Check gating (`gated` is `False`, `auto` or `manual`) and whether each participant needs an account. All pinned workshop models are ungated.
8. For quantized or fine-tuned third-party builds, read that repository's own licence field and the base model's terms.
9. Write the commercial implication for your own situation in one sentence, and write down what you could not determine.

### Open weights and open source

- **Open weights** means that the parameters are published, often under a permissive or custom licence. The training data information and the training code need not be.
- **Open source AI** is the term of the [OSI Open Source AI Definition](https://opensource.org/ai/open-source-ai-definition) (version 1.0). It requires three things together, under OSI-approved terms: information about the training data, the complete code to train and run the system, and the parameters.
- By that wording, the Qwen, Gemma, Mistral, DeepSeek, gpt-oss and Llama checkpoints are at best open weights, even under Apache-2.0 or MIT. This was not audited model by model.
- OSI states that models that passed its validation include Pythia, OLMo, Amber, CrystalCoder and T5, and that it analysed Llama 2, Grok, Phi-2 and Mixtral, which did not pass. These are not certifications.
- The workshop says "open-weight" for every model in this repository. It uses "open source" only where the three elements are met. [`DIGITAL-SOVEREIGNTY.md`](DIGITAL-SOVEREIGNTY.md) uses the same distinction when it asks what a team can reproduce or audit.
- Separate question: the EU AI Act exempts some providers of general-purpose models under a free and open-source licence from some duties (Art. 53(2)). The test looks at the licence (no scale thresholds, no non-commercial limits), at monetisation, at public weights and architecture information, and at systemic risk. It concerns the provider's obligations, not whether you may run the model. RESEARCH 11.2 has the detail; running or LoRA-fine-tuning a downloaded model in a workshop does not make you a provider.

### Licence drift

The licence belongs to a repository at a revision. It does not belong to a family. Adjacent models of one family can differ. A licence read in a blog post, on a slide, or on an earlier model can be wrong for the checkpoint you pin.

| Family | Earlier | Now (RESEARCH 11.4) |
| --- | --- | --- |
| Qwen | Qwen3, 3.5, 3.6 and 3.8-27B: Apache-2.0 | Qwen3.8-2.4T-A95B under the Qwen3.8-Max License, Qwen3.8-Flash-Next under the Qwen Community License 1.0 (August 2026) |
| Google Gemma | Older Gemma repositories keep the `gemma` licence tag | Gemma 4: Apache-2.0 |
| Meta | Llama 3.x and 4 community licences | Muse Glimmer 30B: Apache-2.0 plus a separate usage policy |
| Mistral | Most models Apache-2.0 | Medium 3.5 and Devstral 2: Modified MIT with a US$20M monthly-revenue ceiling |
| DeepSeek | V3: DeepSeek License Agreement 1.0 with use-based restrictions | V3-0324, R1 and V4.x: MIT |
| Moonshot | Kimi K2.x: Modified MIT | Kimi K3: a stricter custom licence |
| Zhipu | GLM-5.2, 5.1, 4.7-Flash: MIT | GLM-5.3: custom licence with a security-review clause; GLM-5.3-Flash stays MIT |

There is no size pattern: Mistral Large 3 (675 B) is Apache-2.0 while Medium 3.5 (128 B) is Modified MIT. The workshop's own rule is to read the licence from the repository at the pinned revision on the day of pinning, and again when the pin changes.

### Thresholds and conditions per family

Licences with a scale, revenue or field-of-use condition (RESEARCH 11.3):

| Family and repositories | Condition that matters | Measured on, and carve-outs |
| --- | --- | --- |
| Llama 4 (Scout, Maverick), Llama 4 Community License | Above 700 million monthly active users: a licence request that Meta may grant "in its sole discretion". "Built with Llama" display. Models improved with Llama outputs must start their name with "Llama". A `Notice` file. The acceptable-use policy withholds multimodal rights from EU-domiciled individuals and companies. | Users of the licensee's and its affiliates' products in the month before the release date. The EU sentence does not apply to end users of a product that incorporates the model. |
| Llama 3.1, 3.3 | Licence clause text was not read in the research notes. | Do not assume it matches Llama 4. |
| Mistral Medium 3.5, Devstral 2 (Modified MIT) | No rights at all if global consolidated monthly revenue of your company (or your employer) exceeds US$20 million. Covers derivatives and third-party hosting. | The whole employer. No internal-use carve-out in the notes. The strictest case for a workshop. |
| Kimi K2.x (Modified MIT) | Display the model name in the UI above 100 million monthly active users or US$20 million monthly revenue (an OR). | The commercial product or service. |
| Kimi K3 | A Model-as-a-Service business above US$20 million over any 12 months needs a separate agreement. Display rule as K2.x. | Licensee and affiliates. Internal use is excepted. |
| Qwen3.8-2.4T-A95B (Qwen3.8-Max License) | A Model-as-a-Service or AI Work Assistant business above US$50 million in any 12 months needs a separate licence. Display the name above 100 million monthly active users or US$20 million monthly revenue. | Licensee and affiliates. Internal use that exposes nothing to third parties is excepted. |
| Qwen3.8-Flash-Next (Qwen Community License 1.0) | Any Model-as-a-Service or AI Work Assistant business needs a separate licence, with no revenue floor. Same display rule. | Licensee and affiliates. Same internal-use exception. |
| GLM-5.3 | A Model-as-a-Service business above US$10 billion over 12 months must pass a security review. | Licensee and affiliates. |
| DeepSeek-V3 (December 2024) | Use-based restrictions that must be passed on to downstream users. | Per the agreement. |
| Muse Glimmer 30B, gpt-oss | Apache-2.0 plus a separate usage policy. | Check whether the policy binds you; the notes could not settle it for Muse Glimmer. |

Licences without a scale threshold in the texts read: Qwen3, 3.5, 3.6, 3.8-27B and the Coder, VL and Embedding models (Apache-2.0); Gemma 4 (Apache-2.0); the Mistral Apache set (Ministral 3, Small 3.2 and 4, Devstral Small 2, Large 3); DeepSeek V3-0324, R1 and V4.x (MIT); GLM-5.3-Flash and Phi-4-reasoning-vision (MIT); Granite 4.2, EuroLLM-9B and Apertus (Apache-2.0, Apertus gated with automatic approval); Nemotron 3.5 Lightning (OpenMDW-1.1). "No threshold" does not mean "no duties": read the notice and attribution terms.

Thresholds measure different things on different entities. Ask for each: whose users, whose revenue, over which period, and is internal use excepted?

### The checklist row

One row per model, filled before a lab or a project uses it: **Publisher, Model, Revision, License, Commercial implications, Source.** The Revision column makes the row auditable. The Source column should point at the licence file at that revision, not at the card. `workshop-artifacts/model-selection.md` carries the empty table. `config/models.yaml` stores revision, licence, commercial note and source of every pinned model, and `pnpm check` rejects a revision that is not a full SHA.

| Publisher | Model | Revision | License | Commercial implications | Source |
| --- | --- | --- | --- | --- | --- |
| Qwen | Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | Apache-2.0 | No scale threshold or naming duty in the text. Notice duties per the Apache-2.0 text. | [LICENSE at the revision](https://huggingface.co/Qwen/Qwen3-8B/blob/b968826d9c46dd6066d109eabc6255188de91218/LICENSE) |
| Mistral AI | Mistral-Medium-3.5-128B | `22b2b868a15677cfa6061277ed2f653d1349a9ab` | Modified MIT | No rights if the licensee's or employer's monthly revenue exceeds US$20 million; covers derivatives and third-party hosting. | [Medium 3.5 LICENSE](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE) |
| Meta | Llama-4-Scout-17B-16E-Instruct | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` | Llama 4 Community License and acceptable-use policy | 700 million monthly-active-user licence request; "Built with Llama"; "Llama" name prefix on derived models; Notice file; EU multimodal clause in the policy; gated, manual approval. | [Llama 4 licence](https://www.llama.com/llama4/license/) |
| Qwen | Qwen3.8-Flash-Next | `de4b8e4d43b917e7706784d8bb445c9af86a3540` | Qwen Community License 1.0 | Any Model-as-a-Service or AI Work Assistant business needs a separate licence; model-name display above the stated limits. | [Flash-Next LICENSE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE) |

The first row is a pinned workshop model (the other five are in `config/models.yaml`). The other three show how a row reads when the licence is not Apache-2.0. They are licence case studies, not lab defaults.

## 6. Worksheets for the four Lab 1 scenarios

The numbers come from [`tasks/01-model-selection.md`](../tasks/01-model-selection.md). Fill the block for each scenario in `workshop-artifacts/model-selection.md`: model, precision, hardware, engine, context, reasoning, why, what I gave up. The worksheets below hold questions and trade-offs. They hold no answers. The trainer's reference answers are not in this repository.

For each scenario you should be able to produce: a `sizing.py` run for your choice, the licence row, a sentence on how you would test quality, the smaller model you considered and why you rejected it, and what you gave up.

### Scenario A: internal German-language enterprise assistant

Given: 300 employees; 20 concurrent users at peak; the data must not leave the company; answers within 10 s; 3,000 tokens of retrieved context per question.

Turn the requirement into numbers (do the arithmetic yourself):

- Tokens of KV cache for 20 concurrent requests, each with retrieved context, question, system prompt, history and answer. Which context length must the server allow?
- What "within 10 s" means: first token or complete answer? Which output length do you assume? What TTFT and ITL does that leave at 20 concurrent requests?

Questions to ask:

- What is a good answer: faithful to the documents, cites its source, says "I do not know" when the documents are silent? How would you test that with 30 items, and how many of them are German, formal, or contain compound words and tables?
- What happens when documents contradict each other, for example a superseded policy next to the current one? Whose job is that, the model's or the pipeline's?
- What evidence do you have that the model's German is good enough: a vendor list, or items of your own? How many tokens does a typical German document use on this tokenizer?
- Does answering from documents need reasoning? What does thinking cost in latency and tokens at 20 concurrent users, and what does it improve on your items?
- Do you need structured output (citations as JSON) or tool calling? Which parser does the candidate need?
- What else must run on the GPU: an embedding model for retrieval? How much of the budget does it take?
- "Must not leave the company": which parts are in scope? Weights, prompts, logs, embeddings, telemetry. Does the licence allow your internal commercial use at your size? Which threshold could apply to your employer?
- When the model is replaced next year, how do you re-run the eval and the benchmark?

Trade-offs in play: quality against latency (thinking); context length against concurrency (KV cache); German quality against model size and licence; one model against a separate retrieval model; precision against headroom; answer freshness against retrieval design.

### Scenario B: customer-service classification and information extraction

Given: 40,000 tickets per day, peaks of 5 per second; 300 input and 60 output tokens; JSON output; 95 % of tickets within 2 s.

Turn the requirement into numbers:

- Tickets per second on average, against the peak of 5 per second.
- Input and output tokens per second at the peak.
- What "95 % within 2 s" leaves for queueing when the peak arrives.

Questions to ask:

- What are the classes and fields? Are there labelled historical tickets to build the eval from? What does a wrong class cost, and does it cost the same for every class?
- How many items per class do you need to see the error rate you care about? What is the interval on 30 items?
- Does classification need reasoning? How would you test thinking on and off, and what would the extra tokens cost at 5 requests per second?
- How small can the model go before the error rate on your items moves? Which smaller models can you actually test here, and what do they score?
- How do you describe the output? The schema, and also the fields in the prompt. What happens with a ticket that fits no class, or in another language?
- Do few-shot examples help, and what do they cost in prefill? Do they form a shared prefix that the prefix cache can reuse?
- Would fine-tuning be justified, or would a better prompt do? If fine-tuning: who owns the labelled data, and does the licence allow derivatives?
- Tickets contain personal data. What is logged, where, and for how long?
- What happens when the peak exceeds capacity: queue, drop, or degrade?

Trade-offs in play: error rate against cost per ticket; model size against peak capacity; thinking against latency; few-shot length against prefill cost; strict schema against flexibility; headroom for the peak against idle GPU time.

### Scenario C: coding assistant

Given: 100 developers; chat with 16,000 to 32,000 tokens of repository context; first token within 1 s for 95 % of requests.

Turn the requirement into numbers:

- How many of the 100 developers send a request at the same moment? State your assumption.
- KV cache per sequence at 16,000 and at 32,000 tokens for each candidate (`sizing.py`), and how many such sequences the pool holds.
- Whether a 32,000-token prompt plus an answer fits the context length you serve.

Questions to ask:

- Which tasks: explain, review, generate, refactor, write tests? Which languages and frameworks? Does the assistant call tools (read a file, run tests)? If so, remember that every tool round re-sends the conversation.
- How would you evaluate: 30 real tasks from your own repository with tests that run? What does a wrong suggestion cost?
- What does prefill cost for 16,000 to 32,000 tokens, and does a TTFT of 1 s survive at your concurrency? Can the repository context be a shared prefix between requests of the same developer? How would you check?
- Does thinking improve the results on your tasks, and can you afford its tokens within the latency you promised?
- Is a dedicated coder model worth it against a general model of the same size, and which tool-call parser, template and licence does it bring?
- Does the candidate fit one GPU at your concurrency? If not, what do you need: a bigger GPU, quantization, several GPUs? That is a finding, not a failure.
- Which licence thresholds are measured on your employer, and which on your product?
- The code is confidential. Which parts of the stack must stay in your control?

Trade-offs in play: context length against concurrency; TTFT against prompt size; model size and quality against the latency promise; thinking against latency; dedicated coder model against a general model; KV precision against quality; one shared server against several replicas.

### Scenario D: high-volume document-processing pipeline

Given: 2 million documents, run once a month; 3,000 input and 300 output tokens each; finish within 72 hours; cost per document matters, latency does not.

Turn the requirement into numbers:

- Documents per second, input tokens per second and output tokens per second needed to finish in 72 hours.
- The throughput your candidate achieves at high concurrency (`./scripts/benchmark.sh --workload doc-processing` has a similar shape: 2,000 input and 400 output tokens).
- GPU hours, and with the price per GPU hour quoted for the workshop GPU, cost per document.

Questions to ask:

- What is the quality per field, and what error rate is tolerable? How do you detect failures among 2 million results: schema validity, spot checks, a human sample?
- Is thinking worth it? Output length multiplies cost: measure the distribution of output tokens with thinking on and off, not only the mean.
- Which levers raise throughput: a smaller model, FP8 weights, an FP8 KV cache, higher concurrency, a shared instruction prefix? For each: what do you measure afterwards, and what does it do to quality (`experiments/quality_probe.py` is the pattern)?
- Are the inputs text, or scanned pages and images? Does that change the model class?
- Does the job need a server with an HTTP API, or is it a batch? How do you retry and resume a 72-hour run when a restart takes 40 s to 3 minutes?
- How much slack is in 72 hours, and would a slower, cheaper setup still make it?
- If you process documents for other companies, could a licence's Model-as-a-Service definition apply to you?

Trade-offs in play: cost per document against accuracy; a smaller model plus human review against a larger model; precision against quality; wall-clock time against GPU count; thinking against cost; simplicity of one server against throughput tuning.

## 7. What changes when the model changes

A model is more than weights. Replace it and each row below can break or move. The profile mechanism ([`config/vllm-profiles/`](../config/vllm-profiles/), rendered by [`infra/pod/render-profile.py`](../infra/pod/render-profile.py)) carries most of them.

| What changes | Why it matters | Where it lives here | What to do |
| --- | --- | --- | --- |
| Tokenizer | Token counts decide context budget, cost and KV use. German and code tokenize differently. | `tokenizer*` files at the pinned revision (fetched by `infra/pod/fetch-models.py`) | Count tokens of your real documents with the new tokenizer (`/tokenize`). Re-derive the context you need. |
| Chat template | Roles, system-prompt handling, the thinking switch and the tool-call format are part of the template. | `tokenizer_config.json` or a template file at the pinned revision | Render one conversation and read it. Test `chat_template_kwargs`. Qwen3 thinks by default; Gemma 4 does not; some releases ship no Jinja template. |
| Tool-call parser | The server turns model text into `tool_calls` with a parser per family. Wrong parser: tool calls arrive as plain text. | `tool-call-parser` and `enable-auto-tool-choice` in `config/vllm-profiles/base.yaml` (`hermes` for Qwen3) | Set the parser for the new family in its profile. Take the name from the vLLM docs, not the card. Smoke-test with `apps/tool-calling-demo/agent.py`. |
| Reasoning parser | It splits thinking from the answer. Wrong or missing parser: a startup error, or thinking leaks into `content`. | `reasoning-parser` in `base.yaml` (`qwen3`) | Same as above. Clients read `reasoning`, not the old `reasoning_content`. |
| Sampling defaults | Cards recommend values per mode. The profiles set `generation-config: vllm`, which ignores the model's `generation_config.json`. | `base.yaml` | Set sampling on every request. Record it with every result. |
| Context | The native maximum, the YaRN option and the length you allow differ per model. | `context_native` in `config/models.yaml`; `max-model-len` in `base.yaml` (32768) | Set `max-model-len` to what you need, not to the maximum. |
| KV bytes per token | Layers, KV heads, head dimension and attention layout decide concurrency. Hybrid and sliding-window models change the picture by a factor of 4 or 5. | `architecture` block in `config/models.yaml`; `scripts/sizing.py` | Fill the fields from `config.json`. Compare the estimate with the `GPU KV cache size` line. |
| Weights and precision | They decide the fit and the decode speed. | `weights_gb`, `precision` in `config/models.yaml` | Use the checkpoint size as the weights term. |
| Quantization support | Pre-quantized checkpoints are detected from the model files. Kernels differ per GPU generation. | `quantization` and `kv-cache-dtype` are allowed `--set` overrides (`infra/pod/render-profile.py`) | Smoke-test on the real GPU. Re-run the eval at that precision. |
| Served model name | Clients pass a model name. A wrong name gives 404. | `served-model-name` in each profile; `WORKSHOP_MODEL` is set to `Qwen/Qwen3-8B` at login | The `fp8` profile keeps the BF16 name. The `small` and `embedding` profiles do not: change `WORKSHOP_MODEL` or pass `--model`. |
| Embedding model (RAG) | Another embedding model means another vector size (1,024 here) and a different query instruction. | `EMBEDDING_MODEL`; `config/vllm-profiles/embedding.yaml` | Re-embed every document. Never mix vectors of two models. |
| Revision and licence | A new revision can change files and licence. | `revision` (40 characters, enforced by `render-profile.py` and `pnpm check`), `license`, `commercial_use`, `source` in `config/models.yaml` | Pin the SHA, add the licence row, fetch the model. |
| Engine flags | Card flags go stale. Some models need a plugin or `trust_remote_code`. | `FORBIDDEN_KEYS` in `render-profile.py` includes `trust-remote-code` | Check every flag against `vllm serve --help` of the pinned image. A model that needs remote code cannot run on the workshop pods. |
| Memory budget | Another model needs another split between weights and KV. | `gpu-memory-utilization` (0.80, plus 0.08 for the embedding server) | Re-run `sizing.py` and read the startup log. |
| Every baseline | TTFT, ITL, KV capacity and quality are all void. | `experiments/`, `benchmark/`, the eval from section 3 | Re-measure, with a fresh seed. The result's `model_revision` and `server_args` say which model produced it. |

### The profile mechanism

A profile is a YAML file in `config/vllm-profiles/` with keys that are `vllm serve` flags without the dashes. It may `extends:` another profile; the child wins. `base.yaml` holds what every server shares: the loopback bind, port 8000, `dtype`, `max-model-len`, the parsers, the structured-output backend. A model profile adds `model`, `revision` and `served-model-name`. The `fp8` profile is five lines on top of `baseline`.

`infra/pod/render-profile.py` resolves the chain, applies `--set` overrides from an allowlist, refuses what would weaken the deployment (a public bind, `trust-remote-code`, an API key in a file, an unpinned revision) and writes the merged YAML that `vllm serve --config` reads. `wsctl start <profile>` calls it, starts the server, rolls back to the previous profile if the start fails, and writes the provenance file that the benchmark harness attaches to every result.

```yaml
# config/vllm-profiles/<name>.yaml (a sketch with placeholders)
extends: base
description: "One line: what this profile is for."
model: <org>/<model>
revision: <40-character commit SHA from config/models.yaml>
served-model-name: <org>/<model>
# Only what differs from base.yaml. Take parser names from the vLLM docs for the pinned version:
tool-call-parser: <parser>
reasoning-parser: <parser>
max-model-len: <tokens you need>
```

Adding a candidate model, in order:

1. Pin it in `config/models.yaml`: full SHA, architecture fields, licence, commercial note, source.
2. Fetch it on the pod: `fetch-models.py --models <role>` (the trainer does this; the deployment script is idempotent).
3. Write the profile. Participants cannot do this on the pods: the profiles directory is root-owned and `infra/verify-machine.sh` checks it. A new profile is committed to the repository and deployed by the trainer. Participants try variants of an existing profile with `--set`.
4. Validate it anywhere: `python3 infra/pod/render-profile.py <name> --dir config/vllm-profiles --out /tmp/check.yaml`.
5. Start it: `sudo wsctl start <name>`. This restarts the server for the whole group. Read the log; `sudo wsctl info` shows profile, arguments and startup facts.
6. Compare the log's `GPU KV cache size` with your `sizing.py` estimate.
7. Re-run your eval and the benchmark. Write the decision record.
