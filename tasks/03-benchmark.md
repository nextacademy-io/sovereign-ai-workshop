# Task 03 — Benchmark the baseline

## Goal

Understand how concurrency affects latency and throughput on your group's server, and find the point where more load stops helping.

## Context

You have a working vLLM deployment. Before anyone optimizes it, you need a **baseline**: the same deployment, the same workload, measured at several levels of concurrency, with percentiles and with the hardware's view next to the user's view. Every later claim of "faster" is a comparison with this baseline.

## Timebox

45 minutes.

## Starting Point

- Your group's server runs the `baseline` profile (BF16, Qwen3-8B). `sudo wsctl status` shows it.
- The workload is `workshop-baseline`: 1,200 input tokens and 180 output tokens per request, the example from the SLO slide.
- `workshop-artifacts/inference-report.md` has an empty *Baseline* table. If your environment is not in this state: `./scripts/reset.sh lab-03 --server`.

## Instructions

**Only one benchmark runs at a time per group** (it is one shared server). Choose a *driver* for the first round; everyone else watches.

1. **Predict first.** Write down, before you measure: at which concurrency will the total tokens per second stop growing? What will happen to time to first token and to the speed one user sees? Which resource will look saturated?
2. **Prepare the dashboard.** Everyone opens Grafana through a tunnel (`ssh -p <port> -L 3000:127.0.0.1:3000 <your-user>@<host>`, then `http://127.0.0.1:3000`, dashboard *KI ohne Cloud: inference*). Watch *Running requests*, *Waiting requests*, *KV cache usage*, *Tokens per second* and *GPU utilization*.
3. **Measure (driver).**

   ```bash
   ./scripts/benchmark.sh --concurrency 1,4,8,16 --label baseline
   ```

   It prints a table and writes JSON to `benchmark/results/mine/<time>-baseline/`. The harness uses fresh prompts on every run; do not pass `--seed`.
4. **Record.** Everyone copies the table into the *Baseline* section of your report: TTFT p50 and p95, latency p50 and p95, output tokens per second per request, aggregate tokens per second, GPU utilization, VRAM.
5. **Contention round.** Now two members run `./scripts/benchmark.sh --concurrency 8 --label contention` **at the same time**. Compare each with the concurrency-8 row of the first run. What did sharing the server do?
6. **Answer the five questions** in your report: when does throughput stop scaling; when does latency deteriorate; what resource looks saturated; which configuration would you deploy; why.

## Expected Result

- Aggregate tokens per second grows with concurrency, less than linearly, then flattens.
- The speed one user sees (tokens per second per request) falls only slowly at first: eight requests together cost little more per token than one. This is why batching works.
- Time to first token grows with concurrency because prompts are prefilled together and queue.
- GPU utilization reads about 100 % at every level, including concurrency 1. It does not tell you how well the GPU is used; power draw and throughput do.
- Your numbers will differ from `benchmark/results/reference/` by a few percent. The shape should be the same.

## Validation

- `ls benchmark/results/mine/*/c*.json` lists four result files, each with `configuration.hardware`, `model_revision`, `engine_version` and `server_args`.
- Your table agrees with `summary.md` in the same directory.
- You can state, in one sentence each, the concurrency at which you would deploy for the SLO of the slide (TTFT p95 under 800 ms, at least 25 output tokens per second per request) and what would break first above it.

## If You Get Stuck

| Symptom | Fix |
| --- | --- |
| `warning: ... prefix cache answered N % ...` | An earlier run used the same prompts. Run again without `--seed`; if the warning stays, ask the trainer. |
| Requests fail or time out | `sudo wsctl status`. Another benchmark may still be running: only one at a time. |
| Your numbers differ from the reference by more than 20 % | Someone else is using the server, or the run was too short. Use `--requests 64` for each level. |
| Your own run failed completely | `./scripts/reset.sh lab-03` copies the reference results to `benchmark/results/reference/`. Continue with those and say so in the report. |

## Further Exploration

- Add `--slo ttft_ms=800,output_tps=25` and compare *goodput* with throughput at concurrency 16.
- Run an open-loop test: `./scripts/benchmark.sh --request-rate 3 --requests 64` and then `--request-rate 8`. What happens when arrivals do not wait for the server?
- Compare `--workload chat-short` with `--workload rag-long-context` at the same concurrency. Which phase dominates each?
- Run `./benchmark/scripts/crosscheck.sh` and look at the differences between our harness and `vllm bench serve`.
