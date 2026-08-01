"""The modelling entry point, and the reason it stops.

`model-domain` produces a domain model and returns. Two entry points rather than one was a deliberate
choice, and the property that decided it is asserted here: the model is the artifact a person reads before
any knowledge object exists. Running modelling and authoring together would write objects from open
questions nobody answered, and each unanswered question becomes a blocked entry discovered a step late.

So what these tests hold is the boundary, not the prose. The skill must delegate the analysis and not
perform it; it must not write knowledge; it must not answer what the modeller refused to answer; and it must
hand the caller the three things a review needs — what was decided, what was refused, what was excluded.

The pair with `tests/test_ingest_domain.py` is the point. That suite asserts the receiving side declares the
model as a contracted prerequisite, which is what makes the order between the two derivable from the
declarations rather than from a sequence anything enforces.
"""

from __future__ import annotations

import json
import unittest

from . import SHIPPED_ROOT

SKILL = SHIPPED_ROOT / "skills" / "model-domain" / "SKILL.md"
INGEST = SHIPPED_ROOT / "skills" / "ingest-domain" / "SKILL.md"
DECLARATION = SHIPPED_ROOT / "capabilities.declaration.json"


class Procedure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SKILL.read_text()

    def test_it_delegates_the_analysis(self) -> None:
        """The skill runs the procedure; the agent does the modelling."""
        self.assertIn("domain-modeler", self.body)

    def test_it_stops_before_authoring(self) -> None:
        """The stop is the procedure. A skill that also authored would remove the review point."""
        self.assertIn("Stopping is the procedure", self.body)

    def test_it_writes_no_knowledge_object(self) -> None:
        self.assertIn("You do not author knowledge", self.body)

    def test_it_does_not_answer_the_open_questions(self) -> None:
        """A question answered by whoever ran this is a domain fact invented by the framework."""
        self.assertIn("You do not answer the model's open questions", self.body)

    def test_it_names_the_next_entry_point(self) -> None:
        """A procedure that stops without saying what follows leaves the caller to guess."""
        self.assertIn("ingest-domain", self.body)

    def test_it_reports_what_was_decided_refused_and_excluded(self) -> None:
        """The three things a reviewer needs, none of which the model surfaces on its own."""
        for phrase in ("what was decided rather than stated", "what was refused", "what was excluded"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.body)

    def test_it_rejects_a_failing_model_rather_than_repairing_it(self) -> None:
        """A patched design is a design nobody produced, and its origin fields would then be lying."""
        self.assertIn("rejected,\nnever repaired", self.body)

    def test_it_is_not_model_invocable(self) -> None:
        self.assertIn("disable-model-invocation: true", self.body)


class TwoEntryPoints(unittest.TestCase):
    """The split, asserted from both sides.

    A single skill would satisfy every test above and lose the property they exist for. What makes the
    boundary real is that the receiving procedure requires the model as a contracted input — so the order
    is derivable from the declarations, and neither skill contains the other's procedure.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.declarations = json.loads(DECLARATION.read_text())["declarations"]
        cls.model = next(d for d in cls.declarations if d["identifier"] == "model-domain")
        cls.ingest = next(d for d in cls.declarations if d["identifier"] == "ingest-domain")

    def test_modelling_produces_what_ingestion_requires(self) -> None:
        produced = {o["contract"] for o in self.model["outputs"]}
        required = {i.get("contract") for i in self.ingest["inputs"]}
        self.assertIn("domain-model/1", produced & required)

    def test_modelling_authors_nothing(self) -> None:
        self.assertNotIn("knowledge-object", self.model.get("produced_artifacts", []))

    def test_ingestion_does_not_model(self) -> None:
        """The classifying and authoring procedure must not carry the modelling agent."""
        self.assertNotIn("domain-modeler", INGEST.read_text())

    def test_neither_skill_answers_an_open_question(self) -> None:
        for path in (SKILL, INGEST):
            with self.subTest(skill=path.name):
                self.assertIn("open question", path.read_text())

    def test_modelling_declares_it_writes_no_knowledge(self) -> None:
        behaviour = " ".join(self.model["deterministic_behavior"])
        self.assertIn("no file under the knowledge root is written", behaviour)

    def test_a_blocked_analysis_is_a_result_and_not_an_error(self) -> None:
        """A request that describes no domain is a finished run with a negative result."""
        blocked = next(
            f for f in self.model["failure_outcomes"] if f["outcome"] == "no_domain_in_request"
        )
        self.assertIn("negative result", blocked["reason"])
