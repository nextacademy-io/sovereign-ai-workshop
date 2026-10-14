import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "quality_probe", Path(__file__).with_name("quality_probe.py")
)
qp = importlib.util.module_from_spec(spec)
sys.modules["quality_probe"] = qp
spec.loader.exec_module(qp)


def test_items_are_deterministic_balanced_and_have_correct_answers():
    a, b = qp.make_items(30), qp.make_items(30)
    assert a == b and len({it["prompt"] for it in a}) == 30
    kinds = [it["kind"] for it in a]
    assert kinds.count("arith") == kinds.count("extract") == kinds.count("classify") == 10
    arith = next(it for it in a if it["kind"] == "arith")
    nums = [int(x) for x in __import__("re").findall(r"\d+", arith["prompt"])][:3]
    assert int(arith["answer"]) == nums[0] - nums[1] + nums[2]


def test_answer_checking_is_strict_enough_and_tolerant_of_formatting():
    arith = {"kind": "arith", "answer": "512"}
    assert (
        qp.is_correct(arith, "512")
        and qp.is_correct(arith, " 512.")
        and qp.is_correct(arith, "The answer is 512")
    )
    assert not qp.is_correct(arith, "513") and not qp.is_correct(arith, "")
    assert qp.is_correct({"kind": "arith", "answer": "1234"}, "1,234")
    cls = {"kind": "classify", "answer": "billing"}
    assert (
        qp.is_correct(cls, "Billing")
        and qp.is_correct(cls, "billing.")
        and not qp.is_correct(cls, "delivery")
    )


def test_wilson_interval_is_sane():
    lo, hi = qp.wilson(90, 100)
    assert lo < 0.9 < hi and lo > 0.80 and hi < 0.96
    assert qp.wilson(0, 0) == (0.0, 0.0)
    lo, hi = qp.wilson(100, 100)
    assert abs(hi - 1.0) < 1e-9 and lo > 0.95


def test_compare_pairs_items_and_measures_agreement():
    ref = {
        "label": "bf16",
        "accuracy_items": [True] * 8 + [False] * 2,
        "open_replies": ["alpha beta", "same", "x"],
    }
    oth = {
        "label": "fp8",
        "accuracy_items": [True] * 7 + [False, True, False],
        "open_replies": ["alpha beta", "samX", "x"],
    }
    out = qp.compare(ref, oth)
    assert (
        out["items"] == 10
        and out["reference_right_other_wrong"] == 1
        and out["other_right_reference_wrong"] == 1
    )
    assert out["accuracy_difference_points"] == 0.0
    assert abs(out["greedy_completions_identical"] - 2 / 3) < 1e-9
    assert 0.8 < out["mean_matching_prefix_fraction"] < 1.0
