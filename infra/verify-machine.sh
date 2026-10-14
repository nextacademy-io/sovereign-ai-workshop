#!/usr/bin/env bash
# Verify that a GPU pod is ready for participants. Prints PASS / WARN / FAIL per check, exits non-zero on FAIL.
#
#   infra/verify-machine.sh --host H --port P            from the trainer laptop (runs the checks on the pod over SSH)
#   infra/verify-machine.sh --local                      on the pod itself, as root
#   infra/verify-machine.sh --host H --port P --no-gpu   structural checks only (accounts, SSH, permissions)
#
# Options: --expect-gpu SUBSTRING (default "RTX PRO 6000"), --gpus N (default 1), --quiet
#
# Never prints the API key. Safe to run during the workshop: it sends a handful of 8-token requests.
set -uo pipefail

MODE=remote
EXPECT_GPU="RTX PRO 6000"
EXPECT_GPUS=1
NO_GPU=0
QUIET=0
ARGS=("$@")
HOST_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local) MODE=local; shift ;;
    --host | --port | --identity) HOST_ARGS+=("$1" "$2"); shift 2 ;;
    --expect-gpu) EXPECT_GPU=$2; shift 2 ;;
    --gpus) EXPECT_GPUS=$2; shift 2 ;;
    --no-gpu) NO_GPU=1; shift ;;
    --quiet) QUIET=1; shift ;;
    -h | --help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ $MODE == remote ]]; then
  # Re-run this very script on the pod, feeding it over stdin.
  # shellcheck source=lib/common.sh
  source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
  parse_pod_args ${HOST_ARGS[@]+"${HOST_ARGS[@]}"}
  require_pod
  fwd=(--local --expect-gpu "$EXPECT_GPU" --gpus "$EXPECT_GPUS")
  [[ $NO_GPU -eq 1 ]] && fwd+=(--no-gpu)
  [[ $QUIET -eq 1 ]] && fwd+=(--quiet)
  # shellcheck disable=SC2029
  exec ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$STATE_DIR/known_hosts" \
    -p "$POD_PORT" ${POD_IDENTITY:+-i "$POD_IDENTITY"} "$POD_USER@$POD_HOST" "bash -s -- ${fwd[*]}" <"${BASH_SOURCE[0]}"
fi
: "${ARGS[*]}"

# ------------------------------------------------------------------ on the pod from here
PASS=0 WARN=0 FAIL=0
pass() { PASS=$((PASS + 1)); [[ $QUIET -eq 1 ]] || printf '  PASS  %s\n' "$*"; }
warn() { WARN=$((WARN + 1)); printf '  WARN  %s\n' "$*"; }
fail() { FAIL=$((FAIL + 1)); printf '  FAIL  %s\n' "$*"; }
section() { printf '\n%s\n' "$*"; }
check() { # description command...
  local desc=$1
  shift
  if "$@" >/dev/null 2>&1; then pass "$desc"; else fail "$desc"; fi
}

WS=/workspace
STATE=$WS/state
[[ -f /etc/workshop-path ]] && PATH=$(</etc/workshop-path) && export PATH
KEY=""
[[ -r $STATE/api-key ]] && KEY=$(<"$STATE/api-key")
api() { curl -fsS --max-time 20 -H "Authorization: Bearer $KEY" "$@"; }

section "Host"
check "running as root" test "$EUID" -eq 0
free_gb=$(df -BG --output=avail "$WS" 2>/dev/null | tail -1 | tr -dc '0-9')
if [[ ${free_gb:-0} -ge 40 ]]; then pass "$WS has ${free_gb} GB free"; else fail "$WS has only ${free_gb:-?} GB free (need 40+)"; fi

if [[ $NO_GPU -eq 0 ]]; then
  section "GPU"
  if command -v nvidia-smi >/dev/null; then
    names=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)
    count=$(echo "$names" | grep -c . || true)
    if [[ $count -ge $EXPECT_GPUS ]]; then pass "$count GPU(s) visible"; else fail "expected $EXPECT_GPUS GPU(s), found $count"; fi
    if echo "$names" | grep -qi "$EXPECT_GPU"; then pass "GPU model matches '$EXPECT_GPU': $(echo "$names" | sort -u | head -1)"; else warn "GPU model is '$(echo "$names" | sort -u | head -1)', expected '$EXPECT_GPU' (measured numbers will not be comparable)"; fi
    driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
    if [[ ${driver%%.*} -ge 580 ]]; then pass "driver $driver supports CUDA 13 images (R580+)"; else fail "driver $driver is older than R580, which the CUDA 13 vLLM image needs"; fi
    echo "        $(nvidia-smi --query-gpu=memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader | head -1)"
  else
    fail "nvidia-smi not found"
  fi
