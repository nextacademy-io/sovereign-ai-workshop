# Metrics

What to measure when you run a language model yourself, and how to read what you measured. The definitions here are the ones the benchmark harness (`benchmark/infbench/`) and the Grafana dashboard (`monitoring/grafana/`) use. External facts (other tools, vLLM internals, GPU specifications) are sourced in [RESEARCH.md](RESEARCH.md), sections 6, 9 and 10. The modules that teach this material are `11-measuring` and `21-observability`; the labs that use it are Lab 3 and Lab 4 (see [CURRICULUM.md](CURRICULUM.md)).

## 1. How to read the numbers in this document

- **Reference run.** A result committed under `benchmark/results/reference/` with its provenance: hardware, model revision, engine version, server arguments, date. Use these to check your own numbers.
- **Smoke run.** A number taken from the first runs on one pod, made to check that the harness and the pod work. It is indicative only: it is not committed as a result file and it is not an experiment result. The few that remain are marked.
- **Derived.** Arithmetic from stated inputs. The arithmetic is shown, so you can redo it.
- **ILLUSTRATIVE EXAMPLE.** A constructed case that shows how a formula works. It is not a measurement.
- **Dense.** Every TFLOPS figure is a dense BF16 rate, never a sparse one (RESEARCH 6.1).
- **Final numbers** live in `benchmark/results/` and in each experiment's `RESULTS.md`. If a number here disagrees with a result file, the result file wins.

Measurements used in this document (RTX PRO 6000 Blackwell Server Edition, 96 GB; vLLM 0.31.0; Qwen3-8B; workload of 1,200 input and 180 output tokens unless the row says otherwise). Rows marked *reference run* are in `benchmark/results/reference/`; rows marked *smoke run* come from the first sessions on a pod and are not committed as result files:

| Item | Measurement |
| --- | --- |
| BF16, concurrency 1 (reference run) | TTFT p50 69 ms; ITL p50 11.6 ms (86.2 tokens/s per request); aggregate 83.9 tokens/s |
| BF16, concurrency 8 (reference run) | TTFT p50 356 ms; ITL p50 12.3 ms; aggregate 551 tokens/s (6.6 × concurrency 1); GPU-Util 100 % |
| FP8 weights, concurrency 1 (reference run) | ITL p50 7.3 ms (138.2 tokens/s per request, 1.6 × BF16) |
| FP8 weights, concurrency 16 (reference run) | aggregate 1,323 tokens/s (BF16 in the same session: 897) |
| 12 concurrent requests, BF16 (smoke run) | KV cache 3.9 % used; estimated MFU 6.6 %; estimated MBU about 28 % to 60 % depending on the averaging window; 358 W; GPU-Util 100 % |
| Harness against `vllm bench serve` (smoke run; concurrency 8, 64 requests, fresh seeds) | throughput within 0.4 %; TTFT within 3 to 4 %; mean ITL and TPOT within 0.2 %; end-to-end latency within 0.4 %; ITL p99 differed by 29 % |
| Same prompts sent twice (reference run) | TTFT p50 359 ms, then 50 ms; aggregate 550, then 639 tokens/s; with a new seed TTFT p50 back to 360 ms |
| vLLM start-up (reference runs; 198 s and 138 s are from the dry run on a second pod) | cold start (first start in a fresh container): 176 s to ready in the engine log, about 198 s as `wsctl start` measures wall time (188 to 198 s were seen); warm start (compile and kernel caches exist): 55 s in the log, 67.4 s by `wsctl`; restart of the same profile: 29 s in the log, 39.3 s by `wsctl`; first start of the FP8 checkpoint: 138 to 143 s (143 s in the reference session, 138 s on the dry-run machine); rebuild of the whole pod after a restart: 5 min 41 s |
| Pod price | $2.49 per hour |

## 2. The user's view and the operator's view

The same request looks different from the two sides of the API.

- **The user** sits at the end of a stream. They feel the wait before the first word, the speed of the text after that, and whether the answer is complete and right.
- **The operator** sits behind many streams. They care how many users fit, how full the memory is, what a token costs and whether the service stays up.

Most mistakes in benchmarking come from answering one side's question with the other side's metric.

| Question | Asked by | Metric | Measured where |
| --- | --- | --- | --- |
| Did it start quickly? | user | TTFT | client (harness), server histogram |
| Does the text stream at reading speed? | user | output TPS per request, ITL | client (harness), server histogram |
| How long until the whole answer? | user | end-to-end latency | client, server histogram |
| Did it work at all? | both | error rate, availability | client (failed requests), `vllm:request_success_total` by finish reason |
| Was the answer right? | both | quality regression against a baseline | `experiments/quality_probe.py` |
| How many users fit? | operator | aggregate TPS, request throughput, goodput | client run, `rate(vllm:generation_tokens_total)` |
| How close to the limit are we? | operator | running and waiting requests, KV-cache usage, preemptions | server gauges and counters |
| Are we paying for an idle or inefficient GPU? | operator | estimated MFU and MBU, power, VRAM | server estimates, GPU exporter |
| What does a token cost? | operator | price per hour ÷ tokens per hour | derived from aggregate TPS |

Cost per million output tokens at one load is `price per hour ÷ (aggregate TPS × 3,600) × 1,000,000`. With the reference runs and the pod price from section 1 (derived, ignores input tokens and idle time):

- BF16 at concurrency 8: $2.49 ÷ (551 × 3,600) × 1,000,000 ≈ $1.26 per million output tokens.
- BF16 at concurrency 16, the load of the quantization experiment: $2.49 ÷ (897 × 3,600) × 1,000,000 ≈ $0.77.
- FP8 at concurrency 16, same session: $2.49 ÷ (1,323 × 3,600) × 1,000,000 ≈ $0.52.

The FP8 figure says nothing about quality. Pair every cost number with the quality check (section 14).

Client-side and server-side numbers measure different things. The harness runs on the client and sees network time. Through an SSH tunnel from a laptop that includes the tunnel. The server histograms start when the server has the request and know nothing about the client. Quote which one you mean.

