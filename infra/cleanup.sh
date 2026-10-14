#!/usr/bin/env bash
# End-of-workshop (or end-of-day) cleanup for one pod or for every group in participants.yaml.
#
#   infra/cleanup.sh --host H --port P --collect           copy participants' artifacts and benchmark results to this laptop
#   infra/cleanup.sh --host H --port P --revoke            remove every participant's access (accounts are archived on the pod)
#   infra/cleanup.sh --host H --port P --stop-servers      stop vLLM, the embedding server and monitoring (the GPU idles but is still billed)
#   infra/cleanup.sh --all --collect --revoke              the same for every group listed in infra/participants.yaml
#
# This script never terminates a pod. Billing only stops when the pod is deleted: after the last
# step it prints the exact checks to run (Runpod MCP `delete-pod`, then `list-pods` and `list-billing`).
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

parse_pod_args "$@"
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
collect=0 revoke=0 stop=0 all=0 file="$INFRA_DIR/participants.yaml"
while [ $# -gt 0 ]; do
  case "$1" in
    --collect) collect=1; shift ;;
    --revoke) revoke=1; shift ;;
    --stop-servers) stop=1; shift ;;
    --all) all=1; shift ;;
    --file) file="$2"; shift 2 ;;
    -h | --help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ $((collect + revoke + stop)) -gt 0 ] || die "nothing to do: pass --collect, --revoke and/or --stop-servers"

cleanup_pod() { # label host port
  local label=$1
  POD_HOST=$2
  POD_PORT=$3
  info "[$label] $POD_HOST:$POD_PORT"
  if [ "$collect" -eq 1 ]; then
    local dest
    dest="$STATE_DIR/collected/$label-$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "$dest"
    # Participants' artifacts and benchmark results, the access and control logs, and the server provenance.
    ssh_pod "cd /workspace && tar -czf - home/*/ki-ohne-cloud/workshop-artifacts home/*/ki-ohne-cloud/benchmark/results logs/access.log logs/wsctl.log state/server.json 2>/dev/null" >"$dest/collected.tar.gz" || true
    info "[$label] collected to $dest ($(wc -c <"$dest/collected.tar.gz" | tr -d ' ') bytes)"
  fi
  if [ "$stop" -eq 1 ]; then
    ssh_pod "wsctl stop; wsctl embed stop; wsmon stop" || true
  fi
  if [ "$revoke" -eq 1 ]; then
    ssh_pod "ws-user revoke-all --delete"
  fi
}

if [ "$all" -eq 1 ]; then
  [ -f "$file" ] || die "$file not found"
  parser=(python3 "$INFRA_DIR/lib/participants.py" "$file" --groups)
  if ! python3 -c 'import yaml' 2>/dev/null; then parser=(uv run --quiet --with pyyaml python "$INFRA_DIR/lib/participants.py" "$file" --groups); fi
  while IFS=$'\t' read -r g host port; do
    [ -n "$g" ] && cleanup_pod "$g" "$host" "$port"
  done < <("${parser[@]}")
else
  require_pod
  cleanup_pod "pod" "$POD_HOST" "$POD_PORT"
fi

cat >&2 <<'MSG'

Cleanup done. Billing is NOT stopped yet. Remaining checklist:
  [ ] Delete every pod (Runpod MCP `delete-pod` or the console)
  [ ] Run `list-pods`: it must return no pods
  [ ] Run `list-network-volumes`: delete volumes you no longer need (they bill while idle)
  [ ] Run `list-billing` for the last day and confirm the hourly spend is zero
  [ ] Remove any API keys or tokens created for the workshop; keep infra/participants.yaml out of git
MSG
