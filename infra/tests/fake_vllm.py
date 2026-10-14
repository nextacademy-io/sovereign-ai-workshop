#!/usr/bin/env python3
"""A stand-in for `vllm serve --config FILE`, to test wsctl without a GPU.

It reads the rendered profile (port, served model), prints the startup log lines of vLLM v0.31.0 that
infra/pod/server-info.py parses, then serves /health, /version, /v1/models and /metrics. Like the real
server it ignores nothing silently: an unknown subcommand exits with an error.
"""

import json
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml


def main() -> int:
    if len(sys.argv) < 4 or sys.argv[1] != "serve" or sys.argv[2] != "--config":
        print("fake vllm: usage: vllm serve --config FILE", file=sys.stderr)
        return 2
    cfg = yaml.safe_load(open(sys.argv[3]))
    port, name = cfg["port"], cfg.get("served-model-name", cfg["model"])
    if (
        cfg.get("max-num-seqs") == 666
    ):  # simulated startup failure (like a rejected engine argument)
        print(
            "vllm serve: error: argument --max-num-seqs: simulated failure",
            file=sys.stderr,
            flush=True,
        )
        return 3
    print("INFO Model loading took 15.27 GiB memory and 5.669437 seconds", flush=True)
    print("INFO Available KV cache memory: 58.14 GiB", flush=True)
    print(
        "INFO GPU KV cache size: 423,328 tokens, Maximum concurrency for 32,768 tokens per request: 12.92x",
        flush=True,
    )
    time.sleep(float(cfg.get("_fake_startup_seconds", 1.0)))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, body: bytes, ctype="application/json"):
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            if self.path == "/health":
                self._send(b"", "text/plain")
            elif self.path == "/version":
                self._send(json.dumps({"version": "0.31.0-fake"}).encode())
            elif self.path == "/v1/models":
                self._send(json.dumps({"data": [{"id": name}]}).encode())
            elif self.path == "/metrics":
                self._send(b"vllm:num_requests_running 0\n", "text/plain")
            else:
                self.send_error(404)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown).start())
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
