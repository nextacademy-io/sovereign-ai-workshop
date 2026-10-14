# Benchmark results

Everything under this directory is evidence. Every JSON file carries its provenance: hardware, model revision, engine version, server arguments, workload, date (`pnpm check` rejects a result without them).

| Directory | What it is |
| --- | --- |
| `reference/` | The curated results the slides, tasks and workshop states cite. Stable paths without dates. Read-only: `./scripts/reset.sh lab-NN` copies them to participants. Promoted from the sessions below with `benchmark/scripts/promote_reference.py`. |
| `2026-10-14-rtxpro6000-s2/` | Session 1 of the validation (one pod, RTX PRO 6000 Blackwell Server Edition): `baseline`, `concurrency`, start-up timelines. |
| `2026-10-14-rtxpro6000-s2c/` | `context-length`, rerun after the first `kv-constrained` profile refused to start. |
| `2026-10-14-rtxpro6000-s2d/` | `prefix-cache` and `quantization`, rerun after the `no-prefix-cache` profile turned out not to switch the cache off, and with the repaired quality probe. |
| `2026-10-14-rtxpro6000-s2e/` | `demos`, rerun with a valid control for speculative decoding. |
| `2026-10-14-rtxpro6000-s3/` | The dry run as a participant on a second, freshly created pod (a different host): the Lab 3 and Lab 4 results of the test user, the trainer's audit log, and the step timings of the deployment. |
| `mine/` | Your own results on a workshop machine (not committed). |

Superseded runs (a first context-length attempt that failed to start, a prefix-cache comparison whose "cache off" was not off, a control that was not a control) were removed rather than kept next to the corrected ones; `docs/TROUBLESHOOTING.md` section 2.1 and the `RESULTS.md` of each experiment tell what happened.

Session directories are named `<date>-<gpu>-<label>`. Dates inside results are the measurement dates; the teaching content does not carry dates.
