"""The validator's edge table must agree with the one specs/0003 declares closed.

R17 closes the edge vocabulary "per the table under **The ontology: edges, cardinality, and
traversal**", R18 requires a validator to enforce cardinality, and R19 requires every edge to
declare whether expansion traverses it and to what depth. That table is prose, and prose is not
machine-readable, so `scripts/knowledge_graph_lib.py` carries it as data. Two copies of one fact
diverge, and `CLAUDE.md` **Authority placement** forbids leaving them to.

This module reads the specification's own table and compares every column against the module.
The specification stays the authority; the module is a checked transcription rather than a
trusted one.

Cardinality became checkable when the specification's column was split in two and given one
canonical `<min>..<max>` notation. Before that it mixed three questions in one cell — edges out
of a node, edges into a node, and targets named by one attribute — and no parser could tell
them apart, so the numbers the validator enforced were the one part of the table nothing
verified.

Two residuals, named rather than left to be assumed:

- the **In** column's minimum is not modelled. Nothing requires a node to be referenced, and
  whether an unreferenced node is a defect is the orphan rule of R22, not a cardinality bound.
- the zero-`boundary` exception for a bounded-context boundary cannot live in a table cell. It
  is stated in prose below the table and implemented in one named function, so this module
  checks the rule and not its exception.
"""

from __future__ import annotations

import re
import unittest

from knowledge_graph_lib import EDGE_KINDS
from tests.support import REPO_ROOT

SPEC = REPO_ROOT / "specs" / "0003-knowledge-ontology-and-notation.md"
HEADER = "| Edge | Origin → target | Out | In | Authored or structural | Traversed | Depth |"
BACKTICKED = re.compile(r"`([^`]+)`")
BOUNDS = re.compile(r"^(\d+)\.\.(\d+|n)$")

# The module carries no edge the specification's table omits, and the table names none the
# module lacks. Asserted as an exact empty set so a silent addition on either side fails.
UNLISTED: set[str] = set()

# `superseded_by` names a node and is deliberately absent from the table: R22 requires its
# target to resolve and forbids expansion from following it, so it is a resolvable reference
# rather than an edge. It must appear in neither the table nor the edge vocabulary.
NOT_AN_EDGE = "superseded_by"


def parse_bounds(cell: str) -> tuple[int, int | None]:
    """`0..n` → (0, None); `1..1` → (1, 1). Raises on anything else, which is the point."""
    match = BOUNDS.match(cell.strip())
    if not match:
        raise AssertionError(f"cardinality cell {cell.strip()!r} is not in <min>..<max> notation")
    low, high = match.groups()
    return int(low), None if high == "n" else int(high)


def spec_edge_table() -> dict[str, dict]:
    """Every row of the specification's edge table, parsed into the fields the module holds."""
    lines = SPEC.read_text().splitlines()
    start = lines.index(HEADER)
    table: dict[str, dict] = {}
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = line.split("|")
        minimum, maximum = parse_bounds(cells[3])
        _inverse_minimum, inverse_maximum = parse_bounds(cells[4])
        depth = cells[7].strip()
        row = {
            "minimum": minimum,
            "maximum": maximum,
            "inverse_maximum": inverse_maximum,
            "traversed": cells[6].strip().lower().startswith("yes"),
            "depth": int(depth) if depth.isdigit() else None,
        }
        for name in BACKTICKED.findall(cells[1]):
            table[name] = row
    return table


class EdgeTableAgreement(unittest.TestCase):
    def setUp(self):
        self.spec_table = spec_edge_table()

    def test_the_specification_table_was_actually_read(self):
        """A parse that silently found nothing would make every assertion below vacuous."""
        self.assertGreaterEqual(len(self.spec_table), 11, self.spec_table)
        self.assertIn("boundary", self.spec_table)
        self.assertIn("attributes[].of", self.spec_table)
        self.assertIn("rejections[].error", self.spec_table)

    def test_supersession_is_in_neither_the_table_nor_the_edge_vocabulary(self):
        self.assertNotIn(NOT_AN_EDGE, self.spec_table)
        self.assertNotIn(NOT_AN_EDGE, EDGE_KINDS)
        self.assertNotIn("supersedes", self.spec_table)
        self.assertNotIn("supersedes", EDGE_KINDS)

    def test_every_declared_edge_is_implemented(self):
        missing = sorted(set(self.spec_table) - set(EDGE_KINDS))
        self.assertEqual(missing, [], f"the specification declares edges the module lacks: {missing}")

    def test_the_module_adds_no_edge_the_table_omits(self):
        extra = set(EDGE_KINDS) - set(self.spec_table)
        self.assertEqual(
            extra,
            UNLISTED,
            "the module's edge vocabulary drifted from the closed one R17 declares. "
            f"Unrecorded additions: {sorted(extra - UNLISTED)}",
        )

    def test_every_declared_edge_is_traversed(self):
        """R52 removed the three edges no resolution read, so none should remain."""
        untraversed = sorted(name for name, kind in EDGE_KINDS.items() if not kind.traversed)
        self.assertEqual(untraversed, [], f"edges no resolution reads: {untraversed}")

    def test_cardinality_agrees_for_every_declared_edge(self):
        """R18's numbers, compared rather than trusted."""
        disagreements = {}
        for name, declared in self.spec_table.items():
            kind = EDGE_KINDS.get(name)
            if kind is None:
                continue
            actual = {
                "minimum": kind.minimum,
                "maximum": kind.maximum,
                "inverse_maximum": kind.inverse_maximum,
            }
            expected = {
                "minimum": declared["minimum"],
                "maximum": declared["maximum"],
                # An unbounded In column means the module declares no inverse bound at all.
                "inverse_maximum": declared["inverse_maximum"],
            }
            if actual != expected:
                disagreements[name] = {"spec": expected, "module": actual}
        self.assertEqual(disagreements, {}, f"cardinality disagreements: {disagreements}")

    def test_traversal_policy_agrees_for_every_declared_edge(self):
        disagreements = {
            name: (declared["traversed"], EDGE_KINDS[name].traversed)
            for name, declared in self.spec_table.items()
            if name in EDGE_KINDS and EDGE_KINDS[name].traversed != declared["traversed"]
        }
        self.assertEqual(disagreements, {}, f"spec says / module says: {disagreements}")

    def test_depth_agrees_for_every_declared_edge(self):
        disagreements = {
            name: (declared["depth"], EDGE_KINDS[name].depth)
            for name, declared in self.spec_table.items()
            if name in EDGE_KINDS and EDGE_KINDS[name].depth != declared["depth"]
        }
        self.assertEqual(disagreements, {}, f"spec says / module says: {disagreements}")

    def test_a_traversed_edge_declares_a_depth(self):
        """R19 requires the depth as well as the policy, so a traversed edge without one is a gap."""
        for name, kind in EDGE_KINDS.items():
            if kind.traversed:
                self.assertIsNotNone(kind.depth, f"{name} is traversed with no declared depth")
            else:
                self.assertIsNone(kind.depth, f"{name} is not traversed but declares a depth")
