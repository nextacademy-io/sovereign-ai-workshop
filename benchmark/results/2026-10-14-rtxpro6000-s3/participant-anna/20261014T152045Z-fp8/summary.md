# Benchmark: workshop-baseline

- **Hardware:** 1× NVIDIA RTX PRO 6000 Blackwell Server Edition (95.6 GB), driver 580.159.04
- **Model:** `Qwen/Qwen3-8B` @ `220b46e3b218`
- **Engine:** vllm 0.31.0 · CUDA 13.0
- **Workload:** 1200 input tokens, 180 output tokens
- **Server arguments:** `--host 127.0.0.1 --port 8000 --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.8 --generation-config vllm --enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3 --enable-mfu-metrics --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' --model Qwen/Qwen3-8B-FP8 --revision 220b46e3b2180893580a4454f21f22d3ebb187d3 --served-model-name Qwen/Qwen3-8B`
- **Date:** 2026-10-14T15:20:46+00:00 · prompt seed 1537752537

| Load | Requests | TTFT p50 (ms) | TTFT p95 (ms) | Latency p50 (ms) | Latency p95 (ms) | ITL p50 (ms) | Output TPS/req p50 | Aggregate TPS | Req/s | GPU util mean (%) | VRAM max (GiB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 32 | 49 | 54 | 1,401 | 1,410 | 7.5 | 132.2 | 129 | 0.72 | 99 | 83.3 |
| 8 | 64 | 232 | 274 | 1,764 | 1,783 | 8.4 | 116.8 | 815 | 4.53 | 100 | 84.6 |
| 16 | 128 | 392 | 509 | 2,215 | 2,284 | 9.6 | 98.4 | 1,296 | 7.20 | 100 | 84.6 |

TTFT = time to first token. ITL = inter-token latency. Output TPS/req = tokens per second one
request sees after its first token (1 / TPOT). Aggregate TPS = output tokens per second
delivered by the whole server over the run. GPU utilization is the share of time any kernel
ran, not an efficiency measure.
