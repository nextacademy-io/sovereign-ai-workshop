# Reference results

Measured results from the trainer's validation runs on the workshop GPU (NVIDIA RTX PRO 6000 Blackwell Server Edition, vLLM 0.31.0, Qwen3-8B). They are **read-only reference material**: use them to check your own numbers, or as a fallback when your own run failed. Every file carries its provenance (hardware, model revision, engine version, server arguments, date); your own results are in `benchmark/results/mine/`.

`./scripts/reset.sh lab-03` (and later labs) copies the relevant results here on your machine.

| Directory | Experiment | Runs |
| --- | --- | --- |
| `baseline/` | [baseline](../../../experiments/baseline/RESULTS.md) | one request at a time, the KV-formula check, the start-up log excerpt and memory accounting |
| `startup/` | baseline | cold start, warm start and restart timelines |
| `concurrency/` | [concurrency](../../../experiments/concurrency/RESULTS.md) | concurrency 1 to 64, and the capped batch (`max-seqs-8`) |
| `context-length/` | [context-length](../../../experiments/context-length/RESULTS.md) | growing prompts, and the full against the 4 GiB KV pool |
| `prefix-cache/` | [prefix-cache](../../../experiments/prefix-cache/RESULTS.md) | cache on and off, the control, the repeated-prompts pitfall |
| `quantization/` | [quantization](../../../experiments/quantization/RESULTS.md) | BF16, FP8 weights, FP8 KV cache, and the quality comparison |
| `demos/` | [demos](../../../experiments/demos/RESULTS.md) | speculative decoding with its control, the two refused starts |

There is no `tensor-parallel/` directory: that experiment could not be run (see its `RESULTS.md`).
