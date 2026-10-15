# Results: demos

Raw files: [`benchmark/results/reference/demos/`](../../benchmark/results/reference/demos/). Every file carries hardware, model revision, engine version, server arguments and date. Hypotheses: [`README.md`](README.md).

**Not run in this validation, and not measured anywhere in this repository:** demo 3 (tensor parallelism, which needs a two-GPU pod; see [`../tensor-parallel/RESULTS.md`](../tensor-parallel/RESULTS.md)), demo 4 (vLLM against Ollama or llama.cpp) and demo 5 (the mixture-of-experts model). They remain trainer demonstrations to prepare; the preparation notes below say what is missing. Only demos 1 and 2 (speculative decoding, and the two starts that must fail) have results.

## Setup

1× NVIDIA RTX PRO 6000 Blackwell Server Edition, `Qwen/Qwen3-8B` BF16, vLLM 0.31.0. One session, no repetitions.

## 1. Speculative decoding with n-gram drafting

`spec-ngram` lets the engine guess the next four tokens by looking for the last two to five tokens earlier in the same prompt and output (no second model); a step then verifies the guesses and keeps those that match. It pays when the output repeats the input.

| Workload | Profile | Concurrency | Tokens/s per request | ITL p50 (ms) | Aggregate tokens/s | TTFT p50 (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| Copy the text exactly (1,000 in, up to 350 out) | baseline | 1 | 86.8 | 11.5 | 86.5 | 24 |
| | spec-ngram | 1 | 197.7 | 12.8 | 203.4 | 22 |
| | baseline | 16 | 83.2 | 12.0 | 1,310.5 | 77 |
| | spec-ngram | 16 | 160.2 | 15.8 | 2,499.2 | 59 |
| Open questions, answers are new text (about 20 in, up to 200 out) | baseline | 1 | 87.1 | 11.5 | 86.6 | 22 |
| | spec-ngram | 1 | 87.0 | 12.5 | 94.6 | 20 |
| | baseline | 16 | 86.3 | 11.6 | 1,354.2 | 45 |
| | spec-ngram | 16 | 76.9 | 14.1 | 1,164.4 | 40 |

- **On a copy task it is a large win**: ×2.3 per request at concurrency 1 and ×1.9 aggregate at 16. One step now takes longer (12.8 against 11.5 ms) but carries several tokens: over all speculative runs 14,825 of 34,053 drafted tokens were accepted (43.5 %), 1.74 per draft.
- **The hypothesis that it stops helping under load was wrong for this workload**: at concurrency 16 the GPU is still bound by memory traffic, so checking extra tokens in the same step costs little, and the gain is almost as large as at concurrency 1.
- **On new text it gives nothing at concurrency 1 and costs at concurrency 16**: the per-request speed is unchanged (87.0 against 87.1 tokens/s) and at 16 clients the aggregate throughput falls by 14 % (1,164 against 1,354) and the per-request speed by 11 %: guesses that fail are wasted work, and at high load the work is no longer free.
- **The harness's own synthetic prompts are not a control.** The first run of this experiment used the default synthetic prompts (sentences drawn from a small pool) as the "unrelated" control and showed speculative decoding winning there too. The cause: the model copies them. In one answer 146 of 157 four-word sequences came from the prompt. A synthetic benchmark can flatter any technique that exploits repetition; the open-question prompts (`benchmark/workloads/open-questions.jsonl`) are the control used here.

## 2. Configurations that cannot work

Two ways to ask for something the server refuses, each started with `wsctl start oom-demo` while the baseline was serving:

| Request | What happened |
| --- | --- |
| `oom-demo`: the model's full context (40,960 tokens) with a 4 GiB KV pool | The engine exits during startup, because one request of that length needs more KV memory (computed: 5.6 GiB) than the pool has. `wsctl` rolls back to `baseline`, which was healthy again after about 40 seconds. |
| `oom-demo --set max-model-len=1048576` | A different check fires first, in the model configuration: "User-specified max_model_len (1048576) is greater than the derived max_model_len (max_position_embeddings=40960.0 ...)". The model's own limit is checked before the memory. Rolled back as well. |

Both runs left the server healthy (`healthy afterwards: True` in the runner log). In the first run the saved last 25 log lines contained only the generic "Engine core initialization failed" error, not the root-cause line; `wsctl` now prints the lines that name the cause first (see [`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md), incident 17). The same arithmetic produced the failure of the first `kv-constrained` profile (see [`../context-length/RESULTS.md`](../context-length/RESULTS.md)): "4.5 GiB KV cache is needed, which is larger than the available KV cache memory (4.0 GiB)".

## What surprised

- The control for speculative decoding failed in the first run (see above): the benchmark's own prompts were copyable.
- Speculation helped almost as much at concurrency 16 as at 1 on repetitive output.

## Caveats

- One session, no repetitions; 16 to 32 requests per row. The copy task's prompts were eight different texts cycled, so the prefix cache answered most prompt tokens (98.7 % hit rate): the TTFT of those rows is flattered and is not the point of the comparison, which is decode speed.
- The acceptance counters accumulate over all speculative runs of the session, copy and open questions together; they are not separate per workload.
- n-gram drafting is the cheapest variant. Draft-model, EAGLE and Medusa variants have different costs and are not measured here.

## Preparation notes (demos 4 and 5, not run)

- **Mixture of experts (`moe_demo`, Qwen3-30B-A3B-FP8).** The validation pod's 50 GB container disk was too small for the 32.45 GB FP8 checkpoint plus the download and compile caches. Use the 100 GB container disk of `infra/provision.md`.
- **No vLLM profile exists for the mixture-of-experts model.** `config/vllm-profiles/` has none. Write one (the steps are in [`docs/MODEL-SELECTION.md`](../../docs/MODEL-SELECTION.md), section 7), smoke-test it on the workshop GPU before the session and read the log: the open SM120 issues in `docs/RESEARCH.md` section 3.3 concern mixture-of-experts, MLA, NVFP4 or forced FlashInfer paths.
- **The engine comparison changes two things at once.** The GGUF file for llama.cpp and Ollama (`Qwen3-8B-Q8_0.gguf`) is 8-bit, while the vLLM baseline serves BF16. Engine and precision differ together, so say so next to any number and do not credit the engine alone with a speed difference.

## Production consequence

Speculative decoding is a workload decision, not a switch: measure it on your own traffic. It suits outputs that quote the input (extraction, rewriting, code edits) and can cost throughput on open generation under load. And when a control behaves like the treatment, suspect the benchmark before the technique.