fi

section "SSH and accounts"
check "sshd configuration valid" sshd -t
check "key-only login enforced (PasswordAuthentication no)" bash -c "sshd -T 2>/dev/null | grep -qi '^passwordauthentication no'"
check "AllowGroups restricts logins" bash -c "sshd -T 2>/dev/null | grep -qi '^allowgroups.*workshop'"
check "group 'workshop' exists" getent group workshop
if [[ -r $STATE/users.tsv && -s $STATE/users.tsv ]]; then
  n=0
  while IFS=$'\t' read -r user uid; do
    [[ -n $user ]] || continue
    n=$((n + 1))
    if ! id "$user" >/dev/null 2>&1; then fail "account $user is missing (run: ws-user restore)"; continue; fi
    ak=$WS/home/$user/.ssh/authorized_keys
    if [[ -s $ak ]]; then pass "$user: account (uid $uid) and key present"; else warn "$user: account exists but has no key (revoked?)"; fi
    mode=$(stat -c %a "$WS/home/$user" 2>/dev/null)
    if [[ $mode == 700 ]]; then pass "$user: home is private (700)"; else fail "$user: home mode is $mode, expected 700"; fi
    if [[ ! -d $WS/home/$user/ki-ohne-cloud ]]; then warn "$user: no repository copy (ws-user reset-home $user)"; fi
  done <"$STATE/users.tsv"
  [[ $n -gt 0 ]] && pass "$n participant account(s) registered"
else
  warn "no participant accounts registered yet (infra/sync-participants.sh)"