## 3. Definitions this repository uses

Every request is a stream. The harness records timestamps on it.

```text
t_sched ────── queue + prefill ──────► t_first ── gap ── gap ── … ── gap ──► t_end
|<──────────────  TTFT  ───────────────►|<──────  decode: N − 1 gaps  ──────►|
|<──────────────────────────  latency (end to end)  ────────────────────────►|
```

`t_sched` is the scheduled arrival in open-loop runs and the send time in closed-loop runs. `t_first` is the arrival of the first stream chunk that carries text. `N` is the number of output tokens the server reports in its `usage` block.

| Term | Formula in the harness | Result key | Note |
| --- | --- | --- | --- |
| TTFT | `t_first − t_sched` | `ttft_ms` | Queueing plus prefill: the pass over the prompt already yields the distribution of the first token, so that token is sampled at its end and no separate decode step precedes it. Reasoning deltas count as text. |
| ITL | gap between two consecutive text-carrying chunks, pooled over all requests | `itl_ms` | A chunk gap. It equals a token gap only when each chunk holds one token. |
| TPOT | `(latency − TTFT) ÷ (N − 1)` per request; requests with N < 2 are left out | `tpot_ms` | Per request, so every request weighs the same. |
| End-to-end latency | `t_end − t_sched` | `latency_ms` | Always reported. |
| Output TPS per request | `1 ÷ TPOT` | `output_tps_per_request` (distribution, with p1 and p5), `output_tps` (mean) | The speed one user sees after the first token. It excludes TTFT. |
| Aggregate TPS | `Σ N over successful requests ÷ run duration` | `aggregate_tps` | What the whole server delivered. Also called output token throughput. |
| Input TPS, total TPS | `Σ prompt tokens ÷ duration`, `(Σ prompt + Σ N) ÷ duration` | `input_tps`, `total_tps` | Prefill rate and combined rate. |
| Request throughput | `successful requests ÷ run duration` | `request_throughput_rps` | Failed requests are not counted. |
| Goodput | `requests that met every stated target ÷ run duration` | `slo.goodput_rps` | One load, one run. See the note on DistServe below. |
| SLO attainment | `requests that met every target ÷ all measured requests` | `slo.attainment` | Failed requests count against it. |
| Run duration | first send to last completion of the measured phase | `duration_s` | Warm-up is excluded. Ramp-up and drain are included. |

Rules the harness follows:

- **Start of the clock.** Latency and TTFT start at the scheduled arrival. In open loop a client that falls behind its schedule therefore shows the delay it causes instead of hiding it (section 7).
- **Token counts come from the server.** The request sets `stream_options.include_usage`. Chunks are not counted. Prompt tokens include anything the chat template adds.
- **Output length is pinned.** `ignore_eos` and `min_tokens` make every request produce exactly the requested number of tokens, so runs compare. Real traffic ends earlier and varies. Use `--no-engine-extensions` for engines that do not know these fields.
- **Thinking is off.** Chat requests send `enable_thinking: false`. A model that thinks first has a different TTFT, a different output length and a different cost.
- **Failed requests** are left out of every latency and throughput statistic. They are counted in `requests_failed` and against SLO attainment.
- **The mean of per-request rates is not the rate of the mean.** `output_tps` is the mean of `1 ÷ TPOT`. Read the median and the low percentiles in `output_tps_per_request`. For a per-user target the low percentiles are the interesting tail.
- **ITL and TPOT can disagree.** `--stream-interval` sets how many tokens go into one streamed event (default 1, RESEARCH 3.4). If it is larger, chunk gaps no longer equal token gaps. TPOT uses the server's token count and stays correct.
- **`1000 ÷ ITL in ms` and `1000 ÷ TPOT in ms` are tokens per second only under these definitions.** Other tools use the same words for other quantities (section 4).

A note on goodput. This repository's goodput is a measured rate of requests that met their targets at one tested load. The DistServe paper means something else: the highest request rate per GPU at which a stated share of requests (for example 90 %) meets the SLO. To get that number you need a sweep over rate or concurrency and the highest point whose attainment stays above the target (RESEARCH 10.5).

## 4. How other tools define the same words

The words are shared. The quantities are not. The comparison below comes from RESEARCH 10.4.

| Quantity | This repository | `vllm bench serve` | Other tools |
| --- | --- | --- | --- |
| TTFT | scheduled arrival (open loop) or send time (closed loop) to the first text chunk | request submission to the first token | AIPerf: first non-empty content chunk; reasoning tokens are not excluded (a separate metric skips them) |
| TPOT | `(latency − TTFT) ÷ (N − 1)` | same; set to 0 for goodput when the output has one token or less | NIM calls this quantity ITL. GuideLLM's TPOT includes the first token, which is a different number. MLPerf: average interval between tokens, normalization not stated in the text read. |
| ITL | gaps between text chunks, pooled over all requests | gaps between chunks, pooled over all requests (weighted by tokens) | AIPerf's ITL is per request `(latency − TTFT) ÷ (OSL − 1)`, which is vLLM's TPOT. GuideLLM: average gap between consecutive tokens, first token excluded. |
| End-to-end latency | clock start to end of stream | not printed by default (see below) | AIPerf: start to the last content chunk, without the final usage-only chunk |
| Output throughput | `Σ N ÷ duration` | `total_output_tokens ÷ duration` | AIPerf and NIM: same shape; AIPerf counts reasoning tokens |
| Per-user rate | `1 ÷ TPOT` per request | not reported | AIPerf: `1 ÷ ITL`, which excludes TTFT. NIM: output length ÷ end-to-end latency per request. |
| Goodput | every stated target (`ttft_ms`, `latency_ms`, `output_tps`) met; one load | `--goodput` with `ttft`, `tpot`, `e2el` in ms; no ITL key; requests with one token or less pass a TPOT target | DistServe: maximum rate per GPU at an attainment target. AIPerf: allows a throughput-style target. GuideLLM: reports attainment, errors count against it. |
| Percentiles | p50, p90, p95, p99 always, mean, min, max, count | mean, median, std and p99 only, unless you ask for more | |

