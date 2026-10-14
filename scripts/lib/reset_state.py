#!/usr/bin/env python3
"""Apply a workshop state: give a participant everything a lab needs to start, without losing their work.

A workshop state (workshop-states/<id>/state.yaml) lists
  restore     starter files that live in the repository (templates), restored from the trusted copy
  files       files that exist only inside the state (for example a report filled in up to this lab)
  references  measured reference results to fall back on if a participant's own run failed
  server      the vLLM profile the lab assumes (applied only when asked, because the server is shared)

Default ("soft") behaviour never overwrites a file the participant already has: they may be halfway
through the lab. `--hard` replaces files as well, but first copies whatever it replaces into
~/.workshop-backups/<time>/, so nothing is lost. Reference data is read-only material and always refreshed.

    reset_state.py lab-03                 apply, soft
    reset_state.py lab-03 --hard          apply, replacing starter files (backups are made)
    reset_state.py --list                 show all labs and states
    reset_state.py lab-03 --print-profile print the server profile the state expects
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import time
from pathlib import Path

import yaml


def load_states(root: Path) -> dict[str, dict]:
    """lab id -> state dict (with its directory), from workshop-states/*/state.yaml."""
    states: dict[str, dict] = {}
    for path in sorted((root / "workshop-states").glob("*/state.yaml")):
        state = yaml.safe_load(path.read_text()) or {}
        for key in ("id", "lab", "title"):
            if key not in state:
                raise ValueError(f"{path}: missing '{key}'")
        state["_dir"] = path.parent
        if state["lab"] in states:
            raise ValueError(f"{path}: lab '{state['lab']}' is defined twice")
        states[state["lab"]] = state
    return states


def apply_state(
    state: dict, root: Path, dest: Path, *, hard: bool, backup_dir: Path, dry_run: bool = False
) -> list[str]:
    """Copy the state's files into `dest`. Returns a human-readable list of what happened."""
    actions: list[str] = []

    def backup(target: Path) -> None:
        rel = target.relative_to(dest)
        saved = backup_dir / rel
        if not dry_run:
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        actions.append(f"backed up {rel} -> {saved}")

    # `restore`: starter files that already live in the repository (templates): restored from the trusted copy.
    # `files`: files that only exist inside the state (for example a report filled in up to this lab).
    sources = [(rel, root / rel, "restore") for rel in state.get("restore", [])]
    sources += [(rel, state["_dir"] / "files" / rel, "files") for rel in state.get("files", [])]
    for rel, src, kind in sources:
        dst = dest / rel
        if not src.is_file():
            raise FileNotFoundError(
                f"state {state['id']} lists {rel} under '{kind}' but {src} does not exist"
            )
        if dst.exists():
            if filecmp.cmp(src, dst, shallow=False):
                actions.append(f"unchanged  {rel}")
                continue
            if not hard:
                actions.append(f"kept your  {rel} (use --hard to replace it; a backup is made)")
                continue
            backup(dst)
        actions.append(f"wrote      {rel}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    for ref in state.get("references", []):
        src = root / ref
        if not src.exists():
            actions.append(
                f"missing reference {ref} (ask the trainer: it is produced by the experiments)"
            )
            continue
        target = dest / "benchmark" / "results" / "reference" / src.name
        actions.append(f"reference  {ref} -> {target.relative_to(dest)}")
        if not dry_run:
            if target.exists():
                shutil.rmtree(target)
            if src.is_dir():
                shutil.copytree(src, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
    return actions


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("lab", nargs="?")
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="the TRUSTED copy of the repository to take states and reference data from",
    )
    ap.add_argument("--dest", type=Path)
    ap.add_argument("--hard", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--print-profile", action="store_true")
    a = ap.parse_args()
    states = load_states(a.root)
    if a.list or not a.lab:
        for lab, st in states.items():
            print(f"{lab:8s} state {st['id']:14s} {st['title']}")
        return 0
    if a.lab not in states:
        print(f"unknown lab '{a.lab}'. Known: {', '.join(states)}", file=sys.stderr)
        return 2
    state = states[a.lab]
    if a.print_profile:
        print(state.get("server", {}).get("profile", ""))
        return 0
    dest = a.dest or Path(__file__).resolve().parents[2]
    backup_dir = Path.home() / ".workshop-backups" / time.strftime("%Y%m%dT%H%M%S")
    for line in apply_state(
        state, a.root, dest, hard=a.hard, backup_dir=backup_dir, dry_run=a.dry_run
    ):
        print("  " + line)
    print(f"\n{state['id']}: {state['title']}")
    if state.get("note"):
        print(state["note"].rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
