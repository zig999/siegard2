"""Contract versioning and migration, over `.claude/rules/compatibility.md`.

That rule states four things a breaking change owes and, until this suite, held none of them
to a mechanism.

No contract in this repository carries a second version, so no migration is registered. What
remains under test is the machinery that will meet the first real bump: the refusals a migration owes, and the coverage check that fails a bump
registering no path. `foundation/0013` R11 asks for a migration tested against the old behavior;
with no migration in the registry, R11 is unexercised rather than satisfied, and that is
stated here rather than implied by a green suite.

The contract-version checks are the same argument applied to the schemas
themselves: a constraint change with no version bump must be detected, and an edit to a
description must not be, because the rule calls one breaking and not the other.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator

import check_contract_versions as cv
from migrate_contracts import MIGRATIONS, MigrationError, migrate  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIPPED_SCHEMAS = REPO_ROOT / "src" / "claude" / "schemas"
GENERATOR_SCHEMAS = REPO_ROOT / "schemas"
SCHEMAS = SHIPPED_SCHEMAS


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SCHEMAS / name).read_text()))


class MigrationRefusals(unittest.TestCase):
    """A migration does not guess. Each refusal is the rejection direction of one rule."""

    def test_refuses_an_instance_declaring_another_version(self) -> None:
        with self.assertRaises(MigrationError) as caught:
            migrate({"contract_version": "adr/2"}, "adr/1", "adr/2")
        self.assertIn("does not guess", str(caught.exception))

    def test_refuses_a_downgrade(self) -> None:
        with self.assertRaises(MigrationError):
            migrate({"contract_version": "adr/2"}, "adr/2", "adr/1")

    def test_refuses_crossing_contracts(self) -> None:
        with self.assertRaises(MigrationError):
            migrate({"contract_version": "adr/1"}, "adr/1", "concept/1")

    def test_refuses_an_unregistered_hop(self) -> None:
        with self.assertRaises(MigrationError) as caught:
            migrate({"contract_version": "concept/1"}, "concept/1", "concept/2")
        self.assertIn("no migration registered", str(caught.exception))



class ImpactAnalysisHop(unittest.TestCase):
    """`impact-analysis/1` to `/2`, and the case the bump exists for.

    `.claude/rules/compatibility.md` requires "a compatibility or migration test that fails against
    the old behavior". The old behavior is reachable without reading the old file: `/1` had no
    `base_state` and its `minItems` rule was unconditional, which is exactly what `/2` does when told
    the base was `populated`. So the break is asserted as one pair — the same document is rejected
    under `populated` and admitted under `empty` — and the pair is the whole claim.

    An earlier version of this class read the superseded schema out of `git show HEAD:`. That passed
    only while the change was uncommitted: once `/2` is in HEAD the assertion inverts and the test
    fails for the opposite reason. A test whose meaning depends on not having committed yet is worse
    than no test, because it goes green at the moment it stops being true.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # The current contract, whatever version it is. `/2` has no file of its own — one file per
        # contract leaves every intermediate in a chain fileless — so a `/2` document is checked by
        # running it the rest of the way and validating what comes out.
        cls.current = validator("impact-analysis.json")

    def first_change(self, **over) -> dict:
        """A `create` over a base that held nothing — what `/1` could not express."""
        return {
            "contract_version": "impact-analysis/2",
            "analysis_id": "ia_3f9c1b02",
            "request_id": "cr_7a2e4d10",
            "producer": "impact-analyst",
            "verdict": "create",
            "base_state": "empty",
            "implicated": [],
            **over,
        }

    def test_the_chain_admits_a_create_that_implicates_nothing_over_an_empty_base(self) -> None:
        """The case the `/2` bump exists for, carried to the contract that is current."""
        document = self.first_change()
        document["model_id"] = "dm_4c1e7a90"  # `/3` requires it, and `/2` had nowhere to hold it
        document["implicated"] = [{
            "id": "dm.definition.sales.proposal",
            "kind": "domain-model-element",
            "operation": "create",
            "driver": "dm.definition.sales.proposal",
            "reason": "the base holds nothing answering to this element",
        }]
        migrated = migrate(document, "impact-analysis/2", "impact-analysis/3")
        self.assertEqual([], list(self.current.iter_errors(migrated)))
        self.assertEqual("rq_7a2e4d10", migrated["request_id"])

    def test_the_same_document_is_rejected_under_the_old_rule(self) -> None:
        """The break itself: `populated` is `/1`'s unconditional rule, and it still rejects.

        This is the half that fails against the old behavior. Without it, the test above would only
        show `/2` accepting something, with nothing establishing that anything used to refuse it.
        """
        document = self.first_change(base_state="populated")
        self.assertNotEqual([], list(self.current.iter_errors(document)))

    def test_an_empty_base_admits_no_update(self) -> None:
        document = self.first_change(verdict="update")
        self.assertNotEqual([], list(self.current.iter_errors(document)))

    def test_base_state_is_required(self) -> None:
        document = self.first_change()
        del document["base_state"]
        self.assertNotEqual([], list(self.current.iter_errors(document)))

    def test_the_migration_infers_populated_and_stamps_the_version(self) -> None:
        migrated = migrate(
            {
                "contract_version": "impact-analysis/1",
                "analysis_id": "ia_5c7d9e01",
                "request_id": "cr_2b4f6a80",
                "producer": "impact-analyst",
                "verdict": "update",
                "implicated": [{"id": "billing.invoice", "kind": "knowledge-object",
                                "operation": "update", "reason": "the model narrows it"}],
            },
            "impact-analysis/1",
            "impact-analysis/2",
        )
        self.assertEqual("impact-analysis/2", migrated["contract_version"])
        self.assertEqual("populated", migrated["base_state"])
        migrated["model_id"] = "dm_4c1e7a90"
        current = migrate(migrated, "impact-analysis/2", "impact-analysis/3")
        self.assertEqual([], list(self.current.iter_errors(current)))

    def test_the_migration_leaves_the_input_alone(self) -> None:
        source = {
            "contract_version": "impact-analysis/1",
            "analysis_id": "ia_5c7d9e01",
            "request_id": "cr_2b4f6a80",
            "producer": "impact-analyst",
            "verdict": "none",
            "implicated": [],
        }
        migrate(dict(source), "impact-analysis/1", "impact-analysis/2")
        self.assertEqual("impact-analysis/1", source["contract_version"])
        self.assertNotIn("base_state", source)

    def test_a_none_verdict_also_infers_populated(self) -> None:
        """`none` asserts the request is already answered, which nothing empty can assert."""
        migrated = migrate(
            {
                "contract_version": "impact-analysis/1",
                "analysis_id": "ia_5c7d9e01",
                "request_id": "cr_2b4f6a80",
                "producer": "impact-analyst",
                "verdict": "none",
                "implicated": [],
            },
            "impact-analysis/1",
            "impact-analysis/2",
        )
        self.assertEqual("populated", migrated["base_state"])


