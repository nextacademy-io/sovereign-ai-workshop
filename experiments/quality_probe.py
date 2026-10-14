#!/usr/bin/env python3
"""A small, self-generated quality probe for comparing deployments (BF16 vs FP8, and so on).

It is a SPOT CHECK, not a benchmark. Questions are generated from templates with a fixed seed, so every
deployment sees exactly the same items and every answer has a known correct value. No external dataset
is involved (no licence question, no contamination question). With a few hundred items the statistical
resolution is a few percentage points, so the probe can show that a change is NOT large, and it can flag
a big drop; it cannot prove that two models are equal.

Two measurements per deployment:
  accuracy   fraction of items answered correctly (greedy decoding, thinking mode off)
  agreement  fraction of open-ended greedy completions that are character-for-character identical to the
             reference deployment's, plus how far they match before diverging

    python3 experiments/quality_probe.py run --label bf16 --out bf16.json
    python3 experiments/quality_probe.py compare bf16.json fp8.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SYSTEM = "Answer with the requested value only, no explanation."

ARITH = "A warehouse holds {a} pallets. {b} pallets are shipped out and {c} new pallets arrive. How many pallets are in the warehouse now? Answer with the number only."
EXTRACT = (
    "Read the policy text and answer with the number only.\n\n"
    "Policy: Invoices above {limit} euros need a second approval. Approved invoices are paid within {days} days. "
    "Late payments carry a fee of {fee} percent.\n\n"
    "Question: After how many days are approved invoices paid?"
)
CLASSIFY = (
    "Classify the customer message into exactly one of: billing, delivery, warranty, security. "
    "Answer with the single word only.\n\nMessage: {message}"
)
CLASS_MESSAGES = {
    "billing": [
        "I was charged twice for order {n}.",
        "My invoice {n} shows the wrong amount.",
        "Please refund the overpayment on invoice {n}.",
    ],
    "delivery": [
        "My parcel {n} has not arrived yet.",
        "The package {n} was delivered to the wrong address.",
        "Where is shipment {n}? It is a week late.",
    ],
    "warranty": [
        "The device from order {n} stopped working after two months.",
        "My product {n} is defective and I want a repair.",
        "The screen of item {n} cracked without any impact.",
    ],
    "security": [
        "I think someone logged into my account {n} without permission.",
        "I received a suspicious password reset email for account {n}.",
        "My account {n} shows logins from a country I have never visited.",
    ],
}
OPEN_PROMPTS = [
    "Explain in two sentences why batching improves GPU throughput.",
    "Write a polite two-sentence reply to a customer whose parcel is late.",
    "List three risks of exposing an inference server to the internet.",
    "Summarise what a KV cache is in one sentence.",
    "Give two differences between a dense model and a mixture-of-experts model.",
    "Write a one-sentence definition of time to first token.",
    "Name three metrics you would put on an inference dashboard and say why.",
    "Describe in two sentences what quantization does to a model.",
]


def make_items(n: int, seed: int = 20260101) -> list[dict]:
    """n items, a third of each kind, with the correct answer attached."""
    rng = random.Random(seed)
    items: list[dict] = []
    for i in range(n):
        kind = ("arith", "extract", "classify")[i % 3]
        if kind == "arith":
            a, b, c = rng.randint(200, 900), rng.randint(20, 150), rng.randint(20, 150)
            items.append(
                {"kind": kind, "prompt": ARITH.format(a=a, b=b, c=c), "answer": str(a - b + c)}
            )
        elif kind == "extract":
            limit, days, fee = (
                rng.choice([500, 1000, 2500, 5000]),
                rng.randint(7, 60),
                rng.randint(1, 9),
            )
            items.append(
                {
                    "kind": kind,
                    "prompt": EXTRACT.format(limit=limit, days=days, fee=fee),
                    "answer": str(days),
                }
            )
        else:
            label = rng.choice(sorted(CLASS_MESSAGES))
            message = rng.choice(CLASS_MESSAGES[label]).format(n=rng.randint(10000, 99999))
            items.append(
                {"kind": kind, "prompt": CLASSIFY.format(message=message), "answer": label}
            )
    return items


def is_correct(item: dict, reply: str) -> bool:
    text = reply.strip().lower()
    if item["kind"] in ("arith", "extract"):
        numbers = re.findall(r"-?\d+", text.replace(",", ""))
        return bool(numbers) and numbers[-1] == item["answer"]
    return re.sub(r"[^a-z]", "", text.split()[0] if text.split() else "") == item["answer"]


def wilson(correct: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 % Wilson score interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = correct / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def common_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b, strict=False):
        if x != y:
            break
        n += 1
    return n


def compare(reference: dict, other: dict) -> dict:
    """Compare two runs of the probe. Pairing by item makes the comparison much sharper than comparing totals."""
    ra, oa = reference["accuracy_items"], other["accuracy_items"]
    n = len(ra)
    only_ref = sum(
        1 for x, y in zip(ra, oa, strict=True) if x and not y
    )  # reference right, other wrong
    only_other = sum(1 for x, y in zip(ra, oa, strict=True) if y and not x)
    same = [r == o for r, o in zip(reference["open_replies"], other["open_replies"], strict=True)]
    prefix = [
        common_prefix(r, o) / max(len(r), 1)
        for r, o in zip(reference["open_replies"], other["open_replies"], strict=True)
    ]
    ca, cb = sum(ra), sum(oa)
    return {
        "items": n,
        "reference": {"label": reference["label"], "accuracy": ca / n, "ci95": wilson(ca, n)},
        "other": {"label": other["label"], "accuracy": cb / n, "ci95": wilson(cb, n)},
        "accuracy_difference_points": 100 * (cb - ca) / n,
        "reference_right_other_wrong": only_ref,
        "other_right_reference_wrong": only_other,
        "greedy_completions_identical": sum(same) / len(same),
        "mean_matching_prefix_fraction": sum(prefix) / len(prefix),
    }


def _chat(
    base: str, key: str, model: str, prompt: str, max_tokens: int, system: bool = True
) -> str:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
        if system
        else [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        json.dumps(body).encode(),
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)["choices"][0]["message"]["content"] or ""


def run(label: str, n: int, base: str, key: str, model: str, workers: int = 8) -> dict:
    items = make_items(n)
    with ThreadPoolExecutor(workers) as pool:
        # Room for a short line of working on the arithmetic items: with 16 tokens the model's habit of writing
        # the equation first ("548 - 105 + 131 = 5...") was cut off mid-number and scored as wrong, which pushed
        # that category to the floor where it could not show any difference between deployments.
        replies = list(
            pool.map(
                lambda it: _chat(
                    base, key, model, it["prompt"], 48 if it["kind"] == "arith" else 16
                ),
                items,
            )
        )
        open_replies = list(
            pool.map(lambda p: _chat(base, key, model, p, 96, system=False), OPEN_PROMPTS * 4)
        )
    correct = [is_correct(it, r) for it, r in zip(items, replies, strict=True)]
    by_kind = {
        k: [c for it, c in zip(items, correct, strict=True) if it["kind"] == k]
        for k in ("arith", "extract", "classify")
    }
    return {
        "label": label,
        "model": model,
        "items": n,
        "accuracy": sum(correct) / n,
        "ci95": wilson(sum(correct), n),
        "accuracy_by_kind": {k: sum(v) / len(v) for k, v in by_kind.items()},
        "accuracy_items": correct,
        "replies": replies,
        "open_replies": open_replies,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--label", required=True)
    r.add_argument("--items", type=int, default=240)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument(
        "--base-url", default=os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1")
    )
    r.add_argument("--model", default=os.environ.get("WORKSHOP_MODEL", "Qwen/Qwen3-8B"))
    c = sub.add_parser("compare")
    c.add_argument("reference", type=Path)
    c.add_argument("other", type=Path)
    a = ap.parse_args()
    if a.cmd == "run":
        key = os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or "not-set"
        result = run(a.label, a.items, a.base_url, key, a.model)
        a.out.write_text(json.dumps(result, indent=2) + "\n")
        lo, hi = result["ci95"]
        print(
            f"{a.label}: accuracy {result['accuracy']:.3f} (95% CI {lo:.3f}-{hi:.3f}) {result['accuracy_by_kind']}"
        )
        return 0
    out = compare(json.loads(a.reference.read_text()), json.loads(a.other.read_text()))
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
