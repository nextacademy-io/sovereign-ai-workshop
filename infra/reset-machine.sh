#!/usr/bin/env bash
# Put a pod back into a known-good state without recreating it. Trainer-side wrapper around ws-reset.
#
#   infra/reset-machine.sh --host H --port P servers          restart vLLM (current or default profile), embedding, monitoring
#   infra/reset-machine.sh --host H --port P user anna        fresh repository copy for one participant (artifacts kept)
#   infra/reset-machine.sh --host H --port P user anna --hard also discard their artifacts
#   infra/reset-machine.sh --host H --port P participants     fresh copies for everyone
#   infra/reset-machine.sh --host H --port P all
#
# Replaced directories are archived under /var/backups/workshop on the pod, never deleted.
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

parse_pod_args "$@"
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
[ $# -ge 1 ] || { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
require_pod
case "$1" in
  user) [ $# -ge 2 ] || die "usage: user NAME [--hard]" ;;
  servers | participants | all) ;;
  *) die "unknown target '$1'" ;;
esac
args=""
for a in "$@"; do args="$args '$a'"; done
ssh_pod "ws-reset$args"
