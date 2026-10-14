"""Collect the facts that make a benchmark result reproducible and attributable.

A number without hardware, model revision, engine version, server arguments and date is
an anecdote. `scripts/check-repo.mjs` rejects committed results that lack these fields.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SERVER_INFO = Path("/workspace/state/server.json")


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _run(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return None


def collect_hardware(
    gpu_name: str | None = None, gpu_count: int | None = None, vram_gb: float | None = None
) -> dict:
    """GPU facts from nvidia-smi, overridable when the harness runs away from the GPU host."""
    info: dict = {"gpu": gpu_name, "gpu_count": gpu_count, "vram_gb": vram_gb}
    out = _run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    if out:
        rows = [[c.strip() for c in line.split(",")] for line in out.strip().splitlines()]
        names = {r[0] for r in rows}
        info["gpu"] = gpu_name or (names.pop() if len(names) == 1 else " + ".join(sorted(names)))
        info["gpu_count"] = gpu_count or len(rows)
        info["vram_gb"] = vram_gb or round(float(rows[0][1]) / 1024, 1)
        info["driver_version"] = rows[0][2]
    info["cpu_count"] = os.cpu_count()
    info["os"] = f"{platform.system()} {platform.release()}"
    return info


def driver_cuda_version() -> str | None:
    """Highest CUDA version the driver supports (the number in the nvidia-smi header)."""
    out = _run(["nvidia-smi"])
    m = re.search(r"CUDA Version:\s*(\d+\.\d+)", out or "")
    return m.group(1) if m else None


def read_server_info(path: Path | None) -> dict | None:
    """The supervisor (infra/wsctl) writes this file whenever it starts a server."""
    candidate = path or DEFAULT_SERVER_INFO
    if candidate.exists():
        try:
            return json.loads(candidate.read_text())
        except (OSError, json.JSONDecodeError):
            return None
    return None


def lookup_model_revision(model: str) -> str | None:
    """Find the pinned commit SHA for a served model in config/models.yaml."""
    path = REPO_ROOT / "config" / "models.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text()) or {}
    entries = data.get("models", data)
    for entry in entries.values() if isinstance(entries, dict) else []:
        if isinstance(entry, dict) and entry.get("repo") == model:
            return entry.get("revision")
    return None


def fetch_engine_version(base_url: str, headers: dict[str, str]) -> str | None:
    try:
        r = httpx.get(f"{base_url}/version", headers=headers, timeout=5.0)
        if r.status_code == 200:
            return r.json().get("version")
    except (httpx.HTTPError, ValueError):
        pass
    return None


def collect_configuration(
    *,
    base_url: str,
    headers: dict[str, str],
    model: str,
    engine: str,
    server_info_path: Path | None,
    overrides: dict,
) -> dict:
    """Everything except the workload and load description, which the CLI adds."""
    info = read_server_info(server_info_path) or {}
    engine_version = (
        overrides.get("engine_version")
        or fetch_engine_version(base_url, headers)
        or info.get("engine_version")
    )
    runtime_cuda = overrides.get("runtime_cuda") or info.get("runtime_cuda_version")
    driver_cuda = driver_cuda_version()
    server_args = overrides.get("server_args") or info.get("args")
    return {
        "hardware": collect_hardware(
            overrides.get("gpu_name"), overrides.get("gpu_count"), overrides.get("vram_gb")
        ),
        "model": model,
        "model_revision": overrides.get("model_revision")
        or info.get("model_revision")
        or lookup_model_revision(model),
        "engine": engine,
        "engine_version": engine_version,
        "vllm_version": engine_version if engine == "vllm" else None,
        "cuda_version": runtime_cuda or driver_cuda,
        "cuda_details": {"runtime": runtime_cuda, "driver_max": driver_cuda},
        "server_args": server_args,
        "server_profile": info.get("profile"),
        "date": utc_now(),
        "note": overrides.get("note"),
    }
