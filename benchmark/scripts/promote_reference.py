#!/usr/bin/env python3
"""Promote experiment results from a dated session directory to benchmark/results/reference/.

    python3 benchmark/scripts/promote_reference.py benchmark/results/<date>-rtxpro6000-s2 baseline concurrency

The slides, the tasks and the workshop states cite `benchmark/results/reference/<experiment>/...`:
a stable path that does not carry a date. The dated session directory stays as the raw archive.

Every promoted JSON must carry provenance. Auxiliary documents written by the experiment runner
(for example `kv-formula-check.json`, `startup.json`) have none of their own, so they receive the
`configuration` of a result file in the same experiment, plus a `derived_from` note saying so.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "results"
SKIP_SUFFIXES = {".log", ".jsonl"}


def first_configuration(experiment_dir: Path) -> tuple[dict, str] | None:
    for path in sorted(experiment_dir.rglob("*.json")):
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("configuration"), dict):
            return doc["configuration"], str(path.relative_to(experiment_dir))
    return None


def promote(
    session: Path, experiments: list[str], dest: Path = RESULTS / "reference"
) -> list[Path]:
    written: list[Path] = []
    for name in experiments:
        src = session / name
        if not src.is_dir():
            raise SystemExit(f"{src} is not a directory")
        base = first_configuration(src)
        target_root = dest / name
        if target_root.exists():
            shutil.rmtree(target_root)
        for path in sorted(src.rglob("*")):
            if path.is_dir() or path.suffix in SKIP_SUFFIXES:
                continue
            out = target_root / path.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == ".json":
                doc = json.loads(path.read_text())
                if isinstance(doc, dict) and "configuration" not in doc:
                    if base is None:
                        raise SystemExit(
                            f"{path}: no result with a configuration in {src} to take provenance from"
                        )
                    doc = {
                        "configuration": base[0],
                        "derived_from": f"configuration copied from {name}/{base[1]}; this file was written by experiments/runner.py",
                        **doc,
                    }
                out.write_text(json.dumps(doc, indent=2) + "\n")
            else:
                shutil.copyfile(path, out)
            written.append(out)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("session", type=Path, help="dated session directory under benchmark/results/")
    ap.add_argument("experiments", nargs="+", help="experiment directories inside the session")
    args = ap.parse_args(argv)
    files = promote(args.session, args.experiments)
    print(f"promoted {len(files)} files to {RESULTS / 'reference'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
