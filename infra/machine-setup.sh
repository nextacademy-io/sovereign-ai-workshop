#!/usr/bin/env bash
# Bring a fresh GPU pod to workshop-ready state. Run ON THE POD as root, normally through
# infra/deploy-to-pod.sh, which first copies this repository to /opt/workshop/repo.
#
#   bash /opt/workshop/repo/infra/machine-setup.sh --group alpha
#   bash /opt/workshop/repo/infra/machine-setup.sh --group alpha --skip-servers     # no GPU work yet
#
# Safe to run repeatedly: every step checks before it changes anything. After a pod RESTART the
# container disk is empty again; deploy-to-pod.sh rebuilds everything, and the model files come back
# from the download cache on /workspace instead of the internet.
#
# Storage layout (see infra/pod/paths.sh): the persistent volume /workspace does not enforce file
# permissions on Runpod, so it only holds a download cache. Code, served models, accounts, keys,
# compile caches, logs and participants' homes live on the container disk.
#
# Options:
#   --group NAME        group label shown in the login banner (alpha, beta, ...)
#   --models SET        which models to download: workshop (default), demo, all, or a role list
#   --default-profile P vLLM profile started at the end (default: baseline)
#   --skip-models       do not download models
#   --skip-monitoring   do not install/start Prometheus, Grafana and the GPU exporter
#   --skip-servers      do not start vLLM
#   --no-persist        do not copy downloaded models to the /workspace cache
#   --no-gpu            allow a machine without a GPU (used by tests in plain containers)
set -euo pipefail

GROUP_NAME=workshop
MODELS=workshop
DEFAULT_PROFILE=baseline
SKIP_MODELS=0 SKIP_MON=0 SKIP_SERVERS=0 NO_GPU=0 PERSIST=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --group) GROUP_NAME=$2; shift 2 ;;
    --models) MODELS=$2; shift 2 ;;
    --default-profile) DEFAULT_PROFILE=$2; shift 2 ;;
    --skip-models) SKIP_MODELS=1; shift ;;
    --skip-monitoring) SKIP_MON=1; shift ;;
    --skip-servers) SKIP_SERVERS=1; shift ;;
    --no-persist) PERSIST=0; shift ;;
    --no-gpu) NO_GPU=1; SKIP_MODELS=1; SKIP_MON=1; SKIP_SERVERS=1; shift ;;
    -h | --help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

