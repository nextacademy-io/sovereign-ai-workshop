#!/usr/bin/env bash
# One screen with what the GPU and the server are doing. Run on the GPU host.
#
#   ./scripts/gpu-status.sh           once
#   ./scripts/gpu-status.sh --watch   refresh every 2 seconds (Ctrl-C to stop)
#
# GPU-Util is the share of time any kernel was running. It is NOT how well the GPU is used:
# watch power draw and the server's own numbers (running, waiting, KV cache) next to it.
set -u
watch=0
[ "${1:-}" = "--watch" ] && watch=1
base="${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}"
base="${base%/v1}"

snapshot() {
  echo "== GPU"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,power.draw,temperature.gpu --format=csv,noheader,nounits \
      | awk -F', ' '{printf "%s\n   GPU-Util %s %%   memory %s / %s MiB   power %s W   temp %s C\n", $1, $2, $3, $4, $5, $6}'
    echo "   processes on the GPU:"
    nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null | sed 's/^/     /' || true
  else
    echo "   nvidia-smi not found (not on the GPU host?)"
  fi
  echo "== vLLM server ($base)"
  if m=$(curl -fsS --max-time 3 "$base/metrics" 2>/dev/null); then
    val() { echo "$m" | awk -v name="$1" '$1 ~ "^"name"({|$)" {s += $NF} END {printf "%g", s}'; }
    echo "   running requests: $(val 'vllm:num_requests_running')   waiting: $(val 'vllm:num_requests_waiting')"
    kv=$(val 'vllm:kv_cache_usage_perc')
    echo "   KV cache used: $(awk -v v="$kv" 'BEGIN {printf "%.1f %%", v * 100}')"
    q=$(val 'vllm:prefix_cache_queries_total')
    h=$(val 'vllm:prefix_cache_hits_total')
    echo "   prefix cache hit rate: $(awk -v h="$h" -v q="$q" 'BEGIN {if (q > 0) printf "%.1f %%", 100 * h / q; else print "n/a (no queries yet)"}')"
    echo "   generated tokens so far: $(val 'vllm:generation_tokens_total')   preemptions: $(val 'vllm:num_preemptions_total')"
  else
    echo "   not reachable. Is the server running?  sudo wsctl status"
  fi
}

if [ "$watch" -eq 1 ]; then
  while true; do
    clear
    snapshot
    sleep 2
  done
else
  snapshot
fi