Three consequences:

1. Say which tool's TPOT or ITL you mean. One tool's ITL is another tool's TPOT.
2. Do not compare a number from one tool with a number from another until the two definitions match.
3. `vllm bench serve` run as in its README prints a p99 but no p50, no p95 and no end-to-end latency. Always pass `--metric-percentiles 50,90,95,99` and `--percentile-metrics ttft,tpot,itl,e2el`.

The harness differs from `vllm bench serve` in three places: the clock starts at the scheduled arrival, ITL is pooled over text chunks, and percentiles and end-to-end latency are always reported. Everything else (TPOT, throughput) is defined the same way, and the cross-check in section 9 shows it.

Two related points from RESEARCH 10.5. In `vllm bench serve`, `--request-rate` is open loop, but `--max-concurrency` caps the requests in flight, so the run becomes partly closed loop when the server falls behind. The harness has the same caveat with `--max-inflight`. And `--request-rate inf` is a burst test: every request arrives at time zero and TTFT includes the whole queue.

## 5. Reading vLLM's `/metrics`

The dashboard reads these. A few rules save hours (RESEARCH 9.1 and 9.4).

- **Counters end in `_total` when scraped.** The code defines `vllm:prompt_tokens`, Prometheus exposes `vllm:prompt_tokens_total`. A rate needs the `_total` name.
- **Histograms expose `_bucket`, `_sum` and `_count`.** Percentiles come from `histogram_quantile` over `_bucket`. The mean is `rate(..._sum) ÷ rate(..._count)`.
- **One exception.** `vllm:iteration_tokens_total` is a histogram despite its name. The panels that use it must read `_count`, `_sum` or `_bucket`.
- **Series carry `model_name` and `engine` labels** in 0.31.0, not just `model_name`.
- **Old names give "no data", not an error.** `vllm:gpu_cache_usage_perc` is now `vllm:kv_cache_usage_perc` (a fraction from 0 to 1). `vllm:time_per_output_token_seconds` was replaced by `vllm:inter_token_latency_seconds` and `vllm:request_time_per_output_token_seconds`. Dashboards copied from old tutorials show empty panels.
- **There is no hit-rate gauge.** The prefix-cache hit rate is `rate(vllm:prefix_cache_hits_total) ÷ rate(vllm:prefix_cache_queries_total)`.
- **MFU and MBU are off by default.** The `vllm:estimated_*` series need `--enable-mfu-metrics`. The workshop base profile sets it.
- **The server-side TPOT histogram differs from the harness.** `vllm:request_time_per_output_token_seconds` records 0 for requests with one token or less. That pulls its mean below a client-side TPOT, which leaves those requests out. `vllm:inter_token_latency_seconds` has one sample per streamed event.
- **Buckets limit what you can see.** Request-phase histograms (end to end, queue, prefill, decode) start at 0.3 s. For a fast server, a quantile of queue time or prefill time says nothing: every observation sits in the first bucket, and `histogram_quantile` returns some value between 0 and 0.3 s whatever the true value is. The TTFT and ITL histograms have fine buckets and do not have this problem.
- **Dashboard percentiles are windowed estimates.** A p95 over a few-second window with a handful of requests is as noisy as a p95 from a small benchmark (section 6).
- **`/metrics` is not behind `--api-key`.** Keep the server on loopback (RESEARCH 3.7).

## 6. Percentiles, and why averages mislead

