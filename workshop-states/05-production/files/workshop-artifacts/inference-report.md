# Inference Engineering Report

> Owner: _your name_ · Group: _alpha / beta / gamma / delta_
>
> This document grows over the three days. Each lab adds to it; the last section is your recommendation.
> Write what you **measured** and what you **decided**, and keep the numbers next to the file they came from.
> Prefer short sentences and tables. If you did not measure it, say so.

**Reference version.** The sections filled in below come from the trainer's measured reference run (`benchmark/results/reference/`, workshop GPU). They are here so you can continue if you fell behind: replace every number with your own as soon as you have it, and keep the file next to each number.

## Workload

_What are we serving? Fill in from the SLO example, then change it to your own._

```yaml
workload:
  input_tokens_p50: 1200
  output_tokens_p50: 180
  concurrency: 20

slo:
  ttft_p95_ms: 800
  output_tps_per_request: 25
  availability: 99.9

quality:
  maximum_acceptable_regression: 2_percent
```

## Selected Model

_Lab 1. Model, precision, why this one, which alternatives you rejected and why. Licence and commercial implications._

| | |
| --- | --- |
| Model and revision | `Qwen/Qwen3-8B` at `b968826d9c46dd6066d109eabc6255188de91218` (the workshop's primary model; replace with your own choice for your scenario) |
| Precision | BF16 (FP8 is the Day 2 experiment) |
| Licence (and what it means for commercial use) | Apache-2.0: commercial use permitted; keep the licence and attribution notices |
| Why it is the smallest model that does the task | Reference answer for the workshop workload only: a dense 8B model with tool calling and structured output that fits one GPU with room for a large KV cache. For your scenario, argue it from your own eval. |
| Rejected alternatives | `Qwen/Qwen3-1.7B` (smaller, would need an eval on your items); `Qwen/Qwen3-30B-A3B-FP8` (mixture of experts: all 30.5 B weights must be resident) |

## Hardware

_Lab 2. What is the GPU? How much memory, how much bandwidth? How much of the memory is weights, how much is KV cache, how many tokens fit?_

| | |
| --- | --- |
| GPU | NVIDIA RTX PRO 6000 Blackwell Server Edition, driver 595.91.07 |
| VRAM / memory bandwidth | 94.97 GiB usable of a 96 GB card / 1,597 GB/s (datasheet) |
| Weights (GiB) | 15.27 measured in memory (BF16, 8.2 B parameters × 2 bytes) |
| KV cache capacity (tokens) and how you computed it | 423,328 tokens reported by vLLM; 58.14 GiB available ÷ 147,456 B per token (2 × 36 layers × 8 KV heads × 128 × 2 B) = 423,363 |
| Maximum concurrency at the context length you need | 12.92× at 32,768 tokens per request (as reported by vLLM) |

## Baseline

_Lab 3. The same deployment at concurrency 1, 4, 8 and 16. Link the result files._

Reference results: `benchmark/results/reference/concurrency/baseline-c001` to `baseline-c016`.

| Concurrency | TTFT p50 | TTFT p95 | Latency p50 | Latency p95 | Output TPS / request | Aggregate TPS | GPU util | VRAM |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 69 ms | 73 ms | 2,144 ms | 2,153 ms | 86.2 | 83.9 | 99 % | 83.8 GiB |
| 4 | 162 ms | 210 ms | 2,318 ms | 2,324 ms | 83.0 | 310.4 | 100 % | 83.9 GiB |
| 8 | 356 ms | 416 ms | 2,610 ms | 2,629 ms | 79.4 | 550.8 | 100 % | 85.4 GiB |
| 16 | 587 ms | 821 ms | 3,192 ms | 3,236 ms | 68.7 | 900.0 | 100 % | 84.9 GiB |

1. When does throughput stop scaling? It keeps growing up to concurrency 16 (551 tokens/s at 8, 900 at 16) but every doubling adds less; the reference sweep to 64 does not flatten either.
2. When does latency deteriorate? Time to first token p95 passes the 800 ms of the example SLO between concurrency 8 (416 ms) and 16 (821 ms); the speed per request falls from 86 to 69 tokens/s.
3. What resource looks saturated? GPU utilization reads about 100 % everywhere, so it tells you nothing; power draw rises from 362 W to 425 W and waiting requests appear at 16.
4. Which configuration would you deploy, and why? Concurrency 8 per GPU meets the example SLO (TTFT p95 under 800 ms, at least 25 tokens/s per request) with room; at 20 users you need FP8 weights or a second GPU.

## Experiments

_Lab 4. One hypothesis, one changed variable, measured before and after. Reference results for all four hypotheses (`benchmark/results/reference/`):_

**A. Quantization** (`quantization/`: `baseline-c*` against `fp8-c*`)

```text
Hypothesis: FP8 weights make decode faster and free memory for more KV cache, at some cost in quality
Change (one variable): profile fp8 (published FP8 checkpoint of the same model)
Before: concurrency 1: ITL p50 11.6 ms, 86.2 tokens/s per request; concurrency 16: 897 tokens/s, TTFT p50 616 ms
After:  concurrency 1: ITL p50 7.3 ms, 138.2 tokens/s per request; concurrency 16: 1,323 tokens/s, TTFT p50 360 ms
Metric improved: decode speed, throughput, time to first token
Metric degraded: the first start of a new checkpoint is slow (about 2.5 minutes in the reference session, 41 s once its compile caches exist, against 39 s for baseline)
Quality impact: 77.1 % against 79.6 % on 240 spot-check items (difference -2.5 points, within the noise of this probe); 3 % of greedy completions are identical to BF16
Memory impact: weights 15.27 to 8.85 GiB; KV capacity 426,992 to 473,312 tokens
Operational impact: a second checkpoint to pin and store; a quality check before every model update
Recommendation: use FP8 for latency and cost when your own quality check passes; do not use it where outputs must stay identical to BF16
```

**B. Prefix caching** (`prefix-cache/`: `baseline-shared-c008` against `no-prefix-cache-shared-c008`)

```text
Hypothesis: a long prompt prefix shared by many requests is prefilled only once
Change (one variable): profile no-prefix-cache (prefix caching off)
Before (cache on):  TTFT p50 106 ms, aggregate 620 tokens/s, prefix hit rate 90.9 %
After (cache off):  TTFT p50 588 ms, aggregate 444 tokens/s, prefix hit rate 0.0 %
Metric improved: time to first token with the cache on
Metric degraded: nothing at the server; the cache uses KV memory that could hold other requests
Quality impact: none (same model, same outputs)
Memory impact: cached blocks occupy KV pool until evicted
Operational impact: none; but benchmarks that repeat their prompts measure the cache, not the deployment
Recommendation: leave it on; design prompts so the shared part comes first
```

**C. Context length** (`context-length/`: `baseline-c008-in08192` against `kv-constrained-c008-in08192`)

```text
Hypothesis: with a small KV budget, long prompts queue
Change (one variable): profile kv-constrained (4 GiB KV pool, 16,384-token context limit)
Before: concurrency 8, 8,192-token prompts: TTFT p50 1,601 ms, aggregate 189 tokens/s, 8 requests running, KV usage up to 16 %
After:  TTFT p50 5,083 ms, aggregate 129 tokens/s, 3 requests running, 5 waiting, KV usage up to 86 %
Metric improved: GPU memory in use (about 30 GiB instead of about 85 GiB)
Metric degraded: time to first token and throughput: requests wait for KV space
Quality impact: none
Memory impact: the pool holds 29,120 tokens, about three 8,192-token requests
Operational impact: the pool must be sized for context times concurrency
Recommendation: size the KV pool for the concurrency you promise, or cap the context per request
```

**D. Concurrency and batching** (`concurrency/`: `baseline-c016` against `max-seqs-8-c016`)

```text
Hypothesis: capping the batch limits throughput and creates queueing
Change (one variable): profile max-seqs-8 (--max-num-seqs 8)
Before: concurrency 16: aggregate 900 tokens/s, TTFT p50 587 ms, 68.7 tokens/s per request
After:  aggregate 553 tokens/s, TTFT p50 2,958 ms, 79.8 tokens/s per request, 8 waiting
Metric improved: nothing measured here (a cap protects a shared server from overload)
Metric degraded: throughput and time to first token; the speed of each running request is unchanged
Quality impact: none
Memory impact: none
Operational impact: overload becomes queueing; alert on waiting requests
Recommendation: set the cap from the SLO, not from the throughput curve
```

## Optimized Configuration

_The configuration you would run now, as a vLLM profile or flag list, with the evidence for every non-default setting._

Reference example (replace with your own):

```yaml
extends: baseline
description: "FP8 weights for the example SLO at 20 concurrent users"
# evidence: benchmark/results/reference/quantization/ (speed, memory), quality-comparison.json (spot check)
```

## Production Architecture

_Lab 5. Link `production-architecture.md` and summarise the decisions in five lines._

## Security Considerations

_What data flows through this system? Where does each piece go (prompts, responses, logs, embeddings, weights, telemetry)? What is exposed, to whom, protected by what? What would you pin and what would you monitor?_

## Final Recommendation

_One paragraph a decision maker can act on: what to deploy, on what hardware, at what expected cost per useful workload, what you would monitor, and what would make you change your mind._
