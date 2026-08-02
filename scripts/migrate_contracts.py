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
import re
import sys
from typing import Callable
from cli import cannot_run


class MigrationError(Exception):
    """A migration was asked for something it cannot do."""


def rename_request_prefix(value: str) -> str:
    """`cr_7a2e4d10` becomes `rq_7a2e4d10`, and anything else is refused.

    Two contracts changed the same pattern in the same commit, for the same reason:
    `foundation/0001` R2 stopped treating a request as a contracted artifact, and the `cr_`
    identifier of a change request became the `rq_` identifier of a request. The eight hex
    digits identify the same request either way, so the hop is a prefix rewrite rather than a
    new identity — and R10's rule that a renamed element is a different element does not reach
    here, because nothing about the request changed except what the framework calls the record
    of it.
    """
    if not re.fullmatch(r"cr_[0-9a-f]{8}", value or ""):
        raise MigrationError(
            f"request_id {value!r} is not a `cr_` identifier — only a document carrying the "
            "pattern the previous version required can be rewritten to the current one"
        )
    return "rq_" + value[3:]


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


def capability_declaration_1_to_2(doc: dict) -> dict:
    """Add nothing: `/2` widens where `/1` was narrow, so every `/1` declaration already conforms.

    `/2` lowers `outputs` from `minItems: 1` to `0`, because a capability that produces no
    artifact another capability consumes is describable and was not. The bump is breaking under
    `.claude/rules/compatibility.md` on the second entry — an alteration that makes a previously
    *invalid* instance valid — and the direction is what makes the hop a stamp: nothing valid
    under `/1` stops being valid, so there is no field to add and none to drop.
    """
    migrated = dict(doc)
    migrated["contract_version"] = "capability-declaration/2"
    return migrated


def validation_evidence_1_to_2(doc: dict) -> dict:
    """Rewrite the request identifier from `cr_` to `rq_`, and change nothing else."""
    migrated = dict(doc)
    migrated["request_id"] = rename_request_prefix(doc.get("request_id"))
    migrated["contract_version"] = "validation-evidence/2"
    return migrated


def impact_analysis_2_to_3(doc: dict) -> dict:
    """Rewrite the request identifier, and refuse a document that names no model.

    `/3` requires `model_id`: an impact analysis reads a domain model, and an analysis that
    cannot say which one it read cannot be reproduced — `foundation/0004` R15 wants the inputs
    named. A `/2` document does not carry the field and the value is not recoverable from the
    document, so this hop refuses rather than stamping. Supplying one would assert that a
    specific model produced this verdict, which is the invention the whole boundary exists to
    prevent; a caller who knows which model it was adds the field and migrates.
    """
    if "model_id" not in doc:
        raise MigrationError(
            f"analysis {doc.get('analysis_id')!r} names no model_id, which impact-analysis/3 "
            "requires — the model it read is not recoverable from the document, and choosing one "
            "would assert an input this analysis may not have had"
        )
    migrated = dict(doc)
    migrated["request_id"] = rename_request_prefix(doc.get("request_id"))
    migrated["contract_version"] = "impact-analysis/3"
    return migrated





def capability_declaration_2_to_3(doc: dict) -> dict:
    """Add nothing: `/3` admits an optional `deprecation`, and no `/2` declaration carries one.

    The field is how `foundation/0005` R17 gets its second checkable fact. A status is derived from
    whether the distribution installs a capability and whether it is documented as going away, and
    until now only the first was expressible — so every installed capability derived `active` and
    R15's move through `deprecated` had no mechanism.

    A `/2` declaration describes a capability that is not going away, because there was no way to
    say that it was. Absent means active, so the stamp preserves exactly what each one claimed.
    """
    migrated = dict(doc)
    migrated["contract_version"] = "capability-declaration/3"
    return migrated




