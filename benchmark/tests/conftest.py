import sys
from pathlib import Path

# Make `infbench` (benchmark/infbench) and the fake server importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
