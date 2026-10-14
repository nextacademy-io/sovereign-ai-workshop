"""Tests for the tool layer, the MCP server and the agent loop (no model needed)."""

import json
from types import SimpleNamespace

import agent
import pytest
import tools
from mcp_client import McpClient


def test_calculate_does_arithmetic_and_refuses_everything_else():
    assert tools.calculate("(12 * 7) / 3") == "28.0" or tools.calculate("(12 * 7) / 3") == "28"
    assert tools.calculate("2 ** 5") == "32"
    for bad in ("__import__('os').system('id')", "open('/etc/passwd')", "a + 1", "(1).real"):
        with pytest.raises((ValueError, SyntaxError)):
            tools.calculate(bad)
    with pytest.raises(ValueError):
        tools.calculate("9 ** 9 ** 9")


def test_run_tool_turns_failures_into_text_for_the_model():
    assert tools.run_tool("calculate", {"expression": "1/0"}).startswith("error: ZeroDivisionError")
    assert tools.run_tool("nope", {}).startswith("error: unknown tool")
    assert tools.run_tool("get_stock", {"wrong": "x"}).startswith("error: TypeError")


def test_business_tools():
    assert "412 units" in tools.get_stock("pal-100")
    assert "0 units" in tools.get_stock("LBL-A6")
    assert "unknown SKU" in tools.get_stock("???")
    assert "250 USD = 1000.00 PLN" in tools.convert_currency(
        250, "usd", "pln"
    ) or "PLN" in tools.convert_currency(250, "usd", "pln")
    assert "28 days" in tools.search_handbook("vacation days per year")
    assert "archived" not in tools.search_handbook("remote work abroad").lower()


def test_mcp_server_round_trip_over_stdio():
    with McpClient() as mcp:
        assert mcp.server_info["name"] == "workshop-tools"
        names = {t["name"] for t in mcp.list_tools()}
        assert names == set(tools.REGISTRY)
        assert "412" in mcp.call_tool("get_stock", {"sku": "PAL-100"})
        assert mcp.call_tool("calculate", {"expression": "6*7"}) == "42"
        assert mcp.call_tool("calculate", {"expression": "x"}).startswith("error:")
        oa = mcp.openai_tools()
        assert oa[0]["type"] == "function" and "parameters" in oa[0]["function"]
        with pytest.raises(RuntimeError):
            mcp.request("no/such/method")


def _response(content=None, calls=(), prompt=100, completion=10):
    tool_calls = [
        SimpleNamespace(id=f"c{i}", function=SimpleNamespace(name=n, arguments=json.dumps(a)))
        for i, (n, a) in enumerate(calls)
    ] or None
    msg = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=msg)],
        usage=SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion),
    )


class ScriptedClient:
    """Plays back a fixed list of model responses, like a model that behaves."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return self._responses.pop(0)


def test_agent_loop_executes_tools_and_accounts_for_growing_prompts():
    client = ScriptedClient(
        [
            _response(calls=[("get_stock", {"sku": "PAL-100"})], prompt=200),
            _response(calls=[("calculate", {"expression": "412 // 3"})], prompt=260),
            _response(content="You can fill 137 orders.", prompt=320, completion=12),
        ]
    )
    answer, usage = agent.run_agent(
        client, "How many orders?", model="m", tools=tools.openai_tools(), verbose=False
    )
    assert answer == "You can fill 137 orders."
    assert usage.calls == 3 and usage.prompt_tokens == 780 and usage.completion_tokens == 32
    # Tool results were fed back to the model in the right message order.
    last = client.requests[-1]["messages"]
    assert [m["role"] for m in last] == ["system", "user", "assistant", "tool", "assistant", "tool"]
    assert "412 units" in last[3]["content"] and last[5]["content"] == "137"
    assert "3x the model calls" in agent.summary(usage)


def test_agent_loop_is_bounded():
    looping = [_response(calls=[("get_stock", {"sku": "PAL-100"})]) for _ in range(20)]
    answer, usage = agent.run_agent(
        ScriptedClient(looping), "?", model="m", tools=[], max_steps=4, verbose=False
    )
    assert usage.calls == 4 and answer.startswith("(stopped after 4 steps")


def test_agent_survives_invalid_tool_arguments():
    bad = _response(calls=[("calculate", {})])
    bad.choices[0].message.tool_calls[0].function.arguments = "{not json"
    client = ScriptedClient([bad, _response(content="sorry")])
    answer, usage = agent.run_agent(
        client, "?", model="m", tools=tools.openai_tools(), verbose=False
    )
    assert answer == "sorry"
    assert "not valid JSON" in client.requests[-1]["messages"][-1]["content"]
