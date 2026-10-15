# Results: context-length

Raw files: [`benchmark/results/reference/context-length/`](../../benchmark/results/reference/context-length/). Every file carries hardware, model revision, engine version, server arguments and date. Hypotheses: [`README.md`](README.md).

## Setup

1× NVIDIA RTX PRO 6000 Blackwell Server Edition, `Qwen/Qwen3-8B` BF16, vLLM 0.31.0, fresh random prompts per run (prefix-cache hit rate 0.0 % in every run). Output length 128 tokens. Profiles: `baseline` (KV pool 58.6 GiB, about 427,000 tokens), `kv-constrained` (`--kv-cache-memory-bytes 4G` and `--max-model-len 16384`: about 29,000 tokens, a "small GPU"), `kv-constrained-fp8kv` (the same 4 GiB with an FP8 KV cache). One session, no repetitions.

## 1. One request, growing prompt (profile `baseline`)

| Prompt tokens | TTFT p50 (ms) | Prefill rate (tokens/s) | ITL p50 (ms) | Bandwidth-bound step (ms) | Measured ÷ bound | KV usage max |
| --- | --- | --- | --- | --- | --- | --- |
| 256 | 27 | 9,350 | 11.6 | 10.3 | 1.13 | 0.1 % |
| 1,024 | 60 | 17,100 | 11.6 | 10.4 | 1.12 | 0.3 % |
| 4,096 | 194 | 21,100 | 11.9 | 10.6 | 1.12 | 1.0 % |
| 8,192 | 412 | 19,900 | 12.3 | 11.0 | 1.11 | 1.9 % |
| 16,384 | 947 | 17,300 | 13.1 | 11.8 | 1.11 | 3.9 % |
| 28,672 | 2,018 | 14,200 | 14.3 | 12.9 | 1.10 | 6.7 % |

The prefill rate is the prompt tokens divided by the time to first token (it includes scheduling and the first sampling step). The bound is the arithmetic of the concurrency experiment: weights (16.38 GB) plus the KV cache of the context (prompt plus about half of the output, 147,456 B per token), divided by the datasheet bandwidth of 1,597 GB/s.

- **Time to first token grows faster than linearly with the prompt.** Prefill is compute-bound: the rate rises from 9,350 tokens/s (short prompts are dominated by fixed costs) to a peak of about 21,000 at 4,096 tokens and then *falls* to 14,200 at 28,672, because the attention work per token grows with the context. Doubling the prompt from 8k to 16k costs ×2.3 in TTFT, from 16k to 28k ×2.1 for ×1.75 tokens.
- **The decode step slows with context, and the bytes explain it.** ITL rises from 11.6 ms to 14.3 ms; the model "weights plus the context's KV bytes, over bandwidth" predicts the shape within 10 to 13 % at every length. At 28,672 tokens the KV cache read (4.2 GB) is a fifth of the bytes of a step.
- **Tokens per second per request** fall from 86 to 71 over the same range.

## 2. Four requests at once (profile `baseline`)

| Prompt tokens | Requests | TTFT p50 (ms) | TTFT p95 (ms) | ITL p50 (ms) | Tokens/s per request | Aggregate tokens/s |
| --- | --- | --- | --- | --- | --- | --- |
| 4,096 | 4 | 471 | 755 | 12.9 | 67.0 | 214.9 |
| 16,384 | 4 | 2,294 | 3,396 | 17.6 | 34.9 | 86.0 |

(Concurrency 4 at 4,096 tokens and at 16,384 tokens from the baseline sweep, `baseline-c4-in*`.) Four 16k prompts take over two seconds to first token *and* push the decode step from 13 ms to 17.6 ms, because chunks of prefill are interleaved with the decode steps of the running requests.

## 3. 8,192-token prompts at growing concurrency: the full KV pool and the small one

