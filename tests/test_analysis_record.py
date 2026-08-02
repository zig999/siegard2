"""What one analysis produced that is not a construct, and the direction ambiguity resolves in.

`analysis-record/1` replaced `domain-model/4` when the constructs became files. What is left in the
record is exactly what has no file: a request is not a construct, an exclusion is the absence of one,
and an open question bears on several at once. Holding the constructs here as well would put one fact
in two places with nothing keeping them in step.

The second half of this module outlives the contract it was written beside. `foundation/0005` R24 says
ambiguity resolves in the fail-safe direction, and the risk it closes is a future capability resolving
permissively because nothing said not to. So what is asserted is that the direction stays stated — in
the prose the producer reads, and in the declaration a reader compares capabilities by. The subjects
have changed twice as capabilities came and went; the count has not.
"""

from __future__ import annotations

import json
import re
import unittest

from jsonschema import Draft202012Validator

from . import SHIPPED_ROOT, SHIPPED_SCHEMAS

SCHEMA = SHIPPED_SCHEMAS / "analysis-record.json"


def record(**over) -> dict:
    """The smallest `analysed` record the contract accepts."""
    document = {
        "contract_version": "analysis-record/1",
        "record_id": "ar_1a2b3c4d",
        "producer": "domain-modeler",
        "consumer": ["impact-analyst", "ingest-domain"],
        "request": {
            "id": "rq_7a2e4d10",
            "description": "Sales must issue proposals that expire after a bounded period.",
            "artifacts": ["intake/sales-request.md"],
        },
        "state": "analysed",
        "written": ["dm.context.sales"],
        "excluded": [{"subject": "Proposal storage", "reason": "stack knowledge"}],
    }
    document.update(over)
    return document


