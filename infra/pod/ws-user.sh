#!/usr/bin/env bash
# ws-user: manage workshop participant accounts on a GPU pod. Runs as root ON THE POD.
#
#   ws-user add <user> < pubkey      create the account (if missing) and install the key from stdin
#   ws-user revoke <user> [--lock|--delete]
#                                    remove every key, end the user's sessions; optionally lock
#                                    the account or delete it (the home directory is archived)
#   ws-user revoke-all [--delete]    revoke every participant account
#   ws-user restore                  recreate accounts from the registry (same UIDs) after
#                                    machine-setup was re-run in the same container
#   ws-user reset-home <user> [--hard]
#                                    give the user a fresh copy of the repository. The old one is
#                                    archived first; workshop-artifacts/ is carried over unless --hard
#   ws-user list                     users, UIDs and key fingerprints
#
# Why a registry? `restore` recreates accounts with the same UIDs after machine-setup is re-run on the
# same container. After a pod RESTART the container disk (accounts, registry, homes) is gone; the trainer
# rebuilds with infra/deploy-to-pod.sh and the accounts come back from infra/participants.yaml on the
# trainer's laptop, which is the source of truth. Nothing identity-related is kept on the shared volume,
# because that volume does not enforce permissions.
set -euo pipefail

# shellcheck source=paths.sh
source "${WS_PATHS:-/usr/local/lib/workshop/paths.sh}"
STATE=$WS_STATE
KEYS="$STATE/keys"
REGISTRY="$STATE/users.tsv"
AUDIT=$WS_LOGS/access.log
HOME_BASE=$WS_HOMES
ARCHIVE=$WS_BACKUPS/removed-users
GROUP=workshop
GID=2000
FIRST_UID=2001
USER_RE='^[a-z][a-z0-9_-]{1,30}$'
RESERVED_RE='^(root|admin|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|nobody|ubuntu|trainer|workshop|sshd)$'

TMP=""
cleanup() { if [[ -n "$TMP" ]]; then rm -f "$TMP"; fi; }
trap cleanup EXIT

die() { echo "ws-user: $*" >&2; exit 1; }
need_root() { [[ $EUID -eq 0 ]] || die "must run as root"; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

audit() { # action user detail
  mkdir -p "$(dirname "$AUDIT")"
  printf '%s\t%s\t%s\t%s\n' "$(now)" "$1" "$2" "${3:-}" >>"$AUDIT"
}

ensure_dirs() {
  mkdir -p "$KEYS" "$ARCHIVE" "$(dirname "$AUDIT")"
  # The state directory must stay traversable: participants read api-key (group), group and server.json.
  # Only the registry and the public keys are private.
  chmod 755 "$STATE"
  chmod 700 "$KEYS"
  touch "$REGISTRY"
  chmod 600 "$REGISTRY"
  getent group "$GROUP" >/dev/null || groupadd -g "$GID" "$GROUP"
}

validate_user() {
  [[ "$1" =~ $USER_RE ]] || die "invalid user name '$1' (lowercase letters, digits, - and _; 2-31 chars)"
  [[ ! "$1" =~ $RESERVED_RE ]] || die "user name '$1' is reserved"
}

# Accept exactly one plain public key line (no options such as command="...").
validate_key_file() {
  local file=$1 lines
  lines=$(grep -c . "$file" || true)
  [[ $lines -eq 1 ]] || die "expected exactly one public key, got $lines line(s)"
  grep -Eq '^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(256|384|521)|sk-ssh-ed25519@openssh\.com|sk-ecdsa-sha2-nistp256@openssh\.com) [A-Za-z0-9+/=]+( .*)?$' "$file" \
    || die "not a plain OpenSSH public key (key options are not accepted)"
  ssh-keygen -l -f "$file" >/dev/null 2>&1 || die "ssh-keygen cannot parse the key"
}

fingerprint() { ssh-keygen -l -f "$1" | awk '{print $2}'; }

uid_for() { # existing uid from the registry or the next free one
  local user=$1 uid
  uid=$(awk -F'\t' -v u="$user" '$1 == u {print $2}' "$REGISTRY")
  if [[ -n "$uid" ]]; then echo "$uid"; return; fi
  local max
  max=$(awk -F'\t' 'BEGIN{m=0} {if ($2>m) m=$2} END{print m}' "$REGISTRY")
  [[ $max -ge $FIRST_UID ]] && echo $((max + 1)) || echo "$FIRST_UID"
}

create_account() { # user uid
  local user=$1 uid=$2
  if id "$user" >/dev/null 2>&1; then return; fi
  # '-p *' = no valid password but NOT locked: sshd with UsePAM no refuses key logins to locked accounts.
  local home_flag=--create-home
  [[ -d "$HOME_BASE/$user" ]] && home_flag=--no-create-home
  useradd --uid "$uid" --gid "$GROUP" "$home_flag" --home-dir "$HOME_BASE/$user" \
    --shell /bin/bash --comment "workshop participant" -p '*' "$user"
  chmod 700 "$HOME_BASE/$user"
}

# Each participant works in their own copy of the repository (never overwritten once it exists).
init_home() { # user
  local user=$1 dest="$HOME_BASE/$1/ki-ohne-cloud"
  [[ -d $WS_REPO && ! -d $dest ]] || return 0
  mkdir -p "$dest"
  tar -C "$WS_REPO" --exclude=.git --exclude=node_modules --exclude=./slides --exclude=.venv \
    --exclude=./infra --exclude=participants.yaml --exclude=.env -cf - . | tar -C "$dest" -xf -
  chown -R "$user:$GROUP" "$dest"
}

install_key() { # user keyfile
  local user=$1 keyfile=$2 ssh_dir="$HOME_BASE/$1/.ssh"
  install -d -m 700 -o "$user" -g "$GROUP" "$ssh_dir"
  install -m 600 -o "$user" -g "$GROUP" "$keyfile" "$ssh_dir/authorized_keys"
}

cmd_add() {
  local user=${1:-}
  [[ -n "$user" ]] || die "usage: ws-user add <user> < pubkey"
  validate_user "$user"
  ensure_dirs
  TMP=$(mktemp)
  cat >"$TMP"
  validate_key_file "$TMP"
  local uid
  uid=$(uid_for "$user")
  if ! grep -q "^$user"$'\t' "$REGISTRY"; then printf '%s\t%s\n' "$user" "$uid" >>"$REGISTRY"; fi
  install -m 600 "$TMP" "$KEYS/$user.pub"
  create_account "$user" "$uid"
  usermod -U "$user" 2>/dev/null || true
  install_key "$user" "$KEYS/$user.pub"
  init_home "$user"
  audit add "$user" "$(fingerprint "$KEYS/$user.pub")"
  echo "ok: $user (uid $uid) key $(fingerprint "$KEYS/$user.pub")"
}

end_sessions() {
  local user=$1
  pkill -KILL -u "$user" 2>/dev/null || true
}

cmd_revoke() {
  local user=${1:-} mode=${2:-}
  [[ -n "$user" ]] || die "usage: ws-user revoke <user> [--lock|--delete]"
  validate_user "$user"
  ensure_dirs
  rm -f "$KEYS/$user.pub"
  if id "$user" >/dev/null 2>&1; then
    : >"$HOME_BASE/$user/.ssh/authorized_keys" 2>/dev/null || true
    usermod -L "$user" 2>/dev/null || true
    end_sessions "$user"
  fi
  case "$mode" in
    --delete)
      if [[ -d "$HOME_BASE/$user" ]]; then
        mv "$HOME_BASE/$user" "$ARCHIVE/$user-$(date -u +%Y%m%dT%H%M%SZ)"
      fi
      id "$user" >/dev/null 2>&1 && userdel "$user" 2>/dev/null || true
      sed -i "/^$user\t/d" "$REGISTRY"
      ;;
    --lock | "") ;;
    *) die "unknown option '$mode'" ;;
  esac
  audit revoke "$user" "${mode:-keys-removed}"
  echo "ok: access revoked for $user${mode:+ ($mode)}"
}

