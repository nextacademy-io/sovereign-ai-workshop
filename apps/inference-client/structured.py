#!/usr/bin/env python3
"""Structured output: ask for JSON that must match a schema.

The server constrains decoding to the schema, so the reply is syntactically valid JSON. It does NOT
tell the model what to write: describe the fields in the prompt too. Without that, a model that never
mentions a required field can run out of tokens on whitespace and return truncated JSON (we measured
exactly this: 300 tokens, 5,469 of them blanks). This is the building block for classification and
extraction pipelines (workshop scenarios B and D).

    python apps/inference-client/structured.py "My parcel never arrived and I was charged twice."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import make_client, model_name  # noqa: E402

SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["billing", "delivery", "warranty", "security", "other"],
        },
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "needs_human": {"type": "boolean"},
        "summary": {"type": "string", "maxLength": 160},
    },
    "required": ["category", "urgency", "needs_human", "summary"],
    "additionalProperties": False,
}


def classify(message: str, model: str | None = None) -> dict:
    client = make_client()
    resp = client.chat.completions.create(
        model=model or model_name(),
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the customer message. Reply with one compact JSON object with exactly these fields: "
                    "category (billing, delivery, warranty, security or other), urgency (low, medium or high), "
                    "needs_human (true or false) and summary (at most 160 characters)."
                ),
            },
            {"role": "user", "content": message},
        ],
        temperature=0,
        max_tokens=200,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "ticket", "schema": SCHEMA, "strict": True},
        },
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return json.loads(resp.choices[0].message.content)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("message")
    ap.add_argument("--model", default=model_name())
    args = ap.parse_args()
    print(json.dumps(classify(args.message, args.model), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
