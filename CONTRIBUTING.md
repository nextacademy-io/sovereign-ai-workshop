# Contributing

This repository is a workshop product, not only a collection of files. Changes are judged by one question:

> Does a participant leave understanding how the inference system behaves, and can the trainer deliver that reliably?

## Ground rules

1. **Measure, then teach.** Slides and tasks describe behaviour that was observed on real hardware. Do not write explanations around expected results. If an experiment contradicts the explanation, investigate first.
2. **Never fabricate numbers.** Every number on a slide comes from a file under `benchmark/results/`, or the component is marked `source="illustrative"` and renders an **ILLUSTRATIVE EXAMPLE** badge. `pnpm check` enforces this.
3. **Primary sources first.** vLLM, Hugging Face and NVIDIA documentation, model cards, original papers and official EU texts. Add every source to `docs/REFERENCES.md`.
4. **Do not copy copyrighted material.** The book *Inference Engineering* is a reference. Explain concepts in your own words, draw your own diagrams, cite by chapter.
5. **English only,** except the workshop title *KI ohne Cloud*.
6. **No dates or event details in teaching content.** Use relative times ("Day 2, block 3"). The agenda lives in `config/workshop.yaml`.
7. **No secrets.** Keys, tokens and credentials never enter the repository. Use `.env` (gitignored) and keep `.env.example` as placeholders only.

## Setup

```bash
nvm use                 # Node 24 (>= 22.12 required by Slidev)
corepack enable         # pnpm is pinned via the packageManager field
pnpm install
uv sync --extra dev     # Python tooling for benchmark/ and apps/
```

## Commands

| Command | What it does |
| --- | --- |
| `pnpm dev` | Start the Slidev deck with hot reload |
| `pnpm build` | Build the static deck into `slides/dist/` |
| `pnpm export` | Export the deck to PDF (needs `pnpm exec playwright-chromium install chromium` once) |
| `pnpm check` | Repo consistency checks (tasks, timeboxes, notes, metric sources, results provenance) |
| `pnpm check:release` | Same, but path drift becomes an error and all required files must exist (what CI runs) |
| `pnpm lint` | markdownlint, shellcheck, ruff |
| `pnpm test` | pytest (benchmark harness against a fake streaming server, repo hygiene) |
| `pnpm ci` | Everything CI runs |

## Changing the agenda

Edit `config/workshop.yaml` first. `pnpm check` verifies that the daily teaching time fits, that blocks do not overlap and that every task timebox in `tasks/*.md`, `tasks/README.md` and the lab slides agrees with it.

## Adding or changing a model

Edit `config/models.yaml`. Pin the Hugging Face commit SHA (`revision`), record the licence and the commercial-use implications, and re-run the baseline experiment that depends on the model. Update `docs/MODEL-SELECTION.md` if the selection reasoning changes.

## Adding a benchmark result

Results are produced by `benchmark/run.sh`, which embeds hardware, model, revision, vLLM and CUDA versions, server arguments, workload and date. Commit the JSON together with the Markdown summary under `benchmark/results/<date>-<gpu>-<experiment>/`. Hand-edited result files are rejected in review.

## Pull requests

- Keep each PR to one concern (a task, a diagram, an experiment).
- Run `pnpm ci` before pushing.
- Describe what you measured or verified, and on which hardware.

## Known dependency constraint

`slides/package.json` pins `markdown-it` to 14.x. Slidev's `mdc` support (`@comark/markdown-it`) declares a peer of `^14`, and pnpm otherwise resolves 15.x (pulled in by `markdownlint-cli2`), which breaks the build with `ERR_PACKAGE_PATH_NOT_EXPORTED`. Remove the pin once upstream supports 15.

## Shell script portability

Scripts that participants run on their own machines (`scripts/preflight.sh`, `scripts/benchmark.sh`, `scripts/gpu-status.sh` when called locally) must work with **macOS bash 3.2**: no `mapfile`/`readarray`, no associative arrays, no `${var,,}`. Scripts under `infra/` run on the Linux GPU pods and may use bash 5. All scripts pass `shellcheck` and start with `set -euo pipefail`.
