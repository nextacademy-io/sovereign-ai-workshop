#!/usr/bin/env bash
# (Re)start the shared vLLM server of your group with a profile. Run on the GPU host.
#
#   ./scripts/start-vllm.sh                 list the profiles
#   ./scripts/start-vllm.sh fp8
#   ./scripts/start-vllm.sh baseline --set max-num-seqs=8
#
# This restarts the server for EVERYONE in your group and takes a minute or two (the model is
# offline meanwhile). Tell your group first.
set -euo pipefail
command -v wsctl >/dev/null 2>&1 || { echo "wsctl not found: run this on your group's GPU host, not on your laptop" >&2; exit 127; }
if [ $# -eq 0 ]; then
  sudo wsctl profiles
  exit 0
fi
exec sudo wsctl start "$@"
