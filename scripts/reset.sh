#!/usr/bin/env bash
# Get back to a known-good starting point for a lab, in about a minute, without losing your own work.
#
#   ./scripts/reset.sh lab-02             starter files you do not have yet + reference data
#   ./scripts/reset.sh lab-02 --hard      also replace files you changed (your versions are saved first)
#   ./scripts/reset.sh lab-02 --server    also make sure the shared server runs the profile the lab expects
#   ./scripts/reset.sh --list             the labs
#
# Nothing is deleted. Replaced files are copied to ~/.workshop-backups/<time>/ first.
# --server restarts the shared model for your whole group if (and only if) it runs another profile.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

lab="" hard=() server=0
while [ $# -gt 0 ]; do
  case "$1" in
    --hard) hard=(--hard); shift ;;
    --server) server=1; shift ;;
    --list) lab="--list"; shift ;;
    -h | --help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) lab="$1"; shift ;;
  esac
done
[ -n "$lab" ] || { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

# On a workshop machine the trusted, root-owned copy of the repository is the source of states and reference
# data, so a participant who edited their own copy cannot corrupt a reset. Elsewhere the repository itself is used.
master="${WORKSHOP_MASTER:-/opt/workshop/repo}"
[ -d "$master/workshop-states" ] || master="$here"

run_py() {
  if python3 -c 'import yaml' 2>/dev/null; then
    python3 "$here/scripts/lib/reset_state.py" --root "$master" --dest "$here" "$@"
  elif command -v uv >/dev/null 2>&1; then
    uv run --quiet --with pyyaml python "$here/scripts/lib/reset_state.py" --root "$master" --dest "$here" "$@"
  else
    echo "need python3 with PyYAML, or uv" >&2
    exit 127
  fi
}

if [ "$lab" = "--list" ]; then run_py --list; exit 0; fi
run_py "$lab" ${hard[@]+"${hard[@]}"}

if [ "$server" -eq 1 ]; then
  command -v wsctl >/dev/null 2>&1 || { echo "--server only works on your group's GPU host" >&2; exit 1; }
  want=$(run_py "$lab" --print-profile)
  have=$(cat /var/lib/workshop/active-profile 2>/dev/null || true)
  if [ -z "$want" ]; then
    echo "this lab does not need a particular server profile"
  elif [ "$want" = "$have" ]; then
    echo "the shared server already runs '$want'"
  else
    echo "the shared server runs '${have:-nothing}', the lab expects '$want'. Restarting it for your group..."
    sudo wsctl start "$want"
  fi
fi
