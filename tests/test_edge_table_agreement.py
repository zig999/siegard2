"""The edge table `foundation/0003` declares closed, held to a form a transcription can read.

R13 closes the edge vocabulary "per the edge table", R14 requires a validator to enforce each
edge's cardinality and whether expansion traverses it, and R18 requires an edge naming an id the
graph does not hold to be reported. The table is prose, and prose is not machine-readable, so
whatever enforces R14 has to carry a transcription of it.

**The transcription is gone, and the agreement half of this module went with it.** It compared
every column against `EDGE_KINDS` in the shipped graph library, which was removed with the
generation path. `src/claude/schemas/knowledge-graph.json` is not a replacement: it fixes the
*shape* of an `edge_kinds` entry — `minimum`, `maximum`, `inverse_maximum`, `traversed`, `depth` —
and keys it by edge name under `additionalProperties`, so it constrains how a vocabulary is written
down and never says which edges are in it.

What is left is the half that needs no second copy: the table has to be parseable, its cells
canonical, and its vocabulary free of the one reference that must never become an edge. That keeps
the next transcription checkable against something rather than typed from a reading, which is why
the columns were given a canonical notation in the first place. The comparison returns with the
component that carries the vocabulary again.

Cardinality became checkable when the specification's column was split in two and given one
canonical `<min>..<max>` notation. Before that it mixed three questions in one cell — edges out of
a node, edges into a node, and targets named by one attribute — and no parser could tell them
apart, so the numbers a validator enforced were the one part of the table nothing verified.

Two residuals, named rather than left to be assumed:

- the **In** column's minimum is not modelled. Nothing requires a node to be referenced, and
  whether an unreferenced node is a defect is the orphan rule of R18, not a cardinality bound.
- the zero-`boundary` exception for a bounded-context boundary cannot live in a table cell. R16
  states it in prose, so this module checks the rule and not its exception.
"""

from __future__ import annotations

import re
import unittest

from tests.support import REPO_ROOT

SPEC = REPO_ROOT / "foundation" / "0003-knowledge-ontology-and-notation.md"
HEADER = "| Edge | Origin → target | Out | In | Traversed | Depth |"
BACKTICKED = re.compile(r"`([^`]+)`")
BOUNDS = re.compile(r"^(\d+)\.\.(\d+|n)$")

# `superseded_by` named a node and was deliberately absent from the table: it was a resolvable
# reference rather than an edge, with a traversal prohibition written for it in both directions.
# The change that removed the maturity ladder then removed the field itself, so the
# name must appear in neither the table nor any vocabulary derived from it — now because there is
# nothing left for it to point at, which is a stronger reason than the one it was excluded for.
NOT_AN_EDGE = "superseded_by"


def parse_bounds(cell: str) -> tuple[int, int | None]:
    """`0..n` → (0, None); `1..1` → (1, 1). Raises on anything else, which is the point."""
    match = BOUNDS.match(cell.strip())
    if not match:
        raise AssertionError(f"cardinality cell {cell.strip()!r} is not in <min>..<max> notation")
    low, high = match.groups()
    return int(low), None if high == "n" else int(high)


def rows() -> list[list[str]]:
    """Every data row of the edge table, cells split and stripped."""
    lines = SPEC.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == HEADER)
    out: list[list[str]] = []
    for line in lines[start + 2:]:
        if not line.strip().startswith("|"):
            break
        out.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return out


def edge_of(row: list[str]) -> str:
    match = BACKTICKED.search(row[0])
    assert match, f"{row[0]!r} names no edge in backticks"
    return match.group(1)


class TheTableIsParseable(unittest.TestCase):
    """Without this the table is prose that only reads as data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = rows()

    def test_the_header_is_where_this_module_expects_it(self) -> None:
        self.assertTrue(self.rows, f"no data row followed {HEADER!r} in {SPEC.name}")

    def test_every_row_has_the_columns_the_header_declares(self) -> None:
        width = len(HEADER.strip().strip("|").split("|"))
        for row in self.rows:
            with self.subTest(edge=row[0]):
                self.assertEqual(width, len(row))

    def test_every_edge_is_named_in_backticks(self) -> None:
        """The name is what a transcription keys on, so it may not be prose."""
        for row in self.rows:
            with self.subTest(edge=row[0]):
                self.assertTrue(BACKTICKED.search(row[0]), f"{row[0]!r} names no edge in backticks")

    def test_no_edge_is_listed_twice(self) -> None:
        names = [edge_of(row) for row in self.rows]
        self.assertEqual(sorted(set(names)), sorted(names), "an edge appears twice in the table")

    def test_both_cardinality_columns_are_canonical(self) -> None:
        for row in self.rows:
            with self.subTest(edge=edge_of(row)):
                out_low, out_high = parse_bounds(row[2])
                _in_low, in_high = parse_bounds(row[3])
                if out_high is not None:
                    self.assertLessEqual(out_low, out_high)
                self.assertNotEqual(0, in_high, "an edge nothing may point at is not an edge")

    def test_traversal_is_decidable_and_depth_is_a_number(self) -> None:
        """R14: expansion follows only traversed edges, so neither column may read two ways."""
        for row in self.rows:
            with self.subTest(edge=edge_of(row)):
                self.assertTrue(row[4], "the traversal cell is empty")
                self.assertRegex(row[5], r"^\d+$", "depth is not a number")

    def test_the_reference_that_is_not_an_edge_is_absent(self) -> None:
        self.assertNotIn(NOT_AN_EDGE, {edge_of(row) for row in self.rows})


if __name__ == "__main__":
    unittest.main()
