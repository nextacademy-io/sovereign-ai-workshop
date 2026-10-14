#!/usr/bin/env bash
# Check your laptop before the workshop. Nothing is downloaded and nothing is changed.
#
#   ./scripts/preflight.sh
#   ./scripts/preflight.sh --host <gpu-host> --port <ssh-port> --user <your-user>    # after the trainer sent you access
#
# Needs: git, ssh, docker, python3 (3.11 or newer), curl, an SSH key, about 20 GB of free disk.
# Works with the bash that ships with macOS (3.2).
set -u

host="" port=22 user=""
while [ $# -gt 0 ]; do
  case "$1" in
    --host) host="$2"; shift 2 ;;
    --port) port="$2"; shift 2 ;;
    --user) user="$2"; shift 2 ;;
    -h | --help) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

pass=0 warn=0 fail=0
ok() { pass=$((pass + 1)); printf '  OK    %s\n' "$*"; }
warning() { warn=$((warn + 1)); printf '  WARN  %s\n' "$*"; }
bad() { fail=$((fail + 1)); printf '  FAIL  %s\n' "$*"; }

echo "Tools"
for tool in git ssh curl; do
  if command -v "$tool" >/dev/null 2>&1; then
    case "$tool" in
      ssh) version=$(ssh -V 2>&1 | head -1) ;; # ssh has -V, not --version
      *) version=$("$tool" --version 2>&1 | head -1) ;;
    esac
    ok "$tool: $version"
  else
    bad "$tool is not installed"
  fi
done

if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    ok "python3: $(python3 --version 2>&1)"
  else
    bad "python3 is $(python3 --version 2>&1); version 3.11 or newer is needed"
  fi
else
  bad "python3 is not installed (3.11 or newer)"
fi

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker: $(docker --version 2>&1 | head -1), daemon reachable"
  else
    warning "docker is installed but the daemon is not running. Start Docker Desktop before Day 3."
  fi
else
  bad "docker is not installed (needed for the Day 3 container exercise)"
fi

echo
echo "SSH key"
key=""
for candidate in "$HOME/.ssh/id_ed25519.pub" "$HOME/.ssh/id_ecdsa.pub" "$HOME/.ssh/id_rsa.pub"; do
  if [ -f "$candidate" ]; then key="$candidate"; break; fi
done
if [ -n "$key" ]; then
  ok "public key found: $key"
  echo "        Send THIS file's content (one line) to the trainer. Never send the file without .pub:"
  echo "        $(cut -c1-70 "$key")..."
else
  bad "no SSH key found. Create one with:  ssh-keygen -t ed25519 -C \"$(whoami)@workshop\""
fi

echo
echo "Disk"
free_kb=$(df -k "$HOME" 2>/dev/null | awk 'NR==2 {print $4}')
if [ -n "${free_kb:-}" ]; then
  free_gb=$((free_kb / 1024 / 1024))
  if [ "$free_gb" -ge 20 ]; then ok "${free_gb} GB free in your home directory"; else warning "only ${free_gb} GB free; about 20 GB are recommended for Docker images"; fi
fi

if [ -n "$host" ]; then
  echo
  echo "GPU host $host:$port"
  [ -n "$user" ] || { bad "pass --user <your-user> together with --host"; user=""; }
  if [ -n "$user" ]; then
    if out=$(ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -p "$port" "$user@$host" 'echo connected; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader' 2>&1); then
      ok "login works"
      printf '%s\n' "$out" | sed 's/^/        /'
    else
      bad "cannot log in: $(echo "$out" | tail -1)"
      echo "        Check the user name, the port (it changes if the trainer recreated the machine) and that your key was added."
    fi
  fi
fi

echo
echo "Result: $pass ok, $warn warning(s), $fail failed"
[ "$fail" -eq 0 ]
