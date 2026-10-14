"""Settings shared by the example applications.

Every app talks to an OpenAI-compatible server. Three environment variables decide which:

  OPENAI_BASE_URL   default http://127.0.0.1:8000/v1   (an SSH tunnel to your group's GPU host)
  OPENAI_API_KEY    the shared key for the workshop server
  WORKSHOP_MODEL    default Qwen/Qwen3-8B

Nothing here is specific to vLLM, which is the point: the application layer only sees an API.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field

from openai import OpenAI

DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
DEFAULT_MODEL = "Qwen/Qwen3-8B"


def base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)


def model_name() -> str:
    return os.environ.get("WORKSHOP_MODEL", DEFAULT_MODEL)


def make_client(url: str | None = None, api_key: str | None = None) -> OpenAI:
    key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY")
    if not key:
        # The OpenAI client refuses an empty key even when the server does not check it.
        print("note: OPENAI_API_KEY is not set; sending a placeholder key", file=sys.stderr)
        key = "not-set"
    return OpenAI(base_url=url or base_url(), api_key=key, timeout=300.0, max_retries=0)


@dataclass
class Usage:
    """Token and time accounting across several model calls (used by the agent demo)."""

    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0
    per_call: list[dict] = field(default_factory=list)

    def add(self, prompt: int, completion: int, seconds: float, label: str = "") -> None:
        self.calls += 1
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.seconds += seconds
        self.per_call.append(
            {
                "label": label,
                "prompt": prompt,
                "completion": completion,
                "seconds": round(seconds, 3),
            }
        )


class Stopwatch:
    def __enter__(self) -> Stopwatch:
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed = time.perf_counter() - self.start