class KnowledgeObjectOriginHop(unittest.TestCase):
    """`knowledge-object/2` to `/3`: the provenance a base with no status has no other way to carry.

    `.claude/rules/compatibility.md` requires "a compatibility or migration test that fails against
    the old behavior". The old behavior is an object with no `origin`, and the pair below is the
    whole claim: `/3` rejects it, and the hop is what makes it acceptable.

    The value the hop chooses is the point of the second pair. `modeled` is the weaker of the two
    readings — somebody reading the material reached this — and a reviewer can reject it. `stated`
    would assert that the business said it, and nothing in a `/2` document supports that, so a
    migration that inferred it would manufacture exactly the false claim `origin` exists to prevent.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.current = validator("knowledge-object.json")

    def object_at_2(self, **over) -> dict:
        return {
            "contract_version": "knowledge-object/2",
            "id": "ko.rule.sales.cancelled-order-not-billable",
            "type": "rule",
            "title": "Cancelled order not billable",
            "description": "A cancelled order cannot be invoiced.",
            "question": "May a cancelled order be invoiced?",
            "boundary": "ko.boundary.sales.order",
            "ddd": "domain-rule",
            "statement": "A cancelled order MUST NOT be invoiced.",
            "expression": "order.status == cancelled implies not order.invoiceable",
            "generated": {"by": "knowledge-author", "at": "2026-08-01T09:00:00Z"},
            "out_of_scope": ["How an order is cancelled."],
            **over,
        }

    def test_the_old_shape_is_rejected(self) -> None:
        """The half that fails against the old behavior."""
        errors = list(self.current.iter_errors(self.object_at_2()))
        self.assertTrue(any("origin" in str(e) for e in errors), errors)

    def test_the_hop_makes_it_conform(self) -> None:
        """Carried to the current contract: `/3` stopped being current when `/4` landed, and one
        file per contract leaves the intermediate with no schema of its own to check against."""
        migrated = migrate(self.object_at_2(), "knowledge-object/2", "knowledge-object/4")
        self.assertEqual([], list(self.current.iter_errors(migrated)))

    def test_it_stamps_modeled_and_never_stated(self) -> None:
        """`stated` would assert the business said it, with nothing in the document supporting that."""
        migrated = migrate(self.object_at_2(), "knowledge-object/2", "knowledge-object/3")
        self.assertEqual("modeled", migrated["origin"])
        self.assertEqual("knowledge-object/3", migrated["contract_version"])

    def test_a_hand_corrected_origin_survives(self) -> None:
        """A base part-way through the migration must not lose a correction to the default."""
        migrated = migrate(
            self.object_at_2(origin="stated"), "knowledge-object/2", "knowledge-object/3"
        )
        self.assertEqual("stated", migrated["origin"])

    def test_the_vocabulary_is_two_values(self) -> None:
        """A third would be a distinction nothing consumes."""
        document = migrate(self.object_at_2(), "knowledge-object/2", "knowledge-object/3")
        document["origin"] = "inferred"
        self.assertNotEqual([], list(self.current.iter_errors(document)))

    def test_the_whole_chain_runs(self) -> None:
        """`/1` to `/3` in one call: the registry is walked one hop at a time."""
        at_one = self.object_at_2(contract_version="knowledge-object/1", status="accepted")
        migrated = migrate(at_one, "knowledge-object/1", "knowledge-object/4")
        self.assertEqual([], list(self.current.iter_errors(migrated)))
        self.assertNotIn("status", migrated)
        self.assertEqual("modeled", migrated["origin"])


class KnowledgeObjectGapsHop(unittest.TestCase):
    """`knowledge-object/3` to `/4`: an object declares what its type requires and it does not have.

    `docs/adr/0021-an-object-carries-its-own-gaps.md` decides it. The pair the compatibility rule
    asks for is the alternation itself: `/3` refused an object short of a required field, and `/4`
    accepts the same object once it says which field and who can close it.

    The hop adds nothing, and the cases below are why that is right rather than lazy: no `/3` object
    can have a gap, because `/3` admitted only objects that declared everything their type required.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.current = validator("knowledge-object.json")

    ATTRIBUTE = {"name": "cep", "type": "string", "max_length": 9}

    def incomplete(self, **over) -> dict:
        """An aggregate root whose attributes the request never named."""
        return {
            "contract_version": "knowledge-object/4",
            "id": "ko.definition.enderecos.endereco",
            "type": "definition",
            "title": "Endereco",
            "description": "O local que um cadastro referencia.",
            "question": "O que e um endereco, e o que o identifica?",
            "boundary": "ko.boundary.enderecos.endereco",
            "ddd": "aggregate-root",
            "origin": "modeled",
            "generated": {"by": "domain-analyst", "at": "2026-08-01T17:21:23Z"},
            "out_of_scope": ["A exclusao de um endereco."],
            **over,
        }

    def complete(self, **over) -> dict:
        return self.incomplete(
            attributes=[self.ATTRIBUTE], identity={"attributes": ["cep"]}, **over
        )

    def conforms(self, document: dict) -> bool:
        return list(self.current.iter_errors(document)) == []

    def test_an_incomplete_object_is_refused_when_it_says_nothing(self) -> None:
        """The half that fails against the old behavior, and the reason the field is not a status."""
        self.assertFalse(self.conforms(self.incomplete()))

    def test_the_same_object_is_admitted_once_it_declares_the_gap(self) -> None:
        self.assertTrue(self.conforms(self.incomplete(gaps=[
            {"kind": "domain", "field": "attributes",
             "why": "o pedido diz «endereco» e nao nomeia um campo",
             "question": "oq_endereco_campos"},
        ])))

    def test_a_nested_requirement_is_excused_too(self) -> None:
        """`identity` is required by a conditional on `ddd`, not by the type's own list."""
        self.assertTrue(self.conforms(self.incomplete(
            attributes=[self.ATTRIBUTE],
            gaps=[{"kind": "domain", "field": "identity.attributes",
                   "why": "identificador do sistema, ou chave natural?"}],
        )))

    def test_a_prohibition_is_not_excused(self) -> None:
        """A gap says a fact is absent; it cannot make a forbidden field allowed."""
        document = self.incomplete(
            type="lifecycle", id="ko.lifecycle.enderecos.endereco",
            gaps=[{"kind": "domain", "field": "states", "why": "o pedido nomeia nenhum estado"}],
        )
        self.assertIn("ddd", document, "the fixture must carry the field the type forbids")
        self.assertFalse(self.conforms(document))

    def test_a_complete_object_still_conforms_with_no_gaps(self) -> None:
        """The alternation widens; it does not move the requirement."""
        self.assertTrue(self.conforms(self.complete()))

    def test_a_complete_object_may_still_carry_an_authoring_gap(self) -> None:
        self.assertTrue(self.conforms(self.complete(
            gaps=[{"kind": "authoring", "field": "description"}])))

    def test_why_is_required_of_a_domain_gap_and_refused_of_an_authoring_one(self) -> None:
        self.assertFalse(self.conforms(self.incomplete(
            gaps=[{"kind": "domain", "field": "attributes"}])))
        self.assertFalse(self.conforms(self.complete(
            gaps=[{"kind": "authoring", "field": "question", "why": "nao deveria estar aqui"}])))

    def test_the_kind_vocabulary_is_two_values(self) -> None:
        self.assertFalse(self.conforms(self.incomplete(
            gaps=[{"kind": "unresolved", "field": "attributes", "why": "x"}])))

    def test_an_empty_gaps_array_is_refused(self) -> None:
        """Declaring completeness is the absent key, never an empty list."""
        self.assertFalse(self.conforms(self.complete(gaps=[])))

    def test_a_shared_question_is_named_in_the_open_question_form(self) -> None:
        self.assertFalse(self.conforms(self.incomplete(
            gaps=[{"kind": "domain", "field": "attributes", "why": "x", "question": "campos"}])))

    def test_the_hop_adds_nothing_and_stamps_the_version(self) -> None:
        at_three = self.complete(contract_version="knowledge-object/3")
        migrated = migrate(at_three, "knowledge-object/3", "knowledge-object/4")
        self.assertEqual("knowledge-object/4", migrated["contract_version"])
        self.assertNotIn("gaps", migrated)
        self.assertTrue(self.conforms(migrated))


