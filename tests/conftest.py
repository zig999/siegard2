"""Shared fixtures.

`src/claude/bin` goes on the path the way it sits once installed — its own directory is the
import root for a consumer, so the suite imports each script the way a consumer runs it.
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

ELEMENT_BODY = "## Description\nProse for a reader.\n\n## Responsibility\nNone.\n"
ONE_HEADING_BODY = "## Description\nProse for a reader.\n"
PLAN_BODY = "## What it is\nProse for a reader.\n\n## Notes\nNone.\n"


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads((REPO / "src/claude/schemas/node.json").read_text(encoding="utf-8"))


@pytest.fixture
def root(tmp_path: Path) -> Path:
    base = tmp_path / "specification"
    base.mkdir()
    return base


@pytest.fixture
def write(root: Path):
    """Write one specification file at the path its identity computes to (SPEC-003 R1)."""
    def put(nid: str, front: dict, body: str = ELEMENT_BODY) -> Path:
        path = root / f"{nid}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{text}---\n{body}", encoding="utf-8")
        return path
    return put


@pytest.fixture
def sound_base(write):
    """The smallest specification every cross-node check passes: a context, an aggregate root,
    and a value object a rule makes reachable (SPEC-001 R6 exempts an aggregate root, never a
    value object)."""
    write("decision-log", {"entries": []}, body="")
    write("domain/sales/_context", {"strategic": "core"})
    write("domain/sales/order", {
        "type": "aggregate-root",
        "attributes": [
            {"name": "order_number", "type": "string", "required": True},
            {"name": "total", "type": "decimal", "required": True},
        ],
    })
    write("domain/sales/invoice", {
        "type": "value-object",
        "attributes": [{"name": "amount", "type": "decimal", "required": True}],
    })
    write("rules/sales/invoice-immutable", {
        "type": "invariant",
        "statement": "An invoice, once raised, is never modified.",
        "constrains": ["domain/sales/invoice"],
    }, body=ONE_HEADING_BODY)
    return write


# ---------------------------------------------------------------- the plan side


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


def task_pin_of(work: Path, tid: str) -> str:
    """The pin one task computes to right now: the SHA-256 of its own file."""
    import deliver
    return deliver.task_pin(work, tid)


@pytest.fixture
def sound_plan(root, sound_base, write_plan):
    """The smallest plan every cross-node check passes, against the sound fixture specification:
    an inventory, one epic covering two specification nodes, and a task for each."""
    write_plan("inventory/order-service", {
        "title": "Order service", "summary": "One layered service under src/.",
        "area": ["src/"],
        "conventions": [{"statement": "Handlers delegate to a service module.",
                         "seen_at": "src/orders/routes.ts"}],
    })
    write_plan("epic/checkout", {
        "title": "Checkout", "summary": "Everything order placement needs.",
        "covers": ["domain/sales/order", "domain/sales/invoice"],
    })
    write_plan("task/checkout/record-order", {
        "title": "Record order", "summary": "Persist a placed order.",
        "objective": "A valid order is persisted and retrievable by its order_number.",
        "criteria": ["Submitting a valid order returns its order_number."],
        "implements": ["domain/sales/order"],
    })
    write_plan("task/checkout/bill-order", {
        "title": "Bill order", "summary": "Raise the bill for a recorded order.",
        "objective": "A recorded order produces exactly one invoice.",
        "criteria": ["Recording an order twice produces one invoice."],
        "implements": ["domain/sales/invoice"],
        "depends_on": ["task/checkout/record-order"],
    })
    return write_plan


# ------------------------------------------------------------ the delivery side


@pytest.fixture
def delivery(tmp_path: Path) -> Path:
    base = tmp_path / "delivery"
    base.mkdir()
    return base


@pytest.fixture
def write_delivery(delivery: Path):
    """Write one delivery node file at the path its identifier computes to."""
    def put(did: str, front: dict, body: str = PLAN_BODY) -> Path:
        path = delivery / f"{did}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{text}---\n{body}", encoding="utf-8")
        return path
    return put


STANDARD = {
    "contract_version": "siegard-standard/1",
    "standard": "example-service",
    "summary": "How this project's modules are layered and wired.",
    "rules": [
        {"id": "ARC-01",
         "statement": "A constructor receives interfaces, never concrete implementations.",
         "because": "A class bound to a concrete collaborator cannot be exercised without it.",
         "decided_by": "reading",
         "applies_to": [{"under": "src", "suffix": ".ts", "nested": True}]},
        {"id": "ARC-02",
         "statement": "Business logic lives in a service, never in a route handler.",
         "because": "A rule implemented in a handler only exists over that transport.",
         "decided_by": "reading",
         "applies_to": [{"under": "src/routes", "suffix": ".ts"}]},
        {"id": "PRH-01",
         "statement": "Production code logs through the configured logger.",
         "because": "A console line goes nowhere in production.",
         "decided_by": "tool",
         "tool": "lint",
         "applies_to": [{"under": "src", "suffix": ".ts", "nested": True}]},
        {"id": "TST-01",
         "statement": "A test reaches a boundary through its interface, never by constructing it.",
         "because": "A spec bound to a concrete collaborator cannot be run without standing one up.",
         "decided_by": "reading",
         "applies_to": [{"under": "tests", "suffix": ".spec.ts", "nested": True}]},
    ],
    "dependencies": [
        {"package": "pino", "why": "PRH-01 requires production code to log through it.",
         "rules": ["PRH-01"]},
    ],
    "commands": [
        {"step": "install", "command": "true", "timeout_seconds": 60, "role": "install"},
        {"step": "lint", "command": "true", "timeout_seconds": 60},
        {"step": "test", "command": "true", "timeout_seconds": 60, "role": "suite"},
    ],
}


@pytest.fixture
def write_standard(delivery: Path):
    """Copy a standard into the delivery root the way a review does, and return its reference."""
    def put(data: dict = None, name: str = "example-service.yaml") -> dict:
        import hashlib
        where = delivery / "standards"
        where.mkdir(exist_ok=True)
        path = where / name
        path.write_text(yaml.safe_dump(data or STANDARD, sort_keys=False), encoding="utf-8")
        pin = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        return {"at": f"standards/{name}", "pin": pin}
    return put


@pytest.fixture
def sound_delivery(root, work, sound_plan, write_delivery, delivery):
    """The smallest delivery every check passes: one task of the fixture plan implemented and
    proven. The plan's other task stays undelivered on purpose."""
    pin = task_pin_of(work, "task/checkout/record-order")
    delivery_root = delivery
    write_delivery("implementation/checkout/record-order", {
        "title": "Record a placed order",
        "summary": "The entry point that persists a valid order.",
        "task": pin,
        "files": [{"path": "src/orders/place.ts",
                   "effect": "persists a submitted order and answers with its order_number"}],
        "criteria": [{"criterion": "Submitting a valid order returns its order_number.",
                      "met": True,
                      "how": "place() returns the persisted order_number unchanged"}],
        "nodes": [{"node": "domain/sales/order",
                   "encoded_at": ["src/orders/place.ts"],
                   "how": "the order's identity and attributes are the shape place() persists"}],
    })
    import hashlib
    written = delivery_root / "implementation/checkout/record-order.md"
    write_delivery("proof/checkout/record-order", {
        "title": "Proof for recording a placed order",
        "summary": "What proves the recorded order.",
        "implementation": "sha256:" + hashlib.sha256(written.read_bytes()).hexdigest(),
        "tests": [{"file": "tests/place.spec.ts",
                   "name": "returns the order_number for a valid submission",
                   "proves": "Submitting a valid order returns its order_number.",
                   "fails_when": "place() answers with anything but the stored order_number"}],
    })
    return write_delivery
