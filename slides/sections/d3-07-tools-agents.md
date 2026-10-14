---
layout: section
heading: "Tool calling, MCP and agents"
time: "15:30"
minutes: 30
layer: application
question: "What does one user request cost the inference layer when a model can call tools?"
---

---
layout: default
heading: "Tool calling is a protocol between model and application"
---

<D16ToolCalling />

<!--
**Key:** The model never executes anything. It returns a structured request, the application decides whether and how to run it, and the result goes back as one more message. **Example:** Click through: question, call 1 with tool schemas, a function name with JSON arguments as the reply, validation and execution in the application, then call 2 with the whole history plus the result, ending in plain text. The server must run with `--enable-auto-tool-choice` and a tool parser, which is `hermes` for Qwen3 in our profile. **Transition:** What do those messages look like in code? **Question:** "What if the model asks for a tool that does not exist?" `run_tool` returns "error: unknown tool" as text, so the model can read it and correct itself. **Deeper:** `tool_choice="auto"` is unconstrained unless a tool sets `strict: true`; a small model can still emit a malformed call (docs/TROUBLESHOOTING.md).
-->

---
layout: code
class: ki-code-sm
heading: "What crosses the wire"
file: apps/tool-calling-demo/agent.py
---

```python
resp = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    ...
)
msg = resp.choices[0].message
if not msg.tool_calls:
    return (msg.content or "").strip(), usage
...
result = call_tool(call.function.name, args)
messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
```

The reply holds text or `tool_calls`; the result goes back as a `tool` message.

<!--
**Key:** There is no special channel for tools: a request is a field on the assistant message, a result is a message with the role `tool`, and the application sends the whole list again on the next call. **Example:** Point at `tools=tools`: that is the list of JSON schemas the model sees, and `tool_call_id` ties each result to the request that caused it. `args` comes from `json.loads(call.function.arguments)`, and invalid JSON becomes the text "error: arguments were not valid JSON" instead of a crash. **Transition:** Who writes the functions behind those schemas? **Question:** "Can the model call two tools at once?" The loop handles a list of `tool_calls` per reply and appends one `tool` message for each. **Deeper:** The `chat_template_kwargs` setting that switches Qwen3 thinking off is passed in `extra_body`; it is engine- and model-specific, which matters for portability.
-->

---
layout: default
heading: "The application owns the tools"
---

| Tool | What it does | Boundary |
| --- | --- | --- |
| `calculate` | Arithmetic | Parsed with `ast`, no `eval`; length and exponent caps |
| `get_stock` | Stock of one SKU | Read-only, fixed in-memory data |
| `convert_currency` | Five currencies | Fixed workshop rates, not live |
| `search_handbook` | Keyword search | Skips archived files; read-only |

<Takeaway>

The model never executes anything. Unknown tools and bad arguments come back as text it can read.

</Takeaway>

<!--
**Key:** The tool layer is where the boundary lives. Each tool is a plain function with a schema; the application validates input, limits what the function can do and turns every failure into text. **Example:** `calculate` parses with `ast` and rejects names, calls and attributes, and its length and exponent caps stop `9 ** 9 ** 9` from burning CPU. `get_stock` reads a fixed dictionary, so the worst result of a wrong call is a wrong answer. **Transition:** Calls can also constrain the shape of the answer itself. **Question:** "Where would a write tool go?" Behind schema validation, a per-user policy and a human approval step, which is the extension exercise from the security block. **Deeper:** `test_tools_and_agent.py` checks that `__import__` and `open` are refused, and that bad arguments and unknown tools come back as `error:` text.
-->

---
layout: default
heading: "Structured output: syntax is guaranteed, meaning is not"
---

```python
response_format={
    "type": "json_schema",
    "json_schema": {"name": "ticket", "schema": SCHEMA, "strict": True},
},
```

- Constrained decoding enforces the schema's syntax, not what the model says.
- Name every field in the prompt, or the reply can fill its budget with whitespace and arrive truncated.
- A valid answer can still be wrong, or injected: validate meaning where it matters.

<!--
**Key:** Structured output turns "please reply in JSON" into a decoding constraint, which makes classification and extraction pipelines dependable at the syntax level; the content is still the model's. **Example:** `apps/inference-client/structured.py` sends a schema with four required fields and also names those fields in the system prompt. Without the second part we saw valid fields followed by blanks until `max_tokens` ran out, which left truncated, invalid JSON. The server profile uses xgrammar with `disable_any_whitespace` for compact output. **Transition:** Tools and schemas travel between model and application; next, what if the tools live in another process? **Question:** "Does a new schema cost anything?" Its first use pays a one-time grammar compile. **Deeper:** A field such as `needs_human` set by a steered model is data, not authority.
-->

---
layout: default
heading: "MCP: an interface layer between application and tools"
---

<Flow :items='[{ "label": "Application", "sub": "MCP client", "layer": "application" }, { "label": "MCP server", "sub": "JSON-RPC 2.0 over stdio" }, { "label": "Tools", "sub": "the same functions" }]' />

| Method | Purpose |
| --- | --- |
| `initialize` | Capabilities handshake |
| `notifications/initialized` | The client is ready; no reply |
| `tools/list` | The tools and their JSON schemas |
| `tools/call` | Run one tool |

<Warning title="A teaching implementation">

The model is not in this picture. The demo also speaks the `initialize` handshake of an earlier MCP revision; the current one removed it.

</Warning>

