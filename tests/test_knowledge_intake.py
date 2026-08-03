"""The contract that carries a classification from received domain material into the ontology.

`knowledge-intake-plan/1` is the artifact `domain-analyst` produces, and the boundary between
judgment and authoring: deciding that a construct is an aggregate root is model work, and writing the
file that records the decision is not. What makes the split worth a schema is that the plan drives
control flow — a consumer reads `state` to decide whether to author at all — so it is rejected at the
boundary rather than interpreted.

Two properties get most of the attention here.

**Gaps are content, not failure.** Material arriving from analysis does not carry the retrieval
question, the declared out-of-scope, the type parameters, or the identity strategy. A plan that
reported none over such material would have invented the difference, and nothing downstream may supply
a domain fact the source did not state. So `classified` with gaps is the ordinary outcome, and the
contract must accept it rather than treat it as an error.

**The documented example is the thing that gets imitated.** An agent's prose carries a worked result,
and a model reproduces the shape it was shown. An example that does not conform teaches a shape the
boundary then rejects, so the example in `agents/domain-analyst.md` is extracted and validated here
rather than trusted.
"""

from __future__ import annotations

import json
import re
import unittest

from jsonschema import Draft202012Validator

from . import SHIPPED_ROOT, SHIPPED_SCHEMAS

SCHEMA = SHIPPED_SCHEMAS / "knowledge-intake-plan.json"
AGENT = SHIPPED_ROOT / "agents" / "domain-analyst.md"

FENCED_JSON = re.compile(r"```json\n(.*?)\n```", re.DOTALL)


def valid() -> dict:
    """The smallest plan the contract accepts, with one gap because that is the normal case."""
    return {
        "contract_version": "knowledge-intake-plan/1",
        "intake_id": "ki_4c1e7a90",
        "producer": "domain-analyst",
        "source": {
            "description": "The sales domain analysis delivered as DDD entities",
            "artifacts": ["intake/sales-entities.md"],
        },
        "state": "classified",
        "entries": [
            {
                "construct": "Proposal",
                "node_type": "definition",
                "ddd": "aggregate-root",
                "boundary": "ko.boundary.sales.proposal",
                "proposed_id": "ko.definition.sales.proposal",
                "gaps": [{"field": "question", "why": "no retrieval question is stated"}],
            }
        ],
    }


class Case(unittest.TestCase):
    """Helpers only. A base carrying its own `test_` methods would re-run them in every subclass,
    which inflates the suite's count while asserting nothing new."""

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

    def test_a_plan_with_gaps_is_accepted(self) -> None:
        """The ordinary outcome over real material, and the one a stricter contract would reject."""
        self.assertEqual([], self.errors(valid()))

    def test_a_plan_with_no_gaps_is_accepted(self) -> None:
        """Complete material is rarer, not invalid."""
        document = valid()
        document["entries"][0]["gaps"] = []
        self.assertEqual([], self.errors(document))


class ClosedFields(Case):
    def test_a_state_outside_the_closed_set_is_rejected(self) -> None:
        document = valid()
        document["state"] = "partially-classified"
        self.assertRejected(document, "the consumer branches on state, so a fourth value is not a plan")

    def test_a_seventh_node_type_is_rejected(self) -> None:
        document = valid()
        document["entries"][0]["node_type"] = "aggregate"
        self.assertRejected(document, "the ontology closes the vocabulary at six")

    def test_another_producer_is_rejected(self) -> None:
        document = valid()
        document["producer"] = "knowledge-author"
        self.assertRejected(document, "producer is a const, so a result claiming another is not an instance")

    def test_a_minted_looking_intake_id_is_rejected(self) -> None:
        document = valid()
        document["intake_id"] = "intake-1"
        self.assertRejected(document, "the caller supplies ki_ plus eight hex digits")

    def test_an_invented_field_is_rejected(self) -> None:
        document = valid()
        document["confidence"] = 0.8
        self.assertRejected(document, "additionalProperties is false, so a field the producer invented is rejected")

    def test_an_identifier_that_is_not_ontology_arithmetic_is_rejected(self) -> None:
        document = valid()
        document["entries"][0]["proposed_id"] = "Proposal"
        self.assertRejected(document, "an id must be computable from a path, and a bare name is not")


