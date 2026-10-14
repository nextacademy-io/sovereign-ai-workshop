#!/usr/bin/env bash
# Run shellcheck over every shell script (and the extensionless ones listed below).
# Portable to macOS bash 3.2: participant-side scripts run on laptops, so avoid mapfile and
# associative arrays here and in scripts/*.sh.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "shellcheck not found. Install it (brew install shellcheck / apt install shellcheck)." >&2
  exit 127
fi

# Extensionless scripts that are not caught by '*.sh'.
extra=(infra/wsctl)

files=()
while IFS= read -r f; do
  files+=("$f")
done < <(
  {
    find . \( -path ./node_modules -o -path ./.git -o -path ./.venv -o -path ./slides/node_modules \) -prune -o \
      -type f -name '*.sh' -print
    for f in "${extra[@]}"; do [[ -f "$f" ]] && echo "./$f"; done
  } | sort -u
)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "no shell scripts found"
  exit 0
fi

echo "shellcheck: ${#files[@]} file(s)"
shellcheck --external-sources "${files[@]}"
