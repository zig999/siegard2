"""Scope resolution, placement validation, plan derivation, and plan validation.

The four steps `specs/0004` puts between a knowledge base and a written file, in one module
because each consumes the previous one's output and splitting them would multiply the
serialization without separating anything.

**Nothing here invokes a model.** R23 is explicit that no model participates in deriving the
plan, and the reason is R28: identical inputs must yield a byte-identical plan, which is
testable on its own and independent of whether any template is correct. The one judged step —
where a new artifact goes — is upstream, frozen before derivation runs, and arrives as an
input.

**Scope fails closed; context resolution fails soft.** R21 and R22 keep them separate artifacts
for that reason. A member that cannot be resolved blocks generation here, where the same
condition in `resolve_context.py` records a degradation and continues.

Declared dependencies: PyYAML and jsonschema, via scripts/knowledge_graph_lib.py.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_graph_lib import EDGE_KINDS, Graph


class Blocked(Exception):
    """Generation cannot proceed. Never a degradation: specs/0004 R21 fails closed."""


def _digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# --- scope ---------------------------------------------------------------------------


def resolve_scope(graph: Graph, scope_id: str, request_id: str, roots: list[str]) -> dict:
    """Expand `roots` into a frozen scope — R19 through R22.

    Same edge table and the same breadth-first order as context resolution, and deliberately
    not the same function: this one raises where that one records. A shared implementation
    would have to carry a flag for which failure semantics the caller wanted, and a flag is
    how the fail-closed requirement gets passed the wrong way once.
    """
    missing = [root for root in roots if root not in graph.nodes]
    if missing:
        raise Blocked(
            f"scope roots {', '.join(sorted(missing))} resolve to no knowledge object. "
            f"specs/0004 R21 blocks generation rather than degrading: the fail-soft behaviour of "
            f"specs/0001 R13 must not be applied to a generation scope"
        )

    members: list[dict] = []
    seen: set[str] = set()
    frontier = list(roots)
    while frontier:
        node_id = frontier.pop(0)
        if node_id in seen:
            continue
        seen.add(node_id)
        node = graph.nodes[node_id]
        if node.is_ko:
            members.append(
                {"id": node_id, "type": node.kind, "content_hash": content_hash(node.path)}
            )
        for kind, target in sorted(
            {
                (edge.kind, edge.target)
                for edge in graph.edges
                if edge.source == node_id
                and EDGE_KINDS.get(edge.kind) is not None
                and EDGE_KINDS[edge.kind].traversed
            }
        ):
            if target not in graph.nodes:
                raise Blocked(
                    f"{node_id} declares a {kind} edge to {target}, which the graph does not hold. "
                    f"specs/0004 R21: a member that cannot be resolved blocks generation"
                )
            if target not in seen:
                frontier.append(target)

    members.sort(key=lambda m: m["id"])
    return {
        "contract_version": "generation-scope/1",
        "scope_id": scope_id,
        "request_id": request_id,
        "roots": list(roots),
        "members": members,
        "frozen_digest": _digest(
            json.dumps([[m["id"], m["content_hash"]] for m in members], separators=(",", ":"))
        ),
    }


def scope_is_stale(scope: dict, graph: Graph) -> list[str]:
    """Every member whose content no longer matches what the scope froze — R20."""
    changed = []
    for member in scope["members"]:
        node = graph.nodes.get(member["id"])
        if node is None or content_hash(node.path) != member["content_hash"]:
            changed.append(member["id"])
    return changed


# --- demand --------------------------------------------------------------------------


def demand(scope: dict, declaration: dict) -> tuple[list[tuple[str, str, str]], list[str]]:
    """What the scope demands of the pack, and the node types that yield nothing.

    R14's `from` column is what makes this computable without a model. R11 requires the second
    return value to be reported: silence about a type that produces nothing reads as coverage
    that does not exist.
    """
    by_type: dict[str, list[tuple[str, str]]] = {}
    for entry in declaration["produces"]:
        for node_type in entry["from"]:
            by_type.setdefault(node_type, []).append((entry["class"], entry["track"]))

    demanded: list[tuple[str, str, str]] = []
    uncovered: set[str] = set()
    for member in scope["members"]:
        produced = by_type.get(member["type"])
        if not produced:
            uncovered.add(member["type"])
            continue
        for artifact_class, track in produced:
            demanded.append((member["id"], artifact_class, track))
    demanded.sort()
    return demanded, sorted(uncovered)


# --- placement -----------------------------------------------------------------------


def validate_placement(decision: dict, scope: dict, declaration: dict, repo_root: Path) -> list[str]:
    """Every reason the placement decision may not be frozen — R52.

    Rejects, never repairs: a validation failure means no plan is derived from it at all.
    """
    problems: list[str] = []
    declared = {entry["class"] for entry in declaration["produces"]}
    members = {member["id"] for member in scope["members"]}
    seen: dict[str, str] = {}

    if decision["scope_id"] != scope["scope_id"]:
        problems.append(
            f"the decision names scope {decision['scope_id']} and the scope is "
            f"{scope['scope_id']}; a placement frozen against another scope places artifacts "
            f"for knowledge this run does not hold"
        )
    if decision["pack"] != declaration["pack"]:
        problems.append(
            f"the decision names pack {decision['pack']!r} and the active pack is "
            f"{declaration['pack']!r}"
        )

    for entry in decision["entries"]:
        where = f"{entry['ko']}/{entry['class']}"
        if entry["class"] not in declared:
            problems.append(f"{where}: the pack does not declare this artifact class")
        if entry["ko"] not in members:
            problems.append(f"{where}: names a knowledge object the scope does not hold")

        path = entry["path"]
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            problems.append(
                f"{where}: {path!r} is outside the governed repository — R52 rejects an absolute "
                f"or traversing path rather than normalizing it"
            )
        else:
            try:
                (repo_root / candidate).resolve().relative_to(repo_root.resolve())
            except (ValueError, OSError):
                problems.append(f"{where}: {path!r} does not resolve inside the repository")

        if path in seen:
            problems.append(
                f"{where}: claims {path!r}, already claimed by {seen[path]} — two entries naming "
                f"one path is a modelling or an agent error, and R27 reports it rather than "
                f"picking a winner"
            )
        else:
            seen[path] = where

    return problems


# --- plan ----------------------------------------------------------------------------


def derive_plan(
    plan_id: str,
    scope: dict,
    declaration: dict,
    manifest: dict,
    placement: dict,
) -> tuple[dict, list[str]]:
    """The plan, and the node types the pack covers with nothing — R23, R24, R11.

    Four inputs and no model, which is what makes R28 testable. A locked entry takes its path
    from the manifest; a new one from the frozen placement decision.
    """
    demanded, uncovered = demand(scope, declaration)
    locked = {(a["ko"], a["class"]): a["path"] for a in manifest["artifacts"]}
    proposed = {(e["ko"], e["class"]): e["path"] for e in placement["entries"]}

    entries: list[dict] = []
    for ko, artifact_class, track in demanded:
        key = (ko, artifact_class)
        if key in locked:
            entries.append(
                {"ko": ko, "class": artifact_class, "track": track,
                 "path": locked[key], "state": "locked"}
            )
        elif key in proposed:
            entries.append(
                {"ko": ko, "class": artifact_class, "track": track,
                 "path": proposed[key], "state": "new"}
            )
        else:
            raise Blocked(
                f"{ko}/{artifact_class} is demanded by the scope and neither the manifest nor the "
                f"frozen placement decision gives it a path. R24: a plan entry with no target path "
                f"cannot be validated under R25"
            )

    entries.sort(key=lambda e: (e["ko"], e["class"]))
    return (
        {
            "contract_version": "generation-plan/1",
            "plan_id": plan_id,
            "scope_id": scope["scope_id"],
            "pack": declaration["pack"],
            "pack_version": declaration["version"],
            "entries": entries,
        },
        uncovered,
    )


def validate_plan(plan: dict, scope: dict, declaration: dict, repo_root: Path) -> list[str]:
    """Every reason the plan may not be executed — R25, R27.

    Rejected, never repaired. Run before any file is written, which R26 makes possible by
    having the plan producible without writing one.
    """
    problems: list[str] = []
    declared = {entry["class"] for entry in declaration["produces"]}
    members = {member["id"] for member in scope["members"]}
    seen: dict[str, str] = {}

    for entry in plan["entries"]:
        where = f"{entry['ko']}/{entry['class']}"
        if entry["ko"] not in members:
            problems.append(f"{where}: names a knowledge object the scope does not hold")
        if entry["class"] not in declared:
            problems.append(f"{where}: the pack does not declare this artifact class")
        if entry["path"] in seen:
            problems.append(
                f"{where}: claims {entry['path']!r}, already claimed by {seen[entry['path']]} — "
                f"R27 reports a collision as a defect and no policy resolves it silently"
            )
        else:
            seen[entry["path"]] = where
        if entry["state"] == "locked" and not (repo_root / entry["path"]).exists():
            problems.append(
                f"{where}: locked to {entry['path']!r}, which no longer exists — R25 requires "
                f"every locked path to still be there"
            )
    return problems