| Run | Profile | Concurrency | TTFT p50 (ms) | TTFT p95 (ms) | ITL p50 (ms) | Tokens/s per request | Aggregate tokens/s | Running max | Waiting max | KV usage max | Preemptions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline-in08192 | baseline | 1 | 412 | 414 | 12.3 | 81.8 | 65.2 | 1 | 0 | 1.9 % | 0 |
| baseline-c002-in08192 | baseline | 2 | 433 | 804 | 13.3 | 61.9 | 102.8 | 2 | 0 | 3.9 % | 0 |
| baseline-c004-in08192 | baseline | 4 | 1,183 | 1,627 | 14.5 | 56.7 | 149.1 | 4 | 1 | 7.8 % | 0 |
| baseline-c008-in08192 | baseline | 8 | 1,601 | 3,191 | 17.6 | 33.6 | 188.9 | 8 | 5 | 15.6 % | 0 |
| baseline-c016-in08192 | baseline | 16 | 1,654 | 5,950 | 24.2 | 16.4 | 217.0 | 16 | 13 | 31.2 % | 0 |
| kv-constrained-c001-in08192 | kv-constrained | 1 | 410 | 415 | 12.3 | 81.5 | 65.1 | 1 | 0 | 28.5 % | 0 |
| kv-constrained-c002-in08192 | kv-constrained | 2 | 433 | 795 | 13.3 | 61.9 | 102.9 | 2 | 0 | 57.0 % | 0 |
| kv-constrained-c004-in08192 | kv-constrained | 4 | 1,211 | 3,075 | 14.0 | 58.3 | 122.0 | 3 | 1 | 85.3 % | 0 |
| kv-constrained-c008-in08192 | kv-constrained | 8 | 5,083 | 6,699 | 14.0 | 58.4 | 129.3 | 3 | 5 | 85.8 % | 0 |
| kv-constrained-c016-in08192 | kv-constrained | 16 | 12,870 | 14,818 | 14.0 | 58.4 | 129.3 | 3 | 13 | 85.8 % | 0 |
| kv-constrained-fp8kv-c004-in08192 | kv-constrained-fp8kv | 4 | 1,155 | 1,599 | 12.9 | 62.4 | 159.9 | 4 | 1 | 57.0 % | 0 |
| kv-constrained-fp8kv-c008-in08192 | kv-constrained-fp8kv | 8 | 1,427 | 2,840 | 14.1 | 38.5 | 188.5 | 7 | 5 | 99.6 % | 1 |

### What the data says

**With the full KV pool, long prompts are limited by prefill compute, not by memory.** At concurrency 16 the cache is 31 % used and nothing is evicted, yet aggregate throughput stops near 190 to 217 tokens/s and the speed per request falls from 82 to 16 tokens/s. Every 8k prompt costs about 0.4 s of prefill, so prefill alone limits the GPU to about 2.4 such prompts a second, and the decode steps share the same GPU: the measured 1.5 to 1.7 requests per second (189 to 217 tokens/s ÷ 128) is the combined limit, no matter how many users wait. Memory is not what you run out of first on this card.

**With the small KV pool, memory becomes the limit and the server queues.** The pool holds 29,120 tokens; an 8,192-token prompt plus its output is about 8,320 tokens, so three requests fit (85 % usage) and the fourth waits. The effect, compared with the full pool at the same load:

| At concurrency 8 | Full pool | 4 GiB pool |
| --- | --- | --- |
| Requests running at once | 8 | 3 |
| TTFT p50 | 1.6 s | 5.1 s |
| Tokens per second per request | 33.6 | 58.4 |
| Aggregate tokens per second | 189 | 129 |
| GPU memory in use | 84.8 GiB | 30.0 GiB |

The small pool trades **time to first token and throughput for decode speed**: fewer requests run, so each decode step carries less interleaved prefill and the running requests are faster (58 against 34 tokens/s). It acts as admission control: requests wait in the queue instead of slowing the running ones.

**No preemption happened with the 4 GiB pool.** vLLM admitted only what fitted and queued the rest; a preemption needs a running request to run out of space while it decodes, and the free blocks left after admitting three requests (about 4,000 tokens) were enough for their 128 output tokens each. The one preemption in the whole experiment came with the FP8 pool at concurrency 8, which filled 99.6 % of the cache (7 running requests).

**An FP8 KV cache doubles the tokens in the same 4 GiB** and the effect is visible in the same table: four requests run together instead of three (usage 57 % instead of 85 %), aggregate throughput at concurrency 4 rises from 122 to 160 tokens/s (+31 %), and at concurrency 8 from 129 to 188 (+46 %) with a TTFT p50 of 1.4 s instead of 5.1 s. Its quality cost is in [`../quantization/RESULTS.md`](../quantization/RESULTS.md).

## What surprised

- **The profile did not start at first.** With the default `--max-model-len 32768` a 4 GiB pool holds less than one maximum-length request, and vLLM refuses to start ("4.5 GiB KV cache is needed, which is larger than the available KV cache memory (4.0 GiB)... the estimated maximum model length is 29104"); the supervisor rolled back to the previous profile. The profile now lowers the context limit to 16,384. The refusal is the same arithmetic as in the sizing module (`04-gpu-sizing`), enforced.
- The bottleneck on the full card is compute, so the "KV memory" lesson needs the constrained profile to appear at all.
- The small pool is faster per request: a constraint that helps one metric at the expense of another.

## Caveats

- One session, no repetitions. Tail percentiles of 16 to 48 requests are noisy.
- The same-profile control `baseline-c*-in08192` ran in this session after the single-request sweep; the order was baseline first, constrained second, on one pod.
- Output length 128: longer outputs would grow each request's cache and make preemption more likely in the small pool.
- The "4 GiB pool" is a simulation of a small GPU's memory pressure, not of its bandwidth or compute: a real 24 GB card would also be slower per step.

## Production consequence

Memory sizing is a promise about concurrency times context. When the pool is too small, the server queues, and queueing shows up as time to first token. When the pool is large, long prompts still cost prefill compute: plan GPUs for the prompt tokens per second you must prefill, and use prefix caching (see [`../prefix-cache/RESULTS.md`](../prefix-cache/RESULTS.md)) to avoid paying twice for a shared context.
