#!/usr/bin/env bash
# Create or update every participant listed in infra/participants.yaml on their group's pod.
#
#   infra/sync-participants.sh [--group alpha] [--file infra/participants.yaml]
#
# Idempotent: existing users get their key replaced, missing users are created.
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

file="$INFRA_DIR/participants.yaml" group=""
while [ $# -gt 0 ]; do
  case "$1" in
    --file) file="$2"; shift 2 ;;
    --group) group="$2"; shift 2 ;;
    -h | --help) sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -f "$file" ] || die "$file not found (copy infra/participants.example.yaml)"

parser=(python3 "$INFRA_DIR/lib/participants.py" "$file")
if ! python3 -c 'import yaml' 2>/dev/null; then
  command -v uv >/dev/null 2>&1 || die "need python3 with pyyaml, or uv"
  parser=(uv run --quiet --with pyyaml python "$INFRA_DIR/lib/participants.py" "$file")
fi
if [ -n "$group" ]; then parser+=(--group "$group"); fi

count=0
while IFS=$'\t' read -r g host port user key; do
  [ -n "$user" ] || continue
  info "[$g] $user -> $host:$port"
  printf '%s\n' "$key" | "$INFRA_DIR/add-participant-key.sh" --host "$host" --port "$port" --user "$user" --key -
  count=$((count + 1))
done < <("${parser[@]}")
info "done: $count participant(s) synced"