T0=$(date +%s)
step() { printf '\n==> [%3ds] %s\n' "$(($(date +%s) - T0))" "$*"; }
die() { echo "machine-setup: $*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "run as root"
# SSH sessions do not inherit the container's environment (PATH to vllm and python, CUDA variables);
# infra/runpod/pod-start.sh recorded it, minus secrets.
# shellcheck source=/dev/null
[[ -f /etc/workshop-container-env ]] && source /etc/workshop-container-env

REPO_SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
# shellcheck source=pod/paths.sh
source "$REPO_SRC/infra/pod/paths.sh"
[[ $REPO_SRC == "$WS_REPO" ]] || die "the repository must be at $WS_REPO (found at $REPO_SRC); use infra/deploy-to-pod.sh"
[[ -f $WS_REPO/infra/versions.env ]] || die "$WS_REPO/infra/versions.env not found"
# shellcheck source=versions.env
source "$WS_REPO/infra/versions.env"

# --------------------------------------------------------------------------------------------
step "Preconditions"
mkdir -p "$WS_OPT" "$WS_STATE" "$WS_LOGS" "$WS_CACHE" "$WS_BACKUPS" "$WS_HF" "$WS_LIB"
chmod 755 "$WS_OPT" "$WS_REPO" "$WS_STATE" "$WS_LOGS" "$WS_HF"
free_gb=$(df -BG --output=avail "$WS_OPT" | tail -1 | tr -dc '0-9')
# Models that are already on the disk count: a rerun on a populated pod must not fail for lack of space.
have_gb=$(du -s --block-size=1G "$WS_HF" 2>/dev/null | cut -f1 || true)
have_gb=${have_gb:-0}
echo "free space on the container disk ($WS_OPT): ${free_gb} GB (plus ${have_gb} GB of models already there)"
if [[ -d $WS_PERSIST ]]; then
  echo "persistent volume $WS_PERSIST present ($(df -h --output=avail "$WS_PERSIST" | tail -1 | tr -d ' ') free); used as a download cache only"
else
  echo "no persistent volume at $WS_PERSIST: models will be downloaded on every rebuild"
  PERSIST=0
fi
if [[ $NO_GPU -eq 0 ]]; then
  command -v nvidia-smi >/dev/null || die "nvidia-smi not found: is this a GPU pod?"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
  [[ $SKIP_MODELS -eq 1 || $((free_gb + have_gb)) -ge 40 ]] || die "less than 40 GB free on the container disk (${free_gb} GB free, ${have_gb} GB of models already present); the workshop models need about 31 GB. Recreate the pod with a larger disk."
fi
command -v python3 >/dev/null || die "python3 not found"

# --------------------------------------------------------------------------------------------
step "System packages"
need=()
for pkg in openssh-server rsync tmux htop jq less sudo curl bsdutils bc; do
  dpkg -s "$pkg" >/dev/null 2>&1 || need+=("$pkg")
done
if [[ ${#need[@]} -gt 0 ]]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq "${need[@]}" >/dev/null
  echo "installed: ${need[*]}"
else
  echo "all present"
fi

# --------------------------------------------------------------------------------------------
step "Environment facts (PATH, vllm binary, CUDA runtime)"
# sudo resets PATH; record the one that finds python3 and vllm so wsctl/wsmon can restore it.
printf '%s' "$PATH" >/etc/workshop-path
VLLM_BIN=$(command -v vllm || true)
python3 - "$WS_STATE/env.json" "$VLLM_BIN" <<'PY'
import json, platform, re, subprocess, sys
out, vllm_bin = sys.argv[1], sys.argv[2]
info = {"python": platform.python_version(), "vllm_bin": vllm_bin}
try:
    import torch
    info["torch"] = torch.__version__
    info["torch_cuda"] = torch.version.cuda
except Exception as exc:  # no torch on a CPU test machine
    info["torch_error"] = str(exc)
try:
    smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=15).stdout
    m = re.search(r"CUDA Version:\s*(\d+\.\d+)", smi)
    info["driver_cuda"] = m.group(1) if m else None
except Exception:
    info["driver_cuda"] = None
json.dump(info, open(out, "w"), indent=2)
print(json.dumps(info))
PY
chmod 644 "$WS_STATE/env.json"

# --------------------------------------------------------------------------------------------
step "Install tools (wsctl, wsmon, ws-user, helpers)"
install -m 644 "$WS_REPO/infra/pod/paths.sh" "$WS_LIB/paths.sh"
install -m 755 "$WS_REPO/infra/pod/wsctl" /usr/local/bin/wsctl
install -m 755 "$WS_REPO/infra/pod/wsmon" /usr/local/bin/wsmon
install -m 755 "$WS_REPO/infra/pod/ws-user.sh" /usr/local/bin/ws-user
install -m 755 "$WS_REPO/infra/pod/ws-reset.sh" /usr/local/bin/ws-reset
install -m 755 "$WS_REPO/infra/pod/render-profile.py" "$WS_LIB/render-profile.py"
install -m 755 "$WS_REPO/infra/pod/server-info.py" "$WS_LIB/server-info.py"
install -m 755 "$WS_REPO/infra/pod/fetch-models.py" "$WS_LIB/fetch-models.py"
# Participants must not be able to change anything root runs or loads.
chown -R root:root "$WS_REPO" "$WS_LIB"
chmod -R go-w "$WS_REPO" "$WS_LIB"

# --------------------------------------------------------------------------------------------
step "SSH daemon configuration"
install -d -m 755 /etc/ssh/sshd_config.d /run/sshd
cat >/etc/ssh/sshd_config.d/10-workshop.conf <<'EOF'
# KI ohne Cloud workshop pod. Key-only access; participants may forward ports (ssh -L).
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes
AllowGroups root workshop
AllowTcpForwarding local
GatewayPorts no
X11Forwarding no
MaxAuthTries 3
LoginGraceTime 20
ClientAliveInterval 30
ClientAliveCountMax 6
EOF
grep -q '^Include /etc/ssh/sshd_config.d/' /etc/ssh/sshd_config || sed -i '1i Include /etc/ssh/sshd_config.d/*.conf' /etc/ssh/sshd_config
sshd -t && echo "sshd config valid"
# Reload only if a daemon is running (the pod start command launched one).
if [[ -f /run/sshd.pid ]] && kill -0 "$(</run/sshd.pid)" 2>/dev/null; then kill -HUP "$(</run/sshd.pid)" && echo "sshd reloaded"; fi

# --------------------------------------------------------------------------------------------
step "Shared API key and group access"
getent group workshop >/dev/null || groupadd -g 2000 workshop
if [[ ! -s $WS_STATE/api-key ]]; then
  python3 -c 'import secrets; print("wk-" + secrets.token_urlsafe(24))' >"$WS_STATE/api-key"
  echo "generated a new API key"
fi
chown root:workshop "$WS_STATE/api-key" && chmod 640 "$WS_STATE/api-key"
echo "$GROUP_NAME" >"$WS_STATE/group"
chmod 644 "$WS_STATE/group"

cat >/etc/sudoers.d/workshop <<'EOF'
# Participants may control the shared servers, and nothing else.
%workshop ALL=(root) NOPASSWD: /usr/local/bin/wsctl, /usr/local/bin/wsctl *
EOF
chmod 440 /etc/sudoers.d/workshop
visudo -cf /etc/sudoers.d/workshop >/dev/null && echo "sudoers valid"

cat >/etc/profile.d/workshop.sh <<'EOF'
# Environment for workshop participants (login shells over SSH).
[ -r /etc/workshop-container-env ] && . /etc/workshop-container-env
if [ -r /var/lib/workshop/api-key ]; then
  export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
  OPENAI_API_KEY=$(cat /var/lib/workshop/api-key)
  export OPENAI_API_KEY VLLM_API_KEY="$OPENAI_API_KEY"
  export EMBEDDING_BASE_URL=http://127.0.0.1:8001/v1
  export EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
  export WORKSHOP_MODEL=Qwen/Qwen3-8B
  export HF_HOME=/opt/workshop/hf HF_HUB_OFFLINE=1
  export PATH="$PATH:/usr/local/bin"
  [ -d "$HOME/ki-ohne-cloud" ] && export PYTHONPATH="$HOME/ki-ohne-cloud/benchmark${PYTHONPATH:+:$PYTHONPATH}"
  if [ -n "$PS1" ] && [ -z "$WORKSHOP_BANNER_SHOWN" ]; then
    export WORKSHOP_BANNER_SHOWN=1
    echo "KI ohne Cloud · group $(cat /var/lib/workshop/group 2>/dev/null) · $(hostname)"
    echo "  API:       $OPENAI_BASE_URL  (key and model are already in your environment)"
    echo "  server:    sudo wsctl status | sudo wsctl profiles | sudo wsctl start <profile>"
    echo "  your repo: ~/ki-ohne-cloud   (reset a lab: ./scripts/reset.sh lab-02)"
  fi
fi
EOF
chmod 644 /etc/profile.d/workshop.sh

# --------------------------------------------------------------------------------------------
step "Participant accounts (restored from the registry if this container already had them)"
ws-user restore
ws-user list

# --------------------------------------------------------------------------------------------
if [[ $SKIP_MODELS -eq 0 ]]; then
  step "Models ($MODELS): seed from the download cache, fetch what is missing, save back"
  if [[ $PERSIST -eq 1 && -d $WS_PERSIST_HF ]]; then
    # -rlt: the FUSE volume cannot store owners or modes, so do not try to preserve them.
    rsync -rlt "$WS_PERSIST_HF/" "$WS_HF/" && echo "seeded from $WS_PERSIST_HF ($(du -sh "$WS_HF" | cut -f1))"
  fi
  HF_HOME=$WS_HF HF_XET_HIGH_PERFORMANCE=1 python3 "$WS_LIB/fetch-models.py" --models "$MODELS" --config "$WS_REPO/config/models.yaml"
  chown -R root:root "$WS_HF" && chmod -R a+rX,go-w "$WS_HF"
  du -sh "$WS_HF"
else
  step "Skipping model download"
fi

# --------------------------------------------------------------------------------------------
if [[ $SKIP_MON -eq 0 ]]; then
  step "Monitoring (Prometheus, Grafana, GPU exporter)"
  wsmon install
  wsmon start
else
  step "Skipping monitoring"
fi

# --------------------------------------------------------------------------------------------
if [[ $SKIP_SERVERS -eq 0 ]]; then
  step "Start the shared vLLM server (profile: $DEFAULT_PROFILE) and the embedding server"
  wsctl start "$DEFAULT_PROFILE"
  wsctl embed start
else
  step "Skipping server start"
fi

if [[ $SKIP_MODELS -eq 0 && $PERSIST -eq 1 ]]; then
  # Saving 30 GB to the network volume takes minutes; do it in the background so the servers are
  # usable meanwhile. Only a later pod restart needs it.
  step "Saving the models to the download cache in the background (log: $WS_LOGS/persist.log)"
  mkdir -p "$WS_PERSIST_HF"
  nohup rsync -rlt "$WS_HF/" "$WS_PERSIST_HF/" >"$WS_LOGS/persist.log" 2>&1 &
fi

step "Done"
echo "Time to ready: $(($(date +%s) - T0)) s"
[[ $SKIP_SERVERS -eq 0 ]] && wsctl status || true
echo "Next: infra/sync-participants.sh --group $GROUP_NAME, then infra/verify-machine.sh"
