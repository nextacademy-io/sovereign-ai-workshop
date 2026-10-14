"""Streaming request execution against an OpenAI-compatible server.

Timing definitions (see docs/METRICS.md):
  TTFT     send of the request -> arrival of the first chunk that carries text
  ITL      gap between two consecutive text-carrying chunks
  latency  send of the request -> end of the stream
  TPOT     (latency - TTFT) / (output_tokens - 1)
Output token counts come from the server's `usage` block, not from counting chunks.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import httpx

from .workload import Prompt


@dataclass
class RequestResult:
    index: int
    ok: bool
    error: str | None = None
    status: int | None = None
    scheduled_at: float = 0.0  # perf_counter time the request was supposed to start
    started_at: float = 0.0  # perf_counter time the request was actually sent
    finished_at: float = 0.0
    ttft_s: float | None = None
    latency_s: float | None = None
    itl_s: list[float] = field(default_factory=list)
    prompt_tokens: int | None = None
    completion_tokens: int | None = None

    @property
    def tpot_s(self) -> float | None:
        if self.latency_s is None or self.ttft_s is None or not self.completion_tokens:
            return None
        if self.completion_tokens < 2:
            return None
        return (self.latency_s - self.ttft_s) / (self.completion_tokens - 1)

    @property
    def output_tps(self) -> float | None:
        """Tokens per second as the user sees them after the first token arrived."""
        tpot = self.tpot_s
        return (1.0 / tpot) if tpot and tpot > 0 else None


@dataclass(frozen=True)
class RequestConfig:
    model: str
    endpoint_type: str = "completions"  # completions | chat
    max_tokens: int = 200
    temperature: float = 0.0
    # vLLM extensions: force the output length so runs are comparable. Disable for other servers.
    engine_extensions: bool = True
    timeout_s: float = 600.0


def _build_payload(cfg: RequestConfig, prompt: Prompt) -> tuple[str, dict]:
    body: dict = {
        "model": cfg.model,
        "max_tokens": cfg.max_tokens,
        "temperature": cfg.temperature,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if cfg.engine_extensions:
        body["ignore_eos"] = True
        body["min_tokens"] = cfg.max_tokens
    if cfg.endpoint_type == "chat":
        text = prompt.text if prompt.text is not None else ""
        body["messages"] = [{"role": "user", "content": text}]
        # Qwen3-style models think by default; thinking would change the output length profile.
        body["chat_template_kwargs"] = {"enable_thinking": False}
        return "/v1/chat/completions", body
    body["prompt"] = prompt.payload
    return "/v1/completions", body


def _chunk_text(chunk: dict, endpoint_type: str) -> str:
    choices = chunk.get("choices") or []
    if not choices:
        return ""
    choice = choices[0]
    if endpoint_type == "chat":
        delta = choice.get("delta") or {}
        return (
            (delta.get("content") or "")
            + (delta.get("reasoning_content") or "")
            + (delta.get("reasoning") or "")
        )
    return choice.get("text") or ""


async def send_request(
    client: httpx.AsyncClient,
    cfg: RequestConfig,
    prompt: Prompt,
    scheduled_at: float | None = None,
) -> RequestResult:
    path, body = _build_payload(cfg, prompt)
    started = time.perf_counter()
    res = RequestResult(
        index=prompt.index, ok=False, scheduled_at=scheduled_at or started, started_at=started
    )
    last_text_at: float | None = None
    try:
        async with client.stream("POST", path, json=body, timeout=cfg.timeout_s) as resp:
            res.status = resp.status_code
            if resp.status_code != 200:
                payload = (await resp.aread()).decode("utf-8", "replace")[:300]
                res.error = f"HTTP {resp.status_code}: {payload}"
                return res
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                now = time.perf_counter()
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if chunk.get("usage"):
                    res.prompt_tokens = chunk["usage"].get("prompt_tokens")
                    res.completion_tokens = chunk["usage"].get("completion_tokens")
                if _chunk_text(chunk, cfg.endpoint_type):
                    if res.ttft_s is None:
                        res.ttft_s = now - res.scheduled_at
                    elif last_text_at is not None:
                        res.itl_s.append(now - last_text_at)
                    last_text_at = now
        res.finished_at = time.perf_counter()
        res.latency_s = res.finished_at - res.scheduled_at
        if res.ttft_s is None:
            res.error = "stream ended without any text"
            return res
        res.ok = True
        return res
    except httpx.HTTPError as exc:
        res.error = f"{type(exc).__name__}: {exc}"
        res.finished_at = time.perf_counter()
        return res
