#!/usr/bin/env bash
# Take a freshly created pod from "SSH works" to "workshop ready" in one command.
#
#   infra/deploy-to-pod.sh --host 203.0.113.10 --port 40022 --group alpha
#   infra/deploy-to-pod.sh --host H --port P --group alpha --models workshop --no-participants
#
# 1. copies this repository to /opt/workshop/repo on the pod: what git tracks plus untracked files that
#    .gitignore does not exclude (so nothing ignored, such as .env or input/, leaves your laptop)
# 2. runs infra/machine-setup.sh there: tools, SSH policy, models, monitoring, vLLM servers
# 3. creates the participant accounts of this group from infra/participants.yaml
# 4. runs infra/verify-machine.sh
#
# Re-running is safe and is also how a pod is rebuilt after it was restarted.
set -euo pipefail
# shellcheck source=lib/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

parse_pod_args "$@"
set -- ${REST_ARGS[@]+"${REST_ARGS[@]}"}
group="workshop" models="workshop" setup_args=() sync=1
while [ $# -gt 0 ]; do
  case "$1" in
    --group) group="$2"; shift 2 ;;
    --models) models="$2"; shift 2 ;;
    --no-participants) sync=0; shift ;;
    --skip-servers | --skip-models | --skip-monitoring) setup_args+=("$1"); shift ;;
    -h | --help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done
require_pod

info "checking SSH access to $POD_HOST:$POD_PORT"
# shellcheck disable=SC2016  # the command substitutions must run on the pod
ssh_pod 'echo connected as $(whoami) on $(hostname)' || die "cannot log in as root; is your key registered with Runpod and the pod's sshd running?"

info "copying the repository to /opt/workshop/repo"
push_repo /opt/workshop/repo

info "running machine-setup.sh (this downloads models and starts vLLM; the first run takes several minutes)"
ssh_pod "bash /opt/workshop/repo/infra/machine-setup.sh --group '$group' --models '$models' ${setup_args[*]+${setup_args[*]}}"

if [ "$sync" -eq 1 ] && [ -f "$INFRA_DIR/participants.yaml" ]; then
  info "creating participant accounts for group $group"
  "$INFRA_DIR/sync-participants.sh" --group "$group"
elif [ "$sync" -eq 1 ]; then
  info "no infra/participants.yaml: skipping participant accounts"
fi

info "verifying"
"$INFRA_DIR/verify-machine.sh" --host "$POD_HOST" --port "$POD_PORT"