class Case(unittest.TestCase):
    """Helpers only; a base with its own tests would re-run them in every subclass."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def errors(self, document: dict) -> list:
        return list(self.validator.iter_errors(document))

    def assertRejected(self, document: dict, why: str) -> None:
        self.assertNotEqual([], self.errors(document), why)


class Contract(Case):
    def test_the_schema_is_itself_valid(self) -> None:
        Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))

    def test_the_smallest_record_is_accepted(self) -> None:
        self.assertEqual([], self.errors(record()))

    def test_it_holds_no_construct(self) -> None:
        """The constructs are files. A field for one here would be a second home for it."""
        properties = json.loads(SCHEMA.read_text())["properties"]
        for gone in ("subdomains", "contexts", "aggregates", "definitions",
                     "rules", "lifecycles", "interfaces", "processes"):
            with self.subTest(collection=gone):
                self.assertNotIn(gone, properties)

    def test_an_invented_field_is_rejected(self) -> None:
        self.assertRejected(record(confidence=0.9), "additionalProperties is false")

    def test_a_minted_looking_record_id_is_rejected(self) -> None:
        self.assertRejected(record(record_id="record-1"), "the caller supplies ar_ plus eight hex digits")


class WhatWasWritten(Case):
    def test_every_object_is_named_by_its_identifier(self) -> None:
        self.assertRejected(record(written=["Proposal"]),
                            "a name is not addressable; an identifier computes to a path")

    def test_an_identifier_from_the_retired_profile_is_rejected(self) -> None:
        self.assertRejected(record(written=["ko.definition.sales.proposal"]),
                            "`ko.` spelled a vocabulary that collapsed eight kinds into six")

    def test_a_scope_takes_two_segments_and_everything_else_takes_three(self) -> None:
        self.assertEqual([], self.errors(record(written=["dm.subdomain.sales"])))
        self.assertEqual([], self.errors(record(written=["dm.rule.sales.expiration"])))
        self.assertRejected(record(written=["dm.rule.expiration"]), "a rule sits in a scope")


class StateIsExclusive(Case):
    def test_blocked_requires_its_reason(self) -> None:
        self.assertRejected(record(state="blocked", written=[]),
                            "a blocked run that does not say why leaves the caller to re-run it")

    def test_a_blocking_reason_on_an_analysed_run_is_rejected(self) -> None:
        self.assertRejected(record(blocking_reason="the request was thin"),
                            "it says two things at once")

    def test_a_blocked_run_wrote_nothing(self) -> None:
        self.assertEqual([], self.errors(
            record(state="blocked", written=[], blocking_reason="the request names no domain",
                   excluded=None) | {"excluded": [{"subject": "x", "reason": "y"}]}))
        self.assertRejected(
            record(state="blocked", blocking_reason="x", written=["dm.context.sales"]),
            "a run that reached no design cannot have written an object",
        )

    def test_a_third_state_is_rejected(self) -> None:
        self.assertRejected(record(state="partial"), "the set is closed at analysed and blocked")


class AnUnreviewedRunLooksComplete(Case):
    """`foundation/0002` R6: a record with no open question and no exclusion is not complete."""

    def test_a_record_showing_neither_is_rejected(self) -> None:
        document = record()
        del document["excluded"]
        self.assertRejected(document, "every request leaves something out or something undecided")

    def test_an_open_question_alone_satisfies_it(self) -> None:
        document = record()
        del document["excluded"]
        document["open_questions"] = [{
            "id": "oq_validity_period",
            "question": "How long is a proposal valid?",
            "why_it_matters": "it is the only parameter of the expiration invariant",
        }]
        self.assertEqual([], self.errors(document))

    def test_a_question_names_the_objects_it_blocks_by_identifier(self) -> None:
        document = record(open_questions=[{
            "id": "oq_validity_period",
            "question": "How long is a proposal valid?",
            "why_it_matters": "it is the only parameter of the expiration invariant",
            "blocks": ["dm.rule.sales.expiration"],
        }])
        self.assertEqual([], self.errors(document))
        document["open_questions"][0]["blocks"] = ["Expiration"]
        self.assertRejected(document, "a gap on the object names the question, so both must address it")


class DocumentedExample(unittest.TestCase):
    """The worked result in the agent's prose is the shape a producer reproduces.

    The last two assertions are about what the example *refrains* from: it must leave a question open
    and record something excluded, because an example that resolves everything would teach that a
    complete-looking analysis is the normal outcome.
    """

    AGENT = SHIPPED_ROOT / "agents" / "domain-modeler.md"
    FENCED_JSON = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

    @classmethod
    def setUpClass(cls) -> None:
        cls.blocks = cls.FENCED_JSON.findall(cls.AGENT.read_text())

    def test_the_prose_carries_exactly_one_worked_result(self) -> None:
        self.assertEqual(1, len(self.blocks), "a second example is a second shape to imitate")

    def test_the_documented_example_conforms(self) -> None:
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        self.assertEqual([], list(validator.iter_errors(json.loads(self.blocks[0]))))

    def test_the_example_names_what_it_wrote(self) -> None:
        self.assertTrue(json.loads(self.blocks[0])["written"],
                        "a record naming no object teaches that the analysis writes nothing")

    def test_the_example_leaves_something_open(self) -> None:
        self.assertTrue(
            json.loads(self.blocks[0]).get("open_questions"),
            "an analysis that resolves everything is the failure the agent is warned about",
        )


class AmbiguityHasADirection(unittest.TestCase):
    """The rule `foundation/0005` R24 states, asserted where each capability applies it.

    The fail-safe direction is the half worth protecting: a mis-resolution must cost work, never
    coverage. `domain-modeler` defaulting to `stated` instead of `modeled` would be the inversion — it
    would claim the request said something it did not, and drop the rationale a reviewer needs.

    The subjects have moved twice: two agents were retired, and the expansion that had inherited one
    of them went with the conversion — so what refuses a construct now is the analysis itself, and the
    count of capabilities carrying the rule has not dropped.
    """

    AGENTS = SHIPPED_ROOT / "agents"
    DECLARATION = SHIPPED_ROOT / "capabilities.declaration.json"

    @classmethod
    def setUpClass(cls) -> None:
        cls.declarations = {
            d["identifier"]: d
            for d in json.loads(cls.DECLARATION.read_text())["declarations"]
        }

    def behaviour(self, identifier: str) -> str:
        return " ".join(self.declarations[identifier]["deterministic_behavior"])

    def test_the_modeller_defaults_to_modeled_not_stated(self) -> None:
        """Form 2: it must resolve to produce anything, so it takes the reading that demands review."""
        self.assertIn(
            "When you are unsure whether something was stated, it was not",
            (self.AGENTS / "domain-modeler.md").read_text(),
        )
        self.assertIn("recorded as modeled rather than stated", self.behaviour("domain-modeler"))

    def test_the_modeller_refuses_a_name_it_cannot_reduce(self) -> None:
        """Form 1: refusing is available, so it refuses instead of inventing a reduction rule."""
        self.assertIn(
            "is a refusal rather than a transliteration",
            (self.AGENTS / "domain-modeler.md").read_text(),
        )

    def test_the_enricher_reports_rather_than_correcting(self) -> None:
        """Form 1 again, one pass later: a defect it disagrees with travels as a finding."""
        self.assertIn("Report each and edit none", (self.AGENTS / "knowledge-enricher.md").read_text())
        self.assertIn("reported as a finding and never edited", self.behaviour("knowledge-enricher"))

    def test_the_ingestion_carries_an_open_question_rather_than_answering_it(self) -> None:
        self.assertIn("carried rather than answered", self.behaviour("ingest-domain"))

    def test_the_impact_analyst_invents_no_field_for_an_ambiguity(self) -> None:
        """The contract has nowhere to record one, and inventing a field would fail the boundary."""
        body = (self.AGENTS / "impact-analyst.md").read_text()
        self.assertIn("rather than inventing a field", body)
        self.assertNotIn("in `notes`", body)

    def test_the_impact_analysis_contract_has_no_notes_field(self) -> None:
        """The gap the assertion above exists because of, held so a silent addition is noticed."""
        schema = json.loads((SHIPPED_SCHEMAS / "impact-analysis.json").read_text())
        self.assertNotIn("notes", schema["properties"])
        self.assertFalse(schema["additionalProperties"])
