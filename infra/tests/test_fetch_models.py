import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fetch_models", ROOT / "infra/pod/fetch-models.py")
fetch_models = importlib.util.module_from_spec(spec)
sys.modules["fetch_models"] = fetch_models
spec.loader.exec_module(fetch_models)

MODELS = yaml.safe_load((ROOT / "config/models.yaml").read_text())["models"]


def test_workshop_group_is_the_four_lab_models():
    assert set(fetch_models.select(MODELS, "workshop")) == {
        "primary",
        "quantized",
        "small",
        "embedding",
    }


def test_demo_group_is_separate_so_labs_do_not_wait_for_a_30b_download():
    assert set(fetch_models.select(MODELS, "demo")) == {"moe_demo", "gguf_demo"}


def test_explicit_roles_and_unknown_roles():
    assert list(fetch_models.select(MODELS, "primary,small")) == ["primary", "small"]
    with pytest.raises(SystemExit):
        fetch_models.select(MODELS, "primary,nope")


def test_every_model_is_pinned_to_a_full_sha_and_has_a_licence():
    for role, m in MODELS.items():
        assert len(m["revision"]) == 40 and set(m["revision"]) <= set("0123456789abcdef"), role
        assert m["license"] and m["license_url"] and m["source"], role
