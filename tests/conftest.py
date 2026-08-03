"""Shared fixtures.

`src/claude/bin` goes on the path the way it sits once installed — its own directory is the
import root for a consumer, so the suite imports `graph` the way a consumer runs it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src" / "claude" / "bin"

if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

BODY = "## What it is\nProse for a reader.\n\n## Rules\nNone.\n"


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads((REPO / "src/claude/schemas/node.json").read_text(encoding="utf-8"))


@pytest.fixture
def root(tmp_path: Path) -> Path:
    base = tmp_path / "knowledge"
    base.mkdir()
    return base


@pytest.fixture
def write(root: Path):
    """Write one node file at the path its identifier computes to."""
    def put(nid: str, front: dict, body: str = BODY) -> Path:
        path = root / f"{nid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{text}---\n{body}", encoding="utf-8")
        return path
    return put


@pytest.fixture
def sound_base(write):
    """The smallest base every cross-node check passes: a context, an aggregate, and its root."""
    write("context/sales", {"title": "Sales", "summary": "Ordering.", "strategic": "core"})
    write("aggregate/sales/orders", {"title": "Orders", "summary": "Order and lines together."})
    write("definition/sales/order", {
        "title": "Order", "summary": "A customer's order.",
        "ddd": "aggregate-root", "aggregate": "orders",
        "identity": ["order_number"],
        "attributes": [
            {"name": "order_number", "type": "string", "max_length": 20},
            {"name": "total", "type": "decimal", "precision": 12, "scale": 2},
        ],
    })
    return write
