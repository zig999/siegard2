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
import re
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
        self.assertIn("You do not write the four fields only judgment supplies", self.body)

    def test_it_does_not_answer_the_open_questions(self) -> None:
        """A question answered by whoever ran this is a domain fact invented by the framework."""
        self.assertIn("You do not answer the analysis's open questions", self.body)

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
        self.assertIn("rejected, never\nrepaired", self.body)

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
        """Asserted as an overlap rather than by naming one artifact, so the order survives a
        change in which artifact carries it — as it did when the seal replaced the model."""
        produced = {o["contract"] for o in self.model["outputs"]}
        required = {i.get("contract") for i in self.ingest["inputs"]}
        self.assertTrue(produced & required, "nothing the second entry point needs is produced here")
        self.assertIn("analysis-seal/1", produced & required)

    def test_modelling_writes_the_objects(self) -> None:
        """It used to author nothing, and the conversion that stood between it and the base is gone."""
        self.assertIn("domain-object", self.model.get("produced_artifacts", []))

    def test_ingestion_does_not_model(self) -> None:
        """The classifying and authoring procedure must not carry the modelling agent."""
        self.assertNotIn("domain-modeler", INGEST.read_text())

    def test_neither_skill_answers_an_open_question(self) -> None:
        for path in (SKILL, INGEST):
            with self.subTest(skill=path.name):
                self.assertIn("open question", path.read_text())

    def test_modelling_declares_where_it_writes(self) -> None:
        behaviour = " ".join(self.model["deterministic_behavior"])
        self.assertIn("every object is written under the knowledge root", behaviour)

    def test_a_blocked_analysis_is_a_result_and_not_an_error(self) -> None:
        """A request that describes no domain is a finished run with a negative result."""
        blocked = next(
            f for f in self.model["failure_outcomes"] if f["outcome"] == "no_domain_in_request"
        )
        self.assertIn("negative result", blocked["reason"])

class ThePassEndsAtTheReview(unittest.TestCase):
    """Pass 1 produces the staging tree and stops, which is where the review sits.

    It produced only the model and left the expansion to the next entry point, so the run that a
    person was meant to review ended before there was anything to review. The correction is
    structural rather than procedural: `foundation/0004` R2 says the framework ships nothing that
    decides what runs next or records where a run stands, so a "stop here" written into the middle
    of a procedure is a claim about sequence that nothing enforces. A procedure that *ends* has
    stopped whether or not anyone honours it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.body = SKILL.read_text()
        cls.ingest = INGEST.read_text()
        declarations = {e["identifier"]: e
                        for e in json.loads(DECLARATION.read_text())["declarations"]}
        cls.model = declarations["model-domain"]
        cls.entry = declarations["ingest-domain"]

    def test_it_checks_what_the_analysis_wrote(self) -> None:
        self.assertIn("bin/check_knowledge.py", self.body)

    def test_it_runs_the_impact_analysis_before_the_checks(self) -> None:
        """`foundation/0001` R3 runs one for every request, and it informs what the diff shows.

        It used to run before anything was written and now runs after, because the analysis writes as
        it goes — so a verdict of `none` asks for a discard rather than preventing a write. The skill
        says so rather than leaving a reader to notice.
        """
        self.assertIn("impact-analyst", self.body)
        self.assertIn("asks for a discard rather", self.body)
        self.assertLess(self.body.index("impact-analyst"), self.body.index("bin/check_knowledge.py"))

    def test_it_runs_over_an_empty_base_too(self) -> None:
        self.assertIn("including the first one against an empty base", self.body)

    def test_it_produces_what_the_next_entry_point_requires(self) -> None:
        """The order between the two is derivable from the declarations rather than from prose."""
        produced = {o["artifact"] for o in self.model["outputs"]}
        required = {i.get("artifact") for i in self.entry["inputs"]}
        self.assertIn("analysis-seal", produced & required)

    def test_it_enriches_nothing_and_materializes_nothing(self) -> None:
        for owned in ("knowledge-enricher", "materialize.py"):
            with self.subTest(step=owned):
                self.assertNotIn(owned, self.body)

    def test_the_next_entry_point_writes_no_object(self) -> None:
        self.assertNotIn("domain-modeler", self.ingest)

    def test_the_stop_is_the_end_of_the_run(self) -> None:
        """Not a step in the middle: the last thing the procedure says is that it is over.

        Matched on the heading rather than its number, so adding a step before it moves the step
        and not this assertion — what is asserted is that the run ends, never where.
        """
        steps = [line for line in self.body.splitlines() if re.match(r"^### \d+\. ", line)]
        self.assertTrue(steps, "the procedure numbers its steps")
        self.assertRegex(steps[-1], r"^### \d+\. Stop$")
        self.assertLess(self.body.index(steps[-1]), self.body.index("## What you never do"))

    def test_it_writes_the_objects_where_they_are_read(self) -> None:
        """No staging tree: a schema cannot see a directory, so the boundary was never one."""
        behaviour = " ".join(self.model["deterministic_behavior"])
        self.assertIn("every object is written under the knowledge root", behaviour)
        self.assertNotIn("staging", behaviour)

    def test_a_verdict_of_none_ends_it(self) -> None:
        outcomes = {f["outcome"] for f in self.model["failure_outcomes"]}
        self.assertIn("already_held", outcomes)


if __name__ == "__main__":
    unittest.main()
