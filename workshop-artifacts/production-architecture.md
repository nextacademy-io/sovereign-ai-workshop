# Production architecture (Lab 5)

> Design an inference platform for your scenario and be ready to defend it in a short presentation. There is no
> single correct answer: the quality of the reasoning is what counts. Use numbers (yours from the benchmarking and
> optimization labs, or `benchmark/results/reference/`) wherever you can, and mark every estimate as an estimate.

## Scenario

_Which scenario did your group get? Who uses it, how often, with what data?_

## Requirements

```yaml
workload:
  input_tokens_p50:
  output_tokens_p50:
  concurrency:
  requests_per_second_peak:

slo:
  ttft_p95_ms:
  output_tps_per_request:
  availability:

quality:
  maximum_acceptable_regression:
```

## Design

| Decision | Choice | Because (and what you traded) |
| --- | --- | --- |
| Model | | |
| Precision | | |
| GPU | | |
| Inference engine | | |
| Context length | | |
| Replicas | | |
| API and authentication | | |
| Observability | | |
| RAG (if any) | | |
| Scaling | | |
| Security boundary | | |
| SLO | | |

## Estimates

```text
Concurrency:
Latency target:
GPU requirement (how many, how you got there):
Expected bottleneck (compute, memory bandwidth, KV cache, queueing, network):
Scaling strategy:
Cost per useful workload (what is "useful" here?):
```

## Diagram

_Boxes and arrows: client, gateway, authentication, inference replicas, GPU pool, metrics, logs, secrets, storage._

```text

```

## Risks and what you would measure first

_Three risks, and the first measurement that would reduce each of them._

## The 15 questions

Answer in one line each. Skip none; "do not know yet" is a valid answer if you say how you would find out.

1. What task are we solving?
2. What quality do we need?
3. What is the smallest model that satisfies it?
4. What traffic do we expect?
5. What is our latency budget?
6. How large is the context?
7. What concurrency do we expect?
8. How much VRAM is required?
9. What hardware bottleneck do we expect?
10. What does the baseline benchmark show?
11. Which optimization addresses the measured bottleneck?
12. Does the optimization degrade quality?
13. What should we monitor?
14. What security boundary is required?
15. What does this cost per useful workload?
