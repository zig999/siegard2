#!/usr/bin/env python3
"""The door. Every change to the graph comes through one of these calls.

A node is created, edited or deleted inside an open change, and the change records which nodes it
touched. Nothing else in this package writes a node — `node_io` can, and is the mechanism this
module drives, but it neither knows nor asks whether a change is open.

**The door is a convention, not an enforcement.** Python has no way to stop a caller importing
`node_io` and writing directly, or opening the file in an editor. What this module gives is a
single place where the rules are applied, so that a change made through it is known to have been
validated and known to have been recorded. A change made around it is neither, and the set of
touched nodes cannot say so — an empty set means either that nothing changed or that nothing came
through here.

**Three rules the door applies that the layers below do not.**

*A node is written inside a change or not at all.* Which nodes a requirement moved is the question
the change set exists to answer, and a write outside a change is a node that moved with nobody
recording it.

*A node is validated against the frontmatter contract before it is written.* The graph's consumer
generates source from it, so an invalid node is not a file to fix later — it is a generator input
that either fails far from the cause or produces something nobody specified. Refusing at the write
is the last point where the error still names the node that caused it.

*A change does not close while the graph does not hold together.* Closing clears the set, so a
change allowed to close over a dangling reference or a containment loop takes with it the only
record of where to look. The full sweep runs, and it is the same sweep the command line runs —
`check_knowledge.problems_in`, not a second copy that can disagree with it.

**Recorded before written, deliberately.** If the write fails after the record, the set names a
node that did not change and something downstream regenerates it for nothing. If the write
succeeded and the record failed, the set is missing a node that did change, and whatever consumes
it emits stale output while reporting success. The first is waste and the second is a defect, so
the order is the one that fails toward waste.

Declared dependencies: PyYAML, jsonschema.

Usage:
    from graph_edit import open_change, create_node, edit_node, delete_node, close_change

    open_change(root, requirement="rq_2026_0042")
    create_node(root, "dm.definition.sales.order", frontmatter, body)
    edit_node(root, "dm.rule.sales.total-positive", frontmatter, body)
    touched = close_change(root)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import change_set
import check_knowledge
import node_io
from change_set import ChangeError, discard_change, is_open, requirement_of, touched
from node_io import NodeIOError

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: jsonschema is not installed (pip install jsonschema)", file=sys.stderr)
    raise SystemExit(2)

__all__ = [
    "open_change", "close_change", "discard_change", "is_open", "touched", "requirement_of",
    "create_node", "edit_node", "delete_node",
    "GraphEditError", "ChangeError", "NodeIOError",
]


class GraphEditError(Exception):
    """The door refused: no change is open, a precondition failed, or the node is invalid."""


def _contract() -> dict:
    path = check_knowledge.contract_path()
    if not path.is_file():
        raise GraphEditError(
            f"{path} is missing, so nothing can be validated against it. A node written without "
            f"the contract present is a node nobody checked, and it is indistinguishable "
            f"afterwards from one that passed"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _require_open(root: Path) -> None:
    if not change_set.is_open(root):
        raise GraphEditError(
            f"no change is open under {root}. Call `open_change` first — a node written outside a "
            f"change is one that moved with nothing recording that it did"
        )


def _validate(node_id: str, frontmatter: dict) -> None:
    """Hold this node's frontmatter to the contract, and report every way it fails at once.

    Every error rather than the first, because a caller fixing one at a time re-runs the write for
    each and learns the next only by failing again.
    """
    validator = Draft202012Validator(_contract())
    errors = sorted(validator.iter_errors(frontmatter), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    lines = []
    for error in errors:
        where = ".".join(str(part) for part in error.absolute_path) or "(the node)"
        lines.append(f"    {where}: {error.message}")
    joined = "\n".join(lines)
    raise GraphEditError(
        f"`{node_id}` does not satisfy the frontmatter contract, and is not written:\n{joined}"
    )


def open_change(root: Path, requirement: str | None = None) -> None:
    """Begin a change. Every node written through this module is recorded until it closes."""
    change_set.open_change(root, requirement)


def create_node(root: Path, node_id: str, frontmatter: dict, body: str) -> Path:
    """Add a node the graph does not hold."""
    _require_open(root)
    if node_io.exists(root, node_id):
        raise GraphEditError(
            f"`{node_id}` is already in the graph. Editing it is `edit_node`; creating it again "
            f"would overwrite a node without anything saying it had been there"
        )
    _validate(node_id, frontmatter)
    change_set.record(root, node_id)
    return node_io.write(root, node_id, frontmatter, body)


def edit_node(root: Path, node_id: str, frontmatter: dict, body: str) -> Path:
    """Replace a node the graph holds.

    The whole frontmatter and the whole body are supplied. There is no field-level edit here: the
    contract is conditional across fields — what a `definition` requires depends on its `ddd`, what
    an `interface` requires depends on its `ownership` — so a node is valid or not as a whole, and
    validating a fragment would answer a question nobody asked.
    """
    _require_open(root)
    if not node_io.exists(root, node_id):
        raise GraphEditError(
            f"the graph holds no `{node_id}`. Adding it is `create_node`; editing an absent node "
            f"would create one while recording it as a change to something that existed"
        )
    _validate(node_id, frontmatter)
    change_set.record(root, node_id)
    return node_io.write(root, node_id, frontmatter, body)


def delete_node(root: Path, node_id: str) -> Path:
    """Remove a node the graph holds.

    Nothing here checks what still points at the node. A deletion that orphans a reference is
    caught when the change closes, by the same sweep that catches everything else — and refusing
    here instead would make the only legal order of work "unpick every reference first", which is
    not how the removal of a node is arrived at. The change stays open until the references are
    gone; the door is what will not let it close before then.
    """
    _require_open(root)
    if not node_io.exists(root, node_id):
        raise GraphEditError(
            f"the graph holds no `{node_id}`, so there is nothing to delete. Recording a deletion "
            f"that did not happen would send whatever consumes the change set looking for a node "
            f"that was never there"
        )
    change_set.record(root, node_id)
    return node_io.remove(root, node_id)


def close_change(root: Path) -> list[str]:
    """Finish the change and return the nodes it touched, clearing the set.

    Refused while the graph does not hold together. The set is the only thing that says where a
    change happened, and clearing it over an unresolved reference or a containment loop leaves the
    defect in place with nothing pointing at it. Discard the change instead if the intent is to
    abandon it — that is a different statement and has a different call.
    """
    _require_open(root)
    held = change_set.touched(root)
    problems, _, count = check_knowledge.problems_in(root, _contract())
    if problems:
        listed = "\n".join(f"    {problem}" for problem in problems)
        raise GraphEditError(
            f"the change is not closed: {len(problems)} disagreement(s) across {count} node(s), "
            f"and closing would clear the record of the {len(held)} node(s) it touched.\n{listed}"
        )
    return change_set.close_change(root)
