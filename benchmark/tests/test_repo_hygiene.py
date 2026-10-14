"""Repository hygiene tests that need no GPU and no network."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Anything that looks like a real credential. Placeholders (all x's, 'change-me') are fine.
REAL_LOOKING = [
    re.compile(r"hf_[A-Za-z0-9]{30,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"rpa_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----"),
]


def _is_placeholder(token: str) -> bool:
    body = token.split("_", 1)[-1]
    return set(body) <= {"x", "X"}


def test_env_example_has_only_placeholders():
    text = (ROOT / ".env.example").read_text()
    for pattern in REAL_LOOKING:
        for match in pattern.findall(text):
            assert _is_placeholder(match), f"{pattern.pattern} matched a non-placeholder value"


def test_env_example_documents_required_variables():
    text = (ROOT / ".env.example").read_text()
    for name in ("HF_TOKEN", "VLLM_API_KEY", "OPENAI_BASE_URL", "WORKSHOP_MODEL"):
        assert re.search(rf"^{name}=", text, re.M), f"{name} missing from .env.example"


def test_gitignore_protects_secrets():
    text = (ROOT / ".gitignore").read_text()
    for entry in (".env", "participants.yaml", "infra/keys/"):
        assert entry in text.splitlines(), f"{entry} must be gitignored"
