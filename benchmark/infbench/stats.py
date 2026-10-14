"""Percentiles and summaries. Pure Python so the harness needs no numpy."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

PERCENTILES = (50, 90, 95, 99)


def percentile(sorted_values: Sequence[float], p: float) -> float:
    """Percentile with linear interpolation between closest ranks (numpy's default).

    `sorted_values` must be sorted ascending. p is in [0, 100].
    """
    if not sorted_values:
        raise ValueError("percentile of an empty sequence")
    if not 0 <= p <= 100:
        raise ValueError("p must be within [0, 100]")
    n = len(sorted_values)
    if n == 1:
        return float(sorted_values[0])
    rank = (n - 1) * p / 100.0
    lo = math.floor(rank)
    hi = min(lo + 1, n - 1)
    frac = rank - lo
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac)


def summarize(
    values: Iterable[float],
    *,
    scale: float = 1.0,
    ndigits: int = 3,
    low: Sequence[int] = (),
) -> dict[str, float] | None:
    """Summary dict {count, mean, min, [low percentiles], p50, p90, p95, p99, max}.

    `scale` converts units. `low` adds lower percentiles (for example (1, 5)), which are the
    interesting tail for metrics where bigger is better, such as tokens per second.
    Returns None for an empty input so reports can say 'no data' instead of inventing zeros.
    """
    data = sorted(v * scale for v in values)
    if not data:
        return None
    out: dict[str, float] = {
        "count": len(data),
        "mean": sum(data) / len(data),
        "min": data[0],
    }
    for p in low:
        out[f"p{p}"] = percentile(data, p)
    for p in PERCENTILES:
        out[f"p{p}"] = percentile(data, p)
    out["max"] = data[-1]
    return {k: (v if k == "count" else round(v, ndigits)) for k, v in out.items()}
