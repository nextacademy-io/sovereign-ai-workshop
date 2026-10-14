#!/usr/bin/env python3
"""A minimal MCP server over stdio, standard library only.

MCP (Model Context Protocol) is a JSON-RPC 2.0 interface between an *application* and
*tool servers*. The model is not in this picture: the application lists the server's tools,
shows them to the model as ordinary function definitions, and forwards the model's requests.
Read the messages below; the whole protocol surface used here is four methods:

    initialize                -> capabilities handshake
    notifications/initialized -> client says it is ready (no reply)
    tools/list                -> the tools and their JSON schemas
    tools/call                -> run one tool

Messages are newline-delimited JSON on stdin/stdout. Logs go to stderr, never stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import REGISTRY, run_tool  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "workshop-tools", "version": "0.1.0"}


def tool_list() -> list[dict]:
    return [
        {
            "name": name,
            "description": schema["function"]["description"],
            "inputSchema": schema["function"]["parameters"],
        }
        for name, (_, schema) in REGISTRY.items()
    ]


def handle(request: dict) -> dict | None:
    """Return the JSON-RPC response for a request, or None for notifications."""
    method, rid = request.get("method"), request.get("id")
    if rid is None:  # notification: no response allowed
        return None

    def ok(result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def err(code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}

    if method == "initialize":
        return ok(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            }
        )
    if method == "tools/list":
        return ok({"tools": tool_list()})
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        if name not in REGISTRY:
            return err(-32602, f"unknown tool: {name}")
        text = run_tool(name, params.get("arguments") or {})
        # Tool failures are reported inside the result so the model can see and correct them.
        return ok(
            {"content": [{"type": "text", "text": text}], "isError": text.startswith("error:")}
        )
    if method == "ping":
        return ok({})
    return err(-32601, f"method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "parse error"},
                    }
                ),
                flush=True,
            )
            continue
        response = handle(request)
        if response is not None:
            print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
