"""Materialize a knowledge base into the graph specs/0003 defines, and check it.

The materializer and the checks live together because every check the specification
defers to a script needs the same resolved graph: totality (R11), cross-context
targeting (R15), edge cardinality (R18), one lifecycle per subject (R20), unresolved
targets (R22, R29). Building that graph twice would be two answers to one question.

This module holds no frontmatter constraint. Those live in schemas/knowledge-object.v1.json,
which R30 makes the single authority for the attribute type system. What lives here is
what a per-file schema cannot see: the filesystem, other files, and the closure of edges.

The one fact this module copies from the specification is the edge table under **The
ontology: edges, cardinality, and traversal** — origin, target, cardinality, and whether
expansion traverses each edge. Prose is not machine-readable, R18 requires a validator to
enforce cardinality, and R19 requires expansion to follow only traversed edges, so the
table arrives here as data. `schemas/knowledge-graph.v1.json` holds the edge *names* it
emits; this module holds the cardinality and traversal policy the names carry.

Consumers: scripts/validate_knowledge.py (validation), scripts/project_knowledge.py
(projections and graph.json), scripts/measure_ontology.py (the R52 measurement).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from frontmatter_lib import REPO_ROOT, display, split_frontmatter

try:
    import yaml
except ImportError:  # pragma: no cover - frontmatter_lib already exits on this
    raise

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - callers exit with a named error
    raise

KO_SCHEMA_PATH = REPO_ROOT / "schemas" / "knowledge-object.v1.json"
ADR_SCHEMA_PATH = REPO_ROOT / "schemas" / "knowledge-decision.v1.json"
GRAPH_CONTRACT = "knowledge-graph/1"

# Files inside a knowledge tree that are not knowledge objects. `system.md` is authored;
# the rest are derived, and R42 forbids hand-editing them.
RESERVED_NAMES = {"system.md", "index.md", "glossary.md", "context-map.md", "graph.json"}
DECISION_DIR = "decision"

# The two body sections each type carries, in order, per **Body template**. The first is
# always `## Answer`, because the answer is the payload and context is what a consumer skips.
SECTIONS = {
    "definition": ("## Answer", "## Invariants"),
    "rule": ("## Answer", "## Conditions"),
    "lifecycle": ("## Answer", "## State semantics"),
    "interface": ("## Answer", "## Semantics"),
    "boundary": ("## Answer", "## Responsibilities"),
    "process": ("## Answer", "## Outcomes"),
}

# `terminal` names every state listed in a lifecycle's `terminal` field when it appears as
# a rejection's `from`. Reserving it costs one state name and buys a rejection table that
# does not restate the terminal set.
TERMINAL = "terminal"

RFC2119 = (
    "MUST NOT",
    "SHALL NOT",
    "SHOULD NOT",
    "MUST",
    "SHALL",
    "SHOULD",
    "MAY",
    "REQUIRED",
    "RECOMMENDED",
    "OPTIONAL",
)

# R45 forbids a pronoun in a normative statement. This list holds the personal and
# possessive pronouns only. Demonstratives are excluded deliberately: in "this system
# MUST", `this` is a determiner rather than a pronoun, so including it would reject
# conforming text. The check therefore bounds the failure rather than closing it.
PRONOUNS = {
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "he", "him", "his", "she", "her", "hers", "we", "us", "our", "ours",
    "you", "your", "yours",
}

SENTENCE_RUN_ON = re.compile(r"[.!?]\s+[A-Z]")
WORD = re.compile(r"[A-Za-z']+")
SECTION_HEADING = re.compile(r"^#{1,6} ", re.MULTILINE)
NUMERIC = re.compile(r"^[0-9]+$")


@dataclass(frozen=True)
class EdgeKind:
    """One row of the edge table of specs/0003.

    `minimum` and `maximum` bound how many edges of this kind one origin declares;
    `inverse_maximum` bounds how many arrive at one target, which is how R20's "at most
    one lifecycle per definition" becomes a check rather than a note. `traversed` and
    `depth` are what R19 requires every edge to declare, and what expansion reads.
    """

    name: str
    origin_types: tuple[str, ...]  # empty means any knowledge object
    target_types: tuple[str, ...]  # empty means any node
    minimum: int
    maximum: int | None
    inverse_maximum: int | None
    traversed: bool
    depth: int | None
    crosses_context: bool = False  # exempt from R15


EDGE_KINDS: dict[str, EdgeKind] = {
    # Structural. Every knowledge object declares exactly one boundary, except a
    # bounded-context boundary, whose absence identifies a partition root (R21).
    "boundary": EdgeKind(
        "boundary", (), ("boundary",), 1, 1, None, True, 1, crosses_context=True
    ),
    "depends_on": EdgeKind("depends_on", (), (), 0, None, None, True, 2),
    "governed_by": EdgeKind(
        "governed_by", (), ("adr",), 0, None, None, True, 1, crosses_context=True
    ),
    "attributes[].target": EdgeKind(
        "attributes[].target", ("definition",), ("definition",), 0, None, None, True, 1
    ),
    "attributes[].of": EdgeKind(
        "attributes[].of", ("definition",), ("definition",), 0, None, None, True, 1
    ),
    "attributes[].lifecycle": EdgeKind(
        "attributes[].lifecycle", ("definition",), ("lifecycle",), 0, None, None, True, 1
    ),
    "lifecycle.subject": EdgeKind(
        "lifecycle.subject", ("lifecycle",), ("definition",), 1, 1, 1, True, 1
    ),
    "transitions[].guard": EdgeKind(
        "transitions[].guard", ("lifecycle",), ("rule",), 0, None, None, True, 1
    ),
    "rejections[].error": EdgeKind(
        "rejections[].error", ("lifecycle",), ("definition",), 0, None, None, True, 1
    ),
    "steps[].ko": EdgeKind("steps[].ko", ("process",), (), 0, None, None, True, 1),
    "context_relationships[].with": EdgeKind(
        "context_relationships[].with",
        ("boundary",),
        ("boundary",),
        0,
        None,
        None,
        True,
        1,
        crosses_context=True,
    ),
}

# Every edge above is traversed, which is R52 applied rather than a coincidence: the first
# measurement over a fixture found `references`, `supersedes`, and `superseded_by` read by no
# resolution. The first two were removed from the vocabulary. `superseded_by` stayed, because
# R40 requires it, and moved out of the edge table: its target MUST resolve under R22 and
# expansion MUST NOT follow it in either direction, so it is a resolvable reference rather
# than an edge. Graph.supersessions holds those, deliberately outside Graph.edges, so no
# traversal can reach one by accident.

# Edge kinds whose acyclicity is a defect when violated. A blanket cycle check over every
# traversed edge would be wrong: a stateful definition names its lifecycle through
# `attributes[].lifecycle` and that lifecycle names the definition back through
# `lifecycle.subject`, so the two-node cycle is the correct shape rather than a defect.
ACYCLIC_KINDS = ("boundary", "depends_on", "steps[].ko")


@dataclass
class Node:
    id: str
    kind: str  # a knowledge-object type, or "adr"
    path: Path
    data: dict
    body: str = ""

    @property
    def is_ko(self) -> bool:
        return self.kind != "adr"


@dataclass
class Edge:
    source: str
    target: str
    kind: str
    locator: str  # where in the source frontmatter this edge was declared


@dataclass
class Graph:
    root: Path
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    # `superseded_by` references, held apart from `edges` so that nothing traversing the
    # graph can follow one. R22 requires each target to resolve and forbids expansion from
    # following it in either direction; keeping them out of `edges` enforces the second
    # clause structurally rather than by every consumer remembering to filter.
    supersessions: list[Edge] = field(default_factory=list)
    defaults: dict = field(default_factory=dict)
    limits: dict = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def report(self, path: Path | None, message: str) -> None:
        where = display(path) if path is not None else display(self.root)
        self.problems.append(f"{where}: {message}")


def path_for(node_id: str) -> Path:
    """id → path, arithmetic and never a search (R38).

    `ko.<type>.<context>.<slug>` becomes `<type>/<context>/<slug>.md`. The single
    irregular case is stated rather than inferred: `ko.boundary.<slug>` becomes
    `boundary/<slug>.md`, where `<slug>` may carry a dot for an aggregate inside a context.
    """
    parts = node_id.split(".")
    if parts[1] == "boundary":
        return Path("boundary") / (".".join(parts[2:]) + ".md")
    return Path(parts[1]) / parts[2] / (parts[3] + ".md")


def id_for(relative: Path) -> str | None:
    """path → id, the reverse of path_for with no lookup table. None when the shape is wrong."""
    parts = relative.with_suffix("").parts
    if not parts:
        return None
    if parts[0] == "boundary":
        if len(parts) != 2:
            return None
        return f"ko.boundary.{parts[1]}"
    if len(parts) != 3:
        return None
    return f"ko.{parts[0]}.{parts[1]}.{parts[2]}"


def load(root: Path) -> Graph:
    """Read every file under `root` and materialize the graph, reporting as it goes."""
    graph = Graph(root=root)
    ko_validator = Draft202012Validator(json.loads(KO_SCHEMA_PATH.read_text()))
    adr_validator = Draft202012Validator(json.loads(ADR_SCHEMA_PATH.read_text()))

    _load_system(graph)

    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] == DECISION_DIR:
            _load_adr(graph, path, adr_validator)
            continue
        if path.name in RESERVED_NAMES and len(relative.parts) == 1:
            continue
        _load_knowledge_object(graph, path, relative, ko_validator)

    _materialize_edges(graph)
    return graph


def _load_system(graph: Graph) -> None:
    """Read knowledge/system.md, whose three defaults R26 requires it to hold.

    Spec 0003 defers this file's schema beyond the three defaults R26 requires and the
    `limits.body_lines` ceiling R48 requires, so this reads it without one and reports what
    is missing by name. The ceiling is a fact of the knowledge base rather than a hidden
    default in a validator, which .claude/rules/distribution.md rejects; a maintainer settled
    that home on 2026-07-30 and R48 now names it. What value it should hold is still deferred
    to R52's measurement.
    """
    path = graph.root / "system.md"
    if not path.is_file():
        graph.report(path, "knowledge/system.md is missing, so no system default resolves")
        return
    try:
        data, _ = split_frontmatter(path.read_text())
    except (ValueError, yaml.YAMLError) as exc:
        graph.report(path, f"cannot read system defaults: {exc}")
        return
    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        graph.report(path, "`defaults` is missing or is not a mapping")
        return
    for key in ("timezone", "currency", "identity_strategy"):
        if key not in defaults:
            graph.report(path, f"`defaults.{key}` is missing, and R26 requires all three")
    graph.defaults = defaults
    limits = data.get("limits")
    graph.limits = limits if isinstance(limits, dict) else {}


def _load_adr(graph: Graph, path: Path, validator: Draft202012Validator) -> None:
    """An ADR is a permanent graph node and never a knowledge object (R7).

    Validated against schemas/knowledge-decision.v1.json, which spec 0003 names as its contract. The
    similarity check in scripts/validate_adrs.py is not applied: it compares an ADR
    against this repository's own CLAUDE.md, which says nothing about a governed one.
    """
    try:
        data, _body = split_frontmatter(path.read_text())
    except (ValueError, yaml.YAMLError) as exc:
        graph.report(path, str(exc))
        return
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        graph.report(path, f"{where}: {err.message}")
        return
    node_id = f"adr.{data['id']}"
    if node_id in graph.nodes:
        graph.report(path, f"id '{node_id}' already used by {display(graph.nodes[node_id].path)}")
        return
    graph.nodes[node_id] = Node(id=node_id, kind="adr", path=path, data=data)


def _load_knowledge_object(
    graph: Graph, path: Path, relative: Path, validator: Draft202012Validator
) -> None:
    try:
        data, body = split_frontmatter(path.read_text())
    except (ValueError, yaml.YAMLError) as exc:
        graph.report(path, str(exc))
        return

    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    for err in errors:
        where = ".".join(str(p) for p in err.path) or "(root)"
        graph.report(path, f"{where}: {err.message}")
    if errors:
        return

    node_id = data["id"]
    if node_id in graph.nodes:
        graph.report(path, f"id '{node_id}' already used by {display(graph.nodes[node_id].path)}")
        return

    # R38: both directions are arithmetic. A disagreement is reported rather than
    # repaired, because repairing it would decide which of the two is authoritative.
    expected = path_for(node_id)
    if expected != relative:
        graph.report(path, f"id '{node_id}' computes path '{expected}', not '{relative}'")
    derived = id_for(relative)
    if derived is None:
        graph.report(path, f"path '{relative}' has no id under the fixed depth of R41")
    elif not node_id.startswith(derived):
        graph.report(path, f"path '{relative}' computes id '{derived}', not '{node_id}'")

    segments = node_id.split(".")
    if segments[1] != data["type"]:
        graph.report(path, f"id names type '{segments[1]}' but `type` is '{data['type']}'")
    for segment in segments[2:]:
        if NUMERIC.match(segment):
            graph.report(path, f"id segment '{segment}' is a sequential number, which R39 forbids")

    graph.nodes[node_id] = Node(id=node_id, kind=data["type"], path=path, data=data, body=body)


def _materialize_edges(graph: Graph) -> None:
    """Turn every declared relationship into an edge. Only declared relationships are edges."""
    for node in graph.nodes.values():
        if not node.is_ko:
            continue
        data = node.data
        add = lambda kind, target, locator: graph.edges.append(  # noqa: E731
            Edge(source=node.id, target=target, kind=kind, locator=locator)
        )
        if "boundary" in data:
            add("boundary", data["boundary"], "boundary")
        for i, target in enumerate(data.get("depends_on") or []):
            add("depends_on", target, f"depends_on[{i}]")
        for i, target in enumerate(data.get("governed_by") or []):
            add("governed_by", target, f"governed_by[{i}]")
        if "superseded_by" in data:
            graph.supersessions.append(
                Edge(
                    source=node.id,
                    target=data["superseded_by"],
                    kind="superseded_by",
                    locator="superseded_by",
                )
            )
        for i, attribute in enumerate(data.get("attributes") or []):
            name = attribute.get("name", i)
            for param, kind in (
                ("target", "attributes[].target"),
                ("of", "attributes[].of"),
                ("lifecycle", "attributes[].lifecycle"),
            ):
                if param in attribute:
                    add(kind, attribute[param], f"attributes.{name}.{param}")
        if "subject" in data:
            add("lifecycle.subject", data["subject"], "subject")
        for i, transition in enumerate(data.get("transitions") or []):
            if "guard" in transition:
                add("transitions[].guard", transition["guard"], f"transitions[{i}].guard")
        for i, rejection in enumerate(data.get("rejections") or []):
            if "error" in rejection:
                add("rejections[].error", rejection["error"], f"rejections[{i}].error")
        for i, step in enumerate(data.get("steps") or []):
            add("steps[].ko", step["ko"], f"steps[{i}].ko")
        for i, relationship in enumerate(data.get("context_relationships") or []):
            add(
                "context_relationships[].with",
                relationship["with"],
                f"context_relationships[{i}].with",
            )
    graph.edges.sort(key=lambda e: (e.source, e.kind, e.locator, e.target))
    graph.supersessions.sort(key=lambda e: (e.source, e.target))


def context_of(graph: Graph, node_id: str) -> str | None:
    """The bounded context a node belongs to, walked up through its boundary chain.

    An aggregate boundary declares its containing context in the common `boundary` field,
    so membership is derived from each member's own field and never from a list a boundary
    holds. Returns None when the chain does not resolve, which a resolution check reports
    separately rather than this function guessing.
    """
    seen: set[str] = set()
    current = node_id
    while current and current not in seen:
        seen.add(current)
        node = graph.nodes.get(current)
        if node is None:
            return None
        if node.kind == "boundary" and node.data.get("ddd") == "bounded-context":
            return current
        boundary = node.data.get("boundary")
        if not boundary:
            return None
        current = boundary
    return None