cmd_revoke_all() {
  ensure_dirs
  local mode=${1:-}
  local users
  users=$(cut -f1 "$REGISTRY")
  [[ -n "$users" ]] || { echo "no participant accounts"; return; }
  for u in $users; do cmd_revoke "$u" "$mode"; done
}

cmd_restore() {
  ensure_dirs
  local user uid
  while IFS=$'\t' read -r user uid; do
    [[ -n "$user" && -f "$KEYS/$user.pub" ]] || continue
    create_account "$user" "$uid"
    install_key "$user" "$KEYS/$user.pub"
    init_home "$user"
    echo "restored $user (uid $uid)"
  done <"$REGISTRY"
}

cmd_reset_home() {
  local user=${1:-} mode=${2:-}
  [[ -n "$user" ]] || die "usage: ws-user reset-home <user> [--hard]"
  validate_user "$user"
  id "$user" >/dev/null 2>&1 || die "no such user '$user'"
  [[ -z "$mode" || "$mode" == --hard ]] || die "unknown option '$mode'"
  local dest="$HOME_BASE/$user/ki-ohne-cloud" stamp backup
  stamp=$(date -u +%Y%m%dT%H%M%SZ)
  backup="$WS_BACKUPS/home-$user-$stamp-$$"
  mkdir -p "$backup"
  if [[ -d $dest ]]; then
    end_sessions_quiet "$user"
    cp -a "$dest" "$backup/"
    rm -rf "$dest"
  fi
  init_home "$user"
  if [[ -z $mode && -d $backup/ki-ohne-cloud/workshop-artifacts ]]; then
    cp -a "$backup/ki-ohne-cloud/workshop-artifacts/." "$dest/workshop-artifacts/"
    chown -R "$user:$GROUP" "$dest/workshop-artifacts"
  fi
  audit reset-home "$user" "${mode:-keep-artifacts}"
  echo "ok: fresh repository copy for $user (old one archived in $backup)"
}

# Stop processes that would be running inside the directory being replaced (not the SSH session itself).
end_sessions_quiet() { pkill -KILL -u "$1" -f 'infbench|vllm|python3 .*ki-ohne-cloud' 2>/dev/null || true; }

cmd_list() {
  ensure_dirs
  printf '%-16s %-6s %-8s %s\n' USER UID STATE FINGERPRINT
  local user uid state fp
  while IFS=$'\t' read -r user uid; do
    [[ -n "$user" ]] || continue
    state=missing
    id "$user" >/dev/null 2>&1 && state=present
    fp=-
    [[ -f "$KEYS/$user.pub" ]] && fp=$(fingerprint "$KEYS/$user.pub") || state="$state/revoked"
    printf '%-16s %-6s %-8s %s\n' "$user" "$uid" "$state" "$fp"
  done <"$REGISTRY"
}

main() {
  need_root
  local sub=${1:-}
  shift || true
  case "$sub" in
    add) cmd_add "$@" ;;
    revoke) cmd_revoke "$@" ;;
    revoke-all) cmd_revoke_all "$@" ;;
    restore) cmd_restore ;;
    reset-home) cmd_reset_home "$@" ;;
    list) cmd_list ;;
    *) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
  esac
}

main "$@"
