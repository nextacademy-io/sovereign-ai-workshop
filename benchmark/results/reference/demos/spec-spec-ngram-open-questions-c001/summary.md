# Benchmark: custom

- **Hardware:** 1× NVIDIA RTX PRO 6000 Blackwell Server Edition (95.6 GB), driver 595.91.07
- **Model:** `Qwen/Qwen3-8B` @ `b968826d9c46`
- **Engine:** vllm 0.31.0 · CUDA 13.0
- **Workload:** prompts from `open-questions.jsonl`, up to 200 output tokens
- **Server arguments:** `--host 127.0.0.1 --port 8000 --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.8 --generation-config vllm --enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3 --enable-mfu-metrics --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' --model Qwen/Qwen3-8B --revision b968826d9c46dd6066d109eabc6255188de91218 --served-model-name Qwen/Qwen3-8B --speculative-config '{"method":"ngram","num_speculative_tokens":4,"prompt_lookup_min":2,"prompt_lookup_max":5}'`
- **Date:** 2026-10-14T15:32:06+00:00 · prompt seed 1211534780

| Load | Requests | TTFT p50 (ms) | TTFT p95 (ms) | Latency p50 (ms) | Latency p95 (ms) | ITL p50 (ms) | Output TPS/req p50 | Aggregate TPS | Req/s | GPU util mean (%) | VRAM max (GiB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 32 | 20 | 21 | 2,307 | 2,453 | 12.5 | 87.0 | 95 | 0.47 | 89 | 84.3 |

TTFT = time to first token. ITL = inter-token latency. Output TPS/req = tokens per second one
request sees after its first token (1 / TPOT). Aggregate TPS = output tokens per second
delivered by the whole server over the run. GPU utilization is the share of time any kernel
ran, not an efficiency measure.
