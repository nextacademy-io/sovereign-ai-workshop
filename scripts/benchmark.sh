#!/usr/bin/env bash
# Benchmark your group's server. Wraps benchmark/run.sh with the workshop defaults and a results folder
# of your own. Any argument you pass is handed to the harness (see benchmark/README.md).
#
#   ./scripts/benchmark.sh --concurrency 1,4,8,16
#   ./scripts/benchmark.sh --workload rag-long-context --concurrency 4 --label long-context
#
# Defaults: the endpoint and key from your environment (set at login), the workshop-baseline workload
# (1200 input, 180 output tokens). Results: benchmark/results/mine/<time>-<label>/ (JSON + summary.md).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
has() { for a in "$@"; do [ "$a" = "$FLAG" ] && return 0; done; return 1; }
FLAG=--workload; has "$@" || set -- --workload workshop-baseline "$@"
FLAG=--out
if ! has "$@"; then
  label=run
  prev=""
  for a in "$@"; do
    [ "$prev" = "--label" ] && label="$a"
    prev="$a"
  done
  set -- --out "$here/benchmark/results/mine/$(date -u +%Y%m%dT%H%M%SZ)-$label" "$@"
fi
exec "$here/benchmark/run.sh" "$@"
