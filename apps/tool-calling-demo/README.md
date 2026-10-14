# tool-calling-demo

Tool calling, an MCP server and client, and an agent loop, written with the standard library and the `openai` client; no agent framework.

| File | What it is |
| --- | --- |
| `tools.py` | Plain Python functions the model may *request* (stock lookup, currency conversion, a safe calculator, a handbook search), each with a JSON schema and its own input validation. The model never executes anything. |
| `agent.py` | The loop `USER → LLM → TOOL REQUEST → APPLICATION → TOOL → RESULT → LLM → ... → ANSWER` with a ledger of model calls, prompt tokens and time at the end |
| `mcp_server.py`, `mcp_client.py` | A minimal Model Context Protocol server over stdio and a client for it: `initialize`, `notifications/initialized`, `tools/list`, `tools/call`. It implements an earlier revision of the protocol than the current one; it is a teaching implementation, not a reference. |

```bash
python3 apps/tool-calling-demo/agent.py "We have 3 pallets per order. How many orders can we fill from PAL-100 stock?"
python3 apps/tool-calling-demo/agent.py --mcp "Convert 250 USD to PLN and tell me the stock of LBL-A6."
```

The server must run with tool calling enabled; the workshop profiles set `--enable-auto-tool-choice --tool-call-parser hermes`.

## What to look at

The last two lines of the output are the point of the demo: one user request became several model calls, each of which re-sends the whole conversation, so the prompt tokens of the whole request were more than three times those of the first call alone (3 calls, 1,513 prompt tokens against 452 in the validation run). Agents multiply the load on the inference system; they belong in capacity planning.

`test_tools_and_agent.py` tests the tools and the loop without a GPU.