fi
mapfile -t first_two < <(cut -f1 "$STATE/users.tsv" 2>/dev/null | head -2)
if [[ ${#first_two[@]} -eq 2 ]] && id "${first_two[0]}" >/dev/null 2>&1 && id "${first_two[1]}" >/dev/null 2>&1; then
  if runuser -u "${first_two[0]}" -- ls "$WS/home/${first_two[1]}" >/dev/null 2>&1; then fail "isolation: ${first_two[0]} can read ${first_two[1]}'s home"; else pass "isolation: participants cannot read each other's home"; fi
  if runuser -u "${first_two[0]}" -- sudo -n /usr/local/bin/wsctl profiles >/dev/null 2>&1; then pass "participants may run sudo wsctl"; else fail "participant cannot run 'sudo wsctl'"; fi
  if runuser -u "${first_two[0]}" -- sudo -n cat /etc/shadow >/dev/null 2>&1; then fail "participant has unrestricted sudo"; else pass "participant sudo is limited to wsctl"; fi
fi
if [[ -r $STATE/api-key ]]; then
  mode=$(stat -c '%a %U:%G' "$STATE/api-key")
  if [[ $mode == "640 root:workshop" ]]; then pass "API key file is 640 root:workshop"; else fail "API key file is '$mode'"; fi
else
  fail "no API key at $STATE/api-key"
fi

if [[ $NO_GPU -eq 1 ]]; then
  section "Result"
  printf '  %d passed, %d warnings, %d failed (GPU, servers and monitoring skipped)\n' "$PASS" "$WARN" "$FAIL"
  [[ $FAIL -eq 0 ]]
  exit $?
fi

section "Models"
HUB=$WS/hf-cache/hub
if [[ -f $WS/repo/config/models.yaml ]]; then
  while IFS=' ' read -r role repo rev; do
    dir="$HUB/models--${repo//\//--}/snapshots/$rev"
    if [[ -d $dir ]]; then pass "$role: $repo cached at pinned revision ${rev:0:12}"; else fail "$role: $repo @ ${rev:0:12} is not in the cache"; fi
  done < <(python3 - "$WS/repo/config/models.yaml" <<'PY'
import sys, yaml
for role, m in yaml.safe_load(open(sys.argv[1]))["models"].items():
    if m.get("workshop") is True:
        print(role, m["repo"], m["revision"])
PY
)
else
  fail "$WS/repo/config/models.yaml missing"
fi

section "Inference servers"
if curl -fsS --max-time 5 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  pass "main server /health is up"
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://127.0.0.1:8000/v1/models)
  if [[ $code == 401 ]]; then pass "/v1/models without a key is refused (401)"; else fail "/v1/models without a key returned $code (expected 401)"; fi
  models=$(api http://127.0.0.1:8000/v1/models 2>/dev/null | python3 -c 'import json,sys; print(" ".join(m["id"] for m in json.load(sys.stdin)["data"]))' 2>/dev/null)
  if [[ -n $models ]]; then pass "model served: $models"; else fail "/v1/models with the key returned nothing"; fi
  m=${models%% *}
  t0=$(date +%s.%N)
  reply=$(api http://127.0.0.1:8000/v1/completions -H 'Content-Type: application/json' \
    -d "{\"model\":\"$m\",\"prompt\":\"The capital of France is\",\"max_tokens\":8,\"temperature\":0}" 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["text"].strip())' 2>/dev/null)
  t1=$(date +%s.%N)
  if [[ -n $reply ]]; then pass "completion works ($(awk -v a="$t1" -v b="$t0" 'BEGIN{printf "%.0f", (a-b)*1000}') ms for 8 tokens): '$reply'"; else fail "completion request failed"; fi
  if ss -ltn 2>/dev/null | grep -qE '(0\.0\.0\.0|\*|\[::\]):8000\b'; then fail "port 8000 is bound to ALL interfaces (must be 127.0.0.1)"; else pass "port 8000 is bound to loopback only"; fi
else
  fail "main server is not healthy (sudo wsctl status; sudo wsctl logs)"
fi
if curl -fsS --max-time 5 http://127.0.0.1:8001/health >/dev/null 2>&1; then
  dim=$(api http://127.0.0.1:8001/v1/embeddings -H 'Content-Type: application/json' \
    -d '{"model":"Qwen/Qwen3-Embedding-0.6B","input":"hello"}' 2>/dev/null \
    | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"][0]["embedding"]))' 2>/dev/null)
  if [[ ${dim:-0} -gt 0 ]]; then pass "embedding server answers (dimension $dim)"; else fail "embedding request failed"; fi
else
  warn "embedding server (port 8001) is not running; the RAG demo needs it (sudo wsctl embed start)"
fi
if [[ -f $STATE/server.json ]]; then
  pass "provenance file: $(python3 -c 'import json; d=json.load(open("/workspace/state/server.json")); print("vLLM", d["engine_version"], "profile", d["profile"], "started in", d["startup_seconds"], "s")' 2>/dev/null)"
else
  warn "no $STATE/server.json (benchmark results will lack server provenance)"
fi
# shellcheck disable=SC2009  # we want the full command line
strays=$(ps -eo pid=,pgid=,args= | grep -E 'vllm (serve|\.entrypoints)' | grep -v grep | awk '{print $1}' | wc -l)
if [[ $strays -le 8 ]]; then pass "no obvious duplicate vLLM servers"; else warn "$strays vLLM-related processes: run 'wsctl status' and look for stray servers"; fi

section "Monitoring"
check "GPU exporter serves DCGM_FI_DEV_GPU_UTIL" bash -c "curl -fsS --max-time 5 http://127.0.0.1:9400/metrics | grep -q DCGM_FI_DEV_GPU_UTIL"
check "Prometheus is ready" curl -fsS --max-time 5 http://127.0.0.1:9090/-/ready
check "Prometheus scrapes vLLM (target up)" bash -c "curl -fsS --max-time 5 'http://127.0.0.1:9090/api/v1/query?query=up%7Bjob%3D%22vllm%22%7D' | grep -q '\"1\"\]'"
check "Grafana is healthy" curl -fsS --max-time 5 http://127.0.0.1:3000/api/health
check "Grafana dashboard provisioned" bash -c "curl -fsS --max-time 5 'http://127.0.0.1:3000/api/search?query=KI' | grep -qi 'dashboard'"

section "Result"
printf '  %d passed, %d warnings, %d failed\n' "$PASS" "$WARN" "$FAIL"
[[ $FAIL -eq 0 ]]
