#!/usr/bin/env python3
"""Executable migration paths between contract versions.

`.claude/rules/compatibility.md` requires a breaking change to "define the supported
migration path" and to "add a compatibility or migration test that fails against the old
behavior". Every contract carrying a second version registers its hop here;
check_contract_versions.py fails a bump that registers no path, so the registry cannot fall behind
the schemas without a check firing. An earlier version of this paragraph counted the contracts and
kept saying two after the third landed — which is the drift a docstring has and an assertion does
not, so the count is gone rather than corrected.

Three of the hops govern a contract whose instance is markdown frontmatter rather than a JSON
document: a knowledge object and a consumer's decision record. The function migrates the parsed
frontmatter mapping, and the CLI below reads JSON only — a caller migrating a knowledge base parses
the frontmatter, applies the hop, and writes the file back, because rewriting markdown is a
formatting decision this script has no basis to make.

A migration here is a function, not a description, for the reason this repository applies
everywhere else: a path that is only written down is a path nobody has run. Registering one
is also what makes the coverage check in scripts/check_contract_versions.py possible — two
version files of the same contract with no migration between them is a bump that left its
consumers with no way forward, and that is now a validation failure rather than a discovery.

A migration transforms one instance document. It does not touch files, does not guess, and
raises on an input it was not given: an instance that does not declare the version being
migrated *from* is a caller error, and repairing it silently would hide which contract the
document actually came from.

Declared dependencies: none beyond the standard library.

Usage:  scripts/migrate_contracts.py <contract-from> <contract-to> <file.json|->
Exit:   0 migrated to stdout, 1 no path or the input does not match, 2 cannot run
"""

from __future__ import annotations

import json
import sys
from typing import Callable
import generator_lib  # noqa: F401  (puts src/claude/bin on the import path)
from cli import cannot_run


class MigrationError(Exception):
    """A migration was asked for something it cannot do."""


def distribution_manifest_1_to_2(doc: dict) -> dict:
    """Add nothing, and say why that is the whole migration.

    `distribution-manifest/2` adds one optional field, `capabilities[].declaration`, naming the
    authored declaration an entry was derived from. A `/1` manifest predates declarations, so no
    entry has one to name and inventing a file name would assert an artifact that does not exist.

    The migration is therefore a version stamp, and it is registered rather than skipped because
    the bump is breaking under `.claude/rules/compatibility.md` — a property added to a closed
    object makes a previously invalid instance valid — and a breaking bump with no registered path
    is what the coverage check exists to reject. A consumer that reads the stamped document sees a
    `/2` manifest whose entries carry no declaration, which is exactly what it held before.
    """
    migrated = dict(doc)
    migrated["contract_version"] = "distribution-manifest/2"
    return migrated


def impact_analysis_1_to_2(doc: dict) -> dict:
    """Stamp `base_state: populated`, which every valid `/1` instance was.

    `/2` adds a required `base_state` so that the first change to a repository is expressible: a
    `create` verdict over a base holding nothing implicates nothing, and `/1` rejected that. The
    bump is breaking because a `/1` document is missing a field `/2` requires, so the value has to
    come from somewhere — and it is derivable rather than guessed, for every valid `/1` document:

    - `update` or `create` was only valid with a non-empty `implicated`, so something existed to
      name and the state was `populated`;
    - `none` asserts that what the request asks for is already held, which nothing empty can
      assert, so `none` implies `populated` by its own meaning.

    The three verdicts are exhaustive, so no valid `/1` instance is ambiguous and this migration
    never has to refuse. An *invalid* `/1` document — `none` over a base that held nothing — was a
    false statement before this contract moved, and stamping it `populated` preserves exactly what
    it claimed rather than repairing it into something it did not say.
    """
    migrated = dict(doc)
    migrated["contract_version"] = "impact-analysis/2"
    migrated["base_state"] = "populated"
    return migrated


def knowledge_object_1_to_2(doc: dict) -> dict:
    """Drop `status`, and refuse a document whose status was `superseded`.

    `/2` removes the knowledge lifecycle: `foundation/0003` R26 forbids a status on a knowledge
    object and the schema rejects the field rather than preserving it, so the migration is a
    deletion plus the version stamp. `docs/adr/0018-a-knowledge-object-carries-no-status.md`
    records the decision.

    For `proposed` and `accepted` the deletion loses nothing a reader can act on. Both meant "this
    is what the base says", differing only in a gate that no longer exists, and `sources` still
    names the material an object was read from — which is what `proposed` was being read for.

    `superseded` is refused, and that is the whole reason this is a function and not a stamp. A
    superseded object is a retired revision that R35 no longer retains: stamping it `/2` would
    readmit it to the base as a current fact, standing beside the object that replaced it and
    answering the same question differently. Deleting the file instead is a decision about which
    of two statements the domain holds, so it belongs to whoever owns the base. `superseded_by`
    names the replacement and travels in the error, because a caller told only that the document
    was refused would have to reopen the file to find out what replaced it.
    """
    status = doc.get("status")
    if status == "superseded":
        replacement = doc.get("superseded_by")
        raise MigrationError(
            f"{doc.get('id')!r} is superseded"
            + (f" by {replacement!r}" if replacement else " and names no replacement")
            + " — knowledge-object/2 retains no retired revision, so this object is deleted from "
            "the base rather than migrated; version control holds what it said"
        )
    migrated = {key: value for key, value in doc.items() if key not in ("status", "superseded_by")}
    migrated["contract_version"] = "knowledge-object/2"
    return migrated


