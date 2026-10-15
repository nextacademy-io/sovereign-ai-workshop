# Task 02 — First inference server

## Goal

Follow one request through the whole chain `REQUEST → MODEL → GPU → TOKENS → METRICS` on a real server, and check that your arithmetic predicts what the server reports.

## Context

Your group's machine already runs a vLLM server with the baseline model. It is shared by your group on purpose: you will meet queueing and contention first-hand in Task 03. In this task you only observe and measure, and you do not restart anything.

## Scope

Done means you have followed one request through the chain, filled the *Hardware* section of your report and checked the KV-cache arithmetic against the server's own number. Out of scope: changing the server, comparing profiles and systematic benchmarks (the benchmarking lab does that).

## Starting Point

You are logged in to your group's GPU machine (`ssh -p <port> <your-user>@<host>`) and in `~/ki-ohne-cloud`. Your environment already contains `OPENAI_BASE_URL`, `OPENAI_API_KEY` and `WORKSHOP_MODEL`.

## Instructions

1. **Inspect the GPU.**

   ```bash
   nvidia-smi
   ```

   Write down the GPU name, total memory, memory in use and which processes use it.

2. **Inspect the service.**

   ```bash
   sudo wsctl status
   sudo wsctl info | python3 -m json.tool | head -40
   ```

   Find the engine version, the profile, how long startup took, the memory for the weights and the KV cache capacity in tokens.

3. **Ask the API.**

   ```bash
   curl -s -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models | python3 -m json.tool
   curl -s -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" \
     $OPENAI_BASE_URL/chat/completions -d '{"model":"'"$WORKSHOP_MODEL"'","messages":[{"role":"user","content":"Name three uses of a KV cache."}],"max_tokens":120,"chat_template_kwargs":{"enable_thinking":false}}'
   ```

4. **Stream a response and read the numbers.**

   ```bash
   python3 apps/inference-client/chat.py "Explain batching in one paragraph."
   ```

   The last line shows prompt tokens, time to first token, completion tokens and tokens per second.

5. **Watch the GPU while you work.** In a second terminal on the same machine: `./scripts/gpu-status.sh --watch`. Then in the first terminal send a long request: `python3 apps/inference-client/chat.py --max-tokens 800 "Write a detailed essay about GPUs."`

6. **Change one thing at a time** and record what changes in time to first token and tokens per second: the prompt length (paste a long text), the output length (`--max-tokens`), the temperature (`--temperature 1.0`).

7. **Read the server log.** `sudo wsctl logs 40`: find the line with the KV cache size.

8. **Check your arithmetic.**

   ```bash
   python3 scripts/sizing.py --model primary --precision bf16 --context 32768 --concurrency 1
   ```

   Compare the KV cache bytes per token and the memory for the weights with what the server reported.

9. Fill the *Hardware* section of `workshop-artifacts/inference-report.md` and note three observations in your own words.

## Expected Result

- `wsctl info` shows the weights memory and the KV cache memory with its capacity in tokens: the KV cache is several times larger than the weights, and it holds many requests' worth of context.
- Time to first token grows with prompt length; tokens per second per request hardly changes with prompt length but is lower with a very long context; temperature does not change speed.
- GPU utilization shows about 100 % during generation, even for a single request: busy is not the same as efficient.
- The very first request after a server start can be slower than the ones after it, because kernels and caches warm up on first use. Do not take it as the baseline.

## Validation

Compare with the reference (the baseline profile on the workshop GPU, `benchmark/results/reference/startup/`):

- `wsctl info` reports weights of about 15 GiB and a KV cache of about 58 GiB (a few percent different after a restart), which holds about 420,000 tokens.
- The first request after a start took 282 ms to the first token in the dry run, against about 70 ms for the requests after it.

Then check your own work:

- Your KV cache estimate from `sizing.py` for the server's *available KV memory* is within 2 % of the token count in the log. If you are off by 2x, you forgot that the cache stores keys **and** values; if you are off by 4x, you used the 32 query heads instead of the 8 KV heads.
- Your report names the engine version, the GPU, the weights memory, the KV capacity and the highest tokens per second you saw.

## If You Get Stuck

| Symptom | Fix |
| --- | --- |
| `401` from the API | Log in again: the key is set at login. |
| No answer for a long time | `sudo wsctl status`. A restart with warm caches takes about 40 seconds, the first start of a profile up to about two and a half minutes. Do not start another server. |
| `nvidia-smi` shows more memory in use than the model needs | Correct: vLLM reserves its budget at startup. The KV cache fills only as requests arrive. |
| You broke something | `./scripts/reset.sh lab-02` |

## Further Exploration

- Send the same request with `"stream": true` using `curl -N` and count the chunks.
- Use `structured.py` and then add a field to the schema without mentioning it in the prompt. What happens, and why? (`apps/inference-client/structured.py` explains.)
- Open Grafana through an SSH tunnel and find the panel that shows your request.
