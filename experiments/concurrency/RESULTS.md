# Results: concurrency

Raw files: [`benchmark/results/reference/concurrency/`](../../benchmark/results/reference/concurrency/). Every file carries hardware, model revision, engine version, server arguments and date. Hypotheses: [`README.md`](README.md).

## Setup

1× NVIDIA RTX PRO 6000 Blackwell Server Edition, `Qwen/Qwen3-8B` BF16, vLLM 0.31.0, profile `baseline` (or `max-seqs-8`), closed-loop load, 1,200 input and 180 output tokens, 48 to 384 requests per level (`6 × concurrency`, at least 48), fresh random prompts per run. One session, no repetitions; the single-request runs of `baseline` and `concurrency/baseline-c001` agree within 1 %.

## The concurrency sweep (profile `baseline`)

| Concurrency | TTFT p50 (ms) | TTFT p95 (ms) | Latency p50 (ms) | ITL p50 (ms) | Tokens/s per request | Aggregate tokens/s | Requests/s | GPU util (%) | Power (W) | Waiting max | KV usage max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 69 | 73 | 2,144 | 11.6 | 86.2 | 83.9 | 0.47 | 99 | 361.5 | 0 | 0.3 % |
| 2 | 115 | 120 | 2,242 | 11.9 | 84.2 | 160.5 | 0.89 | 100 | 352.5 | 0 | 0.6 % |
| 4 | 162 | 210 | 2,318 | 11.8 | 83.0 | 310.4 | 1.72 | 100 | 365.8 | 0 | 1.3 % |
| 8 | 356 | 416 | 2,610 | 12.3 | 79.4 | 550.8 | 3.06 | 100 | 393.1 | 0 | 2.6 % |
| 16 | 587 | 821 | 3,192 | 13.5 | 68.7 | 900.0 | 5.00 | 100 | 425.0 | 5 | 5.1 % |
| 32 | 970 | 1,463 | 4,439 | 16.2 | 51.0 | 1,294.3 | 7.19 | 100 | 463.6 | 13 | 10.2 % |
| 64 | 1,374 | 2,603 | 6,771 | 20.5 | 32.4 | 1,692.2 | 9.40 | 100 | 491.5 | 42 | 20.4 % |

## What the data says

**Aggregate throughput grows with concurrency and does not flatten before 64.** Each doubling adds less: ×1.91, ×1.93, ×1.77, ×1.63, ×1.44, ×1.31 (concurrency 1 to 2, up to 32 to 64). The workshop's lab goes up to 16; a flat region would only appear above 64 with this workload. Whether more concurrency is worth it is therefore decided by latency, not by throughput.

**One decode step costs almost the same for one request and for eight.** The inter-token latency rises from 11.6 ms to 12.3 ms (+6 %) while the number of tokens produced per step grows eightfold. This is why batching works: every step reads all weights once, and the weights are the dominant bytes.

**The step time follows the bytes moved.** As an arithmetic check (a model, not a measurement): one step reads the weights (16.38 GB) plus the KV cache of every running request (about 1,290 tokens × 147,456 B = 190 MB each, the mean context of this workload). Divided by the datasheet bandwidth of 1,597 GB/s:

| Concurrency | 1 | 4 | 8 | 16 | 32 | 64 |
| --- | --- | --- | --- | --- | --- | --- |
| Bytes read per step (GB) | 16.6 | 17.1 | 17.9 | 19.4 | 22.5 | 28.6 |
| Bandwidth-bound step (ms) | 10.4 | 10.7 | 11.2 | 12.2 | 14.1 | 17.9 |
| Measured ITL p50 (ms) | 11.6 | 11.8 | 12.3 | 13.5 | 16.2 | 20.5 |
| Measured ÷ bound | 1.12 | 1.10 | 1.10 | 1.11 | 1.15 | 1.15 |

The model is off by 10 to 15 % at every level. At concurrency 64 the KV cache read is 43 % of the bytes of a step, which is why the speed per request falls from 86 to 32 tokens per second.

