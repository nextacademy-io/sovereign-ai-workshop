import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "promote_reference", Path(__file__).resolve().parents[1] / "scripts" / "promote_reference.py"
)
promote_reference = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promote_reference)


def test_auxiliary_documents_receive_the_configuration_of_a_result(tmp_path):
    session = tmp_path / "session"
    (session / "baseline" / "single-stream").mkdir(parents=True)
    config = {"model": "m", "date": "2000-01-01T00:00:00+00:00"}
    (session / "baseline" / "single-stream" / "c001.json").write_text(
        json.dumps({"configuration": config, "requests": 3})
    )
    (session / "baseline" / "kv-formula-check.json").write_text(json.dumps({"ratio": 0.9999}))
    (session / "baseline" / "runner.log").write_text("x")

    dest = tmp_path / "reference"
    written = promote_reference.promote(session, ["baseline"], dest)

    check = json.loads((dest / "baseline" / "kv-formula-check.json").read_text())
    assert check["configuration"] == config and check["ratio"] == 0.9999
    assert "derived_from" in check
    assert (dest / "baseline" / "single-stream" / "c001.json").exists()
    assert not any(p.suffix == ".log" for p in written)
