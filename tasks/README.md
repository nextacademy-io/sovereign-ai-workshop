# Tasks

Six exercises carry the workshop. Each one has a timebox, a starting point you can return to, a validation you can check yourself, and a way out if you get stuck.

| # | Task | Day | Timebox | Mode | Reset |
| --- | --- | --- | --- | --- | --- |
| 00 | [Preflight](00-preflight.md) | before Day 1 | 15 min | alone | |
| 01 | [Model selection](01-model-selection.md) | 1 | 30 min | group | `./scripts/reset.sh lab-01` |
| 02 | [First inference server](02-first-inference-server.md) | 1 | 35 min | alone, same server | `./scripts/reset.sh lab-02` |
| 03 | [Benchmark the baseline](03-benchmark.md) | 2 | 45 min | group, one driver | `./scripts/reset.sh lab-03 --server` |
| 04 | [Optimize the deployment](04-optimization.md) | 2 | 40 min | group, one hypothesis | `./scripts/reset.sh lab-04 --server` |
| 05 | [Production architecture](05-production-design.md) | 3 | 45 min | group, defend in 5 min | `./scripts/reset.sh lab-05` |

The times are what you are told in the room. The block in the agenda is longer because it includes the debrief.

## One document through all three days

`workshop-artifacts/inference-report.md` grows from task to task: workload, selected model, hardware, baseline, experiments, optimized configuration, production architecture, security considerations, final recommendation. Every task says which section to fill.

## If you fall behind or break something

`./scripts/reset.sh lab-NN` gives you the starter files of lab NN without deleting your own work (replaced files are saved in `~/.workshop-backups/`), plus measured reference results to fall back on. Add `--server` to also put the shared server on the profile the lab expects (this restarts it for your group).

## Answer keys

The trainer's reference answers are not in this repository. The measured reference results (`benchmark/results/reference/`) are the only "answers" you get: they tell you what the numbers looked like on the workshop GPU, not what to conclude.
