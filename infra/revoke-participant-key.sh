#!/usr/bin/env bash
# Revoke a participant's access: remove their keys, lock the account, end their sessions.
#
#   infra/revoke-participant-key.sh --host H --port P --user anna            # revoke + lock
#   infra/revoke-participant-key.sh --host H --port P --user anna --delete   # also archive and remove the account
#   infra/revoke-participant-key.sh --host H --port P --all [--delete]       # everyone (end of workshop)
#
# Verify afterwards with: ssh -i <their key> ... (must fail), or `ws-user list` on the pod.
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

parse_pod_args "$@"
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
user="" all=0 mode="--lock"
while [ $# -gt 0 ]; do
  case "$1" in
    --user) user="$2"; shift 2 ;;
    --all) all=1; shift ;;
    --delete) mode="--delete"; shift ;;
    -h | --help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
require_pod
if [ "$all" -eq 1 ]; then
  info "revoking ALL participants on $POD_HOST:$POD_PORT"
  ssh_pod "ws-user revoke-all $mode"
else
  [ -n "$user" ] || die "--user NAME or --all is required"
  info "revoking $user on $POD_HOST:$POD_PORT"
  ssh_pod "ws-user revoke '$user' $mode"
fi
