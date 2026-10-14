#!/usr/bin/env python3
"""A tiny GPU metrics exporter that speaks DCGM's metric names.

Pods cannot run dcgm-exporter (it needs privileges and Docker), but NVML, the library behind
nvidia-smi, works anywhere the driver is visible. This exporter publishes the DCGM fields the
workshop dashboard uses, so the very same dashboard works with the real dcgm-exporter in
monitoring/docker-compose.yml.

    python3 monitoring/gpu-exporter/exporter.py --port 9400 --bind 127.0.0.1

Metrics (names and units follow dcgm-exporter's default counters):
    DCGM_FI_DEV_GPU_UTIL        percent of time a kernel was running (NOT efficiency)
    DCGM_FI_DEV_MEM_COPY_UTIL   percent of time the memory interface was busy
    DCGM_FI_DEV_FB_USED         framebuffer memory used, MiB
    DCGM_FI_DEV_FB_FREE         framebuffer memory free, MiB
    DCGM_FI_DEV_POWER_USAGE     watts
    DCGM_FI_DEV_GPU_TEMP        degrees Celsius
    DCGM_FI_DEV_SM_CLOCK        MHz
    DCGM_FI_DEV_MEM_CLOCK       MHz
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

METRICS = (
    ("DCGM_FI_DEV_GPU_UTIL", "GPU utilization (percent of time any kernel was running)", "gauge"),
    ("DCGM_FI_DEV_MEM_COPY_UTIL", "Memory interface utilization (percent)", "gauge"),
    ("DCGM_FI_DEV_FB_USED", "Framebuffer memory used (MiB)", "gauge"),
    ("DCGM_FI_DEV_FB_FREE", "Framebuffer memory free (MiB)", "gauge"),
    ("DCGM_FI_DEV_POWER_USAGE", "Power usage (W)", "gauge"),
    ("DCGM_FI_DEV_GPU_TEMP", "GPU temperature (C)", "gauge"),
    ("DCGM_FI_DEV_SM_CLOCK", "SM clock (MHz)", "gauge"),
    ("DCGM_FI_DEV_MEM_CLOCK", "Memory clock (MHz)", "gauge"),
)
MIB = 1024 * 1024


def collect(nvml) -> list[dict]:
    """One sample per GPU. `nvml` is the pynvml module (injected so tests can fake it)."""
    out = []
    for i in range(nvml.nvmlDeviceGetCount()):
        h = nvml.nvmlDeviceGetHandleByIndex(i)
        name = nvml.nvmlDeviceGetName(h)
        name = name.decode() if isinstance(name, bytes) else name
        util = nvml.nvmlDeviceGetUtilizationRates(h)
        mem = nvml.nvmlDeviceGetMemoryInfo(h)
        out.append(
            {
                "gpu": str(i),
                "modelName": name,
                "DCGM_FI_DEV_GPU_UTIL": util.gpu,
                "DCGM_FI_DEV_MEM_COPY_UTIL": util.memory,
                "DCGM_FI_DEV_FB_USED": mem.used / MIB,
                "DCGM_FI_DEV_FB_FREE": mem.free / MIB,
                "DCGM_FI_DEV_POWER_USAGE": nvml.nvmlDeviceGetPowerUsage(h) / 1000.0,
                "DCGM_FI_DEV_GPU_TEMP": nvml.nvmlDeviceGetTemperature(h, nvml.NVML_TEMPERATURE_GPU),
                "DCGM_FI_DEV_SM_CLOCK": nvml.nvmlDeviceGetClockInfo(h, nvml.NVML_CLOCK_SM),
                "DCGM_FI_DEV_MEM_CLOCK": nvml.nvmlDeviceGetClockInfo(h, nvml.NVML_CLOCK_MEM),
            }
        )
    return out


def render(samples: list[dict]) -> str:
    lines: list[str] = []
    for name, help_text, kind in METRICS:
        lines += [f"# HELP {name} {help_text}", f"# TYPE {name} {kind}"]
        for s in samples:
            labels = f'gpu="{s["gpu"]}",modelName="{s["modelName"]}"'
            lines.append(f"{name}{{{labels}}} {s[name]:.3f}")
    return "\n".join(lines) + "\n"


def make_handler(nvml):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the pod log quiet
            pass

        def do_GET(self):  # noqa: N802
            if self.path != "/metrics":
                self.send_response(404)
                self.end_headers()
                return
            try:
                body = render(collect(nvml)).encode()
                self.send_response(200)
            except Exception as exc:  # noqa: BLE001 - report NVML trouble to the scraper instead of dying
                body = f"# nvml error: {exc}\n".encode()
                self.send_response(500)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--port", type=int, default=9400)
    ap.add_argument("--bind", default="127.0.0.1")
    a = ap.parse_args()
    import pynvml  # provided by the nvidia-ml-py package, which vLLM depends on

    pynvml.nvmlInit()
    server = ThreadingHTTPServer((a.bind, a.port), make_handler(pynvml))
    print(f"gpu exporter on http://{a.bind}:{a.port}/metrics", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
