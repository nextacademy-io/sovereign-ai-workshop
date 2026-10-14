#!/usr/bin/env python3
"""Print participants.yaml as tab-separated lines: group, host, port, user, key.

Used by infra/sync-participants.sh so the shell scripts need no YAML parser.
    python3 infra/lib/participants.py infra/participants.yaml [--group alpha]
"""

import re
import sys
from pathlib import Path

import yaml

USER_RE = re.compile(r"^[a-z][a-z0-9_-]{1,30}$")
KEY_RE = re.compile(r"^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp(256|384|521)|sk-[a-z0-9@.-]+) [A-Za-z0-9+/=]+( .*)?$")


def rows(path: Path, group: str | None):
    data = yaml.safe_load(path.read_text()) or {}
    seen: set[str] = set()
    for g in data.get("groups", []):
        if group and g["id"] != group:
            continue
        for p in g.get("participants", []):
            user, key = p["user"], p["ssh_public_key"].strip()
            if not USER_RE.match(user):
                raise SystemExit(f"invalid user name: {user!r}")
            if "PRIVATE KEY" in key or not KEY_RE.match(key):
                raise SystemExit(f"{user}: not a plain public key")
            if user in seen:
                raise SystemExit(f"duplicate user: {user}")
            seen.add(user)
            yield g["id"], g["host"], g.get("port", 22), user, key


if __name__ == "__main__":
    args = sys.argv[1:]
    group = args[args.index("--group") + 1] if "--group" in args else None
    for r in rows(Path(args[0]), group):
        print("\t".join(map(str, r)))
