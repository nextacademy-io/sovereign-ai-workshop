import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location(
    "gpu_exporter", Path(__file__).with_name("exporter.py")
)
exporter = importlib.util.module_from_spec(spec)
sys.modules["gpu_exporter"] = exporter
spec.loader.exec_module(exporter)


class FakeNvml:
    NVML_TEMPERATURE_GPU = 0
    NVML_CLOCK_SM = 1
    NVML_CLOCK_MEM = 2

    def nvmlDeviceGetCount(self):  # noqa: N802
        return 2

    def nvmlDeviceGetHandleByIndex(self, i):  # noqa: N802
        return i

    def nvmlDeviceGetName(self, h):  # noqa: N802
        return b"Fake GPU"

    def nvmlDeviceGetUtilizationRates(self, h):  # noqa: N802
        return SimpleNamespace(gpu=87 + h, memory=40)

    def nvmlDeviceGetMemoryInfo(self, h):  # noqa: N802
        return SimpleNamespace(used=10 * 1024**3, free=86 * 1024**3, total=96 * 1024**3)

    def nvmlDeviceGetPowerUsage(self, h):  # noqa: N802
        return 412_500  # milliwatts

    def nvmlDeviceGetTemperature(self, h, kind):  # noqa: N802
        return 61

    def nvmlDeviceGetClockInfo(self, h, kind):  # noqa: N802
        return 2400 if kind == self.NVML_CLOCK_SM else 1500


def test_samples_use_dcgm_units():
    samples = exporter.collect(FakeNvml())
    assert len(samples) == 2
    s = samples[0]
    assert s["DCGM_FI_DEV_FB_USED"] == 10 * 1024  # MiB
    assert s["DCGM_FI_DEV_POWER_USAGE"] == 412.5  # watts
    assert s["DCGM_FI_DEV_GPU_UTIL"] == 87 and samples[1]["DCGM_FI_DEV_GPU_UTIL"] == 88


def test_render_is_valid_prometheus_text_with_dcgm_names_and_labels():
    text = exporter.render(exporter.collect(FakeNvml()))
    assert "# TYPE DCGM_FI_DEV_GPU_UTIL gauge" in text
    assert 'DCGM_FI_DEV_FB_USED{gpu="0",modelName="Fake GPU"} 10240.000' in text
    assert text.count("DCGM_FI_DEV_POWER_USAGE{") == 2 and text.endswith("\n")