def impact_analysis_4_to_5(doc: dict) -> dict:
    """Rename the model identifier and retype what an entry implicates.

    `/5` drops `model_id` for `record_id` and replaces the `knowledge-object` and
    `domain-model-element` kinds with `domain-object`. Both follow from the same change: the
    constructs are objects in the base rather than elements of a document held elsewhere, so what
    names a run is the record holding what has no file, and what an entry implicates is an object.

    The rename is mechanical and loses nothing — one identifier for one run, under a new prefix. The
    retype is not, and refuses rather than guessing: a `/4` entry naming an `adr` keeps its kind, and
    one naming either retired kind becomes `domain-object`, but an identifier still spelled `ko.`
    cannot be rewritten here. Its path came from a vocabulary that collapsed eight kinds into six,
    and deriving the kind it would take now is the analysis, not a migration.
    """
    migrated = dict(doc)
    identifier = migrated.pop("model_id", None)
    if identifier:
        migrated["record_id"] = "ar_" + identifier.split("_", 1)[1]
    implicated = []
    for entry in doc.get("implicated") or []:
        moved = dict(entry)
        if moved.get("kind") in ("knowledge-object", "domain-model-element"):
            moved["kind"] = "domain-object"
        for field in ("id", "driver"):
            if str(moved.get(field, "")).startswith("ko."):
                raise MigrationError(
                    f"entry {entry.get('id')!r} names {moved[field]!r}, an identifier from the "
                    f"profile that collapsed eight kinds into six. Which kind it takes now is what "
                    f"an analysis decides, and a migration that guessed would put that decision "
                    f"somewhere nobody could review it — re-run the analysis over the request"
                )
        implicated.append(moved)
    migrated["implicated"] = implicated
    migrated["contract_version"] = "impact-analysis/5"
    return migrated


def enrichment_result_1_to_2(doc: dict) -> dict:
    """Refuse a result naming an object under the retired profile's identifier.

    `/2` requires `object_id` to be a `dm.` identifier. A `/1` result names a `ko.` one, and which
    `dm.` identifier that object takes now is not derivable here: the two vocabularies differ in what
    a kind is, and a `ko.boundary.<context>` was a bounded context or an aggregate depending on a
    field this document does not carry.

    So the hop refuses rather than rewriting. What a holder does instead is discard the result: it
    reports on one pass over one object, both of which are re-runnable, and an enrichment result is
    not something a base keeps.
    """
    identifier = doc.get("object_id", "")
    if not str(identifier).startswith("dm."):
        raise MigrationError(
            f"result {doc.get('result_id')!r} names {identifier!r}, an identifier from the profile "
            f"that collapsed eight kinds into six. Which kind that object takes now is not derivable "
            f"from this document — discard the result and re-run the enrichment over the object"
        )
    migrated = dict(doc)
    migrated["contract_version"] = "knowledge-enrichment-result/2"
    return migrated


def _stamp(version: str):
    """A hop that adds nothing but the version, for a bump that only narrows what was never used."""
    def hop(doc: dict) -> dict:
        migrated = dict(doc)
        migrated["contract_version"] = version
        return migrated
    return hop


def _name_consumer(version: str, consumer):
    """Add the consumer the artifact always had and never stated.

    `.claude/rules/contracts.md` requires a named producer *and* a named consumer of every artifact
    passed between capabilities. Only the producer was ever recorded, so a reader tracing an
    artifact forward had to search the declaration set for whoever parsed it. The value is not
    invented: it is who reads the artifact today, and a document that predates the field was read by
    the same capability.
    """
    def hop(doc: dict) -> dict:
        migrated = dict(doc)
        migrated["consumer"] = list(consumer) if isinstance(consumer, (list, tuple)) else consumer
        migrated["contract_version"] = version
        return migrated
    return hop



# Keyed by (from, to). A key here is the claim that a document can cross that boundary; the
# coverage check in check_contract_versions.py fails when a boundary exists and a key does not.
MIGRATIONS: dict[tuple[str, str], Callable[[dict], dict]] = {
    ("capability-declaration/1", "capability-declaration/2"): capability_declaration_1_to_2,
    ("capability-declaration/2", "capability-declaration/3"): capability_declaration_2_to_3,
    ("distribution-manifest/1", "distribution-manifest/2"): distribution_manifest_1_to_2,
    ("impact-analysis/1", "impact-analysis/2"): impact_analysis_1_to_2,
    ("impact-analysis/2", "impact-analysis/3"): impact_analysis_2_to_3,
    ("validation-evidence/1", "validation-evidence/2"): validation_evidence_1_to_2,
    ("impact-analysis/3", "impact-analysis/4"): _name_consumer("impact-analysis/4", "ingest-domain"),
    ("impact-analysis/4", "impact-analysis/5"): impact_analysis_4_to_5,
    ("knowledge-enrichment-result/1", "knowledge-enrichment-result/2"): enrichment_result_1_to_2,
    ("validation-evidence/2", "validation-evidence/3"): _name_consumer("validation-evidence/3", "ingest-domain"),
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
