import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

spec = importlib.util.spec_from_file_location(
    "reset_state", Path(__file__).parent / "lib" / "reset_state.py"
)
rs = importlib.util.module_from_spec(spec)
sys.modules["reset_state"] = rs
spec.loader.exec_module(rs)

ROOT = Path(__file__).resolve().parents[1]


def make_root(tmp_path):
    root = tmp_path / "repo"
    state_dir = root / "workshop-states" / "02-vllm"
    (state_dir / "files" / "workshop-artifacts").mkdir(parents=True)
    (state_dir / "files" / "workshop-artifacts" / "report.md").write_text("starter\n")
    (root / "benchmark" / "results" / "ref-run").mkdir(parents=True)
    (root / "benchmark" / "results" / "ref-run" / "c001.json").write_text("{}")
    (state_dir / "state.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "02-vllm",
                "lab": "lab-02",
                "title": "A working server",
                "server": {"profile": "baseline"},
                "files": ["workshop-artifacts/report.md"],
                "references": ["benchmark/results/ref-run"],
            }
        )
    )
    return root


def test_soft_reset_creates_missing_files_and_refreshes_references(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    dest.mkdir()
    st = rs.load_states(root)["lab-02"]
    actions = rs.apply_state(st, root, dest, hard=False, backup_dir=tmp_path / "bk")
    assert (dest / "workshop-artifacts" / "report.md").read_text() == "starter\n"
    assert (dest / "benchmark" / "results" / "reference" / "ref-run" / "c001.json").exists()
    assert any(a.startswith("wrote") for a in actions)


def test_soft_reset_never_overwrites_the_participants_work(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    (dest / "workshop-artifacts").mkdir(parents=True)
    mine = dest / "workshop-artifacts" / "report.md"
    mine.write_text("MY HOURS OF WORK\n")
    actions = rs.apply_state(
        rs.load_states(root)["lab-02"], root, dest, hard=False, backup_dir=tmp_path / "bk"
    )
    assert mine.read_text() == "MY HOURS OF WORK\n"
    assert any("kept your" in a for a in actions) and not (tmp_path / "bk").exists()


def test_hard_reset_replaces_but_backs_up_first(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    (dest / "workshop-artifacts").mkdir(parents=True)
    mine = dest / "workshop-artifacts" / "report.md"
    mine.write_text("MY WORK\n")
    rs.apply_state(
        rs.load_states(root)["lab-02"], root, dest, hard=True, backup_dir=tmp_path / "bk"
    )
    assert mine.read_text() == "starter\n"
    assert (tmp_path / "bk" / "workshop-artifacts" / "report.md").read_text() == "MY WORK\n"


def test_dry_run_changes_nothing(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    dest.mkdir()
    rs.apply_state(
        rs.load_states(root)["lab-02"],
        root,
        dest,
        hard=True,
        backup_dir=tmp_path / "bk",
        dry_run=True,
    )
    assert not (dest / "workshop-artifacts").exists()


def test_missing_reference_data_is_reported_not_fatal(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    dest.mkdir()
    st = rs.load_states(root)["lab-02"]
    st["references"] = ["benchmark/results/nope"]
    assert any(
        "missing reference" in a
        for a in rs.apply_state(st, root, dest, hard=False, backup_dir=tmp_path / "bk")
    )


def test_a_state_that_lists_a_file_it_does_not_ship_is_an_error(tmp_path):
    root, dest = make_root(tmp_path), tmp_path / "home"
    st = rs.load_states(root)["lab-02"]
    st["files"] = ["workshop-artifacts/ghost.md"]
    with pytest.raises(FileNotFoundError):
        rs.apply_state(st, root, dest, hard=False, backup_dir=tmp_path / "bk")


def test_the_real_workshop_states_are_complete_once_they_exist():
    """Every shipped state must have a unique lab, ship every file it lists and name a real profile."""
    states = rs.load_states(ROOT)
    profiles = {p.stem for p in (ROOT / "config" / "vllm-profiles").glob("*.yaml")}
    for lab, st in states.items():
        for rel in st.get("files", []):
            assert (st["_dir"] / "files" / rel).is_file(), f"{lab}: {rel}"
        profile = st.get("server", {}).get("profile")
        assert profile is None or profile in profiles, f"{lab}: unknown profile {profile}"


def test_restore_takes_templates_from_the_trusted_copy_not_the_participants_copy(tmp_path):
    trusted, mine = tmp_path / "trusted", tmp_path / "mine"
    (trusted / "workshop-artifacts").mkdir(parents=True)
    (trusted / "workshop-artifacts" / "model-selection.md").write_text("PRISTINE TEMPLATE\n")
    sd = trusted / "workshop-states" / "01-baseline"
    sd.mkdir(parents=True)
    (sd / "state.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "01-baseline",
                "lab": "lab-01",
                "title": "Start",
                "restore": ["workshop-artifacts/model-selection.md"],
            }
        )
    )
    (mine / "workshop-artifacts").mkdir(parents=True)
    (mine / "workshop-artifacts" / "model-selection.md").write_text("MY EDITS\n")
    st = rs.load_states(trusted)["lab-01"]
    rs.apply_state(st, trusted, mine, hard=False, backup_dir=tmp_path / "bk")
    assert (
        mine / "workshop-artifacts" / "model-selection.md"
    ).read_text() == "MY EDITS\n"  # soft keeps work
    rs.apply_state(st, trusted, mine, hard=True, backup_dir=tmp_path / "bk")
    assert (mine / "workshop-artifacts" / "model-selection.md").read_text() == "PRISTINE TEMPLATE\n"
    assert (
        tmp_path / "bk" / "workshop-artifacts" / "model-selection.md"
    ).read_text() == "MY EDITS\n"
