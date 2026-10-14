# Benchmark: custom

- **Hardware:** 1× NVIDIA RTX PRO 6000 Blackwell Server Edition (95.6 GB), driver 595.91.07
- **Model:** `Qwen/Qwen3-8B` @ `b968826d9c46`
- **Engine:** vllm 0.31.0 · CUDA 13.0
- **Workload:** 1200 input tokens, 180 output tokens
- **Server arguments:** `--host 127.0.0.1 --port 8000 --dtype bfloat16 --max-model-len 32768 --gpu-memory-utilization 0.8 --generation-config vllm --enable-auto-tool-choice --tool-call-parser hermes --reasoning-parser qwen3 --enable-mfu-metrics --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' --model Qwen/Qwen3-8B --revision b968826d9c46dd6066d109eabc6255188de91218 --served-model-name Qwen/Qwen3-8B`
- **Date:** 2026-10-14T13:58:29+00:00 · prompt seed 116868736

| Load | Requests | TTFT p50 (ms) | TTFT p95 (ms) | Latency p50 (ms) | Latency p95 (ms) | ITL p50 (ms) | Output TPS/req p50 | Aggregate TPS | Req/s | GPU util mean (%) | VRAM max (GiB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 48 | 115 | 120 | 2,242 | 2,245 | 11.9 | 84.2 | 161 | 0.89 | 100 | 83.9 |

TTFT = time to first token. ITL = inter-token latency. Output TPS/req = tokens per second one
request sees after its first token (1 / TPOT). Aggregate TPS = output tokens per second
delivered by the whole server over the run. GPU utilization is the share of time any kernel
ran, not an efficiency measure.
