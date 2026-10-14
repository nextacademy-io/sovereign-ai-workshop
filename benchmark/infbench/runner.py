"""Load generation: closed-loop (fixed concurrency) and open-loop (fixed arrival rate).

Closed loop: N workers each send a request, wait for it to finish, send the next.
  Concurrency is the controlled variable. Latency under overload shows up as slow
  responses, but the offered load backs off with the server (the classic caveat).
Open loop: requests arrive on a Poisson schedule regardless of how the server copes.
  Arrival rate is the controlled variable. Latency is measured from the scheduled
  arrival, so a client that falls behind does not hide the queueing it causes
  (avoids "coordinated omission").
"""

from __future__ import annotations

import asyncio
import random
import sys
import time
from dataclasses import dataclass

import httpx

from .client import RequestConfig, RequestResult, send_request
from .workload import Prompt


@dataclass
class RunOutcome:
    results: list[RequestResult]
    t_start: float
    t_end: float
    mode: str
    concurrency: int | None = None
    request_rate: float | None = None

    @property
    def duration_s(self) -> float:
        return max(self.t_end - self.t_start, 1e-9)


def _client(base_url: str, headers: dict[str, str], pool: int) -> httpx.AsyncClient:
    limits = httpx.Limits(max_connections=pool, max_keepalive_connections=pool)
    return httpx.AsyncClient(base_url=base_url, headers=headers, limits=limits, http2=False)


def _progress(done: int, total: int, started: float, quiet: bool) -> None:
    if quiet:
        return
    step = max(1, total // 10)
    if done % step == 0 or done == total:
        print(
            f"  {done}/{total} requests done ({time.perf_counter() - started:.0f}s)",
            file=sys.stderr,
        )


async def run_closed_loop(
    base_url: str,
    headers: dict[str, str],
    cfg: RequestConfig,
    prompts: list[Prompt],
    concurrency: int,
    duration_s: float | None = None,
    quiet: bool = False,
) -> RunOutcome:
    """Send all prompts using `concurrency` parallel workers.

    With `duration_s`, workers stop *starting* requests after that time (in-flight ones finish).
    """
    queue: asyncio.Queue[Prompt] = asyncio.Queue()
    for p in prompts:
        queue.put_nowait(p)
    results: list[RequestResult] = []
    total = len(prompts)

    async with _client(base_url, headers, concurrency + 8) as client:
        t_start = time.perf_counter()
        deadline = t_start + duration_s if duration_s else None

        async def worker() -> None:
            while True:
                if deadline is not None and time.perf_counter() >= deadline:
                    return
                try:
                    prompt = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                results.append(await send_request(client, cfg, prompt))
                _progress(len(results), total, t_start, quiet)

        await asyncio.gather(*(worker() for _ in range(concurrency)))
        t_end = time.perf_counter()
    return RunOutcome(results, t_start, t_end, "closed", concurrency=concurrency)


async def run_open_loop(
    base_url: str,
    headers: dict[str, str],
    cfg: RequestConfig,
    prompts: list[Prompt],
    request_rate: float,
    max_inflight: int | None = None,
    seed: int = 0,
    quiet: bool = False,
) -> RunOutcome:
    """Send prompts with exponential inter-arrival times (a Poisson process)."""
    rng = random.Random(seed)
    gate = asyncio.Semaphore(max_inflight) if max_inflight else None
    results: list[RequestResult] = []
    total = len(prompts)

    async with _client(base_url, headers, max_inflight or 1024) as client:
        t_start = time.perf_counter()

        async def fire(prompt: Prompt, at: float) -> None:
            delay = at - time.perf_counter()
            if delay > 0:
                await asyncio.sleep(delay)
            if gate:
                async with gate:
                    results.append(await send_request(client, cfg, prompt, scheduled_at=at))
            else:
                results.append(await send_request(client, cfg, prompt, scheduled_at=at))
            _progress(len(results), total, t_start, quiet)

        arrival = t_start
        tasks = []
        for prompt in prompts:
            arrival += rng.expovariate(request_rate)
            tasks.append(asyncio.create_task(fire(prompt, arrival)))
        await asyncio.gather(*tasks)
        t_end = time.perf_counter()
    return RunOutcome(results, t_start, t_end, "open", request_rate=request_rate)
