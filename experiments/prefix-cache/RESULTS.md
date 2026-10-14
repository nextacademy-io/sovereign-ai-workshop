# Results: prefix-cache

Raw files: [`benchmark/results/reference/prefix-cache/`](../../benchmark/results/reference/prefix-cache/). Every file carries hardware, model revision, engine version, server arguments and date. Hypotheses: [`README.md`](README.md).

## Setup

1× NVIDIA RTX PRO 6000 Blackwell Server Edition, `Qwen/Qwen3-8B` BF16, vLLM 0.31.0. Workload `shared-prefix`: 2,200 input tokens of which the first 2,000 are identical in every request, 150 output tokens; fresh random text after the shared part. Profiles `baseline` (prefix caching on, the vLLM default) and `no-prefix-cache`. Each profile was started fresh so the cache began empty. Concurrency 1 (32 requests) and 8 (64 requests). The control: the same length (2,200 tokens) with nothing shared. One session, no repetitions.

## The effect of the cache

| Run | Profile | Concurrency | TTFT p50 (ms) | TTFT p95 (ms) | Tokens/s per request | Aggregate tokens/s | Prefix hit rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline-shared-c001 | baseline (cache on) | 1 | 33 | 35 | 85.4 | 84.3 | 90.9 % |
| no-prefix-cache-shared-c001 | no-prefix-cache | 1 | 111 | 117 | 85.6 | 81.0 | 0 % |
| baseline-shared-c008 | baseline (cache on) | 8 | 106 | 131 | 81.5 | 619.9 | 90.9 % |
| no-prefix-cache-shared-c008 | no-prefix-cache | 8 | 588 | 771 | 70.6 | 444.3 | 0 % |
| baseline-unique-c008 | baseline, nothing shared | 8 | 635 | 751 | 72.0 | 443.3 | 0 % |

- **A shared 2,000-token prefix cuts the time to first token by 3.4× at concurrency 1 (111 to 33 ms) and 5.5× at concurrency 8 (588 to 106 ms)**, and raises aggregate throughput by 40 % (444 to 620 tokens/s), because 91 % of the prompt tokens are not prefilled again. The effect is larger under load because prefill work competes with decoding for the same GPU.
- **The cache does nothing for decoding.** Tokens per second per request at concurrency 1 is 85.4 with and 85.6 without. Only the prefill is saved.
- **The control matches the "off" profile.** With nothing shared, the baseline server behaves exactly like the server with caching switched off (TTFT p50 635 against 588 ms, aggregate 443 against 444 tokens/s): caching is free when there is nothing to share, and the benefit exists only when requests share a prefix.
- The counters tell the same story: of 233,200 prompt tokens queried during the shared runs, 208,016 (89.2 %) were served from the cache with caching on and none with caching off.

## The pitfall: repeating your own benchmark

Three runs of the same workload at concurrency 8 (1,200 input, 180 output tokens): the same prompts twice (same seed), then new prompts.

| Run | TTFT p50 (ms) | TTFT p95 (ms) | Aggregate tokens/s | Prefix hit rate |
| --- | --- | --- | --- | --- |
| First run (seed A) | 359 | 421 | 550.3 | 0 % |
| Same prompts again (seed A) | 50 | 62 | 638.6 | 98.7 % |
| New prompts (seed B) | 360 | 428 | 549.8 | 0 % |

The repeated run looks seven times faster at the first token and 16 % faster in throughput, and nothing about the deployment changed: the server remembered the prompts. A benchmark that reuses its prompts measures the cache. The harness therefore draws a new random seed for every invocation and warns when the server's hit rate is high for a workload that shares no prefix.

## What surprised

- **The first attempt at this experiment did not switch the cache off.** The profile said `enable-prefix-caching: false`, and the server reported the same 91 % hit rate and the same TTFT as the baseline: vLLM's `--config` loader silently drops `false` for a flag. The stored command line said `--no-enable-prefix-caching`, so the metadata was wrong too. The profile renderer now writes the explicit negative flag; the server's own startup line `non-default args: {... 'enable_prefix_caching': False ...}` is the proof to look for. See [`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md) (incident 18).
- The cache's effect at concurrency 8 (5.5×) is much larger than at concurrency 1 (3.4×).

## Caveats

- A single shared prefix of 2,000 tokens (91 % of the prompt) is the best case. A realistic system prompt of a few hundred tokens saves proportionally less.
- Blocks are cached in units of 16 tokens and evicted when the KV pool is needed for running requests; with the full 58 GiB pool nothing was evicted in these runs. Under the small pool of [`../context-length/RESULTS.md`](../context-length/RESULTS.md) the hit rate would fall.
- One session; the p95 values rest on 32 to 64 requests.

## Production consequence

Put the part of the prompt that does not change (system prompt, instructions, retrieved document that many requests share) **first** and keep it byte-identical: cache hits need an identical prefix. Watch the hit rate (`vllm:prefix_cache_hits_total` over `vllm:prefix_cache_queries_total`) in production, and never publish a benchmark that repeated its prompts.
