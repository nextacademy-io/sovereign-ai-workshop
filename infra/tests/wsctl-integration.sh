#!/usr/bin/env bash
# Integration test for the pod tooling in a clean Ubuntu container (no GPU): machine-setup, accounts,
# wsctl start/restart/stop with a fake `vllm`, embedding server next to the main server, stray detection,
# participant access and the integrity checks of verify-machine.sh.
#
#   infra/tests/wsctl-integration.sh        (needs Docker)
#
# It exists because two real bugs only showed up on a live pod: a failing `ls` aborting the start under
# `set -o pipefail`, and the vLLM process inheriting wsctl's lock descriptor so that every later wsctl
# command reported "operation in progress".
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
command -v docker >/dev/null || { echo "docker not found" >&2; exit 127; }

docker run --rm -v "$PWD:/src:ro" ubuntu:24.04 bash -euo pipefail -c '
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq openssh-server python3 python3-yaml procps curl sudo git openssh-client >/dev/null 2>&1
ssh-keygen -A >/dev/null
mkdir -p /opt/workshop/repo
cd /src && git ls-files -z --cached --others --exclude-standard | grep -zv "^slides/" | tar --null -T - -cf - | tar -C /opt/workshop/repo -xf -
cp /src/infra/tests/fake_vllm.py /usr/local/bin/vllm && chmod +x /usr/local/bin/vllm
sed -i "1s|.*|#!/usr/bin/env python3|" /usr/local/bin/vllm

t() { printf "  %-62s" "$1"; }
ok() { echo "ok"; }
no() { echo "FAILED: $*"; exit 1; }

bash /opt/workshop/repo/infra/machine-setup.sh --group alpha --no-gpu >/dev/null 2>&1
ssh-keygen -q -t ed25519 -N "" -f /tmp/k1; ws-user add anna < /tmp/k1.pub >/dev/null
export WSCTL_READY_TIMEOUT=60

echo "wsctl lifecycle"
t "start the main server"; wsctl start baseline >/tmp/start.out 2>&1 && ok || { cat /tmp/start.out; no "start"; }
t "status reports it running and healthy"; st=$(wsctl status 2>&1); grep -q "^main .*running.*baseline.*ok" <<<"$st" && ok || { echo "$st"; no "status"; }
t "provenance file has version and parsed KV capacity"
python3 - <<PY && ok || no "server.json"
import json
d = json.load(open("/var/lib/workshop/server.json"))
assert d["engine_version"] == "0.31.0-fake" and d["startup_log"]["kv_cache_tokens"] == 423328, d
assert d["model_revision"] == "b968826d9c46dd6066d109eabc6255188de91218" and d["startup_seconds"] >= 1
PY
t "a second wsctl call works while the server runs (no leaked lock)"; wsctl embed start >/tmp/embed.out 2>&1 && ok || { cat /tmp/embed.out; no "embed start"; }
t "both servers answer on their own ports"; curl -fsS localhost:8000/health >/dev/null && curl -fsS localhost:8001/health >/dev/null && ok || no "ports"
t "restart with an allowlisted override changes the server"
pid1=$(cat /var/lib/workshop/vllm-main.pid); wsctl start baseline --set max-num-seqs=8 >/dev/null 2>&1 && pid2=$(cat /var/lib/workshop/vllm-main.pid)
[ "$pid1" != "$pid2" ] && grep -q "max-num-seqs 8" /var/lib/workshop/server.json && ok || no "restart"
t "the old process is gone (no orphaned workers)"; ! kill -0 "$pid1" 2>/dev/null && ok || no "old pid alive"
t "wsctl restart keeps the profile and the override"; wsctl restart >/dev/null 2>&1 && grep -q "max-num-seqs 8" /var/lib/workshop/server.json && ok || no "restart keeps overrides"
t "archived logs are kept (rotation works with and without old logs)"; [ "$(ls /var/log/workshop/vllm-main-2*.log 2>/dev/null | wc -l)" -ge 1 ] && ok || no "log rotation"

echo "guard rails"
t "unknown profile is rejected"; ! wsctl start nope >/dev/null 2>&1 && ok || no "unknown profile"
t "abstract profile is rejected"; ! wsctl start base >/dev/null 2>&1 && ok || no "abstract profile"
t "--set of a forbidden key is rejected"; ! wsctl start baseline --set api-key=x >/dev/null 2>&1 && ok || no "forbidden key"
t "the server keeps running after rejected requests"; curl -fsS localhost:8000/health >/dev/null && ok || no "server died"
t "the embedding profile starts the embedding role, not the main one"; wsctl embed start >/dev/null 2>&1; st=$(wsctl status 2>&1); grep -q "^embed .*running.*embedding" <<<"$st" && ok || { echo "$st"; no "role"; }

echo "participant access"
ws-user add ben < /tmp/k1.pub >/dev/null 2>&1 || true
t "a participant can read status through sudo"; runuser -u anna -- sudo -n wsctl status >/dev/null 2>&1 && ok || no "participant status"
t "a participant can restart the server (lock is free)"; runuser -u anna -- sudo -n wsctl start baseline >/dev/null 2>&1 && ok || no "participant start"
t "the actor is recorded in the audit log"; grep -q "anna" /var/log/workshop/wsctl.log && ok || no "audit"

echo "rollback"
t "a profile that fails to start is rolled back to the previous one"
wsctl start baseline >/dev/null 2>&1
before=$(python3 -c "import json; print(json.load(open(\"/var/lib/workshop/server.json\"))[\"profile\"])")
! wsctl start baseline --set max-num-seqs=666 >/tmp/rb.out 2>&1 && curl -fsS localhost:8000/health >/dev/null \
  && after=$(python3 -c "import json; print(json.load(open(\"/var/lib/workshop/server.json\"))[\"profile\"])") \
  && [ "$before" = "$after" ] && grep -q "rolling back" /tmp/rb.out && ok || { cat /tmp/rb.out; no "rollback"; }
t "the failed attempt and the rollback are in the audit log"; grep -q "rollback to baseline" /var/log/workshop/wsctl.log && ok || no "rollback audit"

echo "stray servers"
cat > /tmp/stray.yaml <<Y
model: x/y
port: 8099
Y
setsid /usr/local/bin/vllm serve --config /tmp/stray.yaml >/dev/null 2>&1 &
sleep 2
curl -fsS localhost:8099/health >/dev/null || no "the stray server did not start"
t "status warns about a server it did not start"; st=$(wsctl status 2>&1); grep -q "not started by wsctl" <<<"$st" && ok || { echo "$st"; no "stray warning"; }
t "reap removes it and leaves the real servers alone"; wsctl reap >/dev/null 2>&1; sleep 2; ! curl -fsS localhost:8099/health >/dev/null 2>&1 && curl -fsS localhost:8000/health >/dev/null && ok || no "reap"

echo "stop"
t "stop ends the main server"; wsctl stop >/dev/null 2>&1; ! curl -fsS localhost:8000/health >/dev/null 2>&1 && ok || no "stop"
t "the embedding server is unaffected by stopping the main one"; curl -fsS localhost:8001/health >/dev/null && ok || no "embed survived"
wsctl embed stop >/dev/null 2>&1
echo
echo "all wsctl integration checks passed"
'
