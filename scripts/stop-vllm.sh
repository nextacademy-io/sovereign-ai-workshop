#!/usr/bin/env bash
# Stop the shared vLLM server of your group. Run on the GPU host.
#   ./scripts/stop-vllm.sh [--yes]
set -euo pipefail
command -v wsctl >/dev/null 2>&1 || { echo "wsctl not found: run this on your group's GPU host" >&2; exit 127; }
if [ "${1:-}" != "--yes" ]; then
  printf 'This stops the model for your whole group. Continue? [y/N] '
  read -r answer
  case "$answer" in y | Y | yes) ;; *) echo "aborted"; exit 1 ;; esac
fi
exec sudo wsctl stop