class IntakePlanOutcomeHop(unittest.TestCase):
    """`knowledge-intake-plan/3` to `/4`: one list of constructs, each saying what became of it.

    `/3` kept classified entries and unmapped constructs in two arrays and could not express a
    third case at all — a construct the model states *wrongly*, as against one it states
    incompletely. `docs/adr/0021-an-object-carries-its-own-gaps.md` draws that line for the object;
    the plan needs the same one, because a gap and a refusal are answered by different people.

    The merge is derivable, which is why this hop performs it rather than refusing: every `/3` entry
    was classified and every `/3` unmapped record was an unmapped construct with its reason.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.current = validator("knowledge-intake-plan.json")

    def at_three(self, **over) -> dict:
        return {
            "contract_version": "knowledge-intake-plan/3",
            "intake_id": "ki_4c1e7a90",
            "producer": "domain-analyst",
            "source": {"description": "The sales analysis", "artifacts": ["intake/sales.md"]},
            "state": "classified",
            "entries": [{
                "construct": "Proposal",
                "node_type": "definition",
                "ddd": "aggregate-root",
                "origin": "modeled",
                "boundary": "ko.boundary.sales.proposal",
                "proposed_id": "ko.definition.sales.proposal",
                "gaps": [{"kind": "domain", "field": "attributes", "why": "none are named"}],
            }],
            "unmapped": [{"construct": "ProposalRepository", "reason": "stack knowledge"}],
            **over,
        }

    def test_the_old_shape_is_rejected(self) -> None:
        self.assertNotEqual([], list(self.current.iter_errors(self.at_three())))

    def test_the_hop_merges_both_lists_and_conforms(self) -> None:
        migrated = migrate(self.at_three(), "knowledge-intake-plan/3", "knowledge-intake-plan/4")
        self.assertEqual([], list(self.current.iter_errors(migrated)))
        self.assertNotIn("unmapped", migrated)
        self.assertEqual(2, len(migrated["entries"]))

    def test_each_construct_keeps_what_it_was(self) -> None:
        migrated = migrate(self.at_three(), "knowledge-intake-plan/3", "knowledge-intake-plan/4")
        outcomes = {e["construct"]: e["outcome"] for e in migrated["entries"]}
        self.assertEqual({"Proposal": "classified", "ProposalRepository": "unmapped"}, outcomes)

    def test_nothing_becomes_refused(self) -> None:
        """`/3` could not record a refusal, so no `/3` document holds one to recover."""
        migrated = migrate(self.at_three(), "knowledge-intake-plan/3", "knowledge-intake-plan/4")
        self.assertNotIn("refused", {e["outcome"] for e in migrated["entries"]})

    def test_the_gaps_travel_unchanged(self) -> None:
        migrated = migrate(self.at_three(), "knowledge-intake-plan/3", "knowledge-intake-plan/4")
        entry = next(e for e in migrated["entries"] if e["construct"] == "Proposal")
        self.assertEqual([{"kind": "domain", "field": "attributes", "why": "none are named"}],
                         entry["gaps"])

    def test_a_plan_with_no_unmapped_records_still_migrates(self) -> None:
        document = self.at_three()
        del document["unmapped"]
        migrated = migrate(document, "knowledge-intake-plan/3", "knowledge-intake-plan/4")
        self.assertEqual([], list(self.current.iter_errors(migrated)))


class ConstraintDigest(unittest.TestCase):
    """What counts as a change, and what does not — the rule's own distinction."""

    def test_annotation_keywords_are_stripped(self) -> None:
        plain = {"type": "object", "properties": {"a": {"type": "string"}}}
        annotated = {
            "type": "object",
            "description": "some prose",
            "properties": {"a": {"type": "string", "description": "more prose"}},
        }
        self.assertEqual(cv.constraint_digest(plain), cv.constraint_digest(annotated))

    def test_a_property_named_description_survives(self) -> None:
        """`properties.description` is a field name, not an annotation — the concept contract has one."""
        schema = {"type": "object", "properties": {"description": {"type": "string"}}}
        stripped = cv.strip_annotations(schema)
        self.assertIn("description", stripped["properties"])

    def test_a_constraint_change_changes_the_digest(self) -> None:
        before = {"type": "object", "properties": {"a": {"type": "string"}}}
        after = {"type": "object", "properties": {"a": {"type": "string", "maxLength": 3}}}
        self.assertNotEqual(cv.constraint_digest(before), cv.constraint_digest(after))

    def test_key_order_does_not_change_the_digest(self) -> None:
        self.assertEqual(
            cv.constraint_digest({"type": "object", "required": ["a"]}),
            cv.constraint_digest({"required": ["a"], "type": "object"}),
        )


