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


def domain_model_1_to_2(doc: dict) -> dict:
    """Derive the element identifiers `/2` requires, and refuse an element whose name will not slug.

    `/2` gives every element the `dm.<kind>.<scope>.<slug>` identifier `foundation/0002` R7 states
    and R8 requires to be *derived rather than allocated* — so the value is computed here rather
    than asked for, and computing it is exactly what R8 says any reader can do.

    Two shapes, per R7: a `subdomain` and a `context` are each a scope themselves and take
    `dm.<kind>.<slug>`; everything else takes the context it belongs to as its scope. A
    `lifecycle` takes the slug of its subject rather than of its own name, because it has no name
    of its own.

    The refusal is where a name will not reduce to `[a-z0-9]+(-[a-z0-9]+)*`. Transliterating one
    that will not — an accented word, a name in a non-Latin script — would mint an identifier by a
    rule no specification states, and R8 requires the same model to yield the same identifiers on
    every run. A rule invented here would not survive being invented differently next time, so the
    element is named and the migration stops.
    """
    scoped = {"aggregate": "aggregates", "definition": "definitions", "rule": "rules",
              "lifecycle": "lifecycles", "interface": "interfaces", "process": "processes"}
    unscoped = {"subdomain": "subdomains", "context": "contexts"}

    def slug(text: str, kind: str, name: str) -> str:
        out = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", out or ""):
            raise MigrationError(
                f"{kind} {name!r} has no identifier and its name does not reduce to a kebab-case "
                "slug — deriving one would mint an identifier by a rule no specification states"
            )
        return out

    migrated = dict(doc)
    for kind, key in {**unscoped, **scoped}.items():
        elements = doc.get(key)
        if not elements:
            continue
        out = []
        for element in elements:
            if "id" in element:
                out.append(element)
                continue
            copy = dict(element)
            name = element.get("name", "")
            if kind in unscoped:
                copy["id"] = f"dm.{kind}.{slug(name, kind, name)}"
            else:
                subject = element.get("subject") if kind == "lifecycle" else name
                scope = slug(element.get("context", ""), kind, name)
                copy["id"] = f"dm.{kind}.{scope}.{slug(subject, kind, name)}"
            out.append(copy)
        migrated[key] = out
    migrated["contract_version"] = "domain-model/2"
    return migrated


def knowledge_object_2_to_3(doc: dict) -> dict:
    """Stamp `origin: modeled`, which is the only honest value for an object already in a base.

    `/3` requires every object to declare whether the material it was read from said the fact or
    the analysis decided it. A `/2` object records neither, and the two are not distinguishable
    after the fact: `sources` names the material but not which of its statements this object is.

    So the migration stamps `modeled` rather than choosing per object. It is the weaker claim of
    the two — that somebody reading the material reached this — and it is the one a reviewer can
    still reject. Stamping `stated` would assert that the business said this, without verification,
    which is the false claim the field exists to make impossible.

    An object that carries `origin` already is left alone: a base part-way through the migration
    must not have a hand-corrected `stated` overwritten by the default.
    """
    migrated = dict(doc)
    migrated.setdefault("origin", "modeled")
    migrated["contract_version"] = "knowledge-object/3"
    return migrated


def knowledge_intake_plan_1_to_2(doc: dict) -> dict:
    """Refuse: `/2` requires an `origin` per entry, and a `/1` plan cannot supply one.

    `/2` carries `origin` from the model element each entry classifies through to the object
    authored from it, because `knowledge-object/3` requires the field and `foundation/0002` R8
    forbids the authoring step from re-deciding it.

    A `/1` plan does not hold the value and the model it was derived from is not reachable from the
    document — the plan names its source in prose, not by identifier. Stamping `modeled` on every
    entry would be defensible for an object already in a base, where nothing better is recoverable;
    it is not defensible here, because the model that holds the true value still exists and
    reclassifying against it costs one run of a step that decides node type and identity
    deterministically. A plan is an intermediate artifact, and regenerating one is cheaper than
    carrying a fabricated provenance into every object authored from it.
    """
    raise MigrationError(
        f"intake plan {doc.get('intake_id')!r} predates per-entry `origin`, which "
        "knowledge-intake-plan/2 requires and a /1 plan does not hold. Reclassify from the domain "
        "model that produced it: the model declares the origin of every element, and a value "
        "invented here would travel into every object authored from this plan"
    )


def knowledge_object_3_to_4(doc: dict) -> dict:
    """Add nothing: every `/3` object satisfied its type outright, so none has a gap to declare.

    `/4` lets an object declare `gaps` in place of the fields its node type requires, and records
    per gap whether the domain or the framework closes it — `docs/adr/0021-an-object-carries-its-own-gaps.md`.

    The bump is breaking on the second entry of `.claude/rules/compatibility.md`: the alternation
    makes a previously *invalid* instance valid. The direction is what makes the hop a stamp.
    Nothing valid under `/3` stops being valid, because `/3` admitted only objects that declared
    everything their type required — an object short of a fact was refused at authoring and never
    written. So there is no gap to derive, and deriving one would assert that the domain owes an
    answer nobody asked for.
    """
    migrated = dict(doc)
    migrated["contract_version"] = "knowledge-object/4"
    return migrated


