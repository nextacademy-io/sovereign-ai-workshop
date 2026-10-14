#!/bin/bash
# Start command of a workshop pod (the pod's PID 1). The upstream vLLM image has no SSH daemon and
# its entrypoint is `vllm serve`, so the pod overrides the entrypoint to `/bin/bash -c "<this script>"`.
# It does only what must happen before anyone can log in; everything else is done over SSH by
# infra/machine-setup.sh, so that a rebuilt pod and a restarted pod take the same path.
#
#   1. install sshd (the image has none) and a few tools
#   2. keep the SSH host keys on the persistent volume, so a restart does not change the host key
#   3. install the registered public key(s) for root (from the PUBLIC_KEY variable Runpod injects)
#   4. record the container's environment (PATH to vllm and python, CUDA variables) for SSH sessions,
#      which do not inherit it; secrets are excluded
#   5. run sshd in the foreground
set -eu
export DEBIAN_FRONTEND=noninteractive

WS=${WORKSPACE_DIR:-/workspace}
mkdir -p /run/sshd "$WS/state/ssh-host-keys" /root/.ssh

if ! command -v sshd >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq openssh-server rsync tmux htop jq less sudo curl >/dev/null
fi

if ls "$WS"/state/ssh-host-keys/ssh_host_* >/dev/null 2>&1; then
  cp -p "$WS"/state/ssh-host-keys/ssh_host_* /etc/ssh/
else
  ssh-keygen -A
  cp -p /etc/ssh/ssh_host_* "$WS/state/ssh-host-keys/"
fi

printf '%s\n' "${PUBLIC_KEY:-}" >/root/.ssh/authorized_keys
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys

: >/etc/workshop-container-env
while IFS='=' read -r name value; do
  case $name in
    *KEY* | *TOKEN* | *SECRET* | *PASSWORD*) continue ;;
  esac
  printf 'export %s=%q\n' "$name" "$value" >>/etc/workshop-container-env
done < <(env | grep -E '^(PATH|LD_LIBRARY_PATH|LIBRARY_PATH|CUDA_|NVIDIA_|PYTHON|UV_|VLLM_|RUNPOD_(POD_ID|PUBLIC_IP|TCP_PORT_|DC_ID|GPU_|POD_HOSTNAME))' || true)
chmod 644 /etc/workshop-container-env

exec /usr/sbin/sshd -D -e
