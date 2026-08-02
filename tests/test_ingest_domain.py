"""The ingestion entry point: what its procedure must keep saying.

`ingest-domain` is prose, and prose has no syntax to fail. What is asserted here is the small set of
statements the procedure cannot lose without becoming wrong — the authoring order, the two refusals, and
the handoff it owes its caller. Each was chosen because losing it produces a specific bad outcome, not
because the sentence reads well.

The order is the load-bearing one. Every object except a bounded-context boundary declares the one
boundary it belongs to, so authoring a definition before its context leaves a reference resolving to
nothing. A skill that stopped naming the order would still run, and would produce a base the
materializer rejects.
"""

from __future__ import annotations

import json
import unittest

from . import SHIPPED_ROOT

SKILL = SHIPPED_ROOT / "skills" / "ingest-domain" / "SKILL.md"
DECLARATION = SHIPPED_ROOT / "capabilities.declaration.json"

# The six node types in the order the ontology's analysis demands: strategic before tactical.
NODE_ORDER = ("boundary", "definition", "rule", "lifecycle", "interface", "process")


class Procedure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SKILL.read_text()

    def test_it_expands_before_enriching(self) -> None:
        """The two passes, in order, and the reason the order is not preference.

        It asserted that `domain-analyst` was delegated to before `knowledge-author`. Neither runs
        here now: the classification is a script because the mapping is a table, and the authoring
        is the enrichment of an object that already exists. What survives is the property those two
        delegations were ordered for — that nothing is written against a base half built.
        """
        self.assertLess(self.body.index("bin/expand_model.py"),
                        self.body.index("`knowledge-enricher`"),
                        "every object exists before any is enriched")
        self.assertNotIn("domain-analyst", self.body,
                         "the classification is a script, and delegating it would pay 75k tokens "
                         "for a table lookup")

    def test_it_enriches_through_the_agent_that_owns_one_object(self) -> None:
        self.assertIn("One delegation to `knowledge-enricher` per staged object", self.body)

    def test_it_names_the_pipeline_order(self) -> None:
        """The node order it asserted is gone, and so is the reason for it.

        Authoring one object at a time made a definition depend on its context existing first, so
        the order was the guarantee. The expansion writes the whole tree at once, so what is ordered
        now is the passes — and the review between them, which is the step a run can skip and the
        one it must not.
        """
        stages = ["expand_model.py", "read the diff", "knowledge-enricher",
                  "check_enrichment.py", "promote_staged.py"]
        positions = [self.body.index(stage) for stage in stages]
        self.assertEqual(sorted(positions), positions, f"order drifted: {stages}")

    def test_it_refuses_to_supply_a_domain_fact(self) -> None:
        self.assertIn("You supply no domain fact", self.body)

    def test_it_does_not_answer_the_models_open_questions(self) -> None:
        """A question the modeller refused to decide is not this procedure's to decide."""
        self.assertIn("carry them, never answer\n  them", self.body)

    def test_it_does_not_reopen_a_modelling_decision(self) -> None:
        self.assertIn("Re-open a modelling decision", self.body)

    def test_it_records_no_status(self) -> None:
        """The inverse of what stood here, and `docs/adr/0018-...` is why.

        This asserted `You do not promote` and a birth at `proposed`. Both described a maturity
        ladder the framework removed: what the base holds is current and binds, the contract rejects
        `status` rather than preserving it, and there is no promotion left to refuse. The assertion
        is inverted rather than deleted, because a skill that quietly reintroduced a tier is exactly
        what this test was watching for.
        """
        self.assertIn("You record no status", self.body)
        self.assertIn("never an object written at a lower tier", self.body)

    def test_it_authors_no_derived_file(self) -> None:
        """The materializer that regenerated them went with the generation path; the rule did not."""
        self.assertIn("Author a derived file", self.body)
        self.assertIn("a hand-written one is a second authority", self.body)

    def test_it_reads_the_enrichment_result_rather_than_the_filesystem(self) -> None:
        """A producer's own report is what tells an authored entry from a blocked one."""
        self.assertIn("knowledge-enrichment-result/1", self.body)
        self.assertIn("you read it rather than the filesystem", self.body)

    def test_it_records_what_validated(self) -> None:
        """`0001` R22: validation carries evidence, and nothing produced any until this skill did."""
        self.assertIn("validation-evidence/2", self.body)
        self.assertIn("saying what validated it is an assertion", self.body)

    def test_it_names_every_script_it_runs(self) -> None:
        """C04 demands the name of a script a component tells its executor to run.

        It named two, and both went with the shipped executables. The skill now says the
        distribution performs none of those checks and reports them as owed, which is the honest
        form — and C04 has nothing to demand because there is no instruction left to run anything.
        """
        for script in ("bin/expand_model.py", "bin/check_enrichment.py", "bin/promote_staged.py"):
            with self.subTest(script=script):
                self.assertIn(script, self.body)
        self.assertIn("The distribution ships nothing that performs them", self.body)

    def test_it_reports_what_stands_between_the_base_and_a_reader(self) -> None:
        """An ingestion reported as finished sends the caller into a block nobody warned about.

        The handoff was to a maintainer who promoted the objects. With no promotion left, what the
        caller must be told is the same thing by its real name: the blocked entries and the checks
        nothing ran.
        """
        self.assertIn("what stands between this base and", self.body)
        self.assertIn("the blocked entries and the owed checks nothing ran", self.body)

    def test_it_is_not_model_invocable(self) -> None:
        """It writes a knowledge base, so a description match must not be able to trigger it."""
        self.assertIn("disable-model-invocation: true", self.body)