class BlockingIsExclusive(Case):
    def test_blocked_requires_its_reason(self) -> None:
        self.assertRejected(
            {
                "contract_version": "knowledge-intake-plan/1",
                "intake_id": "ki_4c1e7a90",
                "producer": "domain-analyst",
                "source": {"description": "an empty file", "artifacts": ["intake/nothing.md"]},
                "state": "blocked",
            },
            "a blocked plan that does not say why leaves the caller to re-run it to find out",
        )

    def test_a_blocking_reason_on_a_classified_plan_is_rejected(self) -> None:
        document = valid()
        document["blocking_reason"] = "the material was thin"
        self.assertRejected(document, "a blocking reason on a successful result says two things at once")

    def test_a_blocked_plan_with_its_reason_is_accepted(self) -> None:
        self.assertEqual(
            [],
            self.errors(
                {
                    "contract_version": "knowledge-intake-plan/1",
                    "intake_id": "ki_4c1e7a90",
                    "producer": "domain-analyst",
                    "source": {"description": "an empty file", "artifacts": ["intake/nothing.md"]},
                    "state": "blocked",
                    "blocking_reason": "the material names no domain construct this ontology can classify",
                }
            ),
        )

    def test_a_classified_plan_must_carry_entries_or_unmapped_constructs(self) -> None:
        document = valid()
        del document["entries"]
        self.assertRejected(document, "a classification that classified nothing is not an outcome")

    def test_unmapped_alone_is_a_classification(self) -> None:
        """Material that is entirely stack knowledge reached a decision about every construct."""
        document = valid()
        del document["entries"]
        document["unmapped"] = [
            {"construct": "ProposalRepository", "reason": "stack knowledge, excluded from the knowledge base"}
        ]
        self.assertEqual([], self.errors(document))


class Provenance(Case):
    def test_a_plan_must_name_the_material_it_read(self) -> None:
        document = valid()
        del document["source"]
        self.assertRejected(document, "an object derived from existing material records the source it came from")

    def test_a_source_naming_no_artifact_is_rejected(self) -> None:
        document = valid()
        document["source"]["artifacts"] = []
        self.assertRejected(document, "nothing states what would have to be re-read to check the classification")


class Gaps(Case):
    def test_a_gap_must_say_what_would_fill_it(self) -> None:
        document = valid()
        document["entries"][0]["gaps"] = [{"field": "question"}]
        self.assertRejected(document, "a gap that says only which field is missing leaves the reader to work out the ask")

    def test_a_gap_must_name_a_field(self) -> None:
        document = valid()
        document["entries"][0]["gaps"] = [{"why": "the material is silent"}]
        self.assertRejected(document, "a gap with no field names nothing to supply")


class DocumentedExample(unittest.TestCase):
    def test_the_agent_prose_carries_exactly_one_worked_result(self) -> None:
        blocks = FENCED_JSON.findall(AGENT.read_text())
        self.assertEqual(1, len(blocks), "a second example is a second shape to imitate")

    def test_the_documented_example_conforms(self) -> None:
        """What the prose shows is what a model reproduces."""
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        example = json.loads(FENCED_JSON.findall(AGENT.read_text())[0])
        self.assertEqual([], list(validator.iter_errors(example)))

    def test_the_example_shows_a_gap(self) -> None:
        """An example with no gap would teach that complete material is the norm; it is not."""
        example = json.loads(FENCED_JSON.findall(AGENT.read_text())[0])
        self.assertTrue(any(entry["gaps"] for entry in example["entries"]))

    def test_the_example_is_sorted_by_identifier(self) -> None:
        """The agent sorts before returning, so the example must show the order it asks for."""
        ids = [entry["proposed_id"] for entry in json.loads(FENCED_JSON.findall(AGENT.read_text())[0])["entries"]]
        self.assertEqual(sorted(ids), ids)