class Declaration(unittest.TestCase):
    """A filename and a self-declared version are two records of one fact."""

    def entry(self, file: str, name: str, schema: dict) -> dict:
        return {"file": file, "name": name, "schema": schema}

    def test_agreement_passes(self) -> None:
        schema = {
            "required": ["contract_version"],
            "properties": {"contract_version": {"const": "widget/1"}},
        }
        self.assertEqual([], cv.check_declaration("widget/1", self.entry("widget.json", "widget", schema)))

    def test_a_const_naming_another_file_is_reported(self) -> None:
        """The filename carries identity, the document carries the version, and they must agree."""
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        directory = Path(holder.name)
        (directory / "widget.json").write_text(json.dumps({
            "required": ["contract_version"],
            "properties": {"contract_version": {"const": "gadget/1"}},
        }))
        with mock.patch.object(cv, "SCHEMA_DIRS", (directory,)):
            _found, problems = cv.contracts()
        self.assertEqual(1, len(problems))
        self.assertIn("does not name this file", problems[0])

    def test_declared_but_not_required_is_reported(self) -> None:
        schema = {"properties": {"contract_version": {"const": "widget/1"}}}
        problems = cv.check_declaration("widget/1", self.entry("widget.json", "widget", schema))
        self.assertIn("does not require it", problems[0])

    def test_a_missing_declaration_is_reported(self) -> None:
        problems = cv.check_declaration("widget/1", self.entry("widget.json", "widget", {}))
        self.assertIn("infer", problems[0])

    def test_harness_owned_contracts_are_exempt(self) -> None:
        schema = {"additionalProperties": False, "properties": {"name": {"type": "string"}}}
        self.assertEqual([], cv.check_declaration("skill/1", self.entry("skill.json", "skill", schema)))

    def test_the_exemption_requires_a_closed_object(self) -> None:
        """The stated reason has to hold, or the exemption is a hole with a comment on it."""
        schema = {"properties": {"name": {"type": "string"}}}
        problems = cv.check_declaration("skill/1", self.entry("skill.json", "skill", schema))
        self.assertIn("additionalProperties", problems[0])


