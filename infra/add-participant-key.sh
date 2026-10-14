#!/usr/bin/env bash
# Create a participant account on a GPU pod and install their SSH public key.
#
#   infra/add-participant-key.sh --host 203.0.113.7 --port 40022 --user anna --key ~/keys/anna.pub
#   cat anna.pub | infra/add-participant-key.sh --host H --port P --user anna --key -
#
# Only public keys are ever handled. Revoke access with infra/revoke-participant-key.sh.
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

parse_pod_args "$@"
# `${arr[@]+"${arr[@]}"}` keeps `set -u` happy on bash 3.2 when the array is empty.
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
user="" key=""
while [ $# -gt 0 ]; do
  case "$1" in
    --user) user="$2"; shift 2 ;;
    --key) key="$2"; shift 2 ;;
    -h | --help) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$user" ] || die "--user is required"
[ -n "$key" ] || die "--key FILE (or - for stdin) is required"
require_pod

if [ "$key" = "-" ]; then material=$(cat); else material=$(cat "$key"); fi
case "$material" in
  *"PRIVATE KEY"*) die "that looks like a PRIVATE key. Never send private keys anywhere." ;;
esac

info "adding $user on $POD_HOST:$POD_PORT"
printf '%s\n' "$material" | ssh_pod "ws-user add '$user'"
