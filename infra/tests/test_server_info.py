import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("server_info", ROOT / "infra/pod/server-info.py")
server_info = importlib.util.module_from_spec(spec)
sys.modules["server_info"] = server_info
spec.loader.exec_module(server_info)

# Lines in the exact formats of vLLM v0.31.0 (see docs/RESEARCH.md for the source of each).
LOG = """\
INFO 10-14 12:00:01 [gpu_model_runner.py:100] Model loading took 15.2711 GiB memory and 9.512000 seconds
INFO 10-14 12:00:02 [default_loader.py:50] Loading weights took 8.91 seconds
INFO 10-14 12:00:20 [gpu_worker.py:300] Available KV cache memory: 52.40 GiB
INFO 10-14 12:00:20 [kv_cache_utils.py:900] GPU KV cache size: 381,248 tokens, Maximum concurrency for 32,768 tokens per request: 11.64x
INFO 10-14 12:00:40 [gpu_model_runner.py:400] Graph capturing finished in 14 secs, took 0.62 GiB
INFO 10-14 12:00:41 [core.py:200] init engine (profile, create kv cache, warmup model) took 41.37 s
"""


def test_parse_log_extracts_the_startup_facts():
    got = server_info.parse_log(LOG)
    assert got["model_memory_gib"] == 15.2711 and got["model_load_seconds"] == 9.512
    assert got["weights_seconds"] == 8.91 and got["kv_cache_memory_gib"] == 52.4
    assert got["kv_cache_tokens"] == 381248 and got["kv_cache_max_model_len"] == 32768
    assert got["kv_cache_max_concurrency"] == 11.64
    assert got["graph_capture_seconds"] == 14.0 and got["graph_capture_gib"] == 0.62
    assert got["engine_init_seconds"] == 41.37


def test_parse_log_ignores_color_codes_and_prefers_the_latest_start():
    colored = "\x1b[0;36m(EngineCore)\x1b[0;0m GPU KV cache size: 1,000 tokens, Maximum concurrency for 500 tokens per request: 2.00x\n"
    later = (
        "GPU KV cache size: 2,000 tokens, Maximum concurrency for 500 tokens per request: 4.00x\n"
    )
    got = server_info.parse_log(colored + later)
    assert got["kv_cache_tokens"] == 2000 and got["kv_cache_max_concurrency"] == 4.0


def test_parse_log_reports_nothing_rather_than_guessing():
    assert server_info.parse_log("INFO unrelated line\n") == {}


def test_kv_capacity_in_the_log_can_be_checked_against_the_formula():
    """Qwen3-8B: 2 (K,V) x 36 layers x 8 KV heads x 128 head_dim x 2 bytes (BF16) = 147,456 B/token."""
    bytes_per_token = 2 * 36 * 8 * 128 * 2
    assert bytes_per_token == 147_456
    gib = server_info.parse_log(LOG)["kv_cache_memory_gib"]
    predicted_tokens = gib * 2**30 / bytes_per_token
    reported = server_info.parse_log(LOG)["kv_cache_tokens"]
    # Within a few percent: block rounding and the max_model_len rounding in vLLM's report.
    assert abs(predicted_tokens - reported) / reported < 0.05
    assert json.dumps(bytes_per_token)


def test_parse_log_reads_the_memory_accounting_line():
    line = (
        "INFO 10-14 13:51:24 [gpu_worker.py:955] Free memory on device (94.43/94.97 GiB) on startup. "
        "Desired GPU memory utilization is (0.8, 75.98 GiB). Actual usage is 16.14 GiB for consumed memory "
        "(weights + non-torch), 1.7 GiB for peak activation, and 0.21 GiB for CUDAGraph memory. Replace ..."
    )
    got = server_info.parse_log(line)["memory_accounting_gib"]
    assert (
        got["device_total"] == 94.97
        and got["budget"] == 75.98
        and got["gpu_memory_utilization"] == 0.8
    )
    assert (
        got["weights_and_non_torch"] == 16.14
        and got["peak_activation"] == 1.7
        and got["cuda_graphs"] == 0.21
    )
    assert "memory_accounting_gib" not in server_info.parse_log(LOG)


def test_timeline_counts_seconds_from_the_first_stamp_and_survives_midnight():
    log = (
        "(APIServer) INFO 10-14 23:59:50 [api_utils.py:1] starting\n"
        "(EngineCore) INFO 10-15 00:00:00 [core.py:129] Initializing a V1 LLM engine (v0.31.0)\n"
        "(EngineCore) INFO 10-15 00:00:05 [model_runner.py:1] Model loading took 15.27 GiB memory and 3.0 seconds\n"
        "(EngineCore) INFO 10-15 00:01:10 [core.py:373] init engine (profile, create kv cache, warmup model) took 60.0 s\n"
    )
    got = server_info.parse_log(log)["timeline_seconds"]
    assert got == {"engine_core_started": 10.0, "weights_loaded": 15.0, "engine_ready": 80.0}
