"""Workload definitions and prompt construction.

A workload fixes what each request looks like: input length, output length, whether a
prefix is shared between requests, and which prompt style is used. Everything is
seeded, so two runs with the same workload send identical prompts.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import yaml

from .corpus import INSTRUCTIONS, SENTENCES

WORKLOAD_DIR = Path(__file__).resolve().parent.parent / "workloads"


@dataclass(frozen=True)
class Workload:
    name: str = "custom"
    description: str = ""
    input_tokens: int = 1000
    output_tokens: int = 200
    # Tokens shared by every request (system prompt, retrieved document). 0 disables sharing.
    shared_prefix_tokens: int = 0
    style: str = "chat"  # key of corpus.INSTRUCTIONS
    # ids: send exact token ids (needs /tokenize); text: send text, size approximate.
    prompt_mode: str = "auto"
    # None = a fresh random seed per invocation. A fixed default would make a second run of the same command
    # send the same prompts, which the server's prefix cache answers almost for free (see benchmark/README.md).
    seed: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "shared_prefix_tokens": self.shared_prefix_tokens,
            "style": self.style,
            "prompt_mode": self.prompt_mode,
            "seed": self.seed,
        }


def load_workload(name_or_path: str) -> Workload:
    """Load benchmark/workloads/<name>.yaml or an explicit path."""
    path = Path(name_or_path)
    if not path.exists():
        path = WORKLOAD_DIR / f"{name_or_path}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"workload '{name_or_path}' not found (looked in {WORKLOAD_DIR})")
    raw = yaml.safe_load(path.read_text()) or {}
    known = {f for f in Workload.__dataclass_fields__ if f != "extra"}
    return Workload(**{k: v for k, v in raw.items() if k in known})


@dataclass(frozen=True)
class Prompt:
    """One request payload. Exactly one of `text` / `token_ids` is set."""

    index: int
    text: str | None = None
    token_ids: list[int] | None = None
    approx_tokens: int = 0

    @property
    def payload(self) -> str | list[int]:
        return self.token_ids if self.token_ids is not None else (self.text or "")


class Tokenizer:
    """Tokenisation through the server's own /tokenize and /detokenize endpoints.

    The server is the only party that must agree with itself about token counts, so we
    do not need a local tokenizer (or the transformers dependency).
    """

    def __init__(self, base_url: str, model: str, headers: dict[str, str], timeout: float = 30.0):
        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)
        self._model = model

    def available(self) -> bool:
        try:
            r = self._client.post("/tokenize", json={"model": self._model, "prompt": "ping"})
            return r.status_code == 200 and "tokens" in r.json()
        except (httpx.HTTPError, ValueError):
            return False

    def encode(self, text: str) -> list[int]:
        r = self._client.post(
            "/tokenize", json={"model": self._model, "prompt": text, "add_special_tokens": False}
        )
        r.raise_for_status()
        return list(r.json()["tokens"])

    def close(self) -> None:
        self._client.close()


def _compose_text(rng: random.Random, target_tokens: int, header: str) -> str:
    """Compose prose of roughly `target_tokens` tokens (about 1.35 tokens per word)."""
    target_words = max(8, int(target_tokens / 1.35))
    words = len(header.split())
    parts = [header]
    while words < target_words:
        sentence = rng.choice(SENTENCES)
        parts.append(sentence)
        words += len(sentence.split())
    return " ".join(parts)


def build_prompts(
    workload: Workload,
    count: int,
    tokenizer: Tokenizer | None,
) -> list[Prompt]:
    """Build `count` prompts. Every prompt differs from the first token on, except for the
    shared prefix, so accidental prefix-cache hits cannot flatter the results."""
    mode = workload.prompt_mode
    if mode == "auto":
        mode = "ids" if tokenizer is not None else "text"
    if mode == "ids" and tokenizer is None:
        raise RuntimeError("prompt_mode 'ids' needs the server's /tokenize endpoint")

    seed = workload.seed if workload.seed is not None else 0
    instruction = INSTRUCTIONS.get(workload.style, INSTRUCTIONS["chat"])
    prefix_rng = random.Random(f"{seed}-prefix")
    shared_text = (
        _compose_text(prefix_rng, workload.shared_prefix_tokens, f"{instruction}\n\nShared notes:")
        if workload.shared_prefix_tokens
        else ""
    )
    shared_ids: list[int] = []
    if mode == "ids" and shared_text:
        shared_ids = tokenizer.encode(shared_text)  # type: ignore[union-attr]
        # The words-to-tokens estimate can undershoot; extend until the prefix is long enough.
        while len(shared_ids) < workload.shared_prefix_tokens:
            shared_ids = shared_ids + tokenizer.encode(" " + prefix_rng.choice(SENTENCES))  # type: ignore[union-attr]
        shared_ids = shared_ids[: workload.shared_prefix_tokens]

    unique_target = max(1, workload.input_tokens - workload.shared_prefix_tokens)
    prompts: list[Prompt] = []
    for i in range(count):
        rng = random.Random(f"{seed}-{i}")
        # A random leading line makes every request unique from its first token.
        nonce = f"Request {rng.getrandbits(48):012x}."
        header = nonce if shared_text else f"{instruction}\n\n{nonce}"
        body = _compose_text(rng, unique_target, header)
        if mode == "text":
            text = f"{shared_text}\n\n{body}" if shared_text else body
            prompts.append(Prompt(index=i, text=text, approx_tokens=workload.input_tokens))
            continue
        ids = tokenizer.encode(body)  # type: ignore[union-attr]
        # Pad by repetition in the rare case the estimate was short, then cut to the exact size.
        while len(ids) < unique_target:
            ids = ids + tokenizer.encode(rng.choice(SENTENCES))  # type: ignore[union-attr]
        full = shared_ids + ids[:unique_target]
        prompts.append(Prompt(index=i, token_ids=full, approx_tokens=len(full)))
    return prompts
