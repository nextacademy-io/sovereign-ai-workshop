"""Tools the model may call. Plain Python functions plus a JSON schema each.

The model never executes anything. It emits a *request* (a function name and JSON
arguments); the application decides whether and how to run it. That separation is the
security boundary of tool calling, so every tool here validates its own input.
"""

from __future__ import annotations

import ast
import operator
import re
from pathlib import Path

HANDBOOK = Path(__file__).resolve().parents[1] / "rag-demo" / "handbook"

INVENTORY = {
    "PAL-100": {"name": "Euro pallet", "stock": 412, "warehouse": "north"},
    "BOX-240": {"name": "Shipping box 240 mm", "stock": 3_180, "warehouse": "north"},
    "TAP-050": {"name": "Packing tape 50 mm", "stock": 96, "warehouse": "south"},
    "LBL-A6": {"name": "Label roll A6", "stock": 0, "warehouse": "south"},
}
RATES_TO_EUR = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17, "CHF": 1.05, "PLN": 0.23}

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def calculate(expression: str) -> str:
    """Evaluate plain arithmetic. Anything else (names, calls, attributes) is rejected."""
    if len(expression) > 200:
        raise ValueError("expression too long")

    def ev(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub | ast.UAdd):
            return -ev(node.operand) if isinstance(node.op, ast.USub) else ev(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            base, exp = ev(node.left), ev(node.right)
            if abs(exp) > 10:  # keeps `9**9**9` from burning the CPU
                raise ValueError("exponent too large")
            return base**exp
        raise ValueError("only arithmetic is allowed")

    result = ev(ast.parse(expression, mode="eval").body)
    return str(round(result, 6)) if isinstance(result, float) else str(result)


def get_stock(sku: str) -> str:
    item = INVENTORY.get(sku.strip().upper())
    if item is None:
        return f"unknown SKU '{sku}'. Known SKUs: {', '.join(sorted(INVENTORY))}"
    return f"{item['name']} ({sku.upper()}): {item['stock']} units in the {item['warehouse']} warehouse"


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    src, dst = from_currency.upper(), to_currency.upper()
    if src not in RATES_TO_EUR or dst not in RATES_TO_EUR:
        return f"unsupported currency. Supported: {', '.join(sorted(RATES_TO_EUR))}"
    value = amount * RATES_TO_EUR[src] / RATES_TO_EUR[dst]
    return f"{amount:g} {src} = {value:.2f} {dst} (fixed workshop rates, not live)"


def search_handbook(query: str, limit: int = 3) -> str:
    """Keyword search over the company handbook (no embeddings: that is the RAG demo's job)."""
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    scored = []
    for path in sorted(HANDBOOK.glob("*.md")):
        if "archived" in path.name:
            continue
        for para in path.read_text().split("\n\n"):
            score = sum(1 for w in words if w in para.lower())
            if score:
                scored.append((score, path.name, " ".join(para.split())))
    scored.sort(key=lambda t: -t[0])
    if not scored:
        return "no matching passage"
    return "\n".join(f"[{name}] {text}" for _, name, text in scored[:limit])


def _schema(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


REGISTRY = {
    "calculate": (
        calculate,
        _schema(
            "calculate",
            "Evaluate an arithmetic expression such as '(12 * 7) / 3'. Use it for every calculation.",
            {"expression": {"type": "string"}},
            ["expression"],
        ),
    ),
    "get_stock": (
        get_stock,
        _schema(
            "get_stock",
            "Look up the current stock of a warehouse item by SKU, for example PAL-100.",
            {"sku": {"type": "string"}},
            ["sku"],
        ),
    ),
    "convert_currency": (
        convert_currency,
        _schema(
            "convert_currency",
            "Convert an amount between EUR, USD, GBP, CHF and PLN.",
            {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
            ["amount", "from_currency", "to_currency"],
        ),
    ),
    "search_handbook": (
        search_handbook,
        _schema(
            "search_handbook",
            "Search the company handbook (vacation, remote work, expenses, incidents, data retention).",
            {"query": {"type": "string"}},
            ["query"],
        ),
    ),
}


def openai_tools() -> list[dict]:
    return [schema for _, schema in REGISTRY.values()]


def run_tool(name: str, arguments: dict) -> str:
    """Execute a tool the model asked for. Unknown names and bad arguments become text the model can read."""
    if name not in REGISTRY:
        return f"error: unknown tool '{name}'"
    func, _ = REGISTRY[name]
    try:
        return func(**arguments)
    except (TypeError, ValueError, SyntaxError, ZeroDivisionError) as exc:
        return f"error: {type(exc).__name__}: {exc}"