class Declaration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        declarations = json.loads(DECLARATION.read_text())["declarations"]
        cls.entry = next(d for d in declarations if d["identifier"] == "ingest-domain")

    def test_it_is_a_skill(self) -> None:
        self.assertEqual("skill", self.entry["class"])

    def test_it_never_chooses_the_system_defaults(self) -> None:
        """A timezone or a ceiling the framework picked would be the hidden default it rejects."""
        defaults = next(i for i in self.entry["inputs"] if i["name"] == "system_defaults")
        self.assertFalse(defaults["required"])
        self.assertIn("stops rather than choosing", defaults["default"])

    def test_one_refused_construct_is_not_a_stop(self) -> None:
        """One construct the model states wrongly must not abandon the ones it states well."""
        refused = next(f for f in self.entry["failure_outcomes"]
                       if f["outcome"] == "construct_refused")
        self.assertIn("still expand", refused["reason"])

    def test_a_blocked_model_authors_nothing(self) -> None:
        blocked = next(f for f in self.entry["failure_outcomes"] if f["outcome"] == "model_blocked")
        self.assertIn("nothing written", blocked["reason"])

    def test_it_declares_the_domain_model_as_a_contracted_prerequisite(self) -> None:
        """The order between modelling and ingesting is what a declared input makes derivable."""
        model = next(i for i in self.entry["inputs"] if i["name"] == "domain_model")
        self.assertEqual("domain-model", model["artifact"])
        self.assertEqual("domain-model/3", model["contract"])
        self.assertTrue(model["required"])

    def test_it_declares_the_ordering_guarantee(self) -> None:
        """The order changed and the guarantee moved with it.

        It was strategic-before-tactical, which existed so an object's boundary and every reference
        it declared existed before it did. The expansion writes the whole tree at once, so nothing
        is ordered behind anything — and the guarantee that replaced it is the one that made the
        old order necessary in the first place: every object exists before any is enriched.
        """
        self.assertTrue(
            any("before any is enriched" in b for b in self.entry["deterministic_behavior"]),
            "the order is the guarantee this capability's correctness rests on",
        )

    def test_it_declares_the_authoring_result_it_consumes(self) -> None:
        """The gap R24 closed on the input side, on the output side: a read that was never declared."""
        consumed = {c["artifact"] for c in self.entry["consumed_artifacts"]}
        self.assertIn("knowledge-enrichment-result", consumed)

    def test_it_produces_the_validation_evidence_the_method_requires(self) -> None:
        """`validation-evidence/2` was the one contract with neither a producer nor a consumer."""
        produced = {o["contract"] for o in self.entry["outputs"]}
        self.assertIn("validation-evidence/2", produced)
        self.assertIn("validation-evidence", self.entry["produced_artifacts"])

    def test_it_declares_provenance_and_no_status(self) -> None:
        """`born proposed` stood here until `docs/adr/0018-...` removed the ladder it named."""
        behaviour = " ".join(self.entry["deterministic_behavior"])
        self.assertIn("never minted", behaviour)
        self.assertIn("never minted", behaviour)
