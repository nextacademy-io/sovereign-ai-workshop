"""Tests for the profile renderer, run against the real profiles in config/vllm-profiles."""

import json
import re
from pathlib import Path

import pytest
import render_profile as rp
import yaml

PROFILES = Path(__file__).resolve().parents[2] / "config" / "vllm-profiles"
SHA = "b968826d9c46dd6066d109eabc6255188de91218"


def startable():
    return [
        p.stem
        for p in PROFILES.glob("*.yaml")
        if not rp.load_profile(p.stem, PROFILES).get("abstract")
    ]


def test_baseline_merges_base_and_is_loopback_only():
    config, summary = rp.render("baseline", PROFILES)
    assert config["model"] == "Qwen/Qwen3-8B" and config["host"] == "127.0.0.1"
    assert config["gpu-memory-utilization"] == 0.80 and config["enable-mfu-metrics"] is True
    assert "extends" not in config and "description" not in config
    assert summary["model_revision"] == SHA and summary["role"] == "generation"
    assert (
        "--generation-config vllm" in summary["args"] and "--enable-mfu-metrics" in summary["args"]
    )


def test_child_overrides_parent_and_chain_is_resolved():
    config, _ = rp.render("kv-constrained-fp8kv", PROFILES)
    assert config["kv-cache-memory-bytes"] == "4G" and config["kv-cache-dtype"] == "fp8"
    assert config["model"] == "Qwen/Qwen3-8B"


def test_fp8_profile_uses_the_fp8_checkpoint_under_the_same_served_name():
    config, _ = rp.render("fp8", PROFILES)
    assert config["model"] == "Qwen/Qwen3-8B-FP8"
    assert (
        config["served-model-name"] == "Qwen/Qwen3-8B"
    )  # clients do not change when the checkpoint does


def test_nested_speculative_config_survives_as_mapping():
    config, summary = rp.render("spec-ngram", PROFILES)
    assert config["speculative-config"]["method"] == "ngram"
    assert "--speculative-config '" in summary["args"]


def test_booleans_render_as_flags_and_negations():
    assert "--no-enable-prefix-caching" in rp.render("no-prefix-cache", PROFILES)[1]["args"]


def test_set_allowlist_and_value_validation():
    config, summary = rp.render(
        "baseline", PROFILES, ["max-num-seqs=8", "enable_prefix_caching=false"]
    )
    assert config["max-num-seqs"] == 8 and config["no-enable-prefix-caching"] is True
    assert summary["overrides"] == ["max-num-seqs=8", "enable_prefix_caching=false"]
    for bad in (
        "api-key=abc",
        "host=0.0.0.0",
        "trust-remote-code=true",
        "max-num-seqs",
        "model=x/y",
    ):
        with pytest.raises(rp.ProfileError):
            rp.render("baseline", PROFILES, [bad])
    with pytest.raises(rp.ProfileError):
        rp.render("baseline", PROFILES, ["max-model-len=1; rm -rf /"])


def test_abstract_unknown_and_malformed_names_are_rejected():
    for name in ("base", "nope", "../etc/passwd", "Baseline", "a b"):
        with pytest.raises(rp.ProfileError):
            rp.render(name, PROFILES)


def test_unpinned_revision_is_rejected(tmp_path):
    (tmp_path / "p.yaml").write_text("model: a/b\nrevision: main\nhost: 127.0.0.1\nport: 8000\n")
    with pytest.raises(rp.ProfileError, match="40-character"):
        rp.render("p", tmp_path)


def test_public_bind_and_odd_ports_are_rejected(tmp_path):
    base = f"model: a/b\nrevision: {SHA}\n"
    (tmp_path / "pub.yaml").write_text(base + "host: 0.0.0.0\nport: 8000\n")
    (tmp_path / "port.yaml").write_text(base + "host: 127.0.0.1\nport: 22\n")
    (tmp_path / "key.yaml").write_text(base + "host: 127.0.0.1\nport: 8000\napi-key: hunter2\n")
    for name in ("pub", "port", "key"):
        with pytest.raises(rp.ProfileError):
            rp.render(name, tmp_path)


def test_extends_cycle_is_detected(tmp_path):
    (tmp_path / "a.yaml").write_text("extends: b\n")
    (tmp_path / "b.yaml").write_text("extends: a\n")
    with pytest.raises(rp.ProfileError, match="too deep"):
        rp.load_profile("a", tmp_path)


def test_cli_writes_a_config_vllm_can_read_and_prints_a_json_summary(tmp_path, capsys):
    out = tmp_path / "active.yaml"
    assert rp.main.__module__  # smoke: main is importable
    import sys

    sys.argv = ["render-profile", "baseline", "--dir", str(PROFILES), "--out", str(out)]
    assert rp.main() == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["profile"] == "baseline"
    written = yaml.safe_load(out.read_text())
    assert written["port"] == 8000 and "description" not in written


def test_every_shipped_profile_renders_or_is_pending_a_pin():
    """Profiles must be valid. Only the revision pin of not-yet-validated models may be missing."""
    for name in startable():
        try:
            rp.render(name, PROFILES)
        except rp.ProfileError as exc:
            assert "40-character" in str(exc) and re.search(r"TBD", str(exc)), f"{name}: {exc}"


def test_container_mode_binds_inside_the_container_namespace_only_when_asked():
    host_cfg, _ = rp.render("baseline", PROFILES)
    box_cfg, summary = rp.render("baseline", PROFILES, container=True)
    assert host_cfg["host"] == "127.0.0.1" and box_cfg["host"] == "0.0.0.0"  # noqa: S104
    assert "--host 0.0.0.0" in summary["args"]
    # Everything else is identical: the same profile drives the pod and the container.
    assert {k: v for k, v in box_cfg.items() if k != "host"} == {
        k: v for k, v in host_cfg.items() if k != "host"
    }


def test_false_booleans_become_explicit_negative_flags_because_vllm_drops_false_in_config_files():
    """Measured on the workshop GPU: `enable-prefix-caching: false` in a config file left prefix caching ON."""
    config, summary = rp.render("no-prefix-cache", PROFILES)
    assert "enable-prefix-caching" not in config and config["no-enable-prefix-caching"] is True
    assert not any(v is False for v in config.values())
    assert summary["args"].count("--no-enable-prefix-caching") == 1
