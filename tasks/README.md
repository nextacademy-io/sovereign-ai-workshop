# Tasks

Six exercises carry the workshop. Each one has a scope that says what counts as done, a starting point you can return to, a validation you can check yourself, and a way out if you get stuck.

| # | Task | Module | Mode | Reset |
| --- | --- | --- | --- | --- |
| 00 | [Preflight](00-preflight.md) | `pre-00-preflight` | alone | |
| 01 | [Model selection](01-model-selection.md) | `07-lab-model-selection` | group, one scenario per sub-group | `./scripts/reset.sh lab-01` |
| 02 | [First inference server](02-first-inference-server.md) | `09-lab-first-server` | alone, same server | `./scripts/reset.sh lab-02` |
| 03 | [Benchmark the baseline](03-benchmark.md) | `12-lab-benchmark` | group, four roles | `./scripts/reset.sh lab-03 --server` |
| 04 | [Optimize the deployment](04-optimization.md) | `17-lab-optimize` | group, one lever | `./scripts/reset.sh lab-04 --server` |
| 05 | [Production architecture](05-production-design.md) | `26-lab-architecture` | group, short defense | `./scripts/reset.sh lab-05` |

The module is the id in [`config/workshop.yaml`](../config/workshop.yaml); the task is done when you reach what its *Scope* section says, and the lab's debrief follows.

## One document through the whole path

`workshop-artifacts/inference-report.md` grows from task to task: workload, selected model, hardware, baseline, experiments, optimized configuration, production architecture, security considerations, final recommendation. Every task says which section to fill.

## If you fall behind or break something

`./scripts/reset.sh lab-NN` gives you the starter files of lab NN without deleting your own work (replaced files are saved in `~/.workshop-backups/`), plus measured reference results to fall back on. Add `--server` to also put the shared server on the profile the lab expects (this restarts it for your group). A reset never deletes your own work, so the end of any lab is a safe place to stop.

## Answer keys

The trainer's reference answers are not in this repository. The measured reference results (`benchmark/results/reference/`) show what the numbers looked like on the workshop GPU, not what to conclude. For Lab 4 they cover what the lectures showed, not your variation: nobody has that answer yet.
