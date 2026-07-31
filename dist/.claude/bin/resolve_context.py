#!/usr/bin/env python3
"""Expand a set of roots into a context package, deterministically.

`specs/0009` fixes the package as a contract and leaves the traversal free, with one
constraint that does all the work: R17 pins expansion order to the contract version the
package records and forbids an order free to differ between two runs of one version. Without
that, R13's `claim-recorded` persistence is a label — `specs/0004` R48 requires a discarded
body to recompute to the recorded content hash, and a package truncated by a budget recomputes
to a different set the moment the traversal reorders.

**The order this version fixes, and why each tiebreak exists.** Breadth first from the roots,
so a depth limit removes the furthest knowledge rather than an arbitrary slice. Roots in the
order the caller selected them, because that order is the caller's judgment and reordering it
would silently rank one justification above another. Within a frontier, by `(edge kind, target
id)` — edge kind first so the order does not change when an object is renamed, and target id to
break the remaining ties with the only total order the data supplies.

**Only declared relationships are followed.** R9: a relationship absent from the ontology's edge
table is not traversed, and one a capability wants that the ontology does not hold is a request
to change the ontology. `knowledge_graph_lib.EDGE_KINDS` is that table, and `traversed` is the
flag it already carries — supersessions are structurally unreachable because
`knowledge_graph_lib` keeps them out of `edges` entirely.

**Stopping and degrading are different questions.** R8 gives one stop reason from a closed set;
R15 records every degradation separately. A run can exhaust its budget *and* fail to resolve a
relationship, and a single field would report one of them. R16 fixes which codes can be which.

Declared dependencies: PyYAML and jsonschema, via scripts/knowledge_graph_lib.py.

Usage:  resolve_context.py --knowledge DIR --request cr_xxxxxxxx --package cp_xxxxxxxx
                           --root ID:CLAIM [--root ...] --budget N [--unit objects|bytes]
                           [--depth-limit N] [--out PATH]
Exit:   0 a package was produced, 1 the roots or the graph make one impossible, 2 cannot run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from cli import cannot_run
from knowledge_graph_lib import EDGE_KINDS, Graph, load

# specs/0009 R17. Bumped when a change to the order changes which objects a package holds; a
# consumer reads it to know whether a recorded hash is still recomputable.
EXPANSION_CONTRACT = "context-expansion/1"

CLOSURE_COMPLETE = "closure_complete"
BUDGET_EXHAUSTED = "budget_exhausted"
DEPTH_LIMIT = "depth_limit"
UNRESOLVED = "unresolved_relationship"


def content_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def cost(graph: Graph, node_id: str, unit: str) -> int:
    return 1 if unit == "objects" else len(graph.nodes[node_id].path.read_bytes())


def outgoing(graph: Graph, node_id: str) -> list[tuple[str, str]]:
    """Every traversable edge leaving `node_id`, as (edge kind, target), in expansion order.

    R9: only what the ontology declares. `EDGE_KINDS[...].traversed` is the ontology's own flag,
    read here rather than restated — a second list of traversable kinds would drift from the
    edge table the knowledge validator enforces.
    """
    found = [
        (edge.kind, edge.target)
        for edge in graph.edges
        if edge.source == node_id
        and EDGE_KINDS.get(edge.kind) is not None
        and EDGE_KINDS[edge.kind].traversed
    ]
    return sorted(set(found))


def resolve(
    graph: Graph,
    roots: list[tuple[str, str]],
    budget: int,
    unit: str,
    depth_limit: int | None,
) -> tuple[list[dict], str, list[dict], int]:
    """Expand and return (entries, stop reason, degradations, consumed)."""
    entries: list[dict] = []
    degradations: list[dict] = []
    seen: set[str] = set()
    consumed = 0
    stop = CLOSURE_COMPLETE

    for node_id, _claim in roots:
        if node_id not in graph.nodes:
            degradations.append(
                {
                    "code": "unresolved_root",
                    "subject": node_id,
                    "evidence": "selected as a root and absent from the knowledge graph",
                }
            )

    # (depth, edge kind, id). Roots keep the caller's order: that order is their judgment.
    frontier: list[tuple[int, str | None, str]] = [
        (0, None, node_id) for node_id, _ in roots if node_id in graph.nodes
    ]

    while frontier:
        depth, via, node_id = frontier.pop(0)
        if node_id in seen:
            continue

        if depth_limit is not None and depth > depth_limit:
            stop = DEPTH_LIMIT
            degradations.append(
                {
                    "code": "depth_limit",
                    "subject": node_id,
                    "evidence": f"reached at depth {depth}, past the declared limit of {depth_limit}",
                }
            )
            break

        price = cost(graph, node_id, unit)
        if consumed + price > budget:
            stop = BUDGET_EXHAUSTED
            degradations.append(
                {
                    "code": "budget_exhausted",
                    "subject": node_id,
                    "evidence": f"{consumed + price} would exceed the {unit} budget of {budget}",
                }
            )
            break

        seen.add(node_id)
        consumed += price
        entry = {
            "id": node_id,
            "content_hash": content_hash(graph.nodes[node_id].path),
            "depth": depth,
        }
        if via is not None:
            entry["via"] = via
        entries.append(entry)

        for kind, target in outgoing(graph, node_id):
            if target in graph.nodes:
                if target not in seen:
                    frontier.append((depth + 1, kind, target))
            else:
                degradation = {
                    "code": UNRESOLVED,
                    "subject": target,
                    "evidence": f"{node_id} declares a {kind} edge to it and the graph holds no such node",
                }
                if degradation not in degradations:
                    degradations.append(degradation)
                    # R8: an unresolvable relationship is a stop reason, and R13 of specs/0001
                    # requires resolution to continue past it — so it is recorded as the reason
                    # only when nothing stronger truncated the run.
                    if stop == CLOSURE_COMPLETE:
                        stop = UNRESOLVED

    return entries, stop, degradations, consumed


def package(
    graph: Graph,
    package_id: str,
    request_id: str,
    roots: list[tuple[str, str]],
    budget: int,
    unit: str,
    depth_limit: int | None,
) -> dict:
    entries, stop, degradations, consumed = resolve(graph, roots, budget, unit, depth_limit)
    budget_record = {"unit": unit, "limit": budget, "consumed": consumed}
    if depth_limit is not None:
        budget_record["depth_limit"] = depth_limit
    return {
        "contract_version": "context-package/1",
        "package_id": package_id,
        "request_id": request_id,
        "expansion_contract_version": EXPANSION_CONTRACT,
        "roots": [{"id": node_id, "claim": claim} for node_id, claim in roots],
        "entries": entries,
        "budget": budget_record,
        "stop_reason": stop,
        "degradations": degradations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="resolve_context.py")
    parser.add_argument("--knowledge", type=Path, required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--root", action="append", default=[], metavar="ID:CLAIM")
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--unit", choices=["objects", "bytes"], default="objects")
    parser.add_argument("--depth-limit", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if not args.knowledge.is_dir():
        cannot_run(f"cannot run: knowledge root {args.knowledge} does not exist")
    if not args.root:
        cannot_run("cannot run: at least one --root is required; a package with no root has no scope")

    roots: list[tuple[str, str]] = []
    for pair in args.root:
        node_id, sep, claim = pair.partition(":")
        if not sep or not claim.strip():
            cannot_run(
                f"cannot run: --root expects ID:CLAIM, got {pair!r} — specs/0009 R4 makes a root "
                f"without a claim indistinguishable from an arbitrary inclusion"
            )
        roots.append((node_id, claim.strip()))

    graph = load(args.knowledge)
    if graph.problems:
        print(f"FAILED: the knowledge base has {len(graph.problems)} problem(s)", file=sys.stderr)
        for problem in graph.problems[:10]:
            print(f"  {problem}", file=sys.stderr)
        return 1

    document = package(
        graph, args.package, args.request, roots, args.budget, args.unit, args.depth_limit
    )
    body = json.dumps(document, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body)
        print(
            f"{args.out}: {len(document['entries'])} of {len(graph.nodes)} object(s), "
            f"stop: {document['stop_reason']}, degradations: {len(document['degradations'])}"
        )
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
