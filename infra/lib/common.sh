# shellcheck shell=bash
# Helpers for the trainer-side scripts in infra/. Written for macOS bash 3.2 (the trainer's laptop):
# no mapfile, no associative arrays.

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC2034  # used by the scripts that source this file
REPO_DIR="$(cd "$INFRA_DIR/.." && pwd)"
STATE_DIR="$INFRA_DIR/.state"
mkdir -p "$STATE_DIR"

POD_HOST="${POD_HOST:-}"
POD_PORT="${POD_PORT:-22}"
POD_USER="${POD_USER:-root}"
POD_IDENTITY="${POD_IDENTITY:-}"

die() { echo "error: $*" >&2; exit 1; }
info() { echo "==> $*" >&2; }

# Parse --host/--port/--identity from the front of the argument list; leaves the rest in REST_ARGS.
REST_ARGS=()
parse_pod_args() {
  REST_ARGS=()
  while [ $# -gt 0 ]; do
    case "$1" in
      --host) POD_HOST="$2"; shift 2 ;;
      --port) POD_PORT="$2"; shift 2 ;;
      --identity) POD_IDENTITY="$2"; shift 2 ;;
      *) REST_ARGS+=("$1"); shift ;;
    esac
  done
}

require_pod() {
  [ -n "$POD_HOST" ] || die "no pod given: pass --host HOST --port PORT (or set POD_HOST/POD_PORT)"
}

# Run a command on the pod as root. A project-local known_hosts keeps recreated pods
# (new host keys) from polluting or conflicting with ~/.ssh/known_hosts.
ssh_pod() {
  local opts=(-o BatchMode=yes -o StrictHostKeyChecking=accept-new
    -o "UserKnownHostsFile=$STATE_DIR/known_hosts" -o ConnectTimeout=15
    -o ServerAliveInterval=20 -p "$POD_PORT")
  if [ -n "$POD_IDENTITY" ]; then opts+=(-i "$POD_IDENTITY"); fi
  # shellcheck disable=SC2029  # the command is meant to be expanded on this side
  ssh "${opts[@]}" "$POD_USER@$POD_HOST" "$@"
}

# Copy the repository to the pod. What leaves this laptop is decided by git: tracked files plus
# untracked files that .gitignore does not exclude. Anything ignored (.env, participants.yaml, input/,
# node_modules, results scratch) therefore never reaches a rented machine. The slides are not needed there.
push_repo() { # remote_dir
  local dst=$1
  local tarflags=()
  # macOS bsdtar would add AppleDouble (._*) files and extended attributes that GNU tar cannot digest.
  if tar --version 2>/dev/null | grep -qi bsdtar; then tarflags=(--no-xattrs --no-mac-metadata); fi
  [ -d "$REPO_DIR/.git" ] || die "$REPO_DIR is not a git checkout; push_repo relies on git to decide what may be copied"
  (
    cd "$REPO_DIR" || exit 1
    git ls-files -z --cached --others --exclude-standard | grep -zv -e '^slides/' -e '^\.github/' |
      COPYFILE_DISABLE=1 tar "${tarflags[@]+"${tarflags[@]}"}" --null -T - -cf -
  ) | ssh_pod "mkdir -p '$dst' && tar --no-same-owner --warning=no-unknown-keyword -C '$dst' -xf -"
}
