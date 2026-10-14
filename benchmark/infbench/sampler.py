"""Background samplers: GPU state (nvidia-smi) and the server's Prometheus /metrics.

Both run in threads while the load is being generated, so the report can say not only
what the user experienced (TTFT, latency) but also what the machine was doing.

A word of caution that the workshop repeats on purpose: `utilization.gpu` is the share of
sample periods in which *any* kernel was running. It says nothing about how efficiently the
SMs or the memory system were used. A GPU can show 100 % while moving little data.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field

import httpx

from .stats import summarize

GPU_FIELDS = ("utilization.gpu", "memory.used", "power.draw", "temperature.gpu", "clocks.sm")

# Gauges we chart over time; counters we diff between start and end of the run.
GAUGES = {
    "num_requests_running": ("vllm:num_requests_running",),
    "num_requests_waiting": ("vllm:num_requests_waiting",),
    "kv_cache_usage_perc": ("vllm:kv_cache_usage_perc", "vllm:gpu_cache_usage_perc"),
}
COUNTERS = {
    "prompt_tokens": ("vllm:prompt_tokens_total", "vllm:prompt_tokens"),
    "generation_tokens": ("vllm:generation_tokens_total", "vllm:generation_tokens"),
    "prefix_cache_queries": ("vllm:prefix_cache_queries_total", "vllm:prefix_cache_queries"),
    "prefix_cache_hits": ("vllm:prefix_cache_hits_total", "vllm:prefix_cache_hits"),
    "preemptions": ("vllm:num_preemptions_total", "vllm:num_preemptions"),
    "requests_success": ("vllm:request_success_total",),
}

_SAMPLE_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+([-+0-9.eE]+|NaN|[+-]Inf)\s*$")


def parse_prometheus(text: str) -> dict[str, float]:
    """Sum every sample of a metric over its label sets. Histogram buckets are skipped."""
    out: dict[str, float] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = _SAMPLE_RE.match(line)
        if not m:
            continue
        name, _labels, raw = m.groups()
        if name.endswith("_bucket") or raw in ("NaN", "+Inf", "-Inf"):
            continue
        out[name] = out.get(name, 0.0) + float(raw)
    return out


def _first(values: dict[str, float], names: tuple[str, ...]) -> float | None:
    for n in names:
        if n in values:
            return values[n]
    return None


@dataclass
class GpuSampler:
    interval_s: float = 1.0
    samples: list[dict[str, float]] = field(default_factory=list)
    error: str | None = None
    _stop: threading.Event = field(default_factory=threading.Event, repr=False)
    _thread: threading.Thread | None = field(default=None, repr=False)

    @staticmethod
    def available() -> bool:
        return shutil.which("nvidia-smi") is not None

    def _query(self) -> list[dict[str, float]]:
        cmd = [
            "nvidia-smi",
            f"--query-gpu=index,{','.join(GPU_FIELDS)}",
            "--format=csv,noheader,nounits",
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True).stdout
        rows = []
        for line in out.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            row: dict[str, float] = {"index": float(parts[0])}
            for name, value in zip(GPU_FIELDS, parts[1:], strict=False):
                try:
                    row[name] = float(value)
                except ValueError:  # '[N/A]'
                    continue
            rows.append(row)
        return rows

    def _loop(self) -> None:
        while not self._stop.is_set():
            t0 = time.perf_counter()
            try:
                for row in self._query():
                    row["t"] = t0
                    self.samples.append(row)
            except (subprocess.SubprocessError, OSError, ValueError) as exc:
                self.error = str(exc)
                return
            self._stop.wait(max(0.0, self.interval_s - (time.perf_counter() - t0)))

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="gpu-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> dict | None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        if not self.samples:
            return None
        per_gpu: dict[int, list[dict[str, float]]] = {}
        for s in self.samples:
            per_gpu.setdefault(int(s["index"]), []).append(s)

        def col(name: str) -> list[float]:
            return [s[name] for s in self.samples if name in s]

        return {
            "note": "utilization.gpu = share of time any kernel was running, not efficiency",
            "interval_s": self.interval_s,
            "samples": len(self.samples),
            "gpus": len(per_gpu),
            "utilization_pct": summarize(col("utilization.gpu"), ndigits=1),
            "memory_used_mib": summarize(col("memory.used"), ndigits=0),
            "power_w": summarize(col("power.draw"), ndigits=1),
            "temperature_c": summarize(col("temperature.gpu"), ndigits=0),
            "sm_clock_mhz": summarize(col("clocks.sm"), ndigits=0),
        }


@dataclass
class MetricsSampler:
    """Polls the server's /metrics while the load runs."""

    base_url: str
    headers: dict[str, str]
    interval_s: float = 1.0
    series: list[dict[str, float]] = field(default_factory=list)
    first: dict[str, float] = field(default_factory=dict)
    last: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    _stop: threading.Event = field(default_factory=threading.Event, repr=False)
    _thread: threading.Thread | None = field(default=None, repr=False)

    def _scrape(self, client: httpx.Client) -> dict[str, float]:
        resp = client.get("/metrics")
        resp.raise_for_status()
        return parse_prometheus(resp.text)

    def _loop(self) -> None:
        with httpx.Client(base_url=self.base_url, headers=self.headers, timeout=5.0) as client:
            while not self._stop.is_set():
                t0 = time.perf_counter()
                try:
                    values = self._scrape(client)
                except (httpx.HTTPError, ValueError) as exc:
                    self.error = f"{type(exc).__name__}: {exc}"
                    return
                if not self.first:
                    self.first = values
                self.last = values
                point = {"t": t0}
                for key, names in GAUGES.items():
                    v = _first(values, names)
                    if v is not None:
                        point[key] = v
                self.series.append(point)
                self._stop.wait(max(0.0, self.interval_s - (time.perf_counter() - t0)))

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="metrics-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> dict | None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        # One last scrape so the counters cover the whole run, even a run shorter than the interval.
        if self.first:
            try:
                with httpx.Client(
                    base_url=self.base_url, headers=self.headers, timeout=5.0
                ) as client:
                    self.last = self._scrape(client)
            except (httpx.HTTPError, ValueError):
                pass
        if not self.series:
            return None
        gauges = {}
        for key in GAUGES:
            col = [p[key] for p in self.series if key in p]
            if col:
                gauges[key] = {"mean": round(sum(col) / len(col), 3), "max": max(col)}
        deltas = {}
        for key, names in COUNTERS.items():
            a, b = _first(self.first, names), _first(self.last, names)
            if a is not None and b is not None:
                deltas[key] = b - a
        queries = deltas.get("prefix_cache_queries")
        hits = deltas.get("prefix_cache_hits")
        return {
            "interval_s": self.interval_s,
            "samples": len(self.series),
            "gauges": gauges,
            "counters_delta": deltas,
            "prefix_cache_hit_rate": round(hits / queries, 4)
            if queries and hits is not None
            else None,
        }
