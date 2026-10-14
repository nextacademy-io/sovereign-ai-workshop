#!/usr/bin/env bash
# ws-reset: put things back into a known state. Runs as root ON THE POD (trainer, via infra/reset-machine.sh).
#
#   ws-reset servers            restart the shared vLLM server with its current profile (or the default) and
#                               make sure the embedding server and monitoring run
#   ws-reset user <name> [--hard]
#                               fresh repository copy for one participant (their artifacts are kept unless --hard)
#   ws-reset participants       fresh repository copy for everyone
#   ws-reset all                servers, then participants
#
# Nothing here deletes data: replaced directories are archived under /workspace/backups first.
set -euo pipefail

DEFAULT_PROFILE=${WS_DEFAULT_PROFILE:-baseline}
die() { echo "ws-reset: $*" >&2; exit 1; }
[[ $EUID -eq 0 ]] || die "run as root"

reset_servers() {
  if [[ -f /workspace/state/active-profile ]]; then
    wsctl restart
  else
    wsctl start "$DEFAULT_PROFILE"
  fi
  wsctl embed status >/dev/null 2>&1 || true
  if ! wsctl status | grep -q '^embed .*running'; then wsctl embed start; fi
  wsmon status | grep -q stopped && wsmon start || true
  wsctl status
}

reset_participants() {
  local user
  while IFS=$'\t' read -r user _; do
    [[ -n $user ]] || continue
    if id "$user" >/dev/null 2>&1; then ws-user reset-home "$user"; fi
  done </workspace/state/users.tsv
}

case "${1:-}" in
  servers) reset_servers ;;
  user) [[ -n ${2:-} ]] || die "usage: ws-reset user <name> [--hard]"; ws-user reset-home "$2" "${3:-}" ;;
  participants) reset_participants ;;
  all) reset_servers; reset_participants ;;
  *) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
