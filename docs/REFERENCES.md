# References

Sources behind the workshop "KI ohne Cloud: Modelle lokal betreiben, eigene Daten anbinden, Prozesse automatisieren". Slides, tasks and docs cite entries from this list instead of repeating URLs. The findings, numbers and workshop decisions derived from these sources are in `docs/RESEARCH.md`.

How the list is used:

- **Cite primary sources.** Primary means official documentation, source code at a release tag, datasheets, model cards and licence files, original papers and official EU texts. Secondary sources (blogs, reseller guides, unofficial mirrors, incident write-ups) appear only in subsections titled "Secondary sources used only for orientation" and are not cited on slides.
- **Re-read before quoting.** Most pages were read through a summarising fetch tool, so wording in the research notes may be paraphrased. Open the source before putting a quotation or a number on a slide.
- **What "verified" means.** A research pass opened the URL on 2026-10-14. It does not mean every claim in the notes was re-checked against that page. An entry marked "(unverified)" was not opened, could not be read, or is flagged as unconfirmed in the research notes.
- **Versions drift.** vLLM facts are pinned to the `v0.31.0` tag. Pages on `latest` or `main` can be ahead of the release or change later, and model repositories change, so models are pinned by commit SHA in the workshop configuration.
- **Legal and regulatory entries are sources for engineers, not legal advice.**
- **The book is cited by chapter only.** *Inference Engineering* appears once, in its own group, with bibliographic data and a chapter-to-topic table. It is never quoted, and no figure is copied from it.

Each entry reads: title and link, then publisher, authors, venue or year where known, then what the workshop uses it for. Within a group, entries are ordered by importance for the workshop, not alphabetically.

## vLLM

### Releases, images and installation

