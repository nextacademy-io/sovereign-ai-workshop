#!/usr/bin/env python3
"""A tool-calling agent loop, and what it costs the inference server.

    python apps/tool-calling-demo/agent.py "We have 3 pallets per order. How many orders can we fill from PAL-100 stock?"
    python apps/tool-calling-demo/agent.py --mcp "Convert 250 USD to PLN and tell me the stock of LBL-A6."

    USER -> LLM -> TOOL REQUEST -> APPLICATION -> TOOL -> RESULT -> LLM -> ... -> ANSWER

One user request becomes several model calls. Each call re-sends the whole conversation, so
prompt tokens grow with every step. The summary at the end is the point of this demo:
agents multiply load on the inference system, so they belong in capacity planning.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Usage, make_client, model_name  # noqa: E402
from tools import openai_tools, run_tool  # noqa: E402

SYSTEM = (
    "You are an operations assistant. Use the tools for every lookup and every calculation; "
    "never guess numbers. When you have the answer, reply briefly."
)


def run_agent(
    client,
    question: str,
    *,
    model: str,
    tools: list[dict],
    call_tool=run_tool,
    max_steps: int = 8,
    verbose: bool = True,
) -> tuple[str, Usage]:
    """Run the loop. Returns the final answer and per-call accounting.

    `max_steps` is a hard bound: an agent without one can loop (and bill GPU time) forever.
    """
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    usage = Usage()
    for step in range(1, max_steps + 1):
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0,
            max_tokens=400,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        seconds = time.perf_counter() - t0
        msg = resp.choices[0].message
        usage.add(
            resp.usage.prompt_tokens, resp.usage.completion_tokens, seconds, label=f"step {step}"
        )
        if verbose:
            print(
                f"-- model call {step}: prompt={resp.usage.prompt_tokens} completion={resp.usage.completion_tokens} {seconds:.2f}s"
            )
        if not msg.tool_calls:
            return (msg.content or "").strip(), usage
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {"name": c.function.name, "arguments": c.function.arguments},
                    }
                    for c in msg.tool_calls
                ],
            }
        )
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
                result = "error: arguments were not valid JSON"
            else:
                result = call_tool(call.function.name, args)
            if verbose:
                print(f"   tool {call.function.name}({json.dumps(args)}) -> {result[:100]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"(stopped after {max_steps} steps without a final answer)", usage


def summary(usage: Usage) -> str:
    first = usage.per_call[0]["prompt"] if usage.per_call else 0
    return (
        f"model calls: {usage.calls}   prompt tokens: {usage.prompt_tokens} "
        f"(first call alone: {first})   completion tokens: {usage.completion_tokens}   "
        f"model time: {usage.seconds:.2f}s\n"
        f"one user request cost {usage.calls}x the model calls and "
        f"{usage.prompt_tokens / max(first, 1):.1f}x the prompt tokens of a plain chat request"
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("question")
    ap.add_argument("--model", default=model_name())
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument(
        "--mcp", action="store_true", help="fetch and call tools through an MCP server process"
    )
    a = ap.parse_args()

    client = make_client()
    if a.mcp:
        from mcp_client import McpClient

        with McpClient() as mcp:
            print(f"MCP server: {mcp.server_info}")
            answer, usage = run_agent(
                client,
                a.question,
                model=a.model,
                tools=mcp.openai_tools(),
                call_tool=mcp.call_tool,
                max_steps=a.max_steps,
            )
    else:
        answer, usage = run_agent(
            client, a.question, model=a.model, tools=openai_tools(), max_steps=a.max_steps
        )
    print(f"\nanswer: {answer}\n")
    print(summary(usage))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