<!--
**Key:** MCP standardises how an application discovers and calls tools: JSON-RPC 2.0 messages, newline-delimited on stdin and stdout, four methods in this demo. The model never speaks MCP; the application turns the listed tools into ordinary function definitions. **Example:** `python apps/tool-calling-demo/agent.py --mcp "Convert 250 USD to PLN and tell me the stock of LBL-A6."` starts `mcp_server.py` as a subprocess, lists the tools and forwards each call. The protocol version string sits in the code as `PROTOCOL_VERSION`; the current specification revision removed sessions and the `initialize` handshake, so tutorials that show them are stale. **Transition:** With tools in place, the loop around them makes an agent. **Question:** "Is a third-party MCP server safe?" It is code and text you do not control: allowlist, sandbox, log, and treat its tool descriptions as untrusted. **Deeper:** HTTP transports add OAuth-based authorisation and Origin checks; stdio takes credentials from the environment.
-->

---
layout: code
class: ki-code-sm
heading: "An agent is a loop with a bound"
file: apps/tool-calling-demo/agent.py
---

```python
for step in range(1, max_steps + 1):
    resp = client.chat.completions.create(...)
    ...
    if not msg.tool_calls:
        return (msg.content or "").strip(), usage
    ...
return f"(stopped after {max_steps} steps without a final answer)", usage
```

`max_steps` is a hard bound: an agent without one can loop, and bill GPU time, forever. Each call is also capped at 400 completion tokens.

<!--
**Key:** An agent is a while-loop around a model call: call, run the requested tools, append the results, repeat until the model answers in text, with a bound the model cannot talk its way past. **Example:** The loop fits on one screen. `max_steps` defaults to 8, `test_agent_loop_is_bounded` shows that a model that always asks for a tool is stopped, and invalid arguments become text instead of a crash. Production adds a wall-clock limit, a token budget and a cap on tool calls per step; an injected instruction that asks the agent to retry forever is a denial of service. **Transition:** What does this loop do to the inference layer? **Question:** "Where does the planning happen?" In the model's output at each step; frameworks wrap the same loop in graphs. **Deeper:** `Usage` in `apps/common.py` records prompt tokens, completion tokens and seconds per call, which is the ledger.
-->

---
layout: default
heading: "One request fans out into several model calls"
---

<D17AgentAmplification />

<!--
**Key:** Every model call re-sends the whole conversation, so prompt tokens grow with every step. One user request is several requests to the inference server, each longer than the last. **Example:** Click through three calls: the first carries the system prompt and the question; the second adds the model's request and the tool result; the third adds both again. If every step adds a constant amount of text, the total prompt tokens over n steps grow roughly with n squared (derived). Bar lengths are illustrative. **Transition:** The demo prints exactly this as a ledger, so let us run it. **Question:** "Can't the server skip the repeated part?" Prefix caching can reuse blocks when the start of the prompt is identical; whether it does here is a question for your Day 2 prefix-cache results, and it never removes the decode steps.
-->

---
layout: code
class: ki-code-sm
heading: "Run it: the demo's token ledger"
file: apps/tool-calling-demo/agent.py
---

<Terminal title="your laptop, through the SSH tunnel">

```bash
python apps/tool-calling-demo/agent.py "Convert 250 USD to PLN and tell me the stock of LBL-A6."
python apps/tool-calling-demo/agent.py --mcp "Convert 250 USD to PLN and tell me the stock of LBL-A6."
```

</Terminal>

<Terminal title="what it prints (format only)">

```text
-- model call <n>: prompt=<P> completion=<C> <T>s
   tool <name>(<arguments>) -> <result>
model calls: <n>   prompt tokens: <P> (first call alone: <p1>)   completion tokens: <C>   model time: <T>s
one user request cost <n>x the model calls and <x>x the prompt tokens of a plain chat request
```

</Terminal>

<!--
**Key:** The ledger makes the amplification visible: one line per model call and a summary that compares the whole request with its first call alone. **Example:** Predict first: how many model calls will this question take, and how many times the prompt tokens of a plain chat request? Then run both versions, the plain loop and `--mcp`, and compare: the tools and the loop are the same, only the transport differs. The model needs thinking switched off for tool calls, which `agent.py` does with `chat_template_kwargs`. **Transition:** Turn the ledger into a planning rule. **Question:** "Why does the second command start a process?" `--mcp` spawns `mcp_server.py` as a subprocess and talks to it over stdio. **Deeper:** The summary ratio is prompt tokens of the whole request divided by the first call alone; it needs the server's usage block, so it works only against a server that reports usage.
-->

---
layout: default
heading: "Plan for model calls, not requests"
---

<Formula :terms='[{ "t": "MODEL CALLS / s" }, { "op": "=" }, { "t": "USER REQUESTS / s" }, { "op": "×" }, { "t": "CALLS PER REQUEST", "hot": true }]' />

- Multi-agent systems are more of the same: every agent is a loop with its own growing context.
- Prompt tokens grow faster than calls: each call re-sends the history.
- Bound steps, tokens and time. Watch running and waiting requests.

<Consequence>

Lab 5, scenario C: count the model calls per request before you count GPUs.

</Consequence>

<!--
**Key:** Capacity is planned in model calls and tokens, not in user requests: calls per second is requests per second times calls per request, and each call is longer than the one before. **Example:** Lab 5 scenario C has agents that may make many calls per request, so a hundred developers mean several times a hundred calls, each with a 16k to 32k context in the KV cache. Concurrency is arrival rate times time in the system, and an agent request stays for all its steps plus tool time. A multi-agent system adds a loop per agent and the messages between them: more model calls, nothing else. **Transition:** Lab 5 puts this into your own design. **Question:** "How do I find the calls per request?" Measure it with the ledger on realistic tasks and plan with a high percentile, not the mean.
-->
