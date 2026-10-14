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
| GPU | |
| VRAM / memory bandwidth | |
| Weights (GiB) | |
| KV cache capacity (tokens) and how you computed it | |
| Maximum concurrency at the context length you need | |

## Baseline

_Lab 3. The same deployment at concurrency 1, 4, 8 and 16. Link the result files._

| Concurrency | TTFT p50 | TTFT p95 | Latency p50 | Latency p95 | Output TPS / request | Aggregate TPS | GPU util | VRAM |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | | | | | | | | |
| 4 | | | | | | | | |
| 8 | | | | | | | | |
| 16 | | | | | | | | |

1. When does throughput stop scaling?
2. When does latency deteriorate?
3. What resource looks saturated?
4. Which configuration would you deploy, and why?

## Experiments

_Lab 4. One hypothesis, one changed variable, measured before and after._

```text
Hypothesis:
Change (one variable):
Before:
After:
Metric improved:
Metric degraded:
Quality impact:
Memory impact:
Operational impact:
Recommendation:
```

## Optimized Configuration

_The configuration you would run now, as a vLLM profile or flag list, with the evidence for every non-default setting._

## Production Architecture

_Lab 5. Link `production-architecture.md` and summarise the decisions in five lines._

## Security Considerations

_What data flows through this system? Where does each piece go (prompts, responses, logs, embeddings, weights, telemetry)? What is exposed, to whom, protected by what? What would you pin and what would you monitor?_

## Final Recommendation

_One paragraph a decision maker can act on: what to deploy, on what hardware, at what expected cost per useful workload, what you would monitor, and what would make you change your mind._