def knowledge_intake_plan_2_to_3(doc: dict) -> dict:
    """Classify each gap as `domain`, which is what every `/2` gap was.

    `/3` gives a gap a `kind`, so a reader can tell a fact only the domain can supply from one a
    step of this framework fills — `docs/adr/0021-an-object-carries-its-own-gaps.md`.

    Every `/2` gap is `domain` by construction. `/2` required `why` on all of them, and `why` says
    what the *material* would have to state; a gap the framework closes has no such answer, which
    is why `/3` refuses `why` on an `authoring` one. So the classification is derived rather than
    guessed, and the `why` each entry already carries travels unchanged.
    """
    migrated = dict(doc)
    migrated["entries"] = [
        {**entry, "gaps": [{**gap, "kind": "domain"} for gap in entry.get("gaps", [])]}
        for entry in doc.get("entries", [])
    ]
    migrated["contract_version"] = "knowledge-intake-plan/3"
    return migrated


def domain_model_2_to_3(doc: dict) -> dict:
    """Refuse: `/3` identifies each open question, and a `/2` question cannot be identified from itself.

    `/3` gives every open question an `oq_` identifier so a gap on an authored object can name the
    question that blocks it rather than restating it, and changes `blocks` from element names to the
    `dm.` identifiers those elements carry — both per
    `docs/adr/0021-an-object-carries-its-own-gaps.md`.

    Neither is derivable here. An identifier is `oq_` plus the question's *subject*, and reducing a
    sentence to its subject is a reading, not a transformation: two runs over the same question would
    not agree, and `foundation/0002` R8 requires the same model to yield the same identifiers every
    time. `blocks` is worse — a name resolves to an element only against the model's own element
    lists, and where two elements of different kinds share a name it resolves to two.

    So this refuses, and the model is remodelled. That is cheap where a `/2` model still has the
    request it answers, which it carries: the analysis is one delegation, and an identifier invented
    here would be an identifier no producer would reproduce.
    """
    raise MigrationError(
        f"model {doc.get('model_id')!r} predates identified open questions, which domain-model/3 "
        "requires. Re-run the analysis over the request this model names: an `oq_` identifier is "
        "derived from the question's subject and a `blocks` entry from the element's own "
        "identifier, and neither is recoverable from a /2 document without reading it"
    )


def knowledge_intake_plan_3_to_4(doc: dict) -> dict:
    """Merge `unmapped` into `entries`, and give every entry the outcome it always had.

    `/4` puts one entry per construct in one list, each declaring what became of it —
    `classified`, `unmapped`, or `refused`. `/3` had two lists and no way to say the third thing: a
    construct the model states *wrongly*, as against one it states incompletely. A missing fact is a
    gap on a classified entry; an attribute type outside the closed vocabulary is neither a gap nor
    an absent mapping, and `/3` had nowhere to put it.

    The merge is derivable and this hop performs it: every `/3` entry was classified, and every `/3`
    `unmapped` record was exactly an unmapped construct with its reason. Nothing becomes `refused`
    here — that outcome describes a reading of the model that `/3` could not record, so no `/3`
    document holds one, and inventing one would assert a defect nobody found.

    Entry order follows `/3`: its own entries first, then what it recorded as unmapped. A plan is
    sorted by identifier on production and an unmapped construct has none, so the two groups cannot
    interleave by that key anyway.
    """
    entries = [{**entry, "outcome": "classified"} for entry in doc.get("entries", [])]
    entries += [
        {"construct": record["construct"], "outcome": "unmapped", "reason": record["reason"]}
        for record in doc.get("unmapped", [])
    ]
    migrated = {key: value for key, value in doc.items() if key != "unmapped"}
    if entries:
        migrated["entries"] = entries
    migrated["contract_version"] = "knowledge-intake-plan/4"
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


# Keyed by (from, to). A key here is the claim that a document can cross that boundary; the
# coverage check in check_contract_versions.py fails when a boundary exists and a key does not.
MIGRATIONS: dict[tuple[str, str], Callable[[dict], dict]] = {
    ("capability-declaration/1", "capability-declaration/2"): capability_declaration_1_to_2,
    ("capability-declaration/2", "capability-declaration/3"): capability_declaration_2_to_3,
    ("distribution-manifest/1", "distribution-manifest/2"): distribution_manifest_1_to_2,
    ("domain-model/1", "domain-model/2"): domain_model_1_to_2,
    ("domain-model/2", "domain-model/3"): domain_model_2_to_3,
    ("impact-analysis/1", "impact-analysis/2"): impact_analysis_1_to_2,
    ("impact-analysis/2", "impact-analysis/3"): impact_analysis_2_to_3,
    ("validation-evidence/1", "validation-evidence/2"): validation_evidence_1_to_2,
    ("knowledge-object/1", "knowledge-object/2"): knowledge_object_1_to_2,
    ("knowledge-object/2", "knowledge-object/3"): knowledge_object_2_to_3,
    ("knowledge-object/3", "knowledge-object/4"): knowledge_object_3_to_4,
    ("knowledge-intake-plan/1", "knowledge-intake-plan/2"): knowledge_intake_plan_1_to_2,
    ("knowledge-intake-plan/2", "knowledge-intake-plan/3"): knowledge_intake_plan_2_to_3,
    ("knowledge-intake-plan/3", "knowledge-intake-plan/4"): knowledge_intake_plan_3_to_4,
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
