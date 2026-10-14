#!/usr/bin/env bash
# Run experiments on a pod and bring the results home.
#
#   experiments/run-session.sh --host H --port P --label s2 baseline concurrency context-length quantization prefix-cache demos
#
# 1. pushes the current repository to the pod (tools and profiles only; servers keep running)
# 2. starts experiments/runner.py on the pod, detached, so a dropped SSH connection does not kill it
# 3. follows its log until it finishes
# 4. copies the results to benchmark/results/<date>-rtxpro6000-<label>/ (JSON + summaries + logs)
#
# Results are evidence: they carry hardware, model revision, engine version, server arguments and date
# (infbench writes these). Write experiments/<name>/RESULTS.md from them; never from memory.
set -euo pipefail
# shellcheck source=../infra/lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/../infra/lib/common.sh"

parse_pod_args "$@"
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
label="session"
names=()
while [ $# -gt 0 ]; do
  case "$1" in
    --label) label="$2"; shift 2 ;;
    -h | --help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) names+=("$1"); shift ;;
  esac
done
[ ${#names[@]} -gt 0 ] || die "name at least one experiment (python3 experiments/runner.py list)"
require_pod

remote_out="/var/lib/workshop/results/$label"
local_out="$REPO_DIR/benchmark/results/$(date -u +%Y-%m-%d)-rtxpro6000-$label"

info "pushing the repository"
"$INFRA_DIR/deploy-to-pod.sh" --host "$POD_HOST" --port "$POD_PORT" --group "${GROUP_LABEL:-experiments}" \
  --no-participants --skip-models --skip-servers --skip-monitoring >/dev/null

info "starting the runner on the pod: ${names[*]}"
ssh_pod "rm -rf '$remote_out'; mkdir -p '$remote_out'; \
  export OPENAI_API_KEY=\$(cat /var/lib/workshop/api-key) PYTHONUNBUFFERED=1 WORKSHOP_MODEL=${WORKSHOP_MODEL:-Qwen/Qwen3-8B}; \
  nohup python3 /opt/workshop/repo/experiments/runner.py run ${names[*]} --out '$remote_out' > '$remote_out/runner.log' 2>&1 < /dev/null & \
  echo started pid \$!"

info "following the log (Ctrl-C detaches; the runner keeps going)"
seen=0
while true; do
  lines=$(ssh_pod "wc -l < '$remote_out/runner.log'" 2>/dev/null || echo "$seen")
  if [ "$lines" -gt "$seen" ]; then
    ssh_pod "sed -n '$((seen + 1)),${lines}p' '$remote_out/runner.log'" 2>/dev/null || true
    seen=$lines
  fi
  if ! ssh_pod "pgrep -f '[e]xperiments/runner.py run' >/dev/null" 2>/dev/null; then break; fi
  sleep 20
done

info "copying results to $local_out"
mkdir -p "$local_out"
ssh_pod "tar -czf - -C '$remote_out' . 2>/dev/null" | tar -xzf - -C "$local_out"
ssh_pod "cp /var/lib/workshop/server.json /tmp/s.json 2>/dev/null; cat /var/lib/workshop/env.json" >"$local_out/pod-env.json" 2>/dev/null || true
# Files the runner wrote itself (formula checks, start-up times, counters) get the provenance of a result
# from the same session, so every JSON under benchmark/results/ is attributable (pnpm check enforces it).
python3 "$REPO_DIR/benchmark/scripts/promote_reference.py" --normalize "$local_out" || echo "warning: could not add provenance to auxiliary files" >&2
info "done: $(find "$local_out" -name '*.json' | wc -l | tr -d ' ') JSON files in $local_out"
[ -f "$local_out/session-summary.json" ] && cat "$local_out/session-summary.json" | head -30
