#!/usr/bin/env bash
# Benchmark an OpenAI-compatible endpoint. See benchmark/README.md.
#   ./benchmark/run.sh --endpoint http://localhost:8000 --model Qwen/Qwen3-8B \
#       --concurrency 8 --input-tokens 1000 --output-tokens 200
#
# On a GPU pod the vLLM image already has httpx and pyyaml, so plain python3 works.
# On a laptop, `uv` provides an isolated environment on the fly.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${here}${PYTHONPATH:+:${PYTHONPATH}}"

if python3 -c 'import httpx, yaml' >/dev/null 2>&1; then
  exec python3 -m infbench "$@"
elif command -v uv >/dev/null 2>&1; then
  exec uv run --quiet --with httpx --with pyyaml python -m infbench "$@"
else
  echo "need python3 with httpx and pyyaml, or uv (https://docs.astral.sh/uv/)" >&2
  exit 127
fi
