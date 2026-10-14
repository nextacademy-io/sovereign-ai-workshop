import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "render_profile", ROOT / "infra/pod/render-profile.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules["render_profile"] = module
spec.loader.exec_module(module)