- [vLLM v0.31.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.31.0) — vLLM project, published 2026-10-05 — the release under test: breaking changes, CUDA 13.0 default image and `-cu129` variant, new scheduler flags, SM120 items.
- [Dockerfile at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docker/Dockerfile) — vLLM project — base image, Python 3.12, CUDA architecture list, why `nvcc` ships in the runtime image.
- [Docker deployment guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/docker.md) — vLLM project — official `docker run` lines, `--ipc=host`, cache mounts, non-root option.
- [CUDA installation page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/getting_started/installation/gpu.cuda.inc.md) — vLLM project — driver floor for CUDA 13 images and compatibility mode; its CUDA 12.9 wording is stale against the release notes.
- [vLLM v0.30.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.30.0) — vLLM project, 2026-09-22 — SM120 and SM121 items (B12X attention backend, NVFP4 preference).
- [vLLM v0.10.1 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.10.1) — vLLM project, 2025-08-18 — `--task` replaced by `--runner` and `--convert`, which some model cards still print.
- [vLLM v0.9.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.9.0) — vLLM project, 2025-05-15 — deprecation of `--enable-reasoning`, which some model cards still print.
- [vLLM documentation sources at v0.31.0](https://github.com/vllm-project/vllm/tree/v0.31.0/docs) — vLLM project — the pinned docs tree that docs.vllm.ai builds from; use it for release-accurate statements.

### Serving flags, defaults and configuration

- [`vllm serve` CLI reference, stable build](https://docs.vllm.ai/en/stable/cli/serve/) — vLLM project — release-matched defaults, for example `--gpu-memory-utilization` 0.92 and `--kv-cache-memory-bytes`.
- [`vllm serve` CLI reference, latest build](https://docs.vllm.ai/en/latest/cli/serve/) — vLLM project, developer preview — generated from the config dataclasses; flag defaults and TLS options.
- [Engine arguments source at v0.31.0 (arg_utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/engine/arg_utils.py) — vLLM project — batch-size defaults by GPU memory, prefix-caching and chunked-prefill default resolution, `--kv-cache-memory-bytes`.
- [Cache config source at v0.31.0 (config/cache.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/cache.py) — vLLM project — `gpu_memory_utilization`, `kv_cache_memory_bytes`, `kv_cache_dtype`, default block size 16.
- [Model config source at v0.31.0 (config/model.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/model.py) — vLLM project — dtype, `--generation-config auto`, `max_model_len` parsing, revisions, `trust_remote_code`.
- [Scheduler config source at v0.31.0 (config/scheduler.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/scheduler.py) — vLLM project — scheduler fields, new `--max-num-active-seqs`, `scheduler_reserve_full_isl`.
- [vLLM config source at v0.31.0 (config/vllm.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/vllm.py) — vLLM project — Model Runner V2 default and fallback to V1, performance mode, optimisation levels.
- [Frontend arguments source at v0.31.0 (cli_args.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/cli_args.py) — vLLM project — bind address, `--api-key`, tool and reasoning parser flags, request-logging flags.
- [Optimization and tuning guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/optimization.md) — vLLM project — chunked prefill, `max_num_batched_tokens` trade-off, recompute preemption.
- [Conserving memory guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/conserving_memory.md) — vLLM project — the list of knobs for fitting a model into less memory.
- [Serve arguments and YAML config at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/configuration/serve_args.md) — vLLM project — config-file format, key naming, precedence of CLI over file.
- [Argument parser source at v0.31.0 (argparse_utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/utils/argparse_utils.py) — vLLM project — why underscore and dash keys both work in the YAML config.
- [CLI overview at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/cli/README.md) — vLLM project — subcommands, `--help=` forms, human-readable integers with k, K, m, M suffixes.
- [V1 guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/v1_guide.md) — vLLM project — unified token-budget scheduler, FCFS and priority policies, prompt logprobs bypass the prefix cache.
- [Model Runner V2 design at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/model_runner_v2.md) — vLLM project — default runner, async scheduling, what MRV2 does not yet support.
- [Environment variables source at v0.31.0 (envs.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/envs.py) — vLLM project — variables such as `VLLM_LOG_STATS_INTERVAL` (default 10 s).
- [Tokenize request and response source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/tokenize/protocol.py) — vLLM project — `/tokenize` and `/detokenize` shapes for token counting in labs.
- [Initialized snapshots guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/initialized_snapshots.md) — vLLM project — the only v0.31.0 doc that shows `HF_HUB_OFFLINE=1`.

### KV cache, memory accounting and scheduling

- [KV cache utilities source at v0.31.0 (kv_cache_utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/kv_cache_utils.py) — vLLM project — the one-line "GPU KV cache size ... Maximum concurrency" log format and the block-count and capacity formulas to check hand calculations against.
- [GPU worker source at v0.31.0 (gpu_worker.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/gpu_worker.py) — vLLM project — memory profiling, "Available KV cache memory" line, CUDA-graph memory estimate.
- [Worker utilities source at v0.31.0 (worker/utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/utils.py) — vLLM project — `request_memory`: utilisation is a fraction of total device memory, not of free memory.
- [Memory utilities source at v0.31.0 (mem_utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/utils/mem_utils.py) — vLLM project — the `memory_profiling` helper behind the accounting.
- [KV cache interface source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/kv_cache_interface.py) — vLLM project — `page_size_bytes` per layer, the per-block size in the KV-cache formula.
- [GPU model runner source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/worker/gpu_model_runner.py) — vLLM project — the "Model loading took ... GiB" startup line.
- [Scheduler source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/core/sched/scheduler.py) — vLLM project — preemption frees blocks and requeues at the front; victim selection.
- [Prefix caching design at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/prefix_caching.md) — vLLM project — block hashing, `cache_salt`, eviction, why only full blocks are cached.
- [Automatic prefix caching feature page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/automatic_prefix_caching.md) — vLLM project — feature description; its "set enable_prefix_caching" sentence is stale because the default is on.
- [PagedAttention design page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/paged_attention.md) — vLLM project — conceptual kernel background only; it describes the older kernel, not the V1 scheduler.

### Metrics and observability

- [vLLM metrics source at v0.31.0 (loggers.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py) — vLLM project — source of truth for every Prometheus metric name, type, label and help string, and the periodic stats log line.
- [Metrics usage page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/usage/metrics.md) — vLLM project — metric list, `--enable-mfu-metrics`, deprecation policy.
- [Metrics design page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/metrics.md) — vLLM project — legacy metrics, multiprocess-mode caveats, how Prometheus TPOT differs from the benchmark TPOT.
- [Metrics usage page, latest build](https://docs.vllm.ai/en/latest/usage/metrics/) — vLLM project, developer preview — lists metrics that are not in the v0.31.0 source; the example of docs drifting ahead of a release.
- [Histogram bucket source at v0.31.0 (buckets.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/buckets.py) — vLLM project — default bucket bounds for latency histograms.
- [MFU metrics source at v0.31.0 (perf.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/perf.py) — vLLM project — estimated FLOPs and bytes metric names.
- [Speculative-decoding metrics source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/spec_decode/metrics.py) — vLLM project — draft and acceptance counters.
- [Prometheus and Grafana example at v0.31.0](https://github.com/vllm-project/vllm/tree/v0.31.0/examples/observability/prometheus_grafana) — vLLM project — compose file, scrape config and dashboard that the monitoring stack starts from.
- [Grafana dashboard JSON at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/examples/observability/prometheus_grafana/grafana.json) — vLLM project — 12 panels; no panel for prefix-cache hit rate, preemptions or iteration tokens, which the workshop adds.
- [Dashboards directory at v0.31.0](https://github.com/vllm-project/vllm/tree/v0.31.0/examples/observability/dashboards) — vLLM project — newer Grafana and Perses dashboards (performance and query statistics).
- [Observability examples at v0.31.0](https://github.com/vllm-project/vllm/tree/v0.31.0/examples/observability) — vLLM project — parent directory including OpenTelemetry and offline-metrics examples.

### Benchmarking with vLLM

- [`vllm bench serve` CLI reference](https://docs.vllm.ai/en/latest/cli/bench/serve/) — vLLM project — flags including `--request-rate`, `--max-concurrency` and `--goodput` (keys `ttft`, `tpot`, `e2el`).
- [Benchmark serving source at v0.31.0 (serve.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/serve.py) — vLLM project — load-shape semantics, metric formulas, printed block and JSON keys.
- [Benchmark datasets source at v0.31.0 (datasets.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/datasets/datasets.py) — vLLM project — random-dataset and prefix-repetition semantics.
- [Benchmark endpoint request source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/benchmarks/lib/endpoint_request_func.py) — vLLM project — how authentication is sent (`OPENAI_API_KEY` or `--header`), since there is no `--api-key` flag.
- [Benchmark CLI guide at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/benchmarking/cli.md) — vLLM project — "Understanding the latency metrics" definitions of TTFT, TPOT, ITL, E2EL.

### Quantization

- [Quantization overview at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/README.md) — vLLM project — supported formats and the hardware table, which has no Blackwell column.
- [Online quantization at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/online.md) — vLLM project — `fp8_per_tensor`, `fp8_per_block`, `mxfp8` and the other load-time options.
- [FP8 W8A8 with llm-compressor at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/llm_compressor/fp8.md) — vLLM project — FP8 hardware requirements and kernel selection order.
- [NVIDIA ModelOpt formats at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/modelopt.md) — vLLM project — NVFP4 and FP8 checkpoint detection, Marlin weight-only fallback, `--linear-backend`.
- [Quantized KV cache at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/quantized_kvcache.md) — vLLM project — `--kv-cache-dtype fp8` and its scale caveats.
- [Quantization method registry source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/layers/quantization/__init__.py) — vLLM project — valid `--quantization` names and deprecated methods.
- [FP8 quantization source at v0.31.0 (fp8.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/layers/quantization/fp8.py) — vLLM project — error for online `fp8` and the redirect to `fp8_per_tensor`.
- [b12x backend page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/b12x.md) — vLLM project — optional SM120 and SM121 linear and MoE backend, not in the stock image.
- [AutoAWQ page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/auto_awq.md) — vLLM project — AutoAWQ deprecated and adopted by llm-compressor.
- [GPTQModel page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gptqmodel.md) — vLLM project — GPTQ path and Marlin or Machete kernels.
- [GGUF page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/gguf.md) — vLLM project — highly experimental, moved to an out-of-tree plugin.
- [bitsandbytes page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/quantization/bnb.md) — vLLM project — moved to an out-of-tree plugin.

### Speculative decoding

- [Speculative decoding overview at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/README.md) — vLLM project — methods, `--speculative-config` keys, qualitative gain table by load.
- [Dynamic speculative decoding at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/speculative_decoding/dynamic_speculative_decoding.md) — vLLM project — why speculation hurts at high batch sizes and the per-batch-size K setting.

### Structured outputs, tool calling, reasoning and embeddings

- [Tool calling at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/tool_calling.md) — vLLM project — `--enable-auto-tool-choice` with `--tool-call-parser`, strict levels, per-family parser notes.
- [Reasoning outputs at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/reasoning_outputs.md) — vLLM project — `--reasoning-parser qwen3`, the `reasoning` response field, disabling thinking.
- [Structured outputs at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/structured_outputs.md) — vLLM project — the nested `structured_outputs` request object that replaced the `guided_*` fields.
- [Structured outputs config source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/config/structured_outputs.py) — vLLM project — backend selection and options.
- [Tool parser registry source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/tool_parsers/__init__.py) — vLLM project — registered `--tool-call-parser` names.
- [Reasoning parser registry source at v0.31.0](https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/reasoning/__init__.py) — vLLM project — registered `--reasoning-parser` names.
- [Embedding models at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/models/pooling_models/embed.md) — vLLM project — `/v1/embeddings`, `--runner pooling`, supported embedding models.
- [Pooling models overview at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/models/pooling_models/README.md) — vLLM project — `--runner` and `--convert` replacing `--task`.
- [Supported models page, main branch](https://raw.githubusercontent.com/vllm-project/vllm/main/docs/models/supported_models.md) — vLLM project, main branch (not pinned) — which architectures and embedding checkpoints are supported.

### Distributed serving, offload and Kubernetes

- [Data-parallel deployment at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/data_parallel_deployment.md) — vLLM project — replicas behind one endpoint, per-rank `--max-num-seqs`, independent KV caches.
- [Expert-parallel deployment at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/serving/expert_parallel_deployment.md) — vLLM project — `--enable-expert-parallel` and all-to-all backends (MoE only).
- [Disaggregated prefill at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/disagg_prefill.md) — vLLM project — experimental prefill and decode split; it tunes TTFT and tail ITL, not throughput.
- [KV offloading usage at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/features/kv_offloading_usage.md) — vLLM project — `--kv-offloading-size`, native and LMCache backends.
- [production-stack integration page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/production-stack.md) — vLLM project — Helm-based cluster deployment, prefix-aware routing.
- [production-stack repository](https://github.com/vllm-project/production-stack) — vLLM project, Apache-2.0 — Kubernetes reference stack; chart versions still 0.x.
- [NVIDIA Dynamo integration page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/dynamo.md) — vLLM project — Dynamo as an orchestration layer above vLLM.
- [llm-d integration page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/deployment/integrations/llm-d.md) — vLLM project — Kubernetes-native routing and disaggregation.
- [vLLM deployment docs directory at v0.31.0](https://github.com/vllm-project/vllm/tree/v0.31.0/docs/deployment) — vLLM project — index of the other Kubernetes integrations (KServe, KubeAI, KubeRay and others).

### Blackwell SM120 status and known issues

- [Attention backends design page at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/docs/design/attention_backends.md) — vLLM project — the b12x backend for SM120 and SM121; the only docs page that names SM120.
- [CUDA platform source at v0.31.0 (platforms/cuda.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/platforms/cuda.py) — vLLM project — attention backend priority per compute capability, SM120 special cases.
- [FlashAttention version selection source at v0.31.0 (fa_utils.py)](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/attention/backends/fa_utils.py) — vLLM project — FA3 on SM90, FA4 only on SM100, so SM120 runs FA2.
- [vLLM issue 50189](https://github.com/vllm-project/vllm/issues/50189) — vLLM project, open — SM120 MMU fault with the `flashinfer_b12x` MoE path under concurrent chunked prefill.
- [vLLM issue 57932](https://github.com/vllm-project/vllm/issues/57932) — vLLM project, open — a GLM model fails with FlashInfer attention on SM120.
- [vLLM issue 59203](https://github.com/vllm-project/vllm/issues/59203) — vLLM project, open — a DeepSeek model on SM120 lacks a FlashInfer sparse-MLA kernel for the page size.
- [vLLM issue 40677](https://github.com/vllm-project/vllm/issues/40677) — vLLM project, open — Gemma 4 fails when FlashInfer attention is forced on SM120 (head size).
- [vLLM issue 32826](https://github.com/vllm-project/vllm/issues/32826) — vLLM project, closed not planned — MiniMax NVFP4 with expert parallel on RTX PRO 6000.
- [FlashInfer issue 2577](https://github.com/flashinfer-ai/flashinfer/issues/2577) — FlashInfer project, closed as completed on 2026-07-23 — NVFP4 `mm_fp4` GEMM was broken on SM120.

### Other inference engines (for the engine-comparison block)

- [SGLang repository](https://github.com/sgl-project/sglang) — LMSYS, Apache-2.0, v0.5.21 on 2026-10-02 — the main alternative engine; its README names PRO 6000 among supported NVIDIA GPUs.
- [TensorRT-LLM repository](https://github.com/NVIDIA/TensorRT-LLM) — NVIDIA — NVIDIA-only engine; latest stable v1.2.1 (2026-04-20), active line is a v1.3.0 release candidate.
- [TensorRT-LLM licence file](https://raw.githubusercontent.com/NVIDIA/TensorRT-LLM/main/LICENSE) — NVIDIA — Apache 2.0 with third-party notices.
- [llama.cpp repository](https://github.com/ggml-org/llama.cpp) — ggml-org, MIT — GGUF-native CPU and GPU engine; continuous build tags.
- [llama-server README](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md) — ggml-org — `--parallel` slots, continuous batching, OpenAI-compatible routes.
- [Ollama repository](https://github.com/ollama/ollama) — Ollama, MIT, v0.40.4 on 2026-10-12 — the local-runner baseline in the concurrency demo.
- [Ollama FAQ](https://raw.githubusercontent.com/ollama/ollama/main/docs/faq.mdx) — Ollama — `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_QUEUE`, `OLLAMA_KEEP_ALIVE`, loopback bind by default.
- [LM Studio headless mode (llmster)](https://lmstudio.ai/docs/developer/core/headless_llmster) — LM Studio — running LM Studio on a server with `lms`.
- [LM Studio OpenAI-compatible API](https://lmstudio.ai/docs/developer/openai-compat) — LM Studio — the local endpoint and its routes.
- [LM Studio parallel requests](https://lmstudio.ai/docs/app/advanced/parallel-requests) — LM Studio — default Max Concurrent Predictions is 4, llama.cpp engine only.
- [LM Studio download page](https://lmstudio.ai/download) — LM Studio — current app version (0.4.26 on 2026-10-14).
- [LM Studio: free for work](https://lmstudio.ai/blog/free-for-work) — LM Studio blog, 2025-07-08 — licensing statement for work use; the GUI is not open source.
- [lms CLI repository](https://github.com/lmstudio-ai/lms) — LM Studio, MIT — the open-source command-line tool.
- [NVIDIA Dynamo repository](https://github.com/ai-dynamo/dynamo) — NVIDIA, Apache-2.0, v1.5.1 on 2026-10-07 — distributed serving layer above vLLM, SGLang and TensorRT-LLM.

## Hugging Face

- [Pickle serialisation on the Hub](https://huggingface.co/docs/hub/security-pickle) — Hugging Face Hub docs — why pickle checkpoints can run code on load, what the Hub's import scan does and does not guarantee, signed commits.
- [safetensors documentation](https://huggingface.co/docs/safetensors/index) — Hugging Face — the format that avoids code execution on load; zero-copy loading.
- [safetensors README](https://raw.githubusercontent.com/huggingface/safetensors/main/README.md) — Hugging Face — header and byte-buffer layout, pickle versus safetensors comparison table.
- [Malware scanning on the Hub](https://huggingface.co/docs/hub/security-malware) — Hugging Face Hub docs — ClamAV scan scope (files under 2 GB, each commit) and its limits.
- [Transformers: custom models and `trust_remote_code`](https://raw.githubusercontent.com/huggingface/transformers/main/docs/source/en/models.md) — Hugging Face Transformers docs, main branch — remote modeling code is not Transformers code; pin a revision when you must load it.
- [huggingface_hub environment variables](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) — Hugging Face — `HF_HUB_OFFLINE`, telemetry and token switches, `HF_XET_HIGH_PERFORMANCE`, cache locations.
- [huggingface_hub download guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/download.md) — Hugging Face — full-length commit-hash `revision`, `snapshot_download` patterns, the `hf download` CLI.
- [huggingface_hub cache guide](https://raw.githubusercontent.com/huggingface/huggingface_hub/main/docs/source/en/guides/manage-cache.md) — Hugging Face — cache layout, offline revision resolution, `IncompleteSnapshotError`, shared Xet blobs.
- [Gated models on the Hub](https://huggingface.co/docs/hub/models-gated) — Hugging Face Hub docs — access-request flow, automatic versus manual approval, tokens for gated downloads.
- [Xet storage backend](https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/xet/index.md) — Hugging Face Hub docs — chunk-level deduplication behind first-download time.
- [Using Xet storage](https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/xet/using-xet-storage.md) — Hugging Face Hub docs — when `hf-xet` is used and how to disable it.
- [Xet transfer telemetry](https://github.com/huggingface/hub-docs/blob/main/docs/hub/xet/telemetry.md) — Hugging Face Hub docs — what `hf-xet` 1.7.0 and later report after each transfer; opt out with `HF_HUB_DISABLE_TELEMETRY=1`.
- [vLLM default weight loader, main branch](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/model_loader/default_loader.py) — vLLM project, main (not pinned) — `--load-format auto` prefers safetensors and picks the Mistral format when `consolidated*.safetensors` exists.
- [vLLM load config, main branch](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/config/load.py) — vLLM project, main (not pinned) — default `ignore_patterns` (`original/**/*`) and format choices.
- [vLLM weight download utilities at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/model_executor/model_loader/weight_utils.py) — vLLM project — offline-mode handling, index-file based file selection, online-FP8 deprecation log.

## NVIDIA

### The workshop GPU: RTX PRO 6000 Blackwell

- [RTX PRO 6000 Blackwell Server Edition product page](https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/) — NVIDIA — the workshop GPU: 96 GB GDDR7, 1597 GB/s; its FP4, FP8 and FP16 headline figures carry no sparsity label and match the sparse numbers.
- [NVIDIA RTX PRO Blackwell GPU architecture whitepaper v1.1](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf) — NVIDIA — dense and sparse peak rates (Table 4), SM count, L2 and register-file sizes, footnote on boost clock.
- [RTX PRO 6000 family page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/) — NVIDIA — power and cooling per variant (Server 400 to 600 W, passive).
- [RTX PRO 6000 Workstation Edition page](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/) — NVIDIA — the 1792 GB/s sibling card, for the bandwidth comparison.
- [RTX PRO 6000 Workstation Edition datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf) — NVIDIA — "4000 AI TOPS" is theoretical sparse FP4; MIG profiles.
- [RTX PRO 6000 Max-Q datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/products/workstations/professional-desktop-gpus/rtx-pro-6000-max-q/workstation-datasheet-blackwell-rtx-pro-6000-max-q-nvidia-3519233.pdf) — NVIDIA — the 300 W variant.
- [CUDA GPUs and compute capability](https://developer.nvidia.com/cuda-gpus) — NVIDIA — compute capability 12.0 for RTX PRO 6000 and RTX 5090, 8.9 for L4, L40S and RTX 4090.
- [NVIDIA-hosted RTX PRO 6000 literature page](https://resources.nvidia.com/en-us-rtx-pro-6000) — NVIDIA — where the Server Edition datasheet is hosted; the PDFs there are password protected and could not be read (unverified).

### Other GPUs and generations, for comparison

- [H100 page](https://www.nvidia.com/en-us/data-center/h100/) — NVIDIA — SXM and NVL specs; footnote marks the headline tensor numbers as with sparsity.
- [H100 PCIe product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/data-center/h100/PB-11133-001_v01.pdf) — NVIDIA — clocks, power modes, NVLink bridge bandwidth (its overview text contradicts its own table).
- [H200 page](https://www.nvidia.com/en-us/data-center/h200/) — NVIDIA — 141 GB HBM3e and 4.8 TB/s; marked preliminary.
- [HGX platform page](https://www.nvidia.com/en-us/data-center/hgx/) — NVIDIA — HGX B200 totals, sparse versus dense footnotes, NVLink 5.
- [DGX B200 page](https://www.nvidia.com/en-us/data-center/dgx-b200/) — NVIDIA — 1,440 GB across 8 GPUs, which gives 180 GB per B200 rather than 192 GB.
- [A100 page](https://www.nvidia.com/en-us/data-center/a100/) — NVIDIA — TDP footnotes for SXM and HGX variants.
- [A100 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf) — NVIDIA, 2021 — dense and sparse rates, bandwidth, MIG, NVLink for PCIe and SXM.
- [L40S page](https://www.nvidia.com/en-us/data-center/l40s/) — NVIDIA — 48 GB GDDR6, 864 GB/s, no MIG, no NVLink.
- [L4 page](https://www.nvidia.com/en-us/data-center/l4/) — NVIDIA — 24 GB, 300 GB/s, 72 W, sparse-marked figures.
- [L4 product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/l4/PB-11316-001_v01.pdf) — NVIDIA — memory bandwidth and PCIe options.
- [GeForce RTX 5090 page](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/) — NVIDIA — 32 GB, 575 W, "AI TOPS" headline (sparse FP4).
- [GeForce RTX 4090 page](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/) — NVIDIA — 24 GB, 450 W, "AI TOPS" headline.
- [GeForce RTX Blackwell architecture whitepaper](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf) — NVIDIA — Table 3: FP32-accumulate tensor rate is half the FP16-accumulate rate on GeForce.
- [Ada GPU architecture whitepaper v2.1](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf) — NVIDIA — L4 and L40 tables, FP8 tensor cores.
- [Volta architecture whitepaper](https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf) — NVIDIA, 2017 — first tensor cores, 125 tensor TFLOPS, 900 GB/s HBM2.
- [NVIDIA Ampere architecture in depth](https://developer.nvidia.com/blog/nvidia-ampere-architecture-in-depth/) — NVIDIA Technical Blog, 2020-05-14 — BF16, TF32, structured sparsity, MIG, 40 MB L2.
- [NVIDIA Hopper architecture in depth](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/) — NVIDIA Technical Blog — SM, shared memory and L2 sizes, TMA, clusters.
- [Hopper architecture technology page](https://www.nvidia.com/en-us/data-center/technologies/hopper-architecture/) — NVIDIA — NVLink 900 GB/s stated as bidirectional.
- [Blackwell architecture page](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) — NVIDIA — second-generation Transformer Engine, FP4, 208 billion transistors.
- [Inside NVIDIA Blackwell Ultra](https://developer.nvidia.com/blog/inside-nvidia-blackwell-ultra-the-chip-powering-the-ai-factory-era/) — NVIDIA Technical Blog — dense versus sparse NVFP4 and FP8, 192 GB maximum HBM, per-SM resources.
- [CUDA MPS memory-performance blog](https://developer.nvidia.com/blog/boost-gpu-memory-performance-with-no-code-changes-using-nvidia-cuda-mps/) — NVIDIA Technical Blog — B200 "normally has 148 SMs".
- [Rubin technology page](https://www.nvidia.com/en-us/data-center/technologies/rubin/) — NVIDIA — outlook only; adaptive-compression Transformer Engine.
- [Vera Rubin NVL72 page](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/) — NVIDIA — Rubin per-GPU figures, labelled sparse or dense per row.
- [H100 datasheet, Chinese edition](https://images.nvidia.cn/aem-dam/en-zz/Solutions/data-center/h100/nvidia-h100-datasheet-nvidia-a4-2287922-r7-zhCN.pdf) — NVIDIA — "7x PCIe 5.0" NVLink comparison.
- [NVIDIA Hopper announcement](https://nvidianews.nvidia.com/news/nvidia-announces-hopper-architecture-the-next-generation-of-accelerated-computing) — NVIDIA press release, 2022-03-22 — generation dating and Transformer Engine claim.
- [NVIDIA Blackwell platform announcement](https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Blackwell-Platform-Arrives-to-Power-a-New-Era-of-Computing/default.aspx) — NVIDIA press release, 2024-03-18 — NVLink 1.8 TB/s stated as bidirectional, FP4 inference.
- [Vera Rubin full-production announcement](https://nvidianews.nvidia.com/news/vera-rubin-full-production-agentic-ai-factory) — NVIDIA press release, 2026-05-31 — Rubin timing, for the generations slide.
- [NVIDIA Ada launch release](https://nvidianews.nvidia.com/_gallery/download_pdf/6329dad6ed6ae51abfa606f4/) — NVIDIA press release — Ada launch; the exact date was not shown in the retrieved copy (unverified).

### Interconnect

- [NVLink page](https://www.nvidia.com/en-us/data-center/nvlink/) — NVIDIA — NVLink generations and bandwidth per GPU (preliminary for newer rows), NVLink Switch.

### CUDA, drivers and containers

- [CUDA Toolkit release notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html) — NVIDIA — toolkit-to-driver-branch table, minor-version compatibility (13.x needs driver 580 or newer), driver no longer bundled.
- [CUDA minor-version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) — NVIDIA — what an older driver can run and the PTX caveat.
- [CUDA forward compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html) — NVIDIA — `cuda-compat` packages, supported products, error codes 803 and 804.
- [CUDA toolkit, driver and architecture matrix](https://docs.nvidia.com/datacenter/tesla/drivers/cuda-toolkit-driver-and-architecture-matrix.html) — NVIDIA — first CUDA version per architecture (Blackwell 12.8); `nvidia-smi` reports the driver's maximum CUDA.
- [Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html) — NVIDIA — per-SM limits for compute capability 10.0 and 12.0, L2 size.
- [Hopper tuning guide](https://docs.nvidia.com/cuda/hopper-tuning-guide/index.html) — NVIDIA — shared-memory carve-outs, qualitative L2 statements.
- [CUDA programming guide: programming model](https://docs.nvidia.com/cuda/cuda-programming-guide/01-introduction/programming-model.html) — NVIDIA — SMs, warps and the memory hierarchy vocabulary.
- [CUDA programming guide: compute capabilities appendix](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html) — NVIDIA — per-capability limits; its 12.x shared-memory figure differs from the tuning guide.
- [CUDA C best practices guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) — NVIDIA — shared-memory banks (32 banks, 32 bits per clock).
- [Container Toolkit install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) — NVIDIA — installing the toolkit and configuring Docker with `nvidia-ctk`.
- [Container Toolkit sample workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html) — NVIDIA — the `nvidia-smi` smoke test in a container.
- [Container Toolkit: specialised Docker configuration](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html) — NVIDIA — `--gpus` forms, `NVIDIA_VISIBLE_DEVICES`, `NVIDIA_DRIVER_CAPABILITIES`.
- [Container Toolkit architecture overview](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/arch-overview.html) — NVIDIA — runtime, hook and `nvidia-ctk` components.
- [GPU Operator overview](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html) — NVIDIA — Kubernetes bundle including DCGM Exporter and MIG manager.
- [Docker Compose GPU support](https://docs.docker.com/compose/how-tos/gpu-support/) — Docker docs — `deploy.resources.reservations.devices` for the reference compose stack.

### Monitoring and telemetry

- [nvidia-smi documentation](https://docs.nvidia.com/deploy/nvidia-smi/index.html) — NVIDIA — `dmon`, `pmon`, `topo -m` legend, memory and power readings, MIG limits.
- [Useful nvidia-smi queries](https://nvidia.custhelp.com/app/answers/detail/a_id/3751/~/useful-nvidia-smi-queries) — NVIDIA support article — `--query-gpu` field names and what `utilization.gpu` measures.
- [NVML utilization struct](https://docs.nvidia.com/deploy/nvml-api/api/structnvmlUtilization__t.html) — NVIDIA — GPU-Util is the share of time a kernel was running, not an efficiency measure.
- [NVML memory struct](https://docs.nvidia.com/deploy/nvml-api/api/structnvmlMemory__t.html) — NVIDIA — total, free, used and reserved memory semantics.
- [NVML device queries](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html) — NVIDIA — power-usage averaging, clock-event reasons, MIG utilisation limits, ECC scrubbing note.
- [nvidia-ml-py on PyPI](https://pypi.org/project/nvidia-ml-py/) — NVIDIA, 13.615.71, 2026-09-25 — the `pynvml` module used by the NVML exporter.
- [DCGM feature overview](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html) — NVIDIA — definitions of `PROF_SM_ACTIVE`, `PROF_DRAM_ACTIVE`, `PROF_PIPE_TENSOR_ACTIVE`; profiling needs privileges.
- [Installing DCGM Exporter](https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html) — NVIDIA — container run line with `--cap-add SYS_ADMIN`, Helm install, version pairing.
- [dcgm-exporter 4.8.4 release](https://github.com/NVIDIA/dcgm-exporter/releases/tag/4.8.4) — NVIDIA, 2026-09-18 — current exporter release and image tags.
- [dcgm-exporter default counters](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/etc/default-counters.csv) — NVIDIA, main branch — which fields are enabled by default and which profiling fields are opt-in.
- [dcgm-exporter deployment README](https://github.com/NVIDIA/dcgm-exporter/blob/main/deployment/README.md) — NVIDIA — Helm chart values, ServiceMonitor, tolerations.
- [dcgm-exporter release notes (NVIDIA docs)](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/dcgm-exporter.html) — NVIDIA — lags the GitHub releases; distroless default.
- [dcgm-exporter container tests README](https://github.com/NVIDIA/dcgm-exporter/blob/main/tests/container/README.md) — NVIDIA — image variant names.
- [GPU telemetry: dcgm-exporter (older page)](https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/latest/dcgm-exporter.html) — NVIDIA — stale commands; use only for the `-f` and `-a` option names.
- [NVIDIA GPU performance counter permission article](https://developer.nvidia.com/nvidia-development-tools-solutions-err_nvgpuctrperm-permission-issue-performance-counters) — NVIDIA — `NVreg_RestrictProfilingToAdminUsers`, `CAP_SYS_ADMIN` in containers.

### MIG

- [MIG user guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/index.html) — NVIDIA — overview of isolated GPU partitions.
- [MIG concepts](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/concepts.html) — NVIDIA — GPU instance versus compute instance, profile naming, isolation guarantees.
- [MIG supported GPUs](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html) — NVIDIA — RTX PRO 6000 supported (up to 4 instances); L4, L40S, RTX 4090 and 5090 are not.
- [MIG supported profiles](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-mig-profiles.html) — NVIDIA — `1g.24gb`, `2g.48gb`, `4g.96gb` on RTX PRO 6000 and the H100 profile table.

### Performance guides and technical posts

- [GPU performance background](https://docs.nvidia.com/deeplearning/performance/dl-performance-gpu-background/index.html) — NVIDIA Deep Learning Performance guide — ops:byte ratio, arithmetic intensity, math-limited versus memory-limited.
- [Matrix multiplication performance guide](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html) — NVIDIA Deep Learning Performance guide — GEMM arithmetic intensity, why matrix-vector work is memory-limited.
- [Mastering LLM techniques: inference optimization](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/) — NVIDIA Technical Blog — prefill versus decode bottlenecks and the KV-cache size formula (multi-head form).
- [TensorRT benchmarking guidance](https://docs.nvidia.com/deeplearning/tensorrt/11.4.0/performance/benchmarking.html) — NVIDIA — clock locking, power and thermal throttling, `nvidia-smi dmon -s pcu` alongside every benchmark.

### Secondary sources used only for orientation

Copies of NVIDIA documents on third-party hosts, and a reseller guide. The NVIDIA-hosted Server Edition datasheet is password protected, which is why a hosted copy was read. Confirm any number against NVIDIA's own pages above before using it on a slide.

- [RTX PRO 6000 Server Edition datasheet, hosted copy](https://www.akamai.com/site/en/documents/corporate/nvidia-rtx-pro-6000-blackwell-server-edition-datasheet.pdf) — copy of NVIDIA document 3850600 (April 2025) on a CDN host — spec table including 1597 GB/s, 600 W configurable, PCIe Gen5, MIG up to 4 at 24 GB.
- [H100 PCIe datasheet, hosted copy](https://www.pny.com/file%20library/company/support/product%20brochures/nvidia%20data%20center%20gpus/nvidia-h100-datasheet.pdf) — copy of NVIDIA's datasheet on PNY's site — PCIe rates; its text extraction lacks the sparsity footnote.
- [Hopper architecture whitepaper, university mirror](https://www.ece.lsu.edu/koppel/gp/refs/gtc22-whitepaper-hopper.pdf) — mirror of NVIDIA's "H100 Tensor Core GPU Architecture" whitepaper v1.02 at LSU — SM counts, L2, register file, occupancy limits.
- [Lenovo ThinkSystem RTX PRO 6000 product guide](https://lenovopress.lenovo.com/lp2263.pdf) — Lenovo Press, reprints NVIDIA specs — states "NVLink support: No" for the Server Edition, which NVIDIA's own pages do not list.

## Model cards

Model repositories change. The workshop pins each model by full commit SHA (see the model configuration and `docs/RESEARCH.md`); the links below point at `main`, so re-read the card at the pinned revision before quoting it.

### Pinned workshop models (Qwen3 family)

- [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) — Qwen, Apache-2.0 — pinned dense model (8.2B, 36 layers, 8 KV heads, BF16); the card's `--enable-reasoning --reasoning-parser deepseek_r1` line is stale, use `--reasoning-parser qwen3`.
- [Qwen/Qwen3-8B-FP8](https://huggingface.co/Qwen/Qwen3-8B-FP8) — Qwen, Apache-2.0 — pinned block-wise FP8 build (128 by 128, 9.44 GB) for the quantization comparison.
- [Qwen/Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) — Qwen, Apache-2.0 — pinned small dense model for quick runs.
- [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) — Qwen, Apache-2.0 — pinned embedding model for the RAG demo; serve with `--runner pooling` because the card's `task="embed"` snippet is outdated.
- [Qwen/Qwen3-30B-A3B-FP8](https://huggingface.co/Qwen/Qwen3-30B-A3B-FP8) — Qwen, Apache-2.0 — pinned MoE example (30.5B total, 3.3B active) with hybrid thinking.
- [Qwen/Qwen3-30B-A3B-Instruct-2507-FP8](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8) — Qwen, Apache-2.0 — the 2507 generation: non-thinking only, 262,144 native context, so it behaves differently from the original FP8 build.
- [Qwen/Qwen3-8B-GGUF](https://huggingface.co/Qwen/Qwen3-8B-GGUF) — Qwen, Apache-2.0 — official GGUF quantisations (Q4_K_M to Q8_0) for the llama.cpp and Ollama comparison.
- [RedHatAI/Qwen3-8B-NVFP4](https://huggingface.co/RedHatAI/Qwen3-8B-NVFP4) — Red Hat AI, Apache-2.0 — NVFP4 build in compressed-tensors format that is documented for vLLM.
- [nvidia/Qwen3-8B-NVFP4](https://huggingface.co/nvidia/Qwen3-8B-NVFP4) — NVIDIA, Apache-2.0 — ModelOpt NVFP4 build; the card lists only TensorRT-LLM as supported runtime, so test it in vLLM before relying on it.
- [Qwen3-8B licence file](https://huggingface.co/Qwen/Qwen3-8B/blob/main/LICENSE) — Qwen — stock Apache-2.0 text, the licence evidence for the pinned Qwen3 models.

### Repository files used for arithmetic and behaviour

- [Qwen3-8B config.json](https://huggingface.co/Qwen/Qwen3-8B/raw/main/config.json) — Qwen — 36 layers, 8 KV heads, head dimension 128: inputs to the KV-cache formula.
- [Qwen3-8B generation_config.json](https://huggingface.co/Qwen/Qwen3-8B/raw/main/generation_config.json) — Qwen — default sampling that `--generation-config auto` applies silently.
- [Qwen3-8B tokenizer_config.json](https://huggingface.co/Qwen/Qwen3-8B/raw/main/tokenizer_config.json) — Qwen — chat template: thinking on by default, Hermes-style `<tool_call>` blocks.
- [Qwen3-8B-FP8 config.json](https://huggingface.co/Qwen/Qwen3-8B-FP8/raw/main/config.json) — Qwen — `quantization_config` with block-wise E4M3 weights and dynamic activations.
- [Qwen3-1.7B config.json](https://huggingface.co/Qwen/Qwen3-1.7B/raw/main/config.json) — Qwen — 28 layers, 8 KV heads, tied embeddings.
- [Qwen3-30B-A3B-FP8 config.json](https://huggingface.co/Qwen/Qwen3-30B-A3B-FP8/raw/main/config.json) — Qwen — 48 layers, 4 KV heads, 128 experts with 8 active.
- [Qwen3-30B-A3B-Instruct-2507-FP8 config.json](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8/raw/main/config.json) — Qwen — 262,144 position embeddings and a larger rope theta than the original build.
- [Qwen3-30B-A3B-Instruct-2507-FP8 tokenizer_config.json](https://huggingface.co/Qwen/Qwen3-30B-A3B-Instruct-2507-FP8/raw/main/tokenizer_config.json) — Qwen — template without `enable_thinking`, with JSON tool calls.
- [Qwen3-Embedding-0.6B config.json](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/raw/main/config.json) — Qwen — stored as a causal LM architecture, 28 layers.
- [Qwen3-Embedding-0.6B pooling config](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/raw/main/1_Pooling/config.json) — Qwen — last-token pooling.
- [Qwen3-Embedding-0.6B modules.json](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/raw/main/modules.json) — Qwen — the Sentence-Transformers pipeline (transformer, pooling, normalise).
- [nvidia/Qwen3-8B-NVFP4 hf_quant_config.json](https://huggingface.co/nvidia/Qwen3-8B-NVFP4/raw/main/hf_quant_config.json) — NVIDIA — `quant_algo` NVFP4, FP8 KV cache, group size 16.
- [RedHatAI/Qwen3-8B-NVFP4 config.json](https://huggingface.co/RedHatAI/Qwen3-8B-NVFP4/raw/main/config.json) — Red Hat AI — compressed-tensors `nvfp4-pack-quantized` configuration.

### Model-selection lab: alternative families

- [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) — Qwen, Apache-2.0 — hybrid Gated-DeltaNet model with only 8 full-attention layers, so far less KV cache per token; needs `--tool-call-parser qwen3_coder`.
- [Qwen3.5-9B config.json](https://huggingface.co/Qwen/Qwen3.5-9B/raw/main/config.json) — Qwen — `layer_types` (24 linear, 8 full attention), 4 KV heads, head dimension 256.
- [Qwen3.5-9B tokenizer_config.json](https://huggingface.co/Qwen/Qwen3.5-9B/raw/main/tokenizer_config.json) — Qwen — thinking on by default and XML-style tool calls.
- [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) — Qwen, Apache-2.0 — current dense Qwen tier that is still Apache-licensed.
- [Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) — Qwen, Qwen Community License 1.0 — example of a Qwen model outside Apache-2.0.
- [Qwen/Qwen3.8-2.4T-A95B](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) — Qwen, Qwen3.8-Max License — flagship MoE under a custom licence.
- [Qwen/Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) — Qwen, Apache-2.0 — open coding MoE with the `qwen3_coder` tool parser.
- [Qwen/Qwen3-Coder-Next](https://huggingface.co/Qwen/Qwen3-Coder-Next) — Qwen, Apache-2.0 — larger hybrid coding model (80B total, 3B active).
- [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) — Google, Apache-2.0 — Gemma 4 card: thinking via a system-prompt token, native function calling, 35+ languages out of the box.
- [Gemma 4 31B config.json](https://huggingface.co/google/gemma-4-31B-it/raw/main/config.json) — Google — dense 60 layers, 16 KV heads, sliding-window plus full-attention pattern.
- [Gemma 4 26B-A4B config.json](https://huggingface.co/google/gemma-4-26B-A4B-it/raw/main/config.json) — Google — MoE with 128 experts for the active-versus-total parameter discussion.
- [mistralai/Ministral-3-8B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) — Mistral AI, Apache-2.0 — FP8 main checkpoint and two weight copies in one repo (consolidated and sharded).
- [mistralai/Mistral-Small-4-119B-2603](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603) — Mistral AI, Apache-2.0 — 119B MoE with 6.5B active; card shows an MLA attention backend and the `mistral` parsers.
- [Mistral-Small-4-119B-2603 config.json](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603/raw/main/config.json) — Mistral AI — MLA-style `kv_lora_rank`, expert counts.
- [mistralai/Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512) — Mistral AI, Apache-2.0 — coding model that fits one 24 to 32 GB device.
- [mistralai/Mistral-Large-3-675B-Instruct-2512](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512) — Mistral AI, Apache-2.0 — 675B MoE; shows a model far beyond one GPU.
- [mistralai/Mistral-Medium-3.5-128B](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B) — Mistral AI, Modified MIT — dense 128B under a monthly-revenue ceiling licence.
- [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) — OpenAI, Apache-2.0 plus usage policy — MXFP4 MoE (21B total, 3.6B active), harmony format required, repo holds three weight copies.
- [gpt-oss-120b config.json](https://huggingface.co/openai/gpt-oss-120b/raw/main/config.json) — OpenAI — 36 layers, 128 experts, 4 active, alternating sliding-window attention.
- [ibm-granite/granite-4.2-8b](https://huggingface.co/ibm-granite/granite-4.2-8b) — IBM, Apache-2.0 — 8B dense candidate with German among its tested languages; needs a parser plugin file.
- [utter-project/EuroLLM-9B-Instruct-2512](https://huggingface.co/utter-project/EuroLLM-9B-Instruct-2512) — EuroLLM project, Apache-2.0 — covers the official EU languages; European-sovereignty candidate.
- [nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16) — NVIDIA, OpenMDW-1.1 — hybrid 30B MoE with `auto` parser resolution in vLLM.
- [zai-org/GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash) — Z.AI, MIT — multimodal MoE (320B total, 18B active) with the `glm45` and `glm47` parsers.
- [deepseek-ai/DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) — DeepSeek, MIT — ships no Jinja chat template, a poor fit for a "just run vllm serve" lab.
- [deepseek-ai/DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) — DeepSeek, MIT — preview card for the 1.6T MoE with one-million-token context.
- [deepseek-ai/DeepSeek-V4-Pro-0813](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813) — DeepSeek, MIT — updated checkpoint; confirms the MIT statement.
- [moonshotai/Kimi-K3](https://huggingface.co/moonshotai/Kimi-K3) — Moonshot AI, Kimi K3 License — 2.8T MoE, thinking always on, needs `reasoning_content` passed back in multi-turn.
- [Kimi-K3 config.json](https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json) — Moonshot AI — contains `auto_map`, i.e. ships remote code.
- [moonshotai/Kimi-K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) — Moonshot AI, Modified MIT — 1T MoE with INT4 weights.
- [Kimi-K2.6 config.json](https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/config.json) — Moonshot AI — contains `auto_map`, so `trust_remote_code` would be required.
- [meta-models/Muse-Glimmer-30B](https://huggingface.co/meta-models/Muse-Glimmer-30B) — Meta, Apache-2.0 plus a separate usage policy — Meta's newest open-weight model; Meta has published no new `meta-llama` model since April 2025.
- [Llama 3.1 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/MODEL_CARD.md) — Meta, llama-models repository — eight supported languages including German, December 2023 data cutoff.
- [Llama 4 model card](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/MODEL_CARD.md) — Meta, llama-models repository — Scout and Maverick sizes, context lengths, twelve supported languages.

### Licences, usage policies and the open-source question

- [Llama 4 Community License](https://www.llama.com/llama4/license/) — Meta — "Built with Llama" display, "Llama" model-name prefix, 700 million monthly-active-user clause.
- [Llama 4 Acceptable Use Policy](https://www.llama.com/llama4/use-policy/) — Meta — the EU multimodal-rights restriction sits here, not in the licence text.
- [Llama 3.2 use policy](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_2/USE_POLICY.md) — Meta, llama-models repository — first policy with the EU multimodal restriction.
- [Llama 3.3 use policy](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_3/USE_POLICY.md) — Meta, llama-models repository — repeats the clause although 3.3 has no multimodal model.
- [Llama 3.1 use policy](https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/USE_POLICY.md) — Meta, llama-models repository — no EU clause.
- [Qwen3.8-2.4T-A95B licence text](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/LICENSE) — Qwen — custom licence: name display above a user or revenue threshold, separate licence for large Model-as-a-Service businesses.
- [Qwen3.8-Flash-Next licence text](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE) — Qwen — Community License 1.0: same conditions without the revenue threshold on the service clause.
- [Mistral Medium 3.5 licence text](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B/raw/main/LICENSE) — Mistral AI — Modified MIT: no rights if the licensee's consolidated monthly revenue exceeds 20 million dollars.
- [Devstral 2 licence text](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/raw/main/LICENSE) — Mistral AI — same Modified MIT with a different attribution year.
- [Kimi K3 licence text](https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE) — Moonshot AI — stricter than Modified MIT: Model-as-a-Service agreement and name-display rules.
- [Kimi K2.6 licence text](https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/LICENSE) — Moonshot AI — Modified MIT with a "Kimi K2.6" display condition.
- [Kimi K2.7-Code licence text](https://huggingface.co/moonshotai/Kimi-K2.7-Code/raw/main/LICENSE) — Moonshot AI — Modified MIT with a model-specific display string.
- [Kimi K2 Instruct 0905 licence text](https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905/raw/main/LICENSE) — Moonshot AI — the earlier Modified MIT wording.
- [GLM-5.3 licence text](https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE) — Z.AI — MIT-like grant with a security-review condition for very large service businesses; GLM-5.3-Flash stays MIT.
- [DeepSeek V4.1-Flash licence text](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/LICENSE) — DeepSeek — plain MIT.
- [DeepSeek-V3 model licence](https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/LICENSE-MODEL) — DeepSeek — the earlier use-restricted DeepSeek License Agreement v1.0, for the licence-history point.
- [gpt-oss usage policy](https://huggingface.co/openai/gpt-oss-20b/raw/main/USAGE_POLICY) — OpenAI — a one-line "comply with applicable law" policy next to the Apache-2.0 grant.
- [Nemotron 3.5 Lightning licence text](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/raw/main/LICENSE) — NVIDIA — OpenMDW-1.1: permissive, no restrictions on outputs.
- [Gemma 4 licence page](https://ai.google.dev/gemma/docs/gemma_4_license) — Google — standard Apache License 2.0 text for Gemma 4 (earlier Gemma versions used the Gemma Terms of Use).
- [Muse Glimmer usage policy](https://huggingface.co/meta-models/Muse-Glimmer-30B/blob/main/USAGE_POLICY.md) — Meta — prohibited and risk-of-harm uses next to the Apache-2.0 grant; whether it binds beyond Apache-2.0 is open.
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) — Apache Software Foundation — the licence text that most pinned models use; it has no field-of-use restriction.

### Vendor documentation for running the models

- [Qwen docs: deploying with vLLM](https://qwen.readthedocs.io/en/latest/deployment/vllm.html) — Qwen — YaRN setup for long context, out-of-memory mitigations.
- [Qwen docs: function calling](https://qwen.readthedocs.io/en/latest/framework/function_call.html) — Qwen — `hermes` tool parser for Qwen3 (its `deepseek_r1` reasoning flag is stale).
- [Qwen3 announcement](https://qwenlm.github.io/blog/qwen3/) — Qwen blog — the 119-language claim and the model lineup.
- [vLLM recipe for Qwen3.5-9B](https://recipes.vllm.ai/Qwen/Qwen3.5-9B) — vLLM project — serve and tool-call flags, needs vLLM 0.17 or newer.
- [vLLM recipe for Qwen3.8-27B](https://recipes.vllm.ai/Qwen/Qwen3.8-27B) — vLLM project — named in the notes but not opened (unverified).

### Ollama library entries

- [Ollama library: qwen3:8b](https://ollama.com/library/qwen3:8b) — Ollama — packaged as Q4_K_M, 5.2 GB, 40K context, `tools` and `thinking` capabilities.
- [Ollama library: qwen3 tags](https://ollama.com/library/qwen3/tags) — Ollama — other quantisations (`q8_0`, `fp16`) and sizes.
- [Ollama library: qwen3](https://ollama.com/library/qwen3) — Ollama — model family page with all sizes.
- [Ollama library: qwen3.5](https://ollama.com/library/qwen3.5) — Ollama — newer Qwen builds with image input.
- [Ollama library: qwen3.6](https://ollama.com/library/qwen3.6) — Ollama — 27B and 35B packages.
- [Ollama library: qwen3.8](https://ollama.com/library/qwen3.8) — Ollama — 27B package.
- [Ollama library: gemma4](https://ollama.com/library/gemma4) — Ollama — Gemma 4 sizes and download sizes.
- [Ollama library: gpt-oss](https://ollama.com/library/gpt-oss) — Ollama — 20B (14 GB) and 120B (65 GB) packages.

## Inference research

Papers are listed once, at their canonical page (arXiv, USENIX or a DOI record). Alternate proceedings pages and PDF copies are not repeated; where a venue was confirmed on such a page, the venue is named in the entry. Publisher pages at the ACM returned HTTP 403, so those entries rely on Crossref metadata.

### Attention and architectures

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin; NeurIPS 2017 — the decoder-only forward pass: attention, KV, and why prefill is parallel but decode is sequential.
- [Fast Transformer Decoding: One Write-Head is All You Need](https://arxiv.org/abs/1911.02150) — Shazeer; arXiv preprint, 2019 — multi-query attention, the first step of the MQA, GQA, MLA progression that shrinks the KV cache.
- [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints](https://arxiv.org/abs/2305.13245) — Ainslie et al.; EMNLP 2023 — why `num_kv_heads` appears in the KV-bytes-per-token formula.
- [DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model](https://arxiv.org/abs/2405.04434) — DeepSeek-AI et al.; arXiv preprint, 2024 — Multi-head Latent Attention and its 93.3 percent KV-cache reduction; why MLA models need their own attention backend.
- [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135) — Dao, Fu, Ermon, Rudra, Ré; NeurIPS 2022 — IO-aware reasoning behind vLLM's FlashAttention-based backends.
- [FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](https://arxiv.org/abs/2307.08691) — Dao; ICLR 2024 (venue from the ICLR listing, not the arXiv page) — the FA2 backend that SM120 runs.
- [FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision](https://arxiv.org/abs/2407.08608) — Shah et al.; NeurIPS 2024 — why Hopper and FP8 change attention performance; quoted speedups differ by arXiv version, so cite the version.
- [Mixtral of Experts](https://arxiv.org/abs/2401.04088) — Jiang et al.; arXiv preprint, 2024 — total versus active parameters: memory follows total, FLOPs follow active.
- [DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models](https://arxiv.org/abs/2401.06066) — Dai et al.; ACL 2024 — shared plus routed experts, optional MoE background.
- [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388) — Yang et al.; arXiv preprint, 2025 — the Qwen3 family, thinking budget, the "smallest model that satisfies the task" ladder.
- [The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783) — Grattafiori et al.; arXiv preprint, 2024 — dense reference point with GQA for KV-size examples (optional).
- [gpt-oss-120b & gpt-oss-20b Model Card](https://arxiv.org/abs/2508.10925) — OpenAI; arXiv preprint, 2025 — small open-weight MoE option; check memory claims against the Hugging Face card before using them.
- [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) — Hoffmann et al.; arXiv preprint, 2022 — a one-line justification that smaller, well-trained models are cheaper to serve (optional).

### Serving systems

- [Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) — Kwon et al.; SOSP 2023 — the block-based KV cache behind `--gpu-memory-utilization`, `--max-num-seqs` and preemption.
- [Orca: A Distributed Serving System for Transformer-Based Generative Models](https://www.usenix.org/conference/osdi22/presentation/yu) — Yu, Jeong, Kim, Kim, Chun; OSDI 2022 — iteration-level scheduling, the basis of continuous batching.
- [Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve](https://www.usenix.org/conference/osdi24/presentation/agrawal) — Agrawal et al.; OSDI 2024 — chunked prefill and stall-free scheduling behind `--max-num-batched-tokens` tuning.
- [SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/abs/2312.07104) — Zheng et al.; NeurIPS 2024 — RadixAttention (not a standalone paper), compared with vLLM's automatic prefix caching.
- [DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin) — Zhong et al.; OSDI 2024 — prefill and decode disaggregation and the origin of the goodput metric.
- [Splitwise: Efficient generative LLM inference using phase splitting](https://arxiv.org/abs/2311.18677) — Patel et al.; ISCA 2024 — phase splitting with heterogeneous hardware and the cost angle.
- [Mooncake: Trading More Storage for Less Computation — A KVCache-centric Architecture for Serving LLM Chatbot](https://www.usenix.org/conference/fast25/presentation/qin) — Qin et al.; USENIX FAST 2025, Best Paper — the peer-reviewed version; KV-cache offloading and pooling.
- [Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving](https://arxiv.org/abs/2407.00079) — Qin et al.; arXiv preprint, 2024 (revised 2026) — same system under its arXiv title; cite both titles.
- [FlexGen: High-Throughput Generative Inference of Large Language Models with a Single GPU](https://arxiv.org/abs/2303.06865) — Sheng et al.; ICML 2023 — when memory-constrained: offload versus smaller model or quantization (optional).

### Parallelism

- [Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism](https://arxiv.org/abs/1909.08053) — Shoeybi et al.; arXiv preprint, 2019 — tensor parallelism and why `--tensor-parallel-size` needs fast interconnect.
- [Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM](https://arxiv.org/abs/2104.04473) — Narayanan et al.; SC 2021 — trade-offs among tensor, pipeline and data parallelism: TP inside a node, PP across nodes (optional).
- [GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism](https://arxiv.org/abs/1811.06965) — Huang et al.; NeurIPS 2019 — pipeline stages, micro-batches and the bubble.
- [PipeDream: Generalized Pipeline Parallelism for DNN Training](https://doi.org/10.1145/3341301.3359646) — Narayanan et al.; SOSP 2019 — 1F1B schedule; metadata checked via Crossref because the ACM page returned 403.
- [PipeDream: Fast and Efficient Pipeline Parallel DNN Training](https://arxiv.org/abs/1806.03377) — Harlap et al.; arXiv preprint, 2018 — the earlier version under a different title.
- [Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961) — Fedus, Zoph, Shazeer; JMLR 23(120), 2022 — top-1 routing, capacity factor and load imbalance for expert parallelism.
- [GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding](https://arxiv.org/abs/2006.16668) — Lepikhin et al.; ICLR 2021 (venue from Google Research and mlanthology listings) — expert-parallel all-to-all dispatch.

### Speculative decoding

- [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192) — Leviathan, Kalman, Matias; ICML 2023 (oral) — why verifying k tokens is almost free in memory-bound decode; acceptance-rate economics.
- [Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/abs/2302.01318) — Chen et al., DeepMind; arXiv preprint, 2023 — the concurrent derivation of the same idea.
- [Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads](https://arxiv.org/abs/2401.10774) — Cai et al.; ICML 2024 — draft-model-free speculation; reported speedups vary by arXiv version.
- [EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty](https://arxiv.org/abs/2401.15077) — Li, Wei, Zhang, Zhang; ICML 2024 — feature-level drafting; one of the methods in vLLM's `--speculative-config`.
- [EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees](https://arxiv.org/abs/2406.16858) — Li et al.; arXiv preprint, 2024 (conference venue unconfirmed) — dynamic draft trees, the bridge to EAGLE-3 (optional).
- [EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test](https://arxiv.org/abs/2503.01840) — Li et al.; NeurIPS 2025 — whether speculation still helps at high batch size; current EAGLE-3 draft models.

### Quantization

- [FP8 Formats for Deep Learning](https://arxiv.org/abs/2209.05433) — Micikevicius et al.; arXiv preprint, 2022 — E4M3 versus E5M2 behind `--quantization fp8` and `--kv-cache-dtype fp8`.
- [AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration](https://arxiv.org/abs/2306.00978) — Lin et al.; MLSys 2024, Best Paper — weight-only INT4 with a light calibration workflow.
- [GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers](https://arxiv.org/abs/2210.17323) — Frantar, Ashkboos, Hoefler, Alistarh; ICLR 2023 — weight-only 3 to 4 bit quantization and the memory-bandwidth argument.
- [SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models](https://arxiv.org/abs/2211.10438) — Xiao et al.; ICML 2023 — W8A8 and compute-bound versus memory-bound regimes.
- [LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale](https://arxiv.org/abs/2208.07339) — Dettmers, Lewis, Belkada, Zettlemoyer; NeurIPS 2022 — activation outliers and why naive W8A8 fails.
- [Introducing NVFP4 for Efficient and Accurate Low-Precision Inference](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/) — Alvarez et al., NVIDIA Technical Blog, 2025-06-24 — NVFP4 (16-value blocks, FP8 scale) versus MXFP4; Blackwell only.
- [OCP Microscaling Formats (MX) Specification, Version 1.0](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf) — Open Compute Project, September 2023 — the authoritative definition of MXFP8, MXFP6, MXFP4 with a shared E8M0 block scale.
- [Microscaling Data Formats for Deep Learning](https://arxiv.org/abs/2310.10537) — Rouhani et al.; arXiv preprint, 2023 — the evaluation behind the MX formats.
- [Pretraining Large Language Models with NVFP4](https://arxiv.org/abs/2509.25149) — NVIDIA et al.; arXiv preprint, 2025 — evidence that 4-bit NVFP4 is viable beyond inference.
- [KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache](https://arxiv.org/abs/2402.02750) — Liu et al.; ICML 2024 — keys per channel, values per token (optional).
- [KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization](https://arxiv.org/abs/2401.18079) — Hooper et al.; NeurIPS 2024 — sub-4-bit KV caches and long-context budgeting (optional).

### Performance modelling

- [Efficiently Scaling Transformer Inference](https://arxiv.org/abs/2211.05102) — Pope et al., Google; MLSys 2023 — the "memory time" model: weights and KV cache loaded from HBM every step; basis of the decode lower-bound equation.
- [Roofline: An Insightful Visual Performance Model for Floating-Point Programs and Multicore Architectures](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.html) — Williams, Waterman, Patterson; UC Berkeley tech report EECS-2008-134, 2008 — the roofline plot and ridge point behind the "is decode memory-bound" exercise.
- [Roofline: An Insightful Visual Performance Model for Multicore Architectures](https://doi.org/10.1145/1498765.1498785) — Williams, Waterman, Patterson; Communications of the ACM 52(4), 2009 — the journal version; metadata checked via Crossref because the ACM page returned 403.
- [LLM Inference Unveiled: Survey and Roofline Model Insights](https://arxiv.org/abs/2402.16363) — Yuan et al.; arXiv preprint, 2024 — roofline analysis per technique and a reading list.
- [Mind the Memory Gap: Unveiling GPU Bottlenecks in Large-Batch LLM Inference](https://arxiv.org/abs/2503.08311) — Recasens et al.; IEEE CLOUD 2025 — large-batch decode stays DRAM-bound (optional).

### Applications (RAG, tools, agents)

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — Lewis et al.; NeurIPS 2020 — origin of the retrieve-then-generate pattern.
- [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) — Karpukhin et al.; EMNLP 2020 — why dense embeddings and a vector index.
- [Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models](https://arxiv.org/abs/2506.05176) — Zhang et al.; arXiv preprint, 2025 — the open embedding and reranker series used in the RAG demo.
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — Liu et al.; TACL 12, 2024 — chunking, top-k and context ordering: more context is not monotonic.
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Yao et al.; ICLR 2023 — the agent loop and why agents multiply request counts.
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) — Schick et al.; NeurIPS 2023 — the training-side origin of tool calling.
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — Hu et al.; ICLR 2022 — fine-tuned variants served with `--enable-lora`.
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — Dettmers, Pagnoni, Holtzman, Zettlemoyer; NeurIPS 2023 — fine-tune the smallest adequate model on modest hardware.

### Benchmarking methodology

- [GuideLLM repository](https://github.com/vllm-project/guidellm) — vLLM project — load generator with `synchronous`, `concurrent`, `throughput`, `constant`, `poisson`, `sweep` and goodput profiles.
- [GuideLLM guides directory](https://github.com/vllm-project/guidellm/tree/main/docs/en/guides) — vLLM project, main branch — getting-started and profile semantics; flag syntax can change between releases.
- [GuideLLM metrics guide](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/metrics.md) — vLLM project, main branch — its TPOT includes the first token, unlike vLLM's.
- [GuideLLM service-level objectives guide](https://raw.githubusercontent.com/vllm-project/guidellm/main/docs/en/guides/service_level_objectives.md) — vLLM project, main branch — SLO attainment, request goodput, the goodput search profile.
- [AIPerf repository](https://github.com/ai-dynamo/aiperf) — NVIDIA, ai-dynamo project — benchmarking tool positioned as GenAI-Perf's successor.
- [AIPerf metrics reference](https://github.com/ai-dynamo/aiperf/blob/main/docs/metrics-reference.md) — NVIDIA, main branch — code-level definitions of TTFT, ITL, throughput and goodput metrics.
- [AIPerf CLI options](https://github.com/ai-dynamo/aiperf/blob/main/docs/cli-options.md) — NVIDIA, main branch — closed-loop `--concurrency` versus open-loop `--request-rate`.
- [Open Versus Closed: A Cautionary Tale](https://www.usenix.org/conference/nsdi-06/open-versus-closed-cautionary-tale) — Schroeder, Wierman, Harchol-Balter; NSDI 2006 — why `--request-rate` (open) and `--max-concurrency` (closed) give different latencies.
- ["Coordinated Omission" post on the mechanical-sympathy list](https://groups.google.com/g/mechanical-sympathy/c/icNZJejUHfE/m/BfDekfBEs_sJ) — Gil Tene, 2013-08-03 — the written definition of coordinated omission.
- [wrk2](https://github.com/giltene/wrk2) — Gil Tene — constant-rate generator with latency measured from the intended send time.
- [HdrHistogram](https://github.com/HdrHistogram/HdrHistogram) — HdrHistogram project — recording full latency distributions and back-filling stalls.
- [MLPerf Inference Benchmark](https://arxiv.org/abs/1911.02549) — Reddi et al.; ISCA 2020 — LoadGen scenarios SingleStream, MultiStream, Server, Offline.
- [MLPerf Inference rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc) — MLCommons, master branch — per-model TTFT and TPOT limits; percentile rule for LLMs not confirmed in the fetch.
- [Llama 2 70B: an MLPerf Inference benchmark for large language models](https://mlcommons.org/2024/03/mlperf-llama2-70b/) — MLCommons blog, 2024-03-27 — TTFT 2 s and TPOT 200 ms tied to reading speed.
- [NVIDIA NIM LLM benchmarking guide: metrics](https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html) — NVIDIA — TTFT, E2E latency, ITL (equated with TPOT), TPS and RPS formulas.
- [The Tail at Scale](https://research.google/pubs/the-tail-at-scale/) — Dean and Barroso; Communications of the ACM 56(2), 2013 — why the lab reports p50, p95 and p99 rather than means; DOI metadata checked via Crossref.
- [A Proof for the Queuing Formula: L = λW](https://doi.org/10.1287/opre.9.3.383) — Little; Operations Research 9(3), 1961 — concurrency equals throughput times latency, the lab's sanity check; metadata checked via Crossref, paper text not opened.
- [LLMPerf repository](https://github.com/ray-project/llmperf) — Anyscale and Ray project, archived read-only 2025-12-17 — not the workshop default; its README names no TTFT.

### Secondary sources used only for orientation

- [Throughput is Not All You Need: Maximizing Goodput in LLM Serving using Prefill-Decode Disaggregation](https://haoailab.com/blogs/distserve) — Chen, Zhong, Liu, Zhu, Jin, Zhang; Hao AI Lab blog, 2024-03-17 — plain-language goodput explanation with a TTFT 200 ms, TPOT 50 ms, 90 percent example.
- [How NOT to Measure Latency, talk replay page](https://spring.io/blog/2014/06/03/springone2gx-2013-replay-how-not-to-measure-latency) — Gil Tene; SpringOne2GX 2013 — abstract of the talk that introduced coordinated omission.
- [How NOT to Measure Latency, video](https://www.youtube.com/watch?v=0b3sR32m0nU) — Gil Tene; talk recording linked from the replay page — not opened (unverified).
- [How NOT to Measure Latency, QCon SF 2012 slides](https://qconsf.com/sf2012/dl/qcon-sanfran-2012/slides/GilTene_HowNotToMeasureLatency.pdf) — Gil Tene; slides — exceeded the fetch size limit, not read (unverified).

## Security

Two layers are kept apart: infrastructure security (the serving process, network, images, weights, caches, logs) and LLM application security (prompts, tools, agents, outputs).

### vLLM exposure and hardening

- [vLLM security guide](https://docs.vllm.ai/en/latest/usage/security/) — vLLM project, latest build — inter-node traffic is insecure by default, `--api-key` scope, dangerous toggles, multi-tenancy and `cache_salt`, resource limits.
- [vLLM security policy](https://github.com/vllm-project/vllm/blob/main/SECURITY.md) — vLLM project, main branch — private reporting, severity bands, when a CVE is requested.
- [API-key middleware source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/middleware/authenticate.py) — vLLM project — only `/v1`, `/v2`, `/inference` and `/cohere` are guarded by `--api-key`.
- [Middleware registration source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/middleware/register.py) — vLLM project — where the authentication middleware is attached.
- [Health endpoint source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/instrumentator/health.py) — vLLM project — `/health` is unauthenticated and returns 200 with an empty body while the engine is alive.
- [API routers source at v0.31.0](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/api_server/routers.py) — vLLM project — development endpoints exist only with `VLLM_SERVER_DEV_MODE=1`; always-on routers.
- [Server launcher source, main branch](https://github.com/vllm-project/vllm/blob/main/vllm/entrypoints/launchers/launcher.py) — vLLM project, main (not pinned) — the default bind is all interfaces unless `--host` is set.

### vLLM security advisories

The advisory list is the primary source for CVE statements. Severity and dates come from the GitHub advisory metadata read on 2026-10-14; several 2026 CVE identifiers have six digits and are reproduced as GitHub lists them. Check each advisory page for the affected and fixed versions before quoting a version.

- [vLLM security advisories index](https://github.com/vllm-project/vllm/security/advisories) — vLLM project — 104 published advisories (27 in 2025, 77 in 2026) at the time of reading.

Authentication, network exposure and remote code execution:

- [CVE-2026-48746](https://github.com/vllm-project/vllm/security/advisories/GHSA-94f4-hr76-p5j6) — critical 9.1, 2026-06-02 — `--api-key` bypass on the OpenAI-compatible endpoints; advisory metadata lists 0.22.0 as patched.
- [CVE-2026-22778](https://github.com/vllm-project/vllm/security/advisories/GHSA-4r2x-xpjr-7cvv) — critical 9.8, 2026-02-02 — RCE chain through video processing, reachable pre-auth via `/invocations`; fixed in 0.14.1.
- [CVE-2025-59425](https://github.com/vllm-project/vllm/security/advisories/GHSA-wr9h-g72x-mwhm) — high 7.5, 2025-10-07 — API key compared in a timing-attackable way; fixed in 0.11.0.
- [CVE-2026-22807](https://github.com/vllm-project/vllm/security/advisories/GHSA-2pc9-4j83-qjmr) — high 8.8, 2026-01-21 — RCE through `auto_map` dynamic module loading at model initialisation.
- [CVE-2025-66448](https://github.com/vllm-project/vllm/security/advisories/GHSA-8fr4-5q9j-m8gm) — high 7.1, 2025-12-01 — RCE through `transformers_utils/get_config`.
- [CVE-2026-27893](https://github.com/vllm-project/vllm/security/advisories/GHSA-7972-pg2x-xr59) — high 8.8, 2026-03-26 — hard-coded `trust_remote_code=True` in two model classes bypasses the user's opt-out.
- [CVE-2026-90553](https://github.com/vllm-project/vllm/security/advisories/GHSA-3c86-2m5g-59q7) — high 7.8, 2026-08-28 — a processor loader executes attacker model code despite `trust_remote_code=False`.
- [GHSA-h3rc-6mm3-gc2m](https://github.com/vllm-project/vllm/security/advisories/GHSA-h3rc-6mm3-gc2m) — high 8.1, 2026-10-06, no CVE id yet — request-controlled `code_revision` allows RCE when `--trust-remote-code` is on; affects versions below 0.31.0.
- [CVE-2026-41523](https://github.com/vllm-project/vllm/security/advisories/GHSA-q8gq-377p-jq3r) — high 7.5, 2026-06-14 — a security check written as `assert` disappears under `python -O`; fixed in 0.22.0.
- [CVE-2025-62164](https://github.com/vllm-project/vllm/security/advisories/GHSA-mrw7-hf4f-83pf) — high 8.8, 2025-11-20 — `torch.load()` on user-supplied `prompt_embeds`; fixed in 0.11.1.
- [CVE-2026-73557](https://github.com/vllm-project/vllm/security/advisories/GHSA-pr7f-p5mw-fc87) — 2026-07-27 — bypass of the CVE-2025-62164 remediation through concurrent prompt parts.
- [CVE-2025-24357](https://github.com/vllm-project/vllm/security/advisories/GHSA-rh4j-5rhw-hr54) — high 7.5, 2025-01-27 — malicious model RCE via `torch.load` in the weights iterator.
- [CVE-2025-32434](https://github.com/vllm-project/vllm/security/advisories/GHSA-ggpf-24jw-3fcw) — high 7.5, 2025-04-22 — fix bypass with PyTorch older than 2.6.0.
- [CVE-2025-9141](https://github.com/vllm-project/vllm/security/advisories/GHSA-79j6-g2m3-jgfw) — high 8.8, 2025-08-20 — RCE in the Qwen3-Coder tool-call parser.

Pickle, ZeroMQ and multi-node:

- [CVE-2025-32444](https://github.com/vllm-project/vllm/security/advisories/GHSA-hj4w-hm2g-p6w5) — critical 10.0, 2025-04-29 — pickle over ZeroMQ sockets listening on all interfaces in the Mooncake integration.
- [CVE-2025-47277](https://github.com/vllm-project/vllm/security/advisories/GHSA-hjq4-87xh-g4fv) — critical 9.8, 2025-05-20 — KV-transfer service accepts malicious serialised data; fixed in 0.8.5.
- [CVE-2025-29783](https://github.com/vllm-project/vllm/security/advisories/GHSA-x3m8-f7g5-qhm7) — critical 9.0, 2025-03-19 — same Mooncake pickle-over-ZeroMQ class.
- [CVE-2025-30165](https://github.com/vllm-project/vllm/security/advisories/GHSA-9pcc-gvx5-r5wm) — high 8.0, 2025-05-06 — V0 multi-node ZMQ RCE, not fixed; V1 is not affected.
- [CVE-2025-30202](https://github.com/vllm-project/vllm/security/advisories/GHSA-9f8f-2vmf-885j) — high 7.5, 2025-04-29 — denial of service via ZeroMQ on multi-node.

Server-side request forgery:

- [CVE-2025-6242](https://github.com/vllm-project/vllm/security/advisories/GHSA-3f6c-7fw2-ppm4) — high 7.1, 2025-10-07 — SSRF in `MediaConnector`.
- [CVE-2026-24779](https://github.com/vllm-project/vllm/security/advisories/GHSA-qh4c-xf7m-gxfc) — high 7.1, 2026-01-27 — SSRF.
- [CVE-2026-25960](https://github.com/vllm-project/vllm/security/advisories/GHSA-v359-jj2v-j536) — 2026-03-09 — SSRF protection bypass.
- [CVE-2026-34753](https://github.com/vllm-project/vllm/security/advisories/GHSA-pf3h-qjgv-vcpr) — 2026-04-03 — SSRF in `download_bytes_from_url`.
- [CVE-2026-73560](https://github.com/vllm-project/vllm/security/advisories/GHSA-4hhp-h66f-j5j7) — 2026-08-13 — SSRF plus local file read in a multimodal loader.
- [GHSA-vfp2-c8pq-v6h6](https://github.com/vllm-project/vllm/security/advisories/GHSA-vfp2-c8pq-v6h6) — high, 2026-10-09 — SSRF via `X-Request-Id` makes a prefill worker connect outbound and leak KV-cache tensors.

Supply chain and build:

- [CVE-2026-54232](https://github.com/vllm-project/vllm/security/advisories/GHSA-jrf6-vqxq-pjv2) — high 8.8, 2026-06-09 — dependency confusion in the Dockerfile; images below 0.22.1 could be backdoored.
- [CVE-2026-47155](https://github.com/vllm-project/vllm/security/advisories/GHSA-3ww4-5jv9-j5gm) — medium 6.5, 2026-06-10 — "Artifact Pin Decay": `--revision` and `--code-revision` pins do not cover every artifact; the advisory's version fields are ambiguous.

Multi-tenant leakage and cache:

- [CVE-2025-46570](https://github.com/vllm-project/vllm/security/advisories/GHSA-4qjh-9fv9-r85r) — low 2.6, 2025-05-28 — prefix-cache timing side channel; mitigated with `cache_salt`.
- [CVE-2026-73558](https://github.com/vllm-project/vllm/security/advisories/GHSA-7m6h-x95x-82q5) — medium, 2026-08-11 — cross-user data leak.
- [CVE-2026-53923](https://github.com/vllm-project/vllm/security/advisories/GHSA-5jv2-g5wq-cmr4) — medium, 2026-06-11 — GGUF dequantize kernel exposes uninitialised GPU memory in multi-tenant serving.
- [CVE-2026-105752](https://github.com/vllm-project/vllm/security/advisories/GHSA-935w-9g4m-p28p) — low, 2026-09-28 — tool continuations drop `cache_salt`.
- [GHSA-rh6f-3x46-j33q](https://github.com/vllm-project/vllm/security/advisories/GHSA-rh6f-3x46-j33q) — 2026-10-06 — caller-controllable cache keys allow cross-request cache aliasing.
- [CVE-2026-54236](https://github.com/vllm-project/vllm/security/advisories/GHSA-hgg8-fqqc-vfmw) — 2026-06-11 — incomplete fix of CVE-2026-22778 leaks object addresses through the Anthropic-compatible router.

Availability (denial of service), representative:

- [CVE-2026-93592](https://github.com/vllm-project/vllm/security/advisories/GHSA-25q3-v2hm-8vpf) — high 7.5, 2026-09-03 — a negative token id in `/v1/embeddings` or `/pooling` kills the engine.
- [CVE-2026-100647](https://github.com/vllm-project/vllm/security/advisories/GHSA-wpww-v874-ph2p) — 2026-09-12 — unbounded `cache_salt` length stalls the scheduler.
- [GHSA-4xqp-c3mv-qff7](https://github.com/vllm-project/vllm/security/advisories/GHSA-4xqp-c3mv-qff7) — 2026-10-06 — oversized `min_tokens` hangs the engine while `/health` stays green; the case for latency and queue metrics.
- [GHSA-rhcx-5729-88vg](https://github.com/vllm-project/vllm/security/advisories/GHSA-rhcx-5729-88vg) — 7.7 — cross-tenant denial of service.

### Supply chain and air-gapped operation

- [Docker: pulling an image by digest](https://docs.docker.com/reference/cli/docker/image/pull/) — Docker docs — digest pinning freezes what is pulled; it is not provenance.
- [vLLM release build metadata script, main branch](https://github.com/vllm-project/vllm/blob/main/.buildkite/scripts/docker-build-metadata-args.sh) — vLLM project, main (not pinned) — build metadata only; no signing or attestation found.
- [vLLM release image publishing script, main branch](https://github.com/vllm-project/vllm/blob/main/.buildkite/scripts/publish-release-images.sh) — vLLM project, main (not pinned) — copies per-architecture images to Docker Hub; no signing or attestation found.
- [vLLM usage statistics page](https://docs.vllm.ai/en/latest/usage/usage_stats/) — vLLM project — what is collected and how to disable it (`VLLM_NO_USAGE_STATS`, `DO_NOT_TRACK`).
- [vLLM usage statistics source, main branch](https://github.com/vllm-project/vllm/blob/main/vllm/usage/usage_lib.py) — vLLM project, main (not pinned) — the opt-out conditions, including the `do_not_track` file.
- [vLLM environment variables source, main branch](https://github.com/vllm-project/vllm/blob/main/vllm/envs.py) — vLLM project, main (not pinned) — usage-stats server variable and opt-out switches.
- [vLLM offline inference page](https://docs.vllm.ai/en/latest/serving/offline_inference/) — vLLM project, latest build — local model directories; it does not describe `HF_HUB_OFFLINE` or an air-gapped recipe.
- [vLLM issue 23684](https://github.com/vllm-project/vllm/issues/23684) — vLLM project, closed 2025-08-28 — `HF_HUB_OFFLINE=1` once broke local-path loading.
- [vLLM issue 39039](https://github.com/vllm-project/vllm/issues/39039) — vLLM project, closed as not planned 2026-10-04 — an air-gapped Gemma 4 start still tried to reach the Hub cache.
- [Grafana configuration reference](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/) — Grafana Labs — `reporting_enabled`, `check_for_updates`, `check_for_plugin_updates` and the `GF_` environment overrides for an offline monitoring stack.

### LLM application security: OWASP, NIST and prompt injection

- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) — OWASP GenAI Security Project — the ten-item list used as the application-security checklist.
- [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — OWASP — direct versus indirect definitions and the mitigation list.
- [OWASP LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) — OWASP — authorise in downstream systems, not in the model.
- [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) — Greshake et al.; AISec 2023 (DOI 10.1145/3605764.3623985) — the primary paper for indirect injection; retrieved content and tool output are untrusted input.
- [NIST AI 100-2 E2025](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-2e2025.pdf) — NIST, March 2025 — the citable definitions of direct (NISTAML.018) and indirect (NISTAML.015) prompt injection.
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) — OWASP GenAI Security Project, 2025-12-09 — ASI01 to ASI10 for the agent block.
- [Agentic AI: Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) — OWASP Agentic Security Initiative, v1.0, 2025-02-17 — threat model for agents.
- [OWASP MCP Top 10](https://owasp.org/projects/mcp-top-10) — OWASP, beta release and pilot testing — MCP01 to MCP10, including audit and telemetry gaps.
- [OWASP: MCP Tool Poisoning](https://community.owasp.org/attacks/MCP_Tool_Poisoning) — OWASP community — tool poisoning as indirect prompt injection and its mitigations.
- [NIST AI 600-1: Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — NIST, 2024-07-26 — the twelve generative-AI risks; further reading only, no conformance claimed.
- [NIST AI 600-1 publication page](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) — NIST — metadata page for the profile.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — NIST — AI RMF 1.0 (Govern, Map, Measure, Manage); the page says it is being revised.

### Model Context Protocol (specification revision 2026-07-28)

Tutorials written for earlier revisions (HTTP+SSE transport, `Mcp-Session-Id`, the `initialize` handshake) are stale.

- [MCP specification versioning](https://modelcontextprotocol.io/specification/versioning) — Model Context Protocol project — 2026-07-28 is the current revision, 2025-11-25 the previous.
- [MCP specification, latest](https://modelcontextprotocol.io/specification/latest) — Model Context Protocol project — overview principles: consent, data privacy, tool safety.
- [MCP changelog for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog) — Model Context Protocol project — stateless protocol, removed sessions and handshake.
- [MCP transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) — Model Context Protocol project — stdio and Streamable HTTP; HTTP+SSE deprecated.
- [MCP Streamable HTTP transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) — Model Context Protocol project — Origin validation against DNS rebinding, bind to localhost.
- [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) — Model Context Protocol project — OAuth 2.1 resource-server duties, audience validation, no token passthrough.
- [MCP security best practices](https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices) — Model Context Protocol project — confused deputy, token passthrough, SSRF, local server compromise.
- [MCP server tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) — Model Context Protocol project — tool security considerations: human in the loop, untrusted annotations, audit logging.

### BSI and ANSSI guidance

- [Generative AI Models: Opportunities and Risks for Industry and Authorities](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/KI/Generative_AI_Models.html) — BSI, page dated 2025-01-21, continuously updated — German federal overview of LLM risks.
- [Design Principles for LLM-based Systems with Zero Trust](https://cyber.gouv.fr/en/publications/jointly-led-international-publications/design-principles-for-llm-based-systems-with-zero-trust/) — ANSSI and BSI, 2025-08-11 — least privilege, transparent decisions, human oversight of critical decisions.
- [Zero Trust paper, BSI copy](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/ANSSI-BSI-joint-releases/LLM-based_Systems_Zero_Trust.html) — BSI — the same joint publication on the BSI site; the exact principle list was not confirmed, so read the PDF before quoting.
- [Evasion Attacks on LLMs: countermeasures in practice](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/KI/Evasion-Angriffe_auf_LLMs-Gegenmassnahmen.pdf) — BSI, German-language PDF — notes that fine-tuning-based protections often prove insufficient.
- [BSI warning on indirect prompt injection](https://www.bsi.bund.de/SharedDocs/Cybersicherheitswarnungen/EN/2023/2023-249034-1032.pdf) — BSI, 2023 — early official warning.
- [BSI artificial intelligence page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Kuenstliche-Intelligenz/kuenstliche-intelligenz_node.html) — BSI — index of further reading: LLM hardening checklist, AIC4, SBOM for AI, external-model integration criteria; no conformance claimed.

### Secondary sources used only for orientation

Measurements of exposed Ollama servers, used to motivate a loopback bind. They are about Ollama, not vLLM.

- [Silent Brothers: Ollama hosts form an anonymous AI network beyond platform guardrails](https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/) — SentinelLABS with Censys, 2026-01-29 — 175,108 publicly reachable Ollama hosts in 130 countries.
- [Detecting exposed LLM servers: a Shodan case study on Ollama](https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama) — Cisco blog, 2025-09-01 — 1,139 exposed instances, about 18.8 percent answered an unauthenticated prompt.
- [Ollama Drama: investigating the prevalence of Ollama open instances](https://censys.com/blog/ollama-drama-investigating-the-prevalence-of-ollama-open-instances-with-censys/) — Censys blog — an earlier, narrower measurement.

## EU / compliance

These are sources for engineers and teaching, not legal advice. Binding texts and non-binding guidance are labelled apart.

### Legal texts

- [Regulation (EU) 2024/1689, the AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) — European Parliament and Council, OJ L 12.7.2024 — roles (Art. 3), AI literacy (Art. 4), transparency (Art. 50), GPAI obligations (Art. 51 to 55), fines (Art. 99, 101); EUR-Lex serves a bot challenge to scripts, so the text was read from the copy below.
- [AI Act, Publications Office copy (CELEX 32024R1689)](https://publications.europa.eu/resource/celex/32024R1689) — Publications Office of the EU — the same act as XHTML when requested with an `Accept: application/xhtml+xml` header.
- [Regulation (EU) 2026/1744, Digital Omnibus on AI](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) — European Parliament and Council, 2026-07-08, in force 2026-07-27 — replaced Art. 4 (AI literacy), moved high-risk dates to 2027-12-02 and 2028-08-02, added the Art. 50(2) grace period to 2026-12-02.
- [Digital Omnibus on AI, Publications Office copy (CELEX 32026R1744)](https://publications.europa.eu/resource/celex/32026R1744) — Publications Office of the EU — the amending act as XHTML.
- [Regulation (EU) 2016/679, the GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — European Parliament and Council, OJ L 119, 2016 — Art. 4, 5, 6, 9, 25, 28, 30, 32 and 35, Chapter V transfers and fines, applied to prompt, response and log data.
- [Court of Justice judgment C-311/18 (Schrems II)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62018CJ0311) — CJEU Grand Chamber, 2020-07-16 — "essentially equivalent" protection for transfers; Privacy Shield invalid.
- [General Court judgment T-553/23, Latombe v Commission](https://publications.europa.eu/resource/celex/62023TJ0553) — General Court, 2025-09-03 — action against the EU-US Data Privacy Framework dismissed.
- [Court of Justice press release on Latombe v Commission](https://curia.europa.eu/jcms/upload/docs/application/pdf/2025-09/cp250106en.pdf) — Court of Justice of the EU, September 2025 — plain-language summary and the Commission's duty to keep monitoring the framework.
- [Report on the first periodic review of the EU-US Data Privacy Framework](https://commission.europa.eu/document/download/25695177-8073-4ce3-bf81-eb816dc6b468_en?filename=Report+on+the+first+periodic+review+of+the+functioning+of+the+adequacy+decision+on+the+EU-US+Data+Privacy+Framework.pdf) — European Commission, 2024-10-09 — next review planned after three years.
- [Official Journal notice C/2025/6610 (appeal C-703/25 P)](https://eur-lex.europa.eu/eli/C/2025/6610/oj) — Official Journal of the EU — the reported appeal in Latombe; reported only by secondary sources and not opened (unverified).
- [InfoCuria case-law search](https://infocuria.curia.europa.eu/) — Court of Justice of the EU — check the appeal's status here before teaching that the framework is settled (unverified).
- [18 U.S.C. § 2713, the CLOUD Act provision](https://www.law.cornell.edu/uscode/text/18/2713) — US Code, text hosted by Cornell Legal Information Institute — providers must disclose data in their control even if stored abroad.

### AI Act guidance (non-binding)

- [Guidelines on the scope of the obligations for providers of GPAI models, PDF](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2025-07/guidelines_on_the_scope_of_the_obligations_for_generalpurpose_ai_models_established_by_regulation_1cx2atxgq79us4n3x8jfgyy1qlm_118340-3.pdf) — European Commission, header C(2025) 5045 final, 18.7.2025 — downstream-modifier test (one third of original training compute), open-source exemption, compute estimation.
- [Guidelines on the scope of the obligations for providers of GPAI models, second copy](https://ec.europa.eu/newsroom/dae/redirection/document/118340) — European Commission, header C(2025) 7719 final, 19.11.2025 — same title; paragraph numbers differ from the PDF above, and which copy is the current adopted version is unconfirmed.
- [Guidelines for GPAI providers, landing page](https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers) — European Commission — application dates and links to the guidelines.
- [Guidelines library page](https://digital-strategy.ec.europa.eu/en/library/guidelines-scope-obligations-providers-general-purpose-ai-models-under-ai-act) — European Commission — lists publication on 2025-07-18 and says the guidelines are not legally binding.
- [GPAI obligations FAQ](https://digital-strategy.ec.europa.eu/en/faqs/guidelines-obligations-general-purpose-ai-providers) — European Commission — fines enforceable from 2026-08-02; modifiers become providers only in exceptional cases.
- [Guidelines on transparency obligations under Article 50](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-07/guidelines_on_the_implementation_of_the_transparency_obligations_for_certain_ai_systems_under_article_50_of_the_ai_act_bzptwqhk0ikg1dtlddap41psfy_131215.pdf) — European Commission, C(2026) 5054 final, 2026-07-20 — who is the provider of an in-house chatbot, when disclosure is not needed, marking techniques, the grace period.
- [Code of Practice on transparency of AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content) — European Commission, final 2026-06-10 — voluntary marking and labelling tool; draft Art. 50 guidelines history.
- [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai) — European Commission, published 2025-07-10 — transparency, copyright and safety chapters; signatory list; chapter commitments were not read.
- [Template for the GPAI training-content summary (FAQ)](https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content) — European Commission — what providers must publish, including for modifiers; template publication date unconfirmed.
- [AI Act regulatory framework page](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) — European Commission, updated 2026-08-03 — application milestones after the Omnibus.
- [Press release on the political agreement for the AI Omnibus](https://digital-strategy.ec.europa.eu/en/news/eu-agrees-simplify-ai-rules-boost-innovation-and-ban-nudification-apps-protect-citizens) — European Commission, 2026-05-07 — legislative trail.
- [Digital rulebook page](https://digital-strategy.ec.europa.eu/en/policies/digital-rulebook) — European Commission, updated 2026-07-27 — the separate GDPR and data Omnibus is still only "proposed"; treat GDPR as unchanged.

### Data protection guidance

- [EDPB Opinion 28/2024 on AI models and personal data](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf) — European Data Protection Board, adopted 2024-12-17 — when models are anonymous, legitimate interest test, deployer's duty to check lawful development.
- [AI Privacy Risks and Mitigations: Large Language Models](https://www.edpb.europa.eu/system/files/2025-04/ai-privacy-risks-and-mitigations-in-llms.pdf) — Isabel Barberá for the EDPB Support Pool of Experts, 2025 — the author's views, not an EDPB position; log retention and minimisation risks.
- [CNIL Q&A on the use of generative AI systems](https://www.cnil.fr/en/cnils-qa-use-generative-ai-systems) — CNIL, 2024-07-18 — on-premise deployment seen as more appropriate for personal data; history recording is the deployer's setting.
- [CNIL recommendations on AI system development under the GDPR](https://www.cnil.fr/en/ai-system-development-cnils-recommendations-to-comply-gdpr) — CNIL — retention for traceability and performance measurement; known only from a search summary (unverified).

### Sovereignty and certification frameworks

- [Cloud Sovereignty Framework: implementation guidance](https://commission.europa.eu/document/download/2ad80a48-166f-4c77-a513-80c53ca2a128_en) — European Commission, DG DIGIT, issued after the tender concluded — objectives SOV-1 to SOV-8, SEAL levels, the vocabulary for the sovereignty comparison.
- [Commission moves forward on cloud sovereignty with a EUR 180 million tender](https://commission.europa.eu/news-and-media/news/commission-moves-forward-cloud-sovereignty-eur-180-million-tender-2025-10-10_en) — European Commission, 2025-10-10 — origin of the framework.
- [Sovereign cloud framework explained](https://commission.europa.eu/news-and-media/news/sovereign-cloud-framework-explained-2026-06-01_en) — European Commission, 2026-06-01 — scoring based on 48 criteria; no mention of EUCS.
- [BSI press release: C5:2026](https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260407_C5_Cloud_Computing.html) — BSI, 2026-04-07 — new C5 with container, confidential-computing and post-quantum content; sovereignty criteria published separately.
- [BSI C5 criteria catalogue page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Empfehlungen-nach-Angriffszielen/Cloud-Computing/Kriterienkatalog-C5/kriterienkatalog-c5_node.html) — BSI — lists C5:2026 and C5:2020.
- [BSI C5 2025 revision page](https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Empfehlungen-nach-Angriffszielen/Cloud-Computing/Kriterienkatalog-C5/C5_2025/C5_2025.html) — BSI — transition rule and criteria count known only from search summaries (unverified).
- [BSI press release: C3A](https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260427_C3A.html) — BSI, 2026-04-27 — Criteria enabling Cloud Computing Autonomy, following the EU framework.
- [BSI C3A page](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Empfehlungen-nach-Angriffszielen/Cloud-Computing/C3A/C3A.html) — BSI — scope and localisation requirements; no regulatory effect.
- [ENISA cybersecurity certification framework](https://www.enisa.europa.eu/topics/product-security-and-certification/cybersecurity-certification-framework) — ENISA — lists EUCS among schemes still under development.
- [ENISA EUCS candidate scheme](https://www.enisa.europa.eu/publications/eucs-cloud-service-scheme) — ENISA, draft dated 2020-12-22 — the only EUCS document found; adoption status unconfirmed.
- [Gaia-X compliance document, marketing summary](https://gaia-x.eu/wp-content/uploads/2024/09/Compliance-Document_Marketing-Summary-2024.pdf) — Gaia-X, 2025-07-09 — label levels 1 to 3 and the EEA-only data and headquarters conditions.

### Open source definitions

- [Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition) — Open Source Initiative, 2024-10-28 — the four freedoms and the data-information, code and parameters requirements; basis for "open weights is not open source".
- [Open Source AI Definition FAQ](https://opensource.org/ai/faq) — Open Source Initiative — which models were analysed (OLMo and Pythia pass, Llama 2 does not).
- [OSI releases its definition for Open Source AI](https://opensource.org/press-mentions/osi-officially-releases-its-definition-for-open-source-ai) — Open Source Initiative, 2024-10-28 — release announcement.

### Secondary sources used only for orientation

Unofficial or third-party copies. Use them to find the right article, then cite the official text above.

- [AI Act Article 53](https://artificialintelligenceact.eu/article/53/) — artificialintelligenceact.eu, unofficial mirror of an amended text — GPAI provider duties and the open-source exemption in 53(2).
- [AI Act Article 51](https://artificialintelligenceact.eu/article/51/) — artificialintelligenceact.eu, unofficial mirror — the 10^25 FLOP presumption for systemic risk.
- [AI Act Article 54](https://artificialintelligenceact.eu/article/54/) — artificialintelligenceact.eu, unofficial mirror — authorised representatives and the same open-source exception.
- [AI Act Article 2](https://artificialintelligenceact.eu/article/2/) — artificialintelligenceact.eu, unofficial mirror — scope, including the open-source carve-out in 2(12).
- [AI Act Article 113](https://artificialintelligenceact.eu/article/113/) — artificialintelligenceact.eu, unofficial mirror — entry into force and application dates.
- [AI Act Recital 102](https://artificialintelligenceact.eu/recital/102/) — artificialintelligenceact.eu, unofficial mirror — what counts as a free and open-source licence.
- [AI Act Recital 103](https://artificialintelligenceact.eu/recital/103/) — artificialintelligenceact.eu, unofficial mirror — monetisation removes the exception.
- [AI Act Recital 104](https://artificialintelligenceact.eu/recital/104/) — artificialintelligenceact.eu, unofficial mirror — limits of the exception for systemic-risk models.
- [Cloud Sovereignty Framework v1.2.1, third-party host](https://ppc.land/content/files/2025/11/Cloud-Sovereignty-Framework.pdf) — European Commission DG DIGIT, October 2025, PDF copy on a news site — objective weights and SEAL levels as first published.

## Inference Engineering

The book is a technical reference for vocabulary and the optimisation menu, not a source of text, figures or numbers. It is cited by chapter and section only, with printed page numbers. Concepts are re-explained in original words with original diagrams and with measurements from the workshop's own runs. The book has no URL in the research notes, so this group is a bibliographic record and a table instead of a link list.

Bibliographic data:

- Title: *Inference Engineering*
- Author: Philip Kiely
- Publisher and year: Baseten Books, 2026; copyright 2026 Baseten Labs, Inc.
- ISBN: 979-8-9943597-2-3
- Edition: no edition number is stated
- Checked: against the local PDF text on 2026-10-14; equations and code are images in the extracted text, so check the PDF before citing any of them
- Caution: the author works for Baseten, and the book favours TensorRT-LLM; read its engine comparison with that in mind

Chapter-to-topic table:

| Chapter (printed page) | Sections used (printed page) | Workshop topic it anchors |
|---|---|---|
| 0 Inference (p. 15) | none recorded | Overview chapter; no section-level anchor in the research notes |
| 1 Prerequisites (p. 23) | 1.3 Model Selection (p. 31); 1.4 Measuring Latency & Throughput (p. 35) | Model-selection block; TTFT, tokens per second, percentiles, end-to-end versus inference-only latency |
| 2 Models (p. 39) | 2.2 LLM Inference Mechanics (p. 46); 2.4 Calculating Inference Bottlenecks (p. 61); 2.5 Optimizing Attention (p. 67) | Prefill versus decode and their different bottlenecks; ops:byte ratio and arithmetic intensity; attention optimisation |
| 3 Hardware (p. 71) | 3.1 GPU Architecture (p. 74); 3.2 Generations (p. 77); 3.3 Instances (p. 83); 3.5 Local Inference (p. 89) | Hardware and architecture block: GPU choice, generations, instance types, local inference |
| 4 Software (p. 93) | 4.1 CUDA (p. 96); 4.3 Inference Engines (p. 105); 4.5 Benchmarking & Load Testing (p. 112) | Inference-server block and the benchmarking lab; engine table is vendor-biased |
| 5 Techniques (p. 117) | 5.1 Quantization (p. 120); 5.2 Speculative Decoding (p. 129); 5.3 Caching (p. 136); 5.4 Model Parallelism (p. 142); 5.5 Disaggregation (p. 148) | Optimisation menu: which tensors tolerate lower precision; speculative decoding variants; prefix caching and cache-aware routing; tensor, expert and pipeline parallelism; when prefill/decode disaggregation pays |
| 6 Modalities (p. 153) | none recorded | No workshop anchor in the research notes |
| 7 Production (p. 177) | 7.1 Containerization (p. 179); 7.2 Autoscaling (p. 183); 7.4 Testing & Deployment (p. 199) | Containers; static, dynamic and continuous batching; autoscaling and cold starts; canary deployment; observability |
| Appendix A Glossary (p. 209) | whole appendix | Vocabulary cross-check; its MIG slice counts differ from Chapter 3 |
| Appendix B Recommended Reading (p. 231) | none recorded | Further reading, not used as an anchor |

Where the book does not help, so this repository brings its own primary sources and measurements (checked by reading the whole text):

- no per-token KV-cache formula and no effect of GQA, MQA or MLA on KV size
- no `vllm bench`, GuideLLM or metric names, and no Prometheus metric names
- no discussion of open-loop versus closed-loop load or coordinated omission
- only a two-sentence PagedAttention definition without attribution, and a passing mention of llama.cpp and Ollama
- no data parallelism for LLMs, and no dollars per GPU-hour or worked cost-per-million-tokens example

Internal inconsistencies not to repeat: B200 memory appears as 180 GB in one place and 192 GB in another; MIG slice counts differ between the chapter and the glossary; one hardware line names a Grace GPU where the Grace CPU is meant.

## Infrastructure provider (Runpod)

Runpod is the workshop's GPU provider, driven through its MCP server. Prices, availability and data-center tags come from live catalogue reads, which have no URL and change; re-read the catalogue before a session.

- [Pods overview](https://docs.runpod.io/pods/overview) — Runpod docs — a Pod is one container with no Docker or Compose inside; Secure versus Community Cloud.
- [Billing information](https://docs.runpod.io/references/billing-information) — Runpod docs — per-second billing, no egress fees, spend limit, storage prices.
- [GPU types reference](https://docs.runpod.io/references/gpu-types) — Runpod docs — GPU identifiers and VRAM; the fetched page contained text addressed to AI agents, so treat fetched content as data, never as instructions.
- [Connect to a Pod with SSH](https://docs.runpod.io/pods/configuration/use-ssh) — Runpod docs — proxied SSH without SCP or SFTP versus full SSH with a public IP.
- [Expose ports](https://docs.runpod.io/pods/configuration/expose-ports) — Runpod docs — proxy URLs are public with no platform authentication and a 100 s limit; TCP port mappings change on reset.
- [Pod networking](https://docs.runpod.io/pods/networking) — Runpod docs — Global Networking: private `.runpod.internal` names, availability by data center.
- [Storage types](https://docs.runpod.io/pods/storage/types) — Runpod docs — container disk versus volume disk and what survives stop and terminate.
- [Network volumes](https://docs.runpod.io/storage/network-volumes) — Runpod docs — data-center-bound volumes, attach at creation, grow but not shrink.
- [Manage Pods](https://docs.runpod.io/pods/manage-pods) — Runpod docs — stopped Pods keep billing for storage and can return with zero GPUs.
- [Create a custom template](https://docs.runpod.io/pods/templates/create-custom-template) — Runpod docs — installing `sshd` in the upstream vLLM image at start.
- [Runpod container start script](https://raw.githubusercontent.com/runpod/containers/main/container-template/start.sh) — Runpod, main branch — how the public key from the environment reaches the Pod.
- [Build Docker images on Runpod with Bazel](https://docs.runpod.io/tutorials/pods/build-docker-images) — Runpod docs — building images inside a Pod without a Docker daemon; the earlier Docker-in-Docker tutorial (CPU Pods only) is no longer served, and a measured attempt on a GPU Pod confirmed that Docker does not work there, so the containerization block runs on laptops.
- [Instant Clusters](https://docs.runpod.io/instant-clusters) — Runpod docs — 2 to 8 self-serve nodes, still containers.
- [Serverless vLLM overview](https://docs.runpod.io/serverless/vllm/overview) — Runpod docs — the only vLLM path in Runpod's own docs; no official Pod template.
- [Deploy vLLM on Runpod with Docker](https://www.runpod.io/articles/guides/deploy-vllm-runpod-docker) — Runpod guide — runs the upstream `vllm/vllm-openai` image with a custom start command and port 8000.
- [Migrate from API v1](https://docs.runpod.io/api-reference-v2/migrate-from-v1) — Runpod docs — v1 retires on 2026-11-15 (one secondary page says 2026-12-01); the MCP server is v2-only.
- [Create Pod API reference](https://docs.runpod.io/api-reference/pods/POST/pods) — Runpod docs — v2 create-pod fields.
- [Runpod MCP servers](https://docs.runpod.io/get-started/mcp-servers) — Runpod docs — authentication and the tool surface of the hosted MCP server.
- [runpod-mcp repository](https://github.com/runpod/runpod-mcp) — Runpod — the key acts with full account permissions and there is no read-only mode.
- [Data processing agreement](https://www.runpod.io/legal/data-processing-agreement) — Runpod — EU standard contractual clauses, sub-processors, "reasonable efforts" on region placement.
- [Compliance page](https://www.runpod.io/legal/compliance) — Runpod — SOC 2 Type II, SOC 3, ISO/IEC 27001:2022.
- [About Runpod](https://www.runpod.io/about/company) — Runpod — company facts for the jurisdiction discussion; incorporation state unconfirmed.
- [Pricing page](https://www.runpod.io/pricing) — Runpod — per-GPU numbers differ from the API catalogue for some cards; the API read is the budgeting source of truth.
- [Bare Metal](https://www.runpod.io/gpu-bare-metal-server) — Runpod — reserved product, not hourly self-serve.
- [Verda](https://verda.com/) — Verda, formerly DataCrunch, Helsinki — an EU alternative surveyed for the provider comparison.
- [Hetzner GPU server matrix](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/) — Hetzner — an EU alternative surveyed.
- [Scaleway GPU pricing](https://www.scaleway.com/en/pricing/gpu/) — Scaleway — an EU alternative surveyed.
