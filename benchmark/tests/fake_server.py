"""A tiny OpenAI-compatible server with *known* timing, used to test the harness.

Because every delay is configured, tests can assert exact expectations: with a 50 ms
time to first token and 10 ms between tokens, measured TTFT must be about 50 ms and
the per-request output rate about 100 tokens per second.

`capacity` models a server that can work on N requests at once; further requests wait.
That makes queueing visible: with capacity 2 and concurrency 8, TTFT grows.
"""

from __future__ import annotations

import json
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FakeLLMServer:
    def __init__(
        self,
        ttft_s: float = 0.05,
        itl_s: float = 0.01,
        capacity: int = 1000,
        fail_every: int = 0,
        api_key: str | None = None,
        tokenize: bool = True,
    ):
        self.ttft_s, self.itl_s = ttft_s, itl_s
        self.fail_every = fail_every
        self.api_key = api_key
        self.tokenize_enabled = tokenize
        self._slots = threading.Semaphore(capacity)
        self._lock = threading.Lock()
        self.request_count = 0
        self.inflight = 0
        self.max_inflight = 0
        self.prompt_lengths: list[int] = []
        self.prompts_seen: list[object] = []
        self.reset_calls = 0
        self.completion_tokens_total = 0
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def __enter__(self) -> FakeLLMServer:
        self.thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    # ------------------------------------------------------------------ handler
    def _handler(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):  # silence
                pass

            def _authorized(self) -> bool:
                if outer.api_key is None:
                    return True
                return self.headers.get("Authorization") == f"Bearer {outer.api_key}"

            def _json(self, status: int, payload: dict) -> None:
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _text(self, text: str) -> None:
                data = text.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):  # noqa: N802
                if not self._authorized():
                    return self._json(401, {"error": "unauthorized"})
                if self.path == "/v1/models":
                    return self._json(200, {"data": [{"id": "fake-model"}]})
                if self.path == "/version":
                    return self._json(200, {"version": "0.0.0-fake"})
                if self.path == "/metrics":
                    return self._text(
                        "# TYPE vllm:num_requests_running gauge\n"
                        f'vllm:num_requests_running{{engine="0"}} {outer.inflight}\n'
                        'vllm:num_requests_waiting{engine="0"} 0\n'
                        'vllm:kv_cache_usage_perc{engine="0"} 0.25\n'
                        f'vllm:generation_tokens_total{{engine="0"}} {outer.completion_tokens_total}\n'
                        f'vllm:prefix_cache_queries_total{{engine="0"}} {outer.request_count * 100}\n'
                        f'vllm:prefix_cache_hits_total{{engine="0"}} {outer.request_count * 25}\n'
                        'vllm:time_to_first_token_seconds_bucket{le="0.1"} 5\n'
                    )
                self._json(404, {"error": "not found"})

            def do_POST(self):  # noqa: N802
                if not self._authorized():
                    return self._json(401, {"error": "unauthorized"})
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/tokenize":
                    if not outer.tokenize_enabled:
                        return self._json(404, {"error": "no tokenize"})
                    words = str(body.get("prompt", "")).split()
                    tokens = [zlib.crc32(w.encode()) % 50_000 for w in words]
                    return self._json(200, {"tokens": tokens, "count": len(tokens)})
                if self.path == "/reset_prefix_cache":
                    outer.reset_calls += 1
                    return self._json(200, {})
                if self.path in ("/v1/completions", "/v1/chat/completions"):
                    return self._stream(body)
                self._json(404, {"error": "not found"})

            def _stream(self, body: dict) -> None:
                with outer._lock:
                    outer.request_count += 1
                    n = outer.request_count
                    prompt = body.get("prompt", body.get("messages"))
                    outer.prompts_seen.append(prompt)
                    outer.prompt_lengths.append(len(prompt) if isinstance(prompt, list) else 0)
                if outer.fail_every and n % outer.fail_every == 0:
                    return self._json(500, {"error": "injected failure"})
                max_tokens = int(body.get("max_tokens", 16))
                chat = self.path.endswith("chat/completions")
                outer._slots.acquire()
                with outer._lock:
                    outer.inflight += 1
                    outer.max_inflight = max(outer.max_inflight, outer.inflight)
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Transfer-Encoding", "chunked")
                    self.end_headers()

                    def send(obj: dict | str) -> None:
                        payload = obj if isinstance(obj, str) else json.dumps(obj)
                        chunk = f"data: {payload}\n\n".encode()
                        self.wfile.write(f"{len(chunk):x}\r\n".encode() + chunk + b"\r\n")
                        self.wfile.flush()

                    time.sleep(outer.ttft_s)
                    for i in range(max_tokens):
                        if i:
                            time.sleep(outer.itl_s)
                        if chat:
                            send({"choices": [{"delta": {"content": f"t{i} "}}]})
                        else:
                            send({"choices": [{"text": f"t{i} "}]})
                    prompt_tokens = len(prompt) if isinstance(prompt, list) else 10
                    send(
                        {
                            "choices": [],
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": max_tokens,
                            },
                        }
                    )
                    send("[DONE]")
                    self.wfile.write(b"0\r\n\r\n")
                    with outer._lock:
                        outer.completion_tokens_total += max_tokens
                finally:
                    with outer._lock:
                        outer.inflight -= 1
                    outer._slots.release()

        return Handler
