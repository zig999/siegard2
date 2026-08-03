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

    def test_it_delegates_classification_before_authoring(self) -> None:
        """`domain-analyst` decides what each construct becomes; the skill does not."""
        self.assertIn("domain-analyst", self.body)
        self.assertLess(
            self.body.index("domain-analyst"),
            self.body.index("knowledge-author"),
            "classification is delegated before the first authoring",
        )

    def test_it_authors_through_the_agent_that_owns_one_object(self) -> None:
        self.assertIn("knowledge-author", self.body)

    def test_it_names_the_node_order_strategic_before_tactical(self) -> None:
        positions = [self.body.index(f"`{node}`") for node in NODE_ORDER]
        self.assertEqual(sorted(positions), positions, f"order drifted: {NODE_ORDER}")

    def test_it_refuses_to_supply_a_domain_fact(self) -> None:
        self.assertIn("You supply no domain fact", self.body)

    def test_it_does_not_answer_the_models_open_questions(self) -> None:
        """A question the modeller refused to decide is not this procedure's to decide."""
        self.assertIn("carry them, never answer\n  them", self.body)

    def test_it_does_not_reopen_a_modelling_decision(self) -> None:
        self.assertIn("Re-open a modelling decision", self.body)

    def test_it_refuses_to_promote(self) -> None:
        """Generation compiles accepted knowledge only, so promotion is the gate it must not pass."""
        self.assertIn("You do not promote", self.body)

    def test_it_says_objects_are_born_proposed(self) -> None:
        self.assertIn("proposed", self.body)

    def test_it_regenerates_projections_rather_than_writing_them(self) -> None:
        self.assertIn("Never write one by\nhand", self.body)

    def test_it_reads_the_authoring_result_rather_than_the_filesystem(self) -> None:
        """A producer's own report is what tells an authored entry from a blocked one."""
        self.assertIn("knowledge-authoring-result/1", self.body)
        self.assertIn("you read it rather than the filesystem", self.body)

    def test_it_records_what_validated(self) -> None:
        """`0001` R22: validation carries evidence, and nothing produced any until this skill did."""
        self.assertIn("validation-evidence/1", self.body)
        self.assertIn("reported as validated with nothing saying what", self.body)

    def test_it_names_the_scripts_it_runs(self) -> None:
        """C04: an installation holds nine executables and nothing else says which is which."""
        for script in ("bin/validate_knowledge.py", "bin/project_knowledge.py"):
            with self.subTest(script=script):
                self.assertIn(script, self.body)

    def test_it_reports_the_promotion_handoff(self) -> None:
        """An ingestion reported as finished sends the caller into a block nobody warned about."""
        self.assertIn("maintainer promotes them", self.body)

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

    def test_a_blocked_entry_is_not_a_stop(self) -> None:
        """One construct short of a fact must not abandon the constructs that are ready."""
        blocked = next(f for f in self.entry["failure_outcomes"] if f["outcome"] == "entry_blocked")
        self.assertIn("not a stop", blocked["reason"])

    def test_a_blocked_model_authors_nothing(self) -> None:
        blocked = next(f for f in self.entry["failure_outcomes"] if f["outcome"] == "model_blocked")
        self.assertIn("nothing authored", blocked["reason"])

    def test_it_declares_the_domain_model_as_a_contracted_prerequisite(self) -> None:
        """The order between modelling and ingesting is what a declared input makes derivable."""
        model = next(i for i in self.entry["inputs"] if i["name"] == "domain_model")
        self.assertEqual("domain-model", model["artifact"])
        self.assertEqual("domain-model/1", model["contract"])
        self.assertTrue(model["required"])

    def test_it_declares_the_ordering_guarantee(self) -> None:
        self.assertTrue(
            any("strategic before tactical" in b for b in self.entry["deterministic_behavior"]),
            "the order is the guarantee this capability's correctness rests on",
        )

    def test_it_declares_the_authoring_result_it_consumes(self) -> None:
        """The gap R24 closed on the input side, on the output side: a read that was never declared."""
        consumed = {c["artifact"] for c in self.entry["consumed_artifacts"]}
        self.assertIn("knowledge-authoring-result", consumed)

    def test_it_produces_the_validation_evidence_the_method_requires(self) -> None:
        """`validation-evidence/1` was the one contract with neither a producer nor a consumer."""
        produced = {o["contract"] for o in self.entry["outputs"]}
        self.assertIn("validation-evidence/1", produced)
        self.assertIn("validation-evidence", self.entry["produced_artifacts"])

    def test_it_declares_provenance_and_the_proposed_birth(self) -> None:
        behaviour = " ".join(self.entry["deterministic_behavior"])
        self.assertIn("born proposed", behaviour)
        self.assertIn("records the request the model answers", behaviour)
