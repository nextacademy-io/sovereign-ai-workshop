import math

import pytest
from infbench.stats import percentile, summarize


def test_percentile_matches_linear_interpolation():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert percentile(data, 0) == 1.0
    assert percentile(data, 50) == 3.0
    assert percentile(data, 100) == 5.0
    assert percentile(data, 25) == 2.0
    # rank = 4 * 0.9 = 3.6 -> 4 + 0.6 * (5 - 4)
    assert math.isclose(percentile(data, 90), 4.6)


def test_percentile_single_value_and_errors():
    assert percentile([7.0], 99) == 7.0
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1.0], 101)


def test_summarize_scales_and_orders_percentiles():
    s = summarize([0.010, 0.020, 0.030, 0.040, 0.100], scale=1000, ndigits=3)
    assert s["count"] == 5
    assert s["min"] == 10.0 and s["max"] == 100.0
    assert s["p50"] == 30.0
    assert s["p50"] <= s["p90"] <= s["p95"] <= s["p99"] <= s["max"]
    assert math.isclose(s["mean"], 40.0)


def test_summarize_low_percentiles_for_bigger_is_better_metrics():
    s = summarize(range(1, 101), low=(1, 5))
    assert s["p1"] < s["p5"] < s["p50"]


def test_summarize_empty_is_none_not_zero():
    assert summarize([]) is None


def test_mean_hides_the_tail():
    # 99 fast requests and one very slow one: the mean looks fine, p99 does not.
    s = summarize([0.1] * 99 + [10.0])
    assert s["mean"] < 0.25
    assert s["p99"] > 0.1
    assert s["max"] == 10.0
