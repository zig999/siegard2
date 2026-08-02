#!/usr/bin/env python3
"""Compose `domain/` into the one self-contained contract the distribution carries.

The profile is authored as sixteen files because a table is easier to state, cite and correct
than a region of a thousand-line document. The distribution carries one file because a consumer's
boundary validator loads a schema standalone, and a cross-file `$ref` would be resolved over the
network — every sibling reference here has an `$id` under `https://siegard.dev/`, so shipping the
tree would ship sixteen files that do not resolve.

This script is what makes both true at once. It does not ship: it runs in this repository, over
authored source, and its output is what reaches a consumer.

**It composes and never edits.** The rules it follows are declared, not invented here — see
`domain/domain-graph.json#/x-composes-into/rules`. Every one of them was learned by composing the
tree and finding the result wrong, and each is written down there so this script implements a
statement rather than a memory.

**It refuses rather than guessing.** Two tables defining one `$def` differently, a kind naming a
table that is not there, a `$ref` that resolves to nothing: each stops the composition. A composer
that picked a side would produce a contract nobody wrote, and the disagreement would survive as
whichever half it chose.

`--check` compares instead of writing and reports what differs. It never repairs, for the reason
`materialize.py --check` never repairs: a check that fixes what it was meant to detect reports
success on a defect.

Declared dependencies: none beyond the standard library.

Usage:  compose_domain.py [--check] [--out=<path>]
Exit:   0 written, or the target already matches
        1 --check and the target is stale, or missing
        2 cannot run — the tree is inconsistent, or a source file is missing
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOMAIN = REPO / "domain"
NOTATION = REPO / "schemas" / "knowledge-notation.json"
DEFAULT_OUT = REPO / "src" / "claude" / "schemas" / "domain-object.json"

KINDS = ("subdomain", "context", "aggregate", "definition", "rule", "lifecycle", "interface", "process")
DEF_TABLES = ("identifiers", "primitives", "vocabularies")

# Wording a profile may choose for its own readers. Only assertions have to agree, which is the
# same line `schemas/knowledge-notation.json` draws when it says descriptions are stripped.
ANNOTATIONS = ("description", "title", "$comment", "examples", "deprecated")

CANNOT_RUN = 2


class CompositionError(Exception):
    """The tree does not compose, and no document is emitted."""


def load(path: Path) -> dict:
    if not path.is_file():
        raise CompositionError(f"{path} is missing")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as broken:
        raise CompositionError(f"{path}: {broken}") from None


def assertions(node):
    """The same schema with its annotations dropped, for comparing two statements of one rule."""
    if isinstance(node, dict):
        return {k: assertions(v) for k, v in node.items() if k not in ANNOTATIONS}
    if isinstance(node, list):
        return [assertions(v) for v in node]
    return node


def localise(node):
    """Rewrite every sibling `$ref` into a local `#/$defs/<name>`.

    The fragment is what carries the meaning; the file part only says which table stated it, and
    once every table's definitions are in one map the file part has nothing left to select.
    """
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and "#/$defs/" in ref:
            file_part, name = ref.split("#/$defs/", 1)
            if file_part:
                return {"$ref": f"#/$defs/{name}",
                        **{k: localise(v) for k, v in node.items() if k != "$ref"}}
        return {k: localise(v) for k, v in node.items()}
    if isinstance(node, list):
        return [localise(v) for v in node]
    return node


def collect_defs(tables: dict, envelope: dict) -> dict:
    """Every `$def` the profile and the envelope state, refused where two of them disagree."""
    defs: dict = {}
    stated_by: dict[str, str] = {}
    sources = [(f"domain/tables/{name}.json", tables[name].get("$defs", {})) for name in DEF_TABLES]
    sources.append(("schemas/knowledge-notation.json", envelope.get("$defs", {})))

    for where, block in sources:
        for name, schema in block.items():
            if name not in defs:
                defs[name], stated_by[name] = schema, where
                continue
            if assertions(defs[name]) != assertions(schema):
                raise CompositionError(
                    f"`{name}` is stated by both {stated_by[name]} and {where}, and the two do not "
                    f"assert the same thing. Composing would silently keep one; which is right is a "
                    f"decision for whoever wrote them"
                )
            # Same assertions, different wording: the profile's is kept, because it is the one
            # written for a reader of this vocabulary.
    return defs


def compose() -> dict:
    envelope = load(NOTATION)["envelope"]
    manifest = load(DOMAIN / "tables" / "envelope.json")
    graph = load(DOMAIN / "domain-graph.json")
    invariants = load(DOMAIN / "tables" / "invariants.json")
    tables = {name: load(DOMAIN / "tables" / f"{name}.json") for name in DEF_TABLES}
    nodes = {kind: load(DOMAIN / "nodes" / f"{kind}.json") for kind in KINDS}

    version = manifest["x-contract-version"]["const"]
    emits = graph["x-composes-into"]["emits"]

    defs = collect_defs(tables, envelope)
    # The envelope's `properties.id` references the identifier by the name the notation gave it.
    # This profile spells it `nodeId`; the alias is supplied rather than the reference rewritten,
    # so the envelope stays the one statement of its own shape.
    defs["knowledgeObjectId"] = {"$ref": "#/$defs/nodeId"}

    dropped = set(manifest["x-envelope-fields"].get("removed_by_profile", {}).get("fields", []))
    properties: dict = {name: schema for name, schema in envelope["properties"].items()
                        if name not in dropped}
    properties["type"] = tables["vocabularies"]["$defs"]["kind"]
    properties["contract_version"] = {
        "const": version,
        "description": "A consumer rejects an artifact it was not built to read rather than "
                       "inferring version from shape.",
    }
    properties.update(invariants.get("properties", {}))

    # A property more than one kind declares differently stays inside that kind's branch. `ddd` is
    # the case: four kinds declare it against four different vocabularies, and hoisting any one
    # narrows the other three to it. `additionalProperties` is true, so an un-hoisted name is
    # admitted regardless, and the per-kind `then.properties` is what types it.
    declared: dict[str, list] = {}
    for kind in KINDS:
        for name, schema in nodes[kind].get("properties", {}).items():
            declared.setdefault(name, []).append(schema)
    for name in sorted(declared):
        if name in properties:
            continue
        if all(schema == declared[name][0] for schema in declared[name]):
            properties[name] = declared[name][0]

    all_of: list = []
    for kind in KINDS:
        node = nodes[kind]
        if "allOf" not in node:
            raise CompositionError(f"domain/nodes/{kind}.json states no `allOf`, so the kind requires nothing")
        branch: dict = {"allOf": node["allOf"]}
        if node.get("properties"):
            branch["properties"] = node["properties"]
        all_of.append({"if": {"properties": {"type": {"const": kind}}, "required": ["type"]},
                       "then": branch})
    for name, entry in invariants["x-cross-kind"].items():
        if "schema" not in entry:
            raise CompositionError(
                f"the cross-kind rule `{name}` carries no `schema`, so it is prose a composer "
                f"cannot splice. Every rule in `x-cross-kind` states its own assertion"
            )
        all_of.append(entry["schema"])

    document = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://siegard.dev/schemas/domain-object.json",
        "title": emits["title"],
        "description": emits["description"],
        "type": "object",
        # True by contract, not by omission: an unknown field is admitted rather than rejected, so
        # a prohibition is written as a negation and never as closure.
        "additionalProperties": True,
        "required": manifest["x-required-unconditionally"],
        "properties": properties,
        "allOf": all_of,
        "$defs": {name: defs[name] for name in sorted(defs)},
    }
    document = localise(document)

    unresolved = sorted(missing_refs(document, set(document["$defs"])))
    if unresolved:
        raise CompositionError(
            f"the composed document references {len(unresolved)} definition(s) nothing states: "
            f"{', '.join(unresolved)}"
        )
    return document


def missing_refs(node, known: set[str]) -> set[str]:
    """Every `#/$defs/<name>` the document points at and does not hold."""
    found: set[str] = set()
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/") and ref[len("#/$defs/"):] not in known:
            found.add(ref[len("#/$defs/"):])
        for value in node.values():
            found |= missing_refs(value, known)
    elif isinstance(node, list):
        for value in node:
            found |= missing_refs(value, known)
    return found


def rendered(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    verify = "--check" in sys.argv[1:]
    out = Path(next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--out=")),
                    DEFAULT_OUT))
    if [a for a in sys.argv[1:] if not a.startswith("--")]:
        print("cannot run: expected [--check] [--out=<path>]", file=sys.stderr)
        return CANNOT_RUN

    try:
        text = rendered(compose())
    except CompositionError as broken:
        print(f"cannot run: {broken}", file=sys.stderr)
        return CANNOT_RUN

    if verify:
        if not out.is_file():
            print(f"STALE: {out} does not exist; the composition has never been written")
            return 1
        if out.read_text(encoding="utf-8") != text:
            print(f"STALE: {out} is not what domain/ composes to. Run without --check to rewrite "
                  f"it; do not edit it, because every assertion in it is stated once in domain/")
            return 1
        print(f"composed contract checked: {out.relative_to(REPO)} matches domain/")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    document = json.loads(text)
    print(f"composed {out.relative_to(REPO)}: {len(document['properties'])} properties, "
          f"{len(document['allOf'])} allOf blocks, {len(document['$defs'])} definitions, "
          f"contract {document['properties']['contract_version']['const']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