A percentile answers "what share of requests were this fast or faster". p95 of 800 ms means 95 % of requests had a TTFT of 800 ms or less. The harness reports count, mean, min, p50, p90, p95, p99 and max, computed with linear interpolation between the closest ranks (numpy's default). Per-request tokens per second also get p1 and p5, because for a "bigger is better" metric the low end is the tail.

An average hides the requests that went wrong. A user does not experience the average. They experience their own request.

ILLUSTRATIVE EXAMPLE (constructed, not measured). 100 requests: 94 with a TTFT of 60 ms, and 6 that waited behind a long prompt with a TTFT of 4,000 ms.

| Statistic | Value | What it tells you |
| --- | --- | --- |
| mean | 296 ms | No request had this TTFT. |
| p50 | 60 ms | The typical request is fine. |
| p90 | 60 ms | Nine in ten are fine. |
| p95 | 4,000 ms | The tail is a different experience. A TTFT p95 SLO of 800 ms fails. |
| max | 4,000 ms | |

### The p99 from few samples caveat

A percentile rests on the samples beyond it. The harness interpolates between neighboring samples, so with few samples p99 is nearly the maximum.

| Requests in the run | Expected samples above p95 | Expected samples above p99 | p99 is interpolated between |
| --- | --- | --- | --- |
| 32 | 1.6 | 0.3 | the largest and second largest sample |
| 64 | 3.2 | 0.6 | the largest and second largest sample |
| 128 | 6.4 | 1.3 | the second and third largest sample |
| 200 | 10 | 2 | the second and third largest sample |
| 1,000 | 50 | 10 | the 10th and 11th largest sample |

The default run size is `max(32, 8 × concurrency)` requests for closed loop and 64 for open loop. So the default sweep of concurrency 1, 4, 8 and 16 runs 32, 32, 64 and 128 requests. Read p50 and p90 from those runs. Treat p95 as a hint and p99 as an anecdote.

Rule of thumb used in this repository: have at least 10 samples beyond the percentile you quote. That is about 200 requests for p95 and 1,000 for p99. Raise `--requests` for the run you quote, and print the `count` next to the percentile.

More traps:

- **Percentiles do not average and do not add.** The mean of two p95 values is not the p95 of the combined traffic. Do not average p99 values of several small runs. Run once with more requests.
- **ITL has many samples but they are not independent.** Pooling gaps over 64 requests of 180 tokens gives about 11,000 samples. One slow engine step delays every running request at once, so the effective sample count is much smaller (inference). In the smoke-run cross-check (section 9), ITL p99 differed by 29 % between two tools while the mean ITL differed by 0.2 %. Tails are noisy.
- **Repeat the run.** Quote the spread between at least three runs for any number that goes into a decision.

## 7. Load generation: closed loop, open loop, warm-up and run size

### Closed loop and open loop

| | Closed loop | Open loop |
| --- | --- | --- |
| Harness flag | `--concurrency N` (a list runs a sweep) | `--request-rate R` (Poisson arrivals), optionally `--max-inflight` |
| What is fixed | N users, each waiting for an answer before asking again | R arrivals per second, whatever the server does |
| Question it answers | What happens with N users who wait? | What happens when R requests per second arrive? |
| Under overload | The offered load backs off with the server. Queueing hides. | The queue grows and latency climbs. Queueing shows. |
| Use it for | interactive-user experiments, finding the throughput knee | capacity planning, SLO checks |

Report which one you ran. The result JSON records it in `load_mode`.

### Coordinated omission

A test client that waits for a response before it sends the next request stops sampling exactly when the server stalls. The stall shows up as one slow request instead of as many requests that would have arrived during it. Percentiles then look much better than reality (Gil Tene; RESEARCH 10.5).

The harness avoids it in open loop by measuring from the scheduled arrival. If the client itself falls behind, that time is counted as latency. Two caveats remain. `--max-inflight` makes the run partly closed loop. And a closed-loop run is exposed to the effect by design.

### Little's law as a sanity check

Average requests in the system = arrival rate × average time in the system. In a closed loop the left side is the concurrency. The numbers of one run must agree with each other.

Derived from the reference run at concurrency 8 (`concurrency/baseline-c008`), 180 output tokens per request:

- Request rate: 551 ÷ 180 ≈ 3.06 requests/s.
- Average time in the system: 8 ÷ 3.06 ≈ 2.61 s.
- From the medians: TTFT 0.356 s + 179 × ITL 0.01234 s ≈ 2.57 s.

The two agree within 2 %. If yours do not, something is wrong with the run or with the definitions.

### Warm-up

The first requests after a start can be slower than later ones (caches, lazy initialization). NVIDIA's own benchmarking guidance says to warm up before timing (RESEARCH 6.11). The harness sends warm-up requests first, at the run's concurrency, and excludes them from the results. The default is the concurrency, but at least 2 and at most 8 requests. `--warmup` overrides it. Warm-up prompts differ from the measured prompts, so warm-up cannot fill the prefix cache for the measurement (section 8).

### Run size and first-wave artifacts

In a closed loop at concurrency N, N requests are sent at the same moment. Their prefills compete for the same engine steps. The last of them waits for the others. That is real behavior for a burst. It is not what steady arrivals look like.

Reference runs: the median TTFT was 69 ms at concurrency 1 and 356 ms at concurrency 8, where eight prompts of 1,200 tokens were prefilled together. Part of that increase is the first wave. The data cannot say how much.

What this does to small runs:

- **The first wave is a fixed share of the samples.** At the default run size the first wave is 12.5 % of the requests for every concurrency of 4 or more (4 of 32, 8 of 64, 16 of 128). That is more than the 5 % that defines p95. If the first wave has the slowest TTFT, the top 12.5 % of the samples are first-wave requests, and p90, p95 and p99 are first-wave numbers (inference from the arithmetic).
- **Waves can stay in step.** With every request pinned to the same output length, workers that started together tend to finish together and send their next request together. Arrivals stay bunched for longer than you would expect (inference, not measured here). Open-loop Poisson arrivals remove the synchronization.
- **Ramp-up and drain depress aggregate TPS.** The duration includes the start, when the queue is filling, and the end, when workers run out of prompts. A short run at high concurrency pays for both.
- **A fixed output length is comparable but not realistic.** Real outputs end early and vary.

What to do: raise `--requests` for the run you quote (section 6), prefer open loop with a fixed rate for SLO checks, compare runs of the same size, and report the request count.

## 8. The prefix-cache flattery pitfall

vLLM caches the KV blocks of prompt prefixes and reuses them when a later prompt starts with the same tokens (RESEARCH 3.9). A prompt that is mostly cached needs almost no prefill, so its TTFT collapses. For a benchmark that is a trap.

What happened on the pod (reference run, `benchmark/results/reference/prefix-cache/pitfall-*`). The same benchmark command was run twice with the same seed, so both runs sent identical prompts (concurrency 8, 64 requests each):

| Run | TTFT p50 | Aggregate | Prefix-cache hit rate of the run |
| --- | --- | --- | --- |
| First | 359 ms | 550 tokens/s | 0 % |
| Second, same prompts | 50 ms | 639 tokens/s | 98.7 % |
| Third, new seed | 360 ms | 550 tokens/s | 0 % |

Nothing was wrong with the server. The benchmark had measured the cache.

How the harness guards against it:

| Guard | What it prevents |
| --- | --- |
| A random seed per invocation, stored in the result (`workload.seed`). `--seed` repeats a run on purpose. | Re-running the same command sends the same prompts. |
| In a sweep, every level uses `seed + level index × 1,000,003`. `--same-prompts` switches this off. | Concurrency 8 hitting the cache filled by concurrency 4. |
| Every prompt carries a random nonce line. Only a prefix you declare (`--shared-prefix-tokens`) is shared. | Accidental sharing between requests of one run. |
| Warm-up prompts are built as different prompts from the measured ones. | Warm-up filling the cache for the measurement. |
| A warning when the server's hit rate during a run is above 5 % and the workload shares no prefix. The hit rate is stored in `server.prefix_cache_hit_rate`. | Silent flattery. |
| `--reset-prefix-cache` posts to `/reset_prefix_cache`. The route exists only with `VLLM_SERVER_DEV_MODE=1`, which the workshop servers do not set, so there the option warns and continues (RESEARCH 3.9). | A stale cache when you want a cold start. |

Two residual effects, derived from the code and not measured. First, with `--prompts-file` the prompts are used as given and cycled, so a file shorter than the run repeats prompts, and the cache answers the repeats. The hit-rate warning still fires. Second: every prompt starts with a short fixed instruction line before the nonce. That line can fill one or two 16-token cache blocks. For the 1,200-token baseline that is a hit rate of a few percent at most. For a short workload such as `chat-short` (300 input tokens) it can sit near the 5 % warning threshold. If the warning appears with a short workload, read the stored hit rate before you believe it.

Sharing is sometimes the point. The `shared-prefix` workload and the `prefix-cache` experiment declare a shared prefix on purpose and compare cache on and off. In production a high hit rate on shared system prompts is a real gain. Just never let it enter a measurement by accident.

## 9. Cross-checking against `vllm bench serve`

The harness is about 1,500 lines of code written for this workshop. A second, independent load generator keeps it honest. Run both on the pod with the same shape:

```bash
./benchmark/scripts/crosscheck.sh --concurrency 8 --input-tokens 1000 --output-tokens 200 --requests 64
```

The script runs `benchmark/run.sh` and `vllm bench serve` against the same server and writes `comparison.md` through `benchmark/scripts/compare_results.py`. It needs `OPENAI_API_KEY` in the environment, because `vllm bench serve` has no `--api-key` flag. It passes `--ignore-eos`, a fresh seed to each tool, `--percentile-metrics ttft,tpot,itl,e2el` and `--metric-percentiles 50,90,95,99`.

The seed matters for the tool itself. `vllm bench serve` defaults to `--seed 0`, so a second invocation sends the same prompts and meets the same prefix-cache flattery as section 8.

Smoke run (same shape, concurrency 8, 64 requests, fresh seeds; not committed as a result file): throughput within 0.4 %, TTFT within 3 to 4 %, mean ITL and TPOT within 0.2 %, end-to-end latency within 0.4 %, ITL p99 29 % apart.

The comparison script flags pairs that differ by more than 10 %, and tail percentiles at three times that. If a gap is larger, look for:

- a bug in the harness,
- a client-side bottleneck (one Python process generating load),
- different prompts and a prefix-cache pattern,
- a definition mismatch from section 4.

Then compare the harness's `/metrics` scrape (stored under `server` in each result) with the client-side numbers. Server-side TPOT and client-side TPOT differ for requests with one token or less.

## 10. GPU metrics

### What is recorded

- **By the harness**, once per second through `nvidia-smi`: `utilization.gpu`, `memory.used`, `power.draw`, `temperature.gpu` and `clocks.sm`. Each result stores a summary under `gpu` and the table shows the mean utilization and the maximum VRAM.
- **By the pod's GPU exporter** (`monitoring/gpu-exporter/exporter.py`), through NVML, under DCGM names: `DCGM_FI_DEV_GPU_UTIL`, `DCGM_FI_DEV_MEM_COPY_UTIL`, `DCGM_FI_DEV_FB_USED`, `DCGM_FI_DEV_FB_FREE`, `DCGM_FI_DEV_POWER_USAGE`, `DCGM_FI_DEV_GPU_TEMP`, `DCGM_FI_DEV_SM_CLOCK`, `DCGM_FI_DEV_MEM_CLOCK`. The same panels work with NVIDIA's `dcgm-exporter` on your own server.
- **Not available on the pods:** the profiling fields (`DCGM_FI_PROF_DRAM_ACTIVE`, `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE`, `DCGM_FI_PROF_SM_ACTIVE`). They need the `SYS_ADMIN` capability, which a rented container probably does not grant (RESEARCH 6.9, unverified for these pods). On your own hardware they are the best hardware-side view of decode.

### GPU-Util is not efficiency

`utilization.gpu` is the share of the sampling period in which at least one kernel was running (RESEARCH 6.7). It does not say how many of the 188 SMs were busy, how many Tensor Cores were active or how much of the memory bandwidth was used. A kernel that occupies one SM can read 100 %.

Reference runs, BF16, same workload (`concurrency/baseline-c001`, `concurrency/baseline-c008`):

| | Concurrency 1 | Concurrency 8 |
| --- | --- | --- |
| GPU-Util (mean) | 99 % | 100 % |
| Aggregate throughput | 84 tokens/s | 551 tokens/s |
| ITL p50 | 11.6 ms | 12.3 ms |

The gauge is flat while the useful work differs by 6.6 ×. At concurrency 1 the GPU reads about 16 GB of weights to emit one token per step. At concurrency 8 it reads the same weights and emits eight. Both keep a kernel resident all the time.

What to look at instead:

- tokens per second against the bandwidth bound (section 12);
- running requests and KV-cache usage (are there enough sequences in the batch);
- power draw, which follows real work more closely than utilization does (mean 362 W at concurrency 1, 393 W at 8, 425 W at 16 in the reference runs);
- estimated MFU and MBU, with the cautions in section 11;
- on your own hardware, DRAM-active and Tensor-active.

### Memory, power and clocks

- **VRAM used is flat.** vLLM reserves its memory budget at start-up (`--gpu-memory-utilization`, the workshop profile uses 0.80, vLLM's default is 0.92) and fills it with KV blocks. `memory.used` therefore says nothing about load. The KV-cache usage panel does.
- **Clocks and power change results.** The Server Edition card is passively cooled with a configurable power limit. A lower SM clock or a power cap lowers throughput. Compare runs only within one session on one pod, and report the SM clock and power next to every throughput number (RESEARCH 6.11).
- **MIG hides utilization.** On MIG-enabled GPUs the utilization queries are not supported.

## 11. Estimated MFU and MBU

- **MFU** (model FLOPs utilization) = FLOP per second achieved ÷ peak FLOP per second.
- **MBU** (memory bandwidth utilization) = bytes per second moved ÷ peak bytes per second.

vLLM computes both from counters (`vllm:estimated_flops_per_gpu_total`, `vllm:estimated_read_bytes_per_gpu_total`, `vllm:estimated_write_bytes_per_gpu_total`) when started with `--enable-mfu-metrics`. The dashboard divides their rate by the peaks held in two dashboard variables: 504 TFLOPS dense BF16 and 1,597 GB/s.

What they are not:

- **Not hardware counters.** They come from an analytic model of the work the scheduler issued for the model's shape. They do not see kernel stalls, cache hits in L2 or idle SMs.
- **Only as exact as the peak.** NVIDIA does not publish a dense BF16 peak for the Server Edition. 504 TFLOPS is the Workstation-clock figure. The plausible range is about 468 to 504 (RESEARCH 6.3), so the MFU scale is uncertain by several percent. The 1,597 GB/s bandwidth is published.
- **Tied to one precision.** The dashboard uses the BF16 peak. FP8 Tensor Cores have about twice that rate, so an FP8 model measured against the BF16 peak reads about twice as high as against its own peak (derived from RESEARCH 6.2).
- **Sensitive to the averaging window.** In the smoke run, estimated MBU ranged from about 28 % to 60 % depending on the window. Load is bursty and prefill and decode steps differ. Compare numbers only over the same window.
- **Single-GPU.** The panels assume one GPU. With tensor parallelism, check the series labels before trusting them.

How to use them. They are relative signals, not grades. A rule of thumb helps. At batch B with BF16 weights, a decode step that runs exactly at the bandwidth bound has an MFU of B ÷ ops:byte, which is about B ÷ 315 (derived from section 12). At 12 concurrent requests that is 3.8 %. The smoke run showed an estimated MFU of 6.6 % with KV usage at 3.9 %: the GPU was nowhere near compute-bound and had room for far more concurrent sequences. The estimate also contains prefill steps and attention work, so do not read it as the pure decode figure.

## 12. The roofline in ten lines

1. Every operation needs arithmetic (FLOP) and data movement (bytes). Its time is at least the larger of `FLOP ÷ peak FLOP/s` and `bytes ÷ peak bytes/s`.
2. Arithmetic intensity is the FLOP done per byte moved. The hardware's ridge point, NVIDIA's **ops:byte**, is `peak FLOP/s ÷ peak bytes/s`. Below it a kernel waits for memory. Above it a kernel waits for the math units.
3. Workshop GPU: 503.8 TFLOPS dense BF16 ÷ 1,597 GB/s ≈ **315 FLOP per byte** (293 in the unverified lower-clock case of 468 TFLOPS; derived, RESEARCH 6.4).
4. A decode step multiplies B token vectors by every weight matrix once. Its intensity is about `2B ÷ b` FLOP per byte, with `b` bytes per parameter. BF16 (b = 2) gives B. FP8 (b = 1) gives 2B.
5. So BF16 decode stays memory-bound until about 315 sequences share a step. Batches of 8 to 64 are far below that.
6. Prefill pushes the whole prompt through at once. A 1,200-token prompt is a batch of 1,200, above the ridge point, so prefill is compute-bound.
7. Lower bound for one decode step: `t ≥ (weight bytes + KV bytes read) ÷ memory bandwidth`. One step emits one token per sequence.
8. Qwen3-8B in BF16: 16.38 GB ÷ 1,597 GB/s = **10.3 ms** per step, at most 97.5 tokens/s for one sequence. KV reads at about 1,300 tokens of context add 147,456 B × 1,300 ≈ 0.19 GB, so 10.4 ms.
9. Reference run: measured ITL p50 was **11.6 ms**, 13 % above the bound. That gap is attention, sampling, launch and scheduler overhead.
10. Batching shares one weight read between all sequences, so step time barely moves while throughput scales. Reference runs: ITL 11.6 ms at concurrency 1, 12.3 ms at concurrency 8, aggregate throughput 6.6 ×. That is why concurrency, KV capacity and quantization are the levers, and why 1,597 GB/s (not the Workstation card's 1,792) is the number to remember.

The bound against the measurement, with FP8 for comparison:

| | Bytes read per step | Bound per step | Bound as tokens/s | Measured ITL p50 (reference runs) | Measured above bound |
| --- | --- | --- | --- | --- | --- |
| BF16 weights | 16.38 GB | 10.3 ms | 97.5 | 11.6 ms | 13 % |
| FP8 weights | 9.50 GB (8.85 GiB reported by the server) | 5.95 ms | 168 | 7.25 ms | 22 % |

FP8 weights are not half of BF16, because embeddings and the output head stay in BF16. The measured speed-up (1.6 ×) is close to the byte ratio (1.72 ×). Both bounds are derived.

The compute side, derived with the 2N rule (a model of N parameters needs about 2N FLOP per token, RESEARCH 6.10): prefilling 1,200 tokens needs about 2 × 8.19e9 × 1,200 ≈ 1.97e13 FLOP, which takes about 39 ms at 504 TFLOPS. The measured TTFT p50 at concurrency 1 was 69 ms. That figure also holds scheduling and the first decode step of about 10 ms.

How to use the bound. It is a sanity check, not a forecast. A measurement above the bound means the byte count or the bandwidth you used is wrong, for example weights are quantized or you took the Workstation card's figure. A measurement far below it means look at clocks, power and overhead before you blame the engine. Measured results always override the datasheet and the bound.

## 13. Dashboard panel map

The dashboard "KI ohne Cloud: inference" is generated by `monitoring/grafana/build_dashboard.py` and checked against the metric names vLLM 0.31.0 exports (`monitoring/grafana/test_dashboard.py`). Rates use `$__rate_interval`. Percentile panels show p50 and p95 unless stated. The expressions in the tables are shortened for reading (a division is written with ÷, label sets are left out). The exact PromQL is in the generator.

### What the user feels

| Panel | Metric behind it | Question it answers | Read with care |
| --- | --- | --- | --- |
| Request rate | `sum(rate(vllm:request_success_total))` | Is the server completing what we send? | Counts every finish reason. Flat while load rises means saturation. |
| TTFT | `histogram_quantile` over `vllm:time_to_first_token_seconds_bucket` | How long until the first token? | Server-side. Grows with waiting requests and prompt length. |
| Inter-token latency | `histogram_quantile` over `vllm:inter_token_latency_seconds_bucket` | Does the stream feel smooth? | `1 ÷ ITL` is the per-user tokens per second. |
| End-to-end latency | `histogram_quantile` over `vllm:e2e_request_latency_seconds_bucket` | How long until the whole answer? | Bucket floor 0.3 s (section 5). |

### What the server is doing

| Panel | Metric behind it | Question it answers | Read with care |
| --- | --- | --- | --- |
| Running requests | `sum(vllm:num_requests_running)` | How big is the batch? | Bounded by `--max-num-seqs` and by KV capacity. |
| Waiting requests | `sum(vllm:num_requests_waiting)` | Is there a queue? | Above zero for long means arrivals exceed capacity. |
| Tokens per second | `rate(vllm:generation_tokens_total)` and `rate(vllm:prompt_tokens_total)` | How much decode and prefill work is done? | The rate version of aggregate TPS. Decode tokens are what users read. |
| KV cache usage | `max(vllm:kv_cache_usage_perc) * 100` | How close is memory-limited concurrency? | A fraction from 0 to 1 in the metric. Near 100 % the scheduler queues or preempts. |
| Prefix cache hit rate | `rate(vllm:prefix_cache_hits_total) ÷ rate(vllm:prefix_cache_queries_total)` | Is caching helping? | Also the check for flattered benchmarks (section 8). |
| Preemptions | `rate(vllm:num_preemptions_total)` | Is memory pressure forcing recomputation? | A recompute cost, not an error. Non-zero with full KV means pressure. |
| Queue time | `histogram_quantile` over `vllm:request_queue_time_seconds_bucket` | How long do requests wait before they run? | Bucket floor 0.3 s: small values are not resolved. |
| Prefill vs decode time | `vllm:request_prefill_time_seconds_bucket`, `vllm:request_decode_time_seconds_bucket`, p50 | Where does a running request spend its time? | Same bucket floor: a fast prefill reads as the first bucket. |
| Finished requests by reason | `sum by (finished_reason) (rate(vllm:request_success_total))` | Why do requests end? | `stop` is the model ending, `length` is a cut at `max_tokens`, `abort` is a client leaving. |

### What the hardware is doing

| Panel | Metric behind it | Question it answers | Read with care |
| --- | --- | --- | --- |
| GPU utilization | `avg(DCGM_FI_DEV_GPU_UTIL)` | Is a kernel running? | Not efficiency (section 10). |
| VRAM used | `DCGM_FI_DEV_FB_USED`, `DCGM_FI_DEV_FB_FREE` | How much memory is reserved? | Flat after start-up because vLLM reserves its budget. |
| Power | `sum(DCGM_FI_DEV_POWER_USAGE)` | Is real work happening, or is the card throttled? | Follows work better than utilization. Compare with clocks. |
| Estimated compute use (MFU) | `rate(vllm:estimated_flops_per_gpu_total) ÷ (peak_tflops × 1e12)` | How much of the compute peak is used? | An estimate against a variable peak (section 11). |
| Estimated memory traffic (MBU) | `(rate(read bytes) + rate(write bytes)) ÷ (peak_bw_gbs × 1e9)` | How much of the bandwidth peak is used? | An estimate. Decode is usually limited here, prefill by compute. |

### Reading the panels together

A reading guide for the incident investigation of the observability module (inference from what each metric measures, not a rule):

| What you see | Likely reading |
| --- | --- |
| Waiting above zero, TTFT and queue time rising, KV usage low | Too few sequences allowed (`--max-num-seqs`) or a burst of prefill work. |
| Waiting above zero, KV usage near 100 %, preemptions above zero | KV pressure. More KV, shorter contexts or fewer sequences help. More clients do not. |
| ITL rising while running requests rise | Heavier decode batches, or long contexts adding KV reads. |
| Request rate flat while the offered load rises | Saturation. Find out which resource: KV, bandwidth or compute. |
| GPU-Util 100 %, running requests low, estimated MBU low | A small batch. The GPU is busy but the load is too low to use it. |
| Running and waiting at zero, tokens per second at zero, power near idle | An idle GPU: no load, or clients gave up (`abort` in the finish reasons). |

## 14. SLO and goodput: a worked example

### The course SLO

The workshop's running example is a workload of 1,200 input tokens, 180 output tokens and 20 concurrent users, with this SLO (CURRICULUM section 1):

| Objective | Target | Measured by |
| --- | --- | --- |
| Time to first token | p95 ≤ 800 ms | `ttft_ms.p95` of an open-loop or closed-loop run; or per-request attainment on `ttft_ms=800` |
| Speed per user | at least 25 output tokens/s per request, which is a TPOT of at most 40 ms | `output_tps_per_request` (look at p5 and p1); `--slo output_tps=25` |
| Availability | 99.9 % | failed requests during a run; time-based availability needs probes in production |
| Quality | at most 2 % regression against the baseline | `experiments/quality_probe.py` |

For context, MLPerf's server scenario for a Llama 3.1 8B summarization task allows TTFT of 2,000 ms and TPOT of 100 ms (conversational) or 500 ms and 30 ms (interactive) (RESEARCH 10.3). The course SLO sits between the two.

The SLO as written mixes a percentile target (TTFT p95) with a per-request target (25 tokens/s per request). The harness's `--slo ttft_ms=800,output_tps=25` checks both per request: a request is good only if it meets every target. That is stricter than a TTFT p95 on its own. Say in the report which form you checked.

### What the SLO implies

- **Latency ceiling.** A request that just meets both targets takes 0.8 s plus 180 ÷ 25 = 7.2 s of decoding, 8.0 s in total. That is the `latency_ms=8000` of the harness's SLO example.
- **Aggregate rate.** 20 users who all stream at once, each at 25 tokens/s, need 20 × 25 = 500 tokens/s from the server.
- **Availability.** 99.9 % allows 0.1 % of requests to fail. As time, that is 43.2 minutes in a 30-day month (30 × 24 × 60 × 0.001) or 8.76 hours in a year.
- **Quality.** The quality probe reports each deployment's accuracy with a 95 % Wilson interval, and the difference between two deployments in percentage points. At its default of 240 items one item is 0.42 points, so 2 points are about 5 items. The probe can flag a large drop. It cannot prove that two deployments are within 2 %. State whether you read 2 % as points or as a relative drop.

The availability budget against the start-up times (reference runs of the baseline start-up experiment; one replica, so every restart is downtime): the budget is 2,592 s per 30-day month. The primary basis is the engine log, the seconds from the first log line to "ready"; the wall time as `wsctl` measures it is longer and is given in parentheses. A rebuild has no engine-log figure: it is wall time.

| Event | Duration, engine log (`wsctl` wall time) | Share of the monthly budget |
| --- | --- | --- |
| Restart of vLLM with warm caches | 29 s (39 s) | 1.1 % (1.5 %) |
| Cold start of vLLM | 176 s (198 s) | 6.8 % (7.6 %) |
| Rebuild of the whole pod after a restart | 341 s (wall time) | 13.2 % |

Three cold starts in a month use about a fifth of the budget on their own (528 s of 2,592 s; 594 s, 23 %, by wall time). That is an argument for a second replica and for rolling restarts (`22-scaling`).

### What the reference runs can and cannot say

| SLO term | What the reference runs show (`concurrency/`) | Verdict |
| --- | --- | --- |
| TTFT p95 ≤ 800 ms | p95 of 73 ms at concurrency 1, 416 ms at 8 and 821 ms at 16 (48 to 96 requests per run). | Met at 8, missed by 21 ms at 16. The p95 rests on a few requests and is what first-wave effects distort (section 7). Concurrency 20 was not run. |
| ≥ 25 tokens/s per request | Per-request speed p5 of 70.7 tokens/s at concurrency 8, 58.6 at 16 and 28.3 at 64 (p50: 79.4, 68.7 and 32.4). | Met at every tested level, about 3 × above the target at 8. The TTFT target breaks first. |
| Aggregate 500 tokens/s for 20 users | 551 tokens/s at concurrency 8, 900 at 16. | Enough capacity on throughput alone. The TTFT target decides, not the throughput. |
| Quality ≤ 2 % | Not part of the concurrency sweep. | Run the probe for every deployment you recommend (`experiments/quantization/RESULTS.md` shows it for FP8). |

### A goodput computation

ILLUSTRATIVE EXAMPLE (constructed, not measured). A run lasts 10 s. The harness sent 21 measured requests with `--slo ttft_ms=800,output_tps=25`:

| Outcome | Requests |
| --- | --- |
| Met both targets | 17 |
| TTFT above 800 ms, speed fine | 2 |
| TTFT fine, speed below 25 tokens/s | 1 |
| Failed (HTTP error) | 1 |
| Total | 21 |

The harness reports:

- request throughput = 20 successful ÷ 10 s = 2.0 requests/s (the failed one is not counted);
- attainment = 17 ÷ 21 = 0.81, because failed requests count against it;
- goodput = 17 ÷ 10 s = 1.7 requests/s.

Compare the percentile form of the same SLO. Two of the 20 successful requests have a TTFT above 800 ms. That is 10 %, more than the 5 % a p95 target allows, so `ttft_ms.p95` is above 800 ms and the TTFT objective fails, even though 81 % of all requests were fully good. The two statements are different questions.

To turn one load into a capacity statement, repeat at several rates or concurrencies and read off the highest load whose attainment stays at or above the target you set (95 % is a common choice). That is the DistServe meaning of goodput. Then divide the pod price by that goodput to get the cost per good request.

### The decision loop

1. Fix the workload and the SLO before you measure.
2. Sweep the load (concurrency 1, 4, 8, 16, and one or two points beyond the knee).
3. At each point read the user metrics (TTFT, output TPS per request, attainment) and the server metrics (running, waiting, KV usage, preemptions).
4. Name the saturated resource: queue slots, KV memory, bandwidth or compute.
5. Change one thing, repeat, and write down what improved, what got worse, what it cost in quality and in operations.

## 15. Checklist before you trust a number

- Which tool produced it, and which definition of TTFT, TPOT and ITL does it use?
- How many requests were measured, and was warm-up excluded? Is the `count` printed next to the percentile?
- Closed or open loop, at what concurrency or rate?
- Fresh seed? What was the prefix-cache hit rate during the run?
- Did any request fail, and were failures counted?
- What were the SM clock and the power draw?
- Is the result file in `benchmark/results/` with its provenance?
- Does the number respect the bandwidth bound and Little's law?
- Was the quality of the deployment checked, not only its speed?

## 16. Where each topic is covered

| Topic | Evidence | Teaching |
| --- | --- | --- |
| Tool definitions, goodput, closed and open loop | RESEARCH 10.1 to 10.6 | `11-measuring` |
| vLLM metric names, buckets, deprecated names | RESEARCH 9.1 to 9.5 | `21-observability` |
| GPU specifications, ops:byte, roofline | RESEARCH 6.2 to 6.4, 6.10 | `03-gpu-fundamentals`, `05-inference-mechanics` |
| `nvidia-smi`, NVML, DCGM, power and clocks | RESEARCH 6.7, 6.9, 6.11 | `03-gpu-fundamentals`, `21-observability` |
| Scheduler, prefix cache, preemption | RESEARCH 3.8, 3.9 | `13-continuous-batching`, `14-kv-cache` |
| Harness behavior | `benchmark/infbench/` | `12-lab-benchmark` |
| Dashboard | `monitoring/grafana/build_dashboard.py` | `21-observability` |
| Terms | [GLOSSARY.md](GLOSSARY.md) | all |
