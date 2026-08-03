"""Shared fixtures for the suite.

The shipped modules are written to be run from their own directory — that is the import root once
installed, and it is what makes a sibling import resolve for a consumer. So the suite puts
`src/claude/bin` on the path rather than importing through a package: importing them any other way
would exercise an arrangement no consumer has.

Nothing here hard-codes a contract version. `contract_version` is read from the composed contract,
so a bump lands in the tests as a bump rather than as a wall of failures about a string.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src" / "claude" / "bin"
SCRIPTS = REPO / "scripts"

if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def bin_dir() -> Path:
    return BIN


@pytest.fixture(scope="session")
def contract() -> dict:
    return json.loads((REPO / "src/claude/schemas/domain-object.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def contract_version(contract: dict) -> str:
    return contract["properties"]["contract_version"]["const"]


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """An empty knowledge root, one per test, so no test depends on another having run."""
    base = tmp_path / "knowledge"
    base.mkdir()
    return base


@pytest.fixture
def node(contract_version: str):
    """A frontmatter mapping that satisfies the contract, with the kind's own fields supplied."""
    def build(node_id: str, kind: str, **extra) -> dict:
        return {
            "id": node_id,
            "type": kind,
            "title": "T",
            "contract_version": contract_version,
            "generated": {"by": "test", "at": "2026-08-02T00:00:00Z"},
            "origin": "stated",
            "question": "q?",
            "description": "d",
            "out_of_scope": ["x"],
            **extra,
        }
    return build


@pytest.fixture
def sample(node):
    """The three objects most tests need: a subdomain, a context in it, a definition in that."""
    return {
        "subdomain": ("dm.subdomain.commerce",
                      node("dm.subdomain.commerce", "subdomain", subdomain_type="core")),
        "context": ("dm.context.sales",
                    node("dm.context.sales", "context", subdomain="dm.subdomain.commerce")),
        "definition": ("dm.definition.sales.order",
                       node("dm.definition.sales.order", "definition", ddd="value-object",
                            boundary="dm.context.sales",
                            attributes=[{"name": "total", "type": "money"}])),
    }