class LockIntegrity(unittest.TestCase):
    """The committed lock against a disposable copy of both contract trees.

    Contracts sit on two sides now — what the framework ships under `src/claude/schemas/`,
    and what governs this repository under `schemas/` — and one lock covers both, because a
    constraint that moves is a break whichever side it sits on. The copy flattens them, which
    is what the checker sees anyway: it keys on contract version, and a name colliding across
    the two trees would be the defect this arrangement should surface rather than hide.
    """

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.dir = Path(holder.name) / "schemas"
        shutil.copytree(GENERATOR_SCHEMAS, self.dir)
        for source in SHIPPED_SCHEMAS.glob("*.json"):
            shutil.copy(source, self.dir / source.name)
        patches = [
            mock.patch.object(cv, "SCHEMA_DIRS", (self.dir,)),
            mock.patch.object(cv, "SCHEMA_DIR", self.dir),
            mock.patch.object(cv, "LOCK_PATH", self.dir / "contract-versions.json"),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def edit(self, name: str, mutate) -> None:
        path = self.dir / name
        schema = json.loads(path.read_text())
        mutate(schema)
        path.write_text(json.dumps(schema, indent=2) + "\n")

    def test_the_committed_lock_matches_the_committed_schemas(self) -> None:
        count, problems = cv.check(update=False)
        self.assertEqual([], problems)
        self.assertEqual(0, count)

    def test_a_constraint_change_without_a_bump_is_reported(self) -> None:
        self.edit("concept.json", lambda s: s["properties"]["tags"].update(maxItems=3))
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("concept.json" in p and "constraints changed" in p for p in problems),
            f"expected a constraint-drift report naming the file; got {problems}",
        )

    def test_an_annotation_change_is_not_reported(self) -> None:
        self.edit(
            "concept.json",
            lambda s: s["properties"]["title"].update(description="Display name, reworded."),
        )
        _count, problems = cv.check(update=False)
        self.assertEqual([], problems)

    def test_a_removed_contract_is_reported(self) -> None:
        (self.dir / "impact-analysis.json").unlink()
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any(p.startswith("impact-analysis/") for p in problems),
            f"expected a removal report; got {problems}",
        )

    def test_an_unrecorded_contract_is_reported(self) -> None:
        shutil.copy(self.dir / "concept.json", self.dir / "widget.json")
        self.edit("widget.json", lambda s: s["properties"]["contract_version"].update(const="widget/1"))
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("widget.json" in p and "not recorded" in p for p in problems),
            f"expected an unrecorded-contract report; got {problems}",
        )

    def test_a_malformed_filename_is_reported(self) -> None:
        shutil.copy(self.dir / "concept.json", self.dir / "no-version.json")
        _count, problems = cv.check(update=False)
        self.assertTrue(
            any("no-version.json" in p for p in problems),
            f"expected a filename report; got {problems}",
        )

    def test_update_rewrites_the_lock_so_the_check_passes_again(self) -> None:
        self.edit("concept.json", lambda s: s["properties"]["tags"].update(maxItems=3))
        cv.check(update=True)
        _count, problems = cv.check(update=False)
        self.assertEqual([], problems)



