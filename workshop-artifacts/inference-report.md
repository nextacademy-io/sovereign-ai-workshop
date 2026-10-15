# Inference Engineering Report

> Owner: _your name_ · Group: _alpha / beta / gamma / delta_
>
> This document grows over the three days. Each lab adds to it; the last section is your recommendation.
> Write what you **measured** and what you **decided**, and keep the numbers next to the file they came from.
> Prefer short sentences and tables. If you did not measure it, say so.

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

_Lab 1. Model, precision, why this one, which alternatives you rejected and why. License and commercial implications._

| | |
| --- | --- |
| Model and revision | |
| Precision | |
| License (and what it means for commercial use) | |
| Why it is the smallest model that does the task | |
| Rejected alternatives | |

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

_Lab 4. One lever, one changed variable, a prediction written before the run, measured before and after._

```text
Hypothesis:
Prediction (written before the run):
Change (one variable):
Before:
After:
Prediction versus result (what was wrong):
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

_Lab 5. Link `production-architecture.md` and summarize the decisions in five lines._

## Security Considerations

_What data flows through this system? Where does each piece go (prompts, responses, logs, embeddings, weights, telemetry)? What is exposed, to whom, protected by what? What would you pin and what would you monitor?_

## Final Recommendation

_One paragraph a decision maker can act on: what to deploy, on what hardware, at what expected cost per useful workload, what you would monitor, and what would make you change your mind._