**What the user sees degrades first in time to first token.** Prompts are prefilled together, and one scheduler step has a limited token budget, which is consistent with what the gauges show: at concurrency 16 up to 5 requests waited (the 16 prompts of 1,200 tokens arrive at once), at 64 up to 42. TTFT p95 crosses 800 ms between concurrency 8 (416 ms) and 16 (821 ms).

**GPU utilization says nothing.** It reads 99 to 100 % at every level, including one request. Power draw rises from 362 W to 492 W and throughput by a factor of 20 over the same range: energy per generated token falls from 4.3 J to 0.29 J, so the busy GPU at concurrency 1 is mostly waiting for memory.

## Against the example SLO

The course's running SLO is TTFT p95 under 800 ms and at least 25 output tokens per second per request.

| Concurrency | TTFT p95 | Tokens/s per request | Meets the SLO |
| --- | --- | --- | --- |
| 8 | 416 ms | 79.4 | yes |
| 16 | 821 ms | 68.7 | no, by 21 ms |
| 32 | 1,463 ms | 51.0 | no |
| 64 | 2,603 ms | 32.4 | speed yes, TTFT no |

At 20 concurrent users the deployment on one GPU misses the TTFT target slightly and needs either a second GPU, FP8 weights (see [`../quantization/RESULTS.md`](../quantization/RESULTS.md)), or a looser SLO. Cost of the GPU time alone at the price of $2.49 per hour: 8.25 dollars per million output tokens at concurrency 1, 0.77 at 16, 0.41 at 64 (arithmetic from the table; the SLO, not the price, picks the point).

## A capped batch (profile `max-seqs-8`, `--max-num-seqs 8`)

| Concurrency | TTFT p50 (ms) | TTFT p95 (ms) | ITL p50 (ms) | Tokens/s per request | Aggregate tokens/s | Running max | Waiting max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 205 | 216 | 11.8 | 84.5 | 309.7 | 4 | 0 |
| 8 | 342 | 432 | 12.4 | 79.2 | 549.5 | 8 | 0 |
| 16 | 2,958 | 3,035 | 12.4 | 79.8 | 552.7 | 8 | 8 |
| 32 | 8,122 | 8,155 | 12.4 | 78.4 | 552.5 | 8 | 24 |

Up to eight users nothing changes. Beyond that **the aggregate throughput is pinned at about 550 tokens per second** (the baseline reaches 900 at 16 and 1,294 at 32) and **the speed of each running request stays at 79** tokens per second: the extra users do not make the server slower, they wait. The cost shows up entirely as time to first token: 2.96 s at concurrency 16 against 0.59 s uncapped, 8.1 s at 32.

## What surprised

- The throughput curve has no knee within the tested range. The expectation that throughput "stops growing" holds only relative to latency: the SLO breaks long before the throughput saturates.
- The bandwidth model with only two terms (weights plus KV reads) is as accurate as it is. It is the explanation to teach, together with its 10 to 15 % residual (scheduling, attention kernels, sampling).
- With the capped batch the per-request speed did not improve in return for the lost throughput: ITL is 12.4 ms for eight running requests in both profiles.

## Caveats

- One run per level, no confidence intervals; tail percentiles at 48 requests are noisy (the p95 of 48 requests rests on about the three slowest). The harness comparison with `vllm bench serve` is in [`docs/METRICS.md`](../../docs/METRICS.md).
- Every prompt began with the same 16-token block in this session (prefix-cache hit rate 1.3 %, see the baseline results). The effect on TTFT is at most about 1 %.
- The mean context for the bandwidth model (1,290 tokens) is the input length plus half the output; real requests are at different positions at any step.
- Closed-loop load: a new request starts only when one finishes, so the system never faces more concurrent requests than clients. Open-loop behavior (arrival rate above capacity) is a different experiment (task 03, Further Exploration).

## Production consequence

Choose concurrency from the SLO, not from the throughput curve: more users per GPU are cheaper per token until the time to first token or the per-user speed breaks the target. Limits such as `max-num-seqs` turn overload into queueing, and queueing shows up as TTFT, so alert on waiting requests, not on GPU utilization.