if __name__ == "__main__":
    unittest.main()


class SupersededContracts(unittest.TestCase):
    """One file per contract, so the lock is where a bump leaves its trace.

    `.claude/rules/compatibility.md` keeps the current version only in `schemas/`. That removed the
    trace a second version file used to leave, and these cover what replaced it: a superseded entry
    naming its successor, and a migration registered for the hop. The coverage check the older
    convention carried is back, keyed on the record rather than on two files.
    """

    SUCCESSOR = {"distribution-manifest/2": "digest"}

    def entry(self, **overrides) -> dict:
        base = {
            "schema": "distribution-manifest.json",
            "constraint_digest": "sha256:old",
            "superseded_by": "distribution-manifest/2",
        }
        base.update(overrides)
        return {"distribution-manifest/1": base}

    def test_a_superseded_contract_with_a_registered_migration_passes(self) -> None:
        self.assertEqual(
            [], cv.check_superseded("distribution-manifest/1", self.entry(), self.SUCCESSOR)
        )

    def test_a_missing_migration_is_reported(self) -> None:
        """The direction that matters: a bump that left its consumers no way forward."""
        with mock.patch.object(cv, "registered_migrations", lambda: set()):
            problems = cv.check_superseded(
                "distribution-manifest/1", self.entry(), self.SUCCESSOR
            )
        self.assertEqual(1, len(problems))
        self.assertIn("no migration registered", problems[0])

    def test_an_entry_naming_no_successor_is_still_a_removal(self) -> None:
        locked = self.entry()
        del locked["distribution-manifest/1"]["superseded_by"]
        problems = cv.check_superseded("distribution-manifest/1", locked, self.SUCCESSOR)
        self.assertIn("a removed contract is a breaking change", problems[0])

    def test_a_successor_no_schema_declares_is_reported(self) -> None:
        problems = cv.check_superseded("distribution-manifest/1", self.entry(), {})
        self.assertIn("does not exist", problems[0])

    def test_update_carries_a_superseded_entry_forward(self) -> None:
        previous = self.entry(superseded_by=None)
        del previous["distribution-manifest/1"]["superseded_by"]
        carried = cv.carry_superseded(previous, self.SUCCESSOR)
        self.assertEqual("distribution-manifest/2", carried["distribution-manifest/1"]["superseded_by"])
        self.assertEqual("sha256:old", carried["distribution-manifest/1"]["constraint_digest"])

    def test_update_drops_an_entry_with_no_successor(self) -> None:
        """A removal is a break the caller states, not a record --update should preserve."""
        self.assertEqual({}, cv.carry_superseded(self.entry(), {}))

    def test_the_registered_hop_stamps_the_version_and_changes_nothing_else(self) -> None:
        before = {
            "contract_version": "distribution-manifest/1",
            "capabilities": [{"name": "a", "class": "hook", "status": "active", "path": "hooks/a.py"}],
        }
        after = migrate(before, "distribution-manifest/1", "distribution-manifest/2")
        self.assertEqual("distribution-manifest/2", after["contract_version"])
        self.assertEqual(before["capabilities"], after["capabilities"])
        self.assertNotIn("declaration", after["capabilities"][0])

    def test_the_migrated_document_satisfies_the_new_contract(self) -> None:
        """A path that produces an invalid document is not a path."""
        schema = json.loads(
            (REPO_ROOT / "src" / "claude" / "schemas" / "distribution-manifest.json").read_text()
        )
        old = json.loads((REPO_ROOT / "dist" / ".claude" / "siegard-manifest.json").read_text())
        old["contract_version"] = "distribution-manifest/1"
        for capability in old["capabilities"]:
            capability.pop("declaration", None)
        migrated = migrate(old, "distribution-manifest/1", "distribution-manifest/2")
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(migrated)))
