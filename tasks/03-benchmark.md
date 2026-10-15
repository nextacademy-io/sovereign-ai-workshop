# Task 03 — Benchmark the baseline

## Goal

Understand how concurrency affects latency and throughput on your group's server, and find the point where more load stops helping.

## Context

You have a working vLLM deployment. Before anyone optimizes it, you need a **baseline**: the same deployment, the same workload, measured at several levels of concurrency, with percentiles and with the hardware's view next to the user's view. Every later claim of "faster" is a comparison with this baseline.

## Scope

Done means you have a four-level sweep with its result files, the *Baseline* table and the four questions answered in your report, and you have seen what a second benchmark does to the shared server. Out of scope: changing the server configuration (the optimization lab does that) and long sweeps beyond concurrency 16.

## Starting Point

- Your group's server runs the `baseline` profile (BF16, Qwen3-8B). `sudo wsctl status` shows it.
- The workload is `workshop-baseline`: 1,200 input tokens and 180 output tokens per request, the example from the SLO slide.
- `workshop-artifacts/inference-report.md` has an empty *Baseline* table. If your environment is not in this state: `./scripts/reset.sh lab-03 --server`.

## Instructions

**Only one benchmark runs at a time per group** (it is one shared server). Take one role each for the first round (with three people, one person holds two roles):

| Role | Does |
| --- | --- |
| Driver | runs the sweep |
| Dashboard reader | watches Grafana: GPU utilization, running and waiting requests |
| Recorder | fills the report |
| Skeptic | asks which number would change the group's mind |

The roles rotate for the contention round.

1. **Predict first.** Write down, before you measure: at which concurrency will the total tokens per second stop growing? What will happen to time to first token and to the speed one user sees? Which resource will look saturated?
2. **Prepare the dashboard.** Everyone opens Grafana through a tunnel (`ssh -p <port> -L 3000:127.0.0.1:3000 <your-user>@<host>`, then `http://127.0.0.1:3000`, dashboard *KI ohne Cloud: inference*). The dashboard reader calls out *GPU utilization*, *Running requests* and *Waiting requests* while the sweep runs; *KV cache usage* and *Tokens per second* are worth a look too.
3. **Measure (driver).**

   ```bash
   ./scripts/benchmark.sh --concurrency 1,4,8,16 --label baseline
   ```

   It prints a table and writes JSON to `benchmark/results/mine/<time>-baseline/`. The harness uses fresh prompts on every run; do not pass `--seed`.
4. **Record.** The recorder copies the table into the *Baseline* section of your report (everyone keeps a copy): TTFT p50 and p95, latency p50 and p95, output tokens per second per request, aggregate tokens per second, GPU utilization, VRAM. The skeptic names the one number that would change the group's mind about its prediction.
5. **Contention round.** Rotate the roles. Now two members run `./scripts/benchmark.sh --concurrency 8 --label contention` **at the same time**; the others take dashboard reader, recorder and skeptic. Compare each result with the concurrency-8 row of the first run. What did sharing the server do?
6. **Answer the four questions** in your report (they are under the table): when does throughput stop scaling; when does latency deteriorate; what resource looks saturated; which configuration would you deploy, and why.

## Expected Result

- Aggregate tokens per second grows with concurrency, but every doubling adds less. Within the four levels it does not flatten on this GPU.
- The speed one user sees (tokens per second per request) falls only slowly at first: several requests together cost little more per token than one, and the fall speeds up at higher concurrency. This is why batching works.
- Time to first token grows with concurrency because prompts are prefilled together and queue.
- GPU utilization reads about 100 % at every level, including concurrency 1. It does not tell you how well the GPU is used; power draw and throughput do.
- In the contention round each of the two runs is slower than the same concurrency alone: two benchmarks are one load for the server.
- Your numbers will differ from the reference by a few percent. The shape should be the same.

## Validation

Compare your table with the reference run (`benchmark/results/reference/concurrency/`, baseline profile on the workshop GPU):

| Concurrency | 1 | 4 | 8 | 16 |
| --- | --- | --- | --- | --- |
| Aggregate tokens/s | 84 | 310 | 551 | 900 |
| TTFT p95 (ms) | 73 | 210 | 416 | 821 |
| Tokens/s per request (p50) | 86 | 83 | 79 | 69 |
| Power (W, mean) | 362 | 366 | 393 | 425 |

GPU utilization is about 100 % at every level. In the trainer's longer sweep (up to 64) the gain per doubling shrinks from ×1.9 to ×1.3.

Then check your own work:

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