def knowledge_graph_1_to_2(doc: dict) -> dict:
    """Drop `status` from every node, and refuse a graph holding a superseded one.

    The graph mirrors the objects it was materialized from, so it moves for the same reason and
    refuses on the same case: a node the base no longer holds is not a node whose field can be
    dropped. Refusing here rather than dropping it silently keeps the graph and the base in
    agreement about what exists — and a graph is derived, so the honest repair is to migrate the
    objects and materialize again rather than to transform the artifact.
    """
    retired = [
        node.get("id") for node in doc.get("nodes", []) if node.get("status") == "superseded"
    ]
    if retired:
        raise MigrationError(
            f"graph holds {len(retired)} superseded node(s) — {', '.join(map(str, retired))} — "
            "which knowledge-object/2 removes from the base; migrate the objects and materialize "
            "the graph again rather than migrating the derived artifact"
        )
    migrated = dict(doc)
    migrated["contract_version"] = "knowledge-graph/2"
    migrated["nodes"] = [
        {key: value for key, value in node.items() if key != "status"}
        for node in doc.get("nodes", [])
    ]
    return migrated


def knowledge_decision_1_to_2(doc: dict) -> dict:
    """Drop `status`, and refuse a decision record that was superseded.

    A consumer's decision record follows the knowledge object it sits beside: `/2` removes the
    status, and `additionalProperties: false` rejects the field rather than ignoring it. A
    `superseded` record is refused for the reason a superseded object is — the tree holds the
    decisions that stand, and which of two records that is belongs to the consumer.
    """
    if doc.get("status") == "superseded":
        raise MigrationError(
            f"decision {doc.get('id')!r} is superseded — knowledge-decision/2 keeps only the "
            "records that stand, so this one is deleted from the tree rather than migrated"
        )
    migrated = {key: value for key, value in doc.items() if key != "status"}
    migrated["contract_version"] = "knowledge-decision/2"
    return migrated


# Keyed by (from, to). A key here is the claim that a document can cross that boundary; the
# coverage check in check_contract_versions.py fails when a boundary exists and a key does not.
MIGRATIONS: dict[tuple[str, str], Callable[[dict], dict]] = {
    ("distribution-manifest/1", "distribution-manifest/2"): distribution_manifest_1_to_2,
    ("impact-analysis/1", "impact-analysis/2"): impact_analysis_1_to_2,
    ("knowledge-object/1", "knowledge-object/2"): knowledge_object_1_to_2,
    ("knowledge-graph/1", "knowledge-graph/2"): knowledge_graph_1_to_2,
    ("knowledge-decision/1", "knowledge-decision/2"): knowledge_decision_1_to_2,
}


def migrate(doc: dict, source: str, target: str) -> dict:
    """Apply the registered path from `source` to `target`, one step at a time."""
    declared = doc.get("contract_version")
    if declared != source:
        raise MigrationError(
            f"instance declares contract_version {declared!r}, not {source!r} — a migration does "
            f"not guess which contract a document came from"
        )
    name, start = source.rsplit("/", 1)
    end_name, end = target.rsplit("/", 1)
    if name != end_name:
        raise MigrationError(f"cannot migrate across contracts: {source!r} to {target!r}")
    if int(end) < int(start):
        raise MigrationError(f"no downgrade path: {source!r} to {target!r}")

    current = doc
    for step in range(int(start), int(end)):
        hop = (f"{name}/{step}", f"{name}/{step + 1}")
        if hop not in MIGRATIONS:
            raise MigrationError(f"no migration registered for {hop[0]} to {hop[1]}")
        current = MIGRATIONS[hop](current)
    return current


def main() -> int:
    if len(sys.argv) != 4:
        cannot_run(
            "cannot run: usage: migrate_contracts.py <contract-from> <contract-to> <file.json|->"
        )
    source, target, path = sys.argv[1:]
    try:
        text = sys.stdin.read() if path == "-" else open(path).read()
        doc = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        cannot_run(f"cannot run: {exc}")

    try:
        print(json.dumps(migrate(doc, source, target), indent=2))
    except MigrationError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
