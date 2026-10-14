import sys
from pathlib import Path

# The app directories contain hyphens, so they cannot be imported as packages.
# Put each on sys.path so tests can `import rag`, `import agent`, and so on.
APPS = Path(__file__).resolve().parent
for path in [
    APPS,
    *sorted(p for p in APPS.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))),
]:
    sys.path.insert(0, str(path))
sys.path.insert(0, str(APPS.parent / "benchmark"))
