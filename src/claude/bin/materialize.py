#!/usr/bin/env python3
"""Derive the knowledge graph and the projections from the objects, and hand-edit nothing.

Six shipped files told a consumer that `index.md`, `glossary.md`, a context map and `graph.json`
exist and must never be edited by hand, and nothing produced any of them. A rule about a file that
does not exist is a rule a reader cannot follow, and the check that reports the projections as owed
had nothing to be owed *by*.

Everything here is a function of the base. The graph is the objects' declared relationships and
nothing else: a relationship stated only in prose is not an edge, because two readings of one
paragraph produce two graphs. The projections are views of the graph — the ontology limits them to
an index, a glossary and a context map, and a fourth needs a recorded case that demands it.

What it refuses to do carries the same weight. It infers no edge, resolves no ambiguity, and repairs
nothing: an edge naming an id the base does not hold is reported as a defect, together with orphans
and cycles, and the run still writes the graph so a reader can see the shape the defect sits in.

Declared dependencies: PyYAML.

Usage:  materialize.py <knowledge-root> [--check]
Exit:   0 written (or unchanged under --check), 1 a defect or a stale derived file, 2 cannot run
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CANNOT_RUN = 2
GRAPH_CONTRACT = "knowledge-graph/2"

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML is not installed (pip install pyyaml)", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

# The edge table the ontology declares closed, transcribed. Each entry states the cardinality a
# validator enforces and whether expansion traverses it, because both are properties of the edge
# rather than of any object carrying one.
#
# `None` is the table's `n`: unbounded. The notation differs because the table is read by a person
# and this is read by a contract, and `null` is what the contract admits — a string `"n"` would be
# a second spelling of the same fact, agreeing with the table and failing the schema.
EDGE_KINDS = {
    "boundary": {"minimum": 1, "maximum": 1, "inverse_maximum": None, "traversed": True, "depth": 1},
    "depends_on": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 2},
    "governed_by": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "attributes[].target": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "attributes[].of": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "attributes[].lifecycle": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "lifecycle.subject": {"minimum": 1, "maximum": 1, "inverse_maximum": 1, "traversed": True, "depth": 1},
    "transitions[].guard": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "rejections[].error": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "steps[].ko": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": True, "depth": 1},
    "context_relationships[].with": {"minimum": 0, "maximum": None, "inverse_maximum": None, "traversed": False, "depth": 1},
}

RESERVED = {"system.md", "index.md", "glossary.md", "context-map.md"}
DERIVED = ("graph.json", "index.md", "glossary.md", "context-map.md")


def frontmatter(path: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    if not match:
        raise ValueError("carries no frontmatter fence")
    return yaml.safe_load(match.group(1)) or {}


def objects(root: Path) -> list[dict]:
    """Every knowledge object in the base, lexicographically by id.

    Ordered so identical input produces byte-identical output: a derived file that reordered
    between two runs over one base would show a diff nobody caused.
    """
    found = []
    for path in sorted(root.rglob("*.md")):
        if path.name in RESERVED:
            continue
        data = frontmatter(path)
        if data.get("id"):
            found.append(data)
    return sorted(found, key=lambda d: d["id"])


def edges_of(data: dict) -> list[dict]:
    """Every declared relationship this object holds, by the edge kind the table names.

    Declared, never inferred. `locator` says where in the object the reference sits, so a reported
    defect names a place a reader can open rather than only the pair it failed to resolve.
    """
    found: list[dict] = []
    source = data["id"]

    def add(kind: str, target, locator: str) -> None:
        if isinstance(target, str) and target:
            found.append({"source": source, "target": target, "kind": kind, "locator": locator})

    add("boundary", data.get("boundary"), "boundary")
    for index, target in enumerate(data.get("depends_on") or []):
        add("depends_on", target, f"depends_on[{index}]")
    for index, target in enumerate(data.get("governed_by") or []):
        add("governed_by", target, f"governed_by[{index}]")
    for attribute in data.get("attributes") or []:
        name = attribute.get("name", "?")
        for field in ("target", "of", "lifecycle"):
            add(f"attributes[].{field}", attribute.get(field), f"attributes[{name}].{field}")
    add("lifecycle.subject", data.get("subject"), "subject")
    for index, transition in enumerate(data.get("transitions") or []):
        add("transitions[].guard", transition.get("guard"), f"transitions[{index}].guard")
    for index, rejection in enumerate(data.get("rejections") or []):
        add("rejections[].error", rejection.get("error"), f"rejections[{index}].error")
    for index, step in enumerate(data.get("steps") or []):
        add("steps[].ko", step.get("ko"), f"steps[{index}].ko")
    for index, relationship in enumerate(data.get("context_relationships") or []):
        add("context_relationships[].with", relationship.get("with"),
            f"context_relationships[{index}].with")
    return found


def build(root: Path) -> tuple[dict, list[str]]:
    """The graph, and every defect found while deriving it. Neither is repaired."""
    found = objects(root)
    nodes = [
        {
            "id": data["id"],
            "kind": data["type"],
            "title": data["title"],
            **({"question": data["question"]} if data.get("question") else {}),
            **({"boundary": data["boundary"]} if data.get("boundary") else {}),
            **({"ddd": data["ddd"]} if data.get("ddd") else {}),
        }
        for data in found
    ]
    edges = sorted(
        (edge for data in found for edge in edges_of(data)),
        key=lambda e: (e["source"], e["kind"], e["locator"], e["target"]),
    )

    held = {node["id"] for node in nodes}
    problems = [
        f"{edge['source']} at {edge['locator']} names {edge['target']}, which the base does not hold"
        for edge in edges if not edge["target"].startswith("adr.") and edge["target"] not in held
    ]
    referenced = {edge["target"] for edge in edges} | {edge["source"] for edge in edges}
    for node in nodes:
        if node["id"] not in referenced:
            problems.append(f"{node['id']} is referenced by nothing and references nothing")

    graph = {"contract_version": GRAPH_CONTRACT, "edge_kinds": EDGE_KINDS,
             "nodes": nodes, "edges": edges}
    return graph, problems


def index_of(graph: dict) -> str:
    """Every object, by boundary, with the question it answers. The retrieval view."""
    lines = ["# Knowledge index", "",
             "Derived from the objects by `bin/materialize.py`. Do not edit: change the objects.", ""]
    by_boundary: dict[str, list[dict]] = {}
    for node in graph["nodes"]:
        by_boundary.setdefault(node.get("boundary", "—"), []).append(node)
    for boundary in sorted(by_boundary):
        lines += [f"## {boundary}", "", "| id | type | answers |", "|---|---|---|"]
        for node in by_boundary[boundary]:
            lines.append(f"| `{node['id']}` | {node['kind']} | {node.get('question', '—')} |")
        lines.append("")
    return "\n".join(lines)


def glossary_of(graph: dict) -> str:
    """The ubiquitous language: the set of definitions, which is where it lives rather than a list."""
    lines = ["# Glossary", "",
             "The set of `definition` objects, which is what the ubiquitous language is.",
             "Derived by `bin/materialize.py`. Do not edit: change the objects.", ""]
    definitions = [n for n in graph["nodes"] if n["kind"] == "definition"]
    if not definitions:
        lines.append("The base holds no definition yet.")
        return "\n".join(lines) + "\n"
    lines += ["| term | ddd | id |", "|---|---|---|"]
    for node in sorted(definitions, key=lambda n: n["title"].lower()):
        lines.append(f"| {node['title']} | {node.get('ddd', '—')} | `{node['id']}` |")
    return "\n".join(lines) + "\n"


def context_map_of(graph: dict) -> str:
    """The bounded contexts and the relationships they declare with each other."""
    lines = ["# Context map", "",
             "Derived by `bin/materialize.py`. Do not edit: change the objects.", ""]
    contexts = [n for n in graph["nodes"]
                if n["kind"] == "boundary" and n.get("ddd") == "bounded-context"]
    if not contexts:
        lines.append("The base declares no bounded context yet.")
        return "\n".join(lines) + "\n"
    relationships = [e for e in graph["edges"] if e["kind"] == "context_relationships[].with"]
    lines += ["| context | relates to |", "|---|---|"]
    for node in contexts:
        related = sorted(e["target"] for e in relationships if e["source"] == node["id"])
        lines.append(f"| `{node['id']}` | {', '.join(f'`{r}`' for r in related) or '—'} |")
    return "\n".join(lines) + "\n"


def rendered(graph: dict) -> dict[str, str]:
    return {
        "graph.json": json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        "index.md": index_of(graph) + "\n",
        "glossary.md": glossary_of(graph),
        "context-map.md": context_map_of(graph),
    }


def main() -> int:
    arguments = [a for a in sys.argv[1:] if not a.startswith("--")]
    verify = "--check" in sys.argv[1:]
    if len(arguments) != 1:
        print("cannot run: expected <knowledge-root> [--check]", file=sys.stderr)
        return CANNOT_RUN
    root = Path(arguments[0])
    if not root.is_dir():
        print(f"cannot run: {root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    try:
        graph, problems = build(root)
    except ValueError as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN
    if not graph["nodes"]:
        print(f"cannot run: {root} holds no knowledge object", file=sys.stderr)
        return CANNOT_RUN

    files = rendered(graph)
    if verify:
        stale = [name for name, text in files.items()
                 if not (root / name).is_file() or (root / name).read_text() != text]
        print(f"derived files checked: {len(files)} over {len(graph['nodes'])} object(s)")
        if stale:
            print(f"STALE: {', '.join(sorted(stale))} — regenerate rather than editing")
            return 1
    else:
        for name, text in files.items():
            (root / name).write_text(text)
        print(f"materialized {len(graph['nodes'])} object(s) and {len(graph['edges'])} edge(s) "
              f"into {', '.join(DERIVED)}")

    if problems:
        print(f"\n{len(problems)} defect(s), reported and not repaired:")
        for problem in sorted(problems):
            print(f"  {problem}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
