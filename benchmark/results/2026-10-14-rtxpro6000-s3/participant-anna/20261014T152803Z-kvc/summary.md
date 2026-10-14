# Benchmark: workshop-baseline

- **Hardware:** 1× NVIDIA RTX PRO 6000 Blackwell Server Edition (95.6 GB), driver 580.159.04
- **Model:** `Qwen/Qwen3-8B` @ `b968826d9c46`
- **Engine:** vllm 0.31.0 · CUDA 13.0
- **Workload:** 8192 input tokens, 128 output tokens
- **Server arguments:** `--host 127.0.0.1 --port 8000 --dtype bfloat16 --max-model-len 16384 --gpu-memory-utilization 0.8 --generation-config vllm --enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3 --enable-mfu-metrics --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' --model Qwen/Qwen3-8B --revision b968826d9c46dd6066d109eabc6255188de91218 --served-model-name Qwen/Qwen3-8B --kv-cache-memory-bytes 4G`
- **Date:** 2026-10-14T15:28:03+00:00 · prompt seed 1755247959

| Load | Requests | TTFT p50 (ms) | TTFT p95 (ms) | Latency p50 (ms) | Latency p95 (ms) | ITL p50 (ms) | Output TPS/req p50 | Aggregate TPS | Req/s | GPU util mean (%) | VRAM max (GiB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 32 | 415 | 419 | 2,003 | 2,006 | 12.6 | 80.0 | 64 | 0.50 | 100 | 30.1 |
| 4 | 32 | 1,230 | 3,027 | 3,420 | 5,580 | 14.2 | 57.3 | 125 | 0.98 | 100 | 30.1 |
| 8 | 64 | 6,018 | 6,768 | 8,555 | 8,934 | 14.1 | 57.9 | 126 | 0.99 | 100 | 30.1 |

TTFT = time to first token. ITL = inter-token latency. Output TPS/req = tokens per second one
request sees after its first token (1 / TPOT). Aggregate TPS = output tokens per second
delivered by the whole server over the run. GPU utilization is the share of time any kernel
ran, not an efficiency measure.
