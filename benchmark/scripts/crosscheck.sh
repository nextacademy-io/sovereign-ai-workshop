#!/usr/bin/env bash
# Run the same load through infbench and through `vllm bench serve`, then compare the results.
# Runs ON THE POD (vllm is installed there). The API key is taken from OPENAI_API_KEY (set at login).
#
#   ./benchmark/scripts/crosscheck.sh --concurrency 8 --input-tokens 1000 --output-tokens 200 --requests 64
#
# Output goes to benchmark/results/_scratch/crosscheck-<time>/ (infbench/, vllm/, comparison.md).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
concurrency=8 input=1000 output=200 requests=64 model="${WORKSHOP_MODEL:-Qwen/Qwen3-8B}"
base="${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}"
base="${base%/v1}"

while [ $# -gt 0 ]; do
  case "$1" in
    --concurrency) concurrency=$2; shift 2 ;;
    --input-tokens) input=$2; shift 2 ;;
    --output-tokens) output=$2; shift 2 ;;
    --requests) requests=$2; shift 2 ;;
    --model) model=$2; shift 2 ;;
    -h | --help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "${OPENAI_API_KEY:-}" ] || { echo "OPENAI_API_KEY is not set (log in again, or export it)" >&2; exit 2; }
command -v vllm >/dev/null || { echo "vllm not found: run this on a GPU pod" >&2; exit 127; }

out="$here/../results/_scratch/crosscheck-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out/infbench" "$out/vllm"

echo "== infbench: concurrency $concurrency, $input in / $output out, $requests requests"
"$here/../run.sh" --endpoint "$base" --model "$model" --concurrency "$concurrency" \
  --input-tokens "$input" --output-tokens "$output" --requests "$requests" --warmup 4 \
  --out "$out/infbench" --quiet >/dev/null

echo "== vllm bench serve: the same shape"
vllm bench serve --backend openai --base-url "$base" --endpoint /v1/completions --model "$model" \
  --dataset-name random --random-input-len "$input" --random-output-len "$output" \
  --num-prompts "$requests" --max-concurrency "$concurrency" --num-warmups 4 --ignore-eos --seed 1 \
  --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,90,95,99 \
  --save-result --result-dir "$out/vllm" --result-filename vllm.json >"$out/vllm/stdout.txt" 2>&1 || {
  tail -20 "$out/vllm/stdout.txt" >&2
  exit 1
}

f=$(printf 'c%03d.json' "$concurrency")
python3 "$here/compare_results.py" "$out/infbench/$f" "$out/vllm/vllm.json" --markdown-out "$out/comparison.md" || true
echo "results in $out"
