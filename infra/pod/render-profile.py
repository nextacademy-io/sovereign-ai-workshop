#!/usr/bin/env python3
"""Render a workshop vLLM profile into the YAML that `vllm serve --config` reads.

Profiles live in config/vllm-profiles/*.yaml and may `extends:` one another. This script:
  * resolves the extends chain and merges (child wins),
  * applies `--set key=value` overrides, but only for an allowlist of safe engine knobs,
  * refuses anything that would weaken the deployment (public bind, remote code, API key in a file),
  * writes the merged YAML and prints a JSON summary used for the server provenance file.

Runs on the pod with the Python from the vLLM image (PyYAML is a vLLM dependency).

    render-profile.py baseline --dir /workspace/repo/config/vllm-profiles --out /tmp/active.yaml
    render-profile.py baseline --dir ... --set max-num-seqs=8 --set enable-prefix-caching=false
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

META_KEYS = {"description", "extends", "abstract", "role", "experiment"}
# Knobs a lab group may change without a new profile.
SET_ALLOWLIST = {
    "max-num-seqs",
    "max-num-batched-tokens",
    "max-model-len",
    "gpu-memory-utilization",
    "kv-cache-memory-bytes",
    "kv-cache-dtype",
    "enable-prefix-caching",
    "enable-chunked-prefill",
    "long-prefill-token-threshold",
    "quantization",
    "stream-interval",
}
FORBIDDEN_KEYS = {
    "api-key",
    "trust-remote-code",
    "download-dir",
    "ssl-keyfile",
    "ssl-certfile",
    "allowed-origins",
    "uds",
    "model-loader-extra-config",
    "tool-parser-plugin",
}
ALLOWED_PORTS = {8000, 8001}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VALUE_RE = re.compile(r"^[A-Za-z0-9._+-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_DEPTH = 4


class ProfileError(ValueError):
    pass


def _normalize_key(key: str) -> str:
    return key.replace("_", "-")


def load_profile(name: str, directory: Path, _depth: int = 0) -> dict:
    """Return the fully merged profile (meta keys included)."""
    if not NAME_RE.match(name):
        raise ProfileError(f"invalid profile name '{name}'")
    if _depth > MAX_DEPTH:
        raise ProfileError("profile 'extends' chain is too deep (cycle?)")
    path = directory / f"{name}.yaml"
    if not path.is_file():
        available = ", ".join(sorted(p.stem for p in directory.glob("*.yaml")))
        raise ProfileError(f"unknown profile '{name}'. Available: {available}")
    raw = yaml.safe_load(path.read_text()) or {}
    if not isinstance(raw, dict):
        raise ProfileError(f"{path.name}: must be a mapping")
    own = {_normalize_key(k): v for k, v in raw.items()}
    parent = own.get("extends")
    merged: dict = load_profile(parent, directory, _depth + 1) if parent else {}
    # `abstract` and `description` describe one profile; they must not leak to its children.
    merged.pop("abstract", None)
    merged.pop("description", None)
    merged.update(own)
    return merged


def _coerce(value: str):
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d*\.\d+", value):
        return float(value)
    return value


def apply_overrides(profile: dict, sets: list[str]) -> dict:
    out = dict(profile)
    for item in sets:
        key, sep, value = item.partition("=")
        key = _normalize_key(key.strip())
        if not sep or key not in SET_ALLOWLIST:
            raise ProfileError(
                f"--set '{item}': allowed keys are {', '.join(sorted(SET_ALLOWLIST))}"
            )
        if not VALUE_RE.match(value):
            raise ProfileError(
                f"--set '{item}': value may only contain letters, digits and . _ + -"
            )
        out[key] = _coerce(value)
    return out


def validate(profile: dict, name: str) -> None:
    if profile.get("abstract"):
        raise ProfileError(f"profile '{name}' is abstract and cannot be started")
    if not profile.get("model"):
        raise ProfileError(f"profile '{name}' has no 'model'")
    rev = str(profile.get("revision", ""))
    if not SHA_RE.match(rev):
        raise ProfileError(
            f"profile '{name}': 'revision' must be a pinned 40-character commit SHA, got '{rev}'"
        )
    bad = FORBIDDEN_KEYS & set(profile)
    if bad:
        raise ProfileError(f"profile '{name}' sets forbidden keys: {', '.join(sorted(bad))}")
    if profile.get("host") != "127.0.0.1":
        raise ProfileError(
            "'host' must be 127.0.0.1 (the API is reached through SSH, never bound publicly)"
        )
    if profile.get("port") not in ALLOWED_PORTS:
        raise ProfileError(f"'port' must be one of {sorted(ALLOWED_PORTS)}")


def to_args(config: dict) -> str:
    """The equivalent command line, stored in the provenance file for humans and reports."""
    parts: list[str] = []
    for key, value in config.items():
        if value is True:
            parts.append(f"--{key}")
        elif value is False:
            parts.append(f"--no-{key}")
        elif isinstance(value, dict | list):
            parts.append(f"--{key} '{json.dumps(value, separators=(',', ':'))}'")
        else:
            parts.append(f"--{key} {value}")
    return " ".join(parts)


def render(name: str, directory: Path, sets: list[str] | None = None) -> tuple[dict, dict]:
    merged = apply_overrides(load_profile(name, directory), sets or [])
    validate(merged, name)
    config = {k: v for k, v in merged.items() if k not in META_KEYS}
    summary = {
        "profile": name,
        "description": merged.get("description", ""),
        "role": merged.get("role", "generation"),
        "model": config["model"],
        "model_revision": config["revision"],
        "port": config["port"],
        "overrides": sets or [],
        "args": to_args(config),
    }
    return config, summary


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("profile", nargs="?")
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, help="write the rendered vLLM config here")
    ap.add_argument("--set", dest="sets", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--list", action="store_true", help="list startable profiles and exit")
    ap.add_argument(
        "--allowed-sets", action="store_true", help="print the keys --set accepts and exit"
    )
    a = ap.parse_args()
    if a.allowed_sets:
        print(", ".join(sorted(SET_ALLOWLIST)))
        return 0
    if not a.list and not a.profile:
        ap.error("a profile name is required")
    try:
        if a.list:
            for path in sorted(a.dir.glob("*.yaml")):
                p = load_profile(path.stem, a.dir)
                if not p.get("abstract"):
                    print(f"{path.stem}\t{p.get('role', 'generation')}\t{p.get('description', '')}")
            return 0
        config, summary = render(a.profile, a.dir, a.sets)
    except ProfileError as exc:
        print(f"render-profile: {exc}", file=sys.stderr)
        return 2
    if a.out:
        a.out.write_text(yaml.safe_dump(config, sort_keys=False))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
