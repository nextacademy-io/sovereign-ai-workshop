"""A minimal MCP client: spawn a stdio server, handshake, list and call tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


class McpClient:
    def __init__(self, command: list[str] | None = None):
        self.command = command or [sys.executable, str(HERE / "mcp_server.py")]
        self._next_id = 0
        self.proc: subprocess.Popen[str] | None = None
        self.server_info: dict = {}

    def __enter__(self) -> McpClient:
        self.proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            bufsize=1,
        )
        init = self.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "workshop-agent", "version": "0.1.0"},
            },
        )
        self.server_info = init.get("serverInfo", {})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return self

    def __exit__(self, *exc) -> None:
        if self.proc:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)

    def _send(self, message: dict) -> None:
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def request(self, method: str, params: dict | None = None) -> dict:
        assert self.proc and self.proc.stdout
        self._next_id += 1
        self._send(
            {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params or {}}
        )
        response = json.loads(self.proc.stdout.readline())
        if "error" in response:
            raise RuntimeError(
                f"MCP error {response['error']['code']}: {response['error']['message']}"
            )
        return response["result"]

    def list_tools(self) -> list[dict]:
        return self.request("tools/list")["tools"]

    def call_tool(self, name: str, arguments: dict) -> str:
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        return "\n".join(c.get("text", "") for c in result.get("content", []))

    def openai_tools(self) -> list[dict]:
        """Present MCP tools to the model as ordinary OpenAI function definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t["inputSchema"],
                },
            }
            for t in self.list_tools()
        ]
