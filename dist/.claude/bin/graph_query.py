#!/usr/bin/env python3
"""Read the graph backwards: what points at a node.

Every edge is declared by the node that leaves it, and a scope never enumerates what it holds, so
the graph is cheap to walk forwards and answers nothing backwards. That is the right arrangement —
an inverse recorded on the target is a second home for the same fact, and it goes stale the moment
one of the two is edited without the other. The inverse is derived instead, by reading every node
and keeping the edges that arrive.

**It is needed because deletion is never local.** A node that changes kind, boundary or name takes
a new identifier and the old one is removed with every reference to it, so removing a node
obligates edits to everything pointing at it — and nothing else tells a person which those are.
Without this they find out from the check that refuses to close their change, listing the damage
after it is done.

**The edges come from `check_knowledge`, not from a list here.** Which fields name another node is
stated in one place already; a second list would be a second thing to keep in step, and the one
that goes stale would go stale silently — the answer would simply be missing edges, and a missing
edge reads exactly like a node nothing points at.

Declared dependencies: PyYAML.
"""

from __future__ import annotations

from pathlib import Path

import check_knowledge
import node_io


def references_to(root: Path, node_id: str) -> list[tuple[str, str]]:
    """Every edge in the graph arriving at this node, as `(source identifier, locator)`.

    Sorted, and includes the structural edges — a `boundary` naming the node, or a context's
    `subdomain`. Those are what make deleting a scope different from deleting anything else: what
    arrives at a context is everything inside it, and each of them has to be dealt with before the
    context can go.

    A node whose file cannot be read is skipped rather than reported. This function answers what
    points at a node; that some other node is malformed is a different question, and the check is
    where it gets asked.
    """
    arriving: list[tuple[str, str]] = []
    for source in node_io.every_node(root):
        if source == node_id:
            continue
        try:
            frontmatter, _ = node_io.read(root, source)
        except node_io.NodeIOError:
            continue
        edges = check_knowledge.references(frontmatter) + check_knowledge.structural_references(frontmatter)
        arriving += [(source, locator) for target, locator in edges if target == node_id]
    return sorted(arriving)


def describe(arriving: list[tuple[str, str]]) -> str:
    """The arriving edges as lines a person reads, one per edge."""
    return "\n".join(f"    {source} — {locator}" for source, locator in arriving)
