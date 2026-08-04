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
PLAN_BODY = "## What it is\nProse for a reader.\n\n## Notes\nNone.\n"


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


# ---------------------------------------------------------------- the plan side


def base_pin_of(root: Path) -> str:
    """The pin the base at `root` computes to right now, by the validator's own pipeline."""
    import graph
    import plan
    validator, allowed, obligations = graph.contract()
    nodes, problems = graph.collect(root, validator, allowed, obligations)
    problems += graph.cross_problems(nodes)
    assert problems == [], f"the fixture base does not hold together: {problems}"
    return plan.base_pin(nodes)


@pytest.fixture
def work(tmp_path: Path) -> Path:
    base = tmp_path / "work"
    base.mkdir()
    return base


@pytest.fixture
def write_plan(work: Path):
    """Write one plan node file at the path its identifier computes to."""
    def put(pid: str, front: dict, body: str = PLAN_BODY) -> Path:
        path = work / f"{pid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{text}---\n{body}", encoding="utf-8")
        return path
    return put


@pytest.fixture
def gapped_base(sound_base):
    """The sound base plus one definition carrying an open gap — the triage checks' subject."""
    sound_base("definition/sales/invoice", {
        "title": "Invoice", "summary": "The bill.", "ddd": "value-object",
        "gaps": [{"field": "attributes", "why": "The material lists no fields."}],
    })
    return sound_base


@pytest.fixture
def sound_plan(root, gapped_base, write_plan):
    """The smallest plan every cross-node check passes, bound to the gapped fixture base:
    an inventory, one epic covering two base nodes, and a task for each — one of them
    triaging the seeded gap."""
    pin = base_pin_of(root)
    write_plan("inventory/order-service", {
        "title": "Order service", "summary": "One layered service under src/.",
        "area": ["src/"],
        "conventions": [{"statement": "Handlers delegate to a service module.",
                         "seen_at": "src/orders/routes.ts"}],
    })
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["definition/sales/order", "definition/sales/invoice"],
    })
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "nodes": ["definition/sales/order"],
        "base": pin,
    })
    write_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill for a recorded order.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "nodes": ["definition/sales/invoice"],
        "base": pin,
        "depends_on": ["task/checkout/record-order"],
        "unresolved": [{"gap": "definition/sales/invoice#attributes"}],
    })
    return write_plan
