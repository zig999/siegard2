"""The DDD analysis contract, and the one field the whole thing turns on.

`domain-model/1` is the artifact produced by analysing a request, before anything is normalized into the
ontology. It is the one artifact in this framework whose content is *invented*: everywhere else a fact
nobody stated is the defect, and here deciding the aggregates, the boundaries, and the invariants is the
work.

That is why `origin` gets most of the attention below. A reviewer disagrees with a decision and accepts a
requirement, and can do neither if the two look alike — so `modeled` demands a rationale and the check is
asserted on every element kind rather than on one. A contract that enforced it for subdomains and forgot
it for rules would be the shape that lets a guessed invariant read as a stated one.

The two vocabularies this contract deliberately does not re-encode are asserted too, in the direction that
catches something: a value wrong for its element kind is *accepted* here, because the per-node-type sets
and the primitive type system belong to `knowledge-object.json`. Those tests exist so the omission stays a
recorded decision rather than becoming a defect someone repairs by adding a second authority.
"""

from __future__ import annotations

import json
import re
import unittest

from jsonschema import Draft202012Validator

from . import SHIPPED_ROOT, SHIPPED_SCHEMAS

SCHEMA = SHIPPED_SCHEMAS / "domain-model.json"

# Every element kind that carries provenance, with the smallest instance the contract accepts.
ELEMENTS = {
    "subdomains": {"name": "Sales", "type": "core"},
    "contexts": {"name": "Sales", "subdomain": "Sales"},
    "aggregates": {"name": "Proposal", "context": "Sales", "root": "Proposal"},
    "definitions": {"name": "Proposal", "context": "Sales", "ddd": "aggregate-root", "attributes": []},
    "rules": {"name": "Expiration", "context": "Sales", "ddd": "invariant", "statement": "A proposal expires."},
    "lifecycles": {
        "subject": "Proposal", "context": "Sales", "states": ["draft"], "initial": "draft",
        "transitions": [{"from": "draft", "trigger": "issue", "to": "issued"}],
    },
    "interfaces": {"name": "ContractSigned", "context": "Sales", "ddd": "domain-event", "ownership": "published"},
    "processes": {
        "name": "Approval", "context": "Sales", "ddd": "use-case",
        "steps": [{"order": 1, "element": "Proposal"}],
    },
}


def model(**over) -> dict:
    """The smallest `modeled` analysis the contract accepts."""
    document = {
        "contract_version": "domain-model/1",
        "model_id": "dm_1a2b3c4d",
        "producer": "domain-modeler",
        "request": {
            "id": "cr_7a2e4d10",
            "description": "Sales must issue proposals that expire after a bounded period.",
            "artifacts": ["intake/sales-request.md"],
        },
        "state": "modeled",
        "subdomains": [dict(ELEMENTS["subdomains"], origin="stated")],
        "contexts": [dict(ELEMENTS["contexts"], origin="stated")],
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

    def test_the_smallest_analysis_is_accepted(self) -> None:
        self.assertEqual([], self.errors(model()))

    def test_a_full_analysis_is_accepted(self) -> None:
        """Every element kind at once, so the $defs are exercised together."""
        self.assertEqual(
            [],
            self.errors(model(**{kind: [dict(body, origin="stated")] for kind, body in ELEMENTS.items()})),
        )

    def test_an_invented_field_is_rejected(self) -> None:
        self.assertRejected(model(confidence=0.9), "additionalProperties is false")

    def test_a_minted_looking_model_id_is_rejected(self) -> None:
        self.assertRejected(model(model_id="model-1"), "the caller supplies dm_ plus eight hex digits")


class Provenance(Case):
    """`origin` and the rationale it demands — the field the contract exists for."""

    def test_every_element_kind_demands_a_rationale_when_modeled(self) -> None:
        for kind, body in ELEMENTS.items():
            with self.subTest(element=kind):
                self.assertRejected(
                    model(**{kind: [dict(body, origin="modeled")]}),
                    f"{kind}: a decision with no reasoning is indistinguishable from a guess",
                )

    def test_every_element_kind_accepts_a_modeled_element_with_its_rationale(self) -> None:
        """Otherwise the test above could be passing because `modeled` is rejected outright."""
        for kind, body in ELEMENTS.items():
            with self.subTest(element=kind):
                document = model(**{kind: [dict(body, origin="modeled", rationale="the request implies it")]})
                self.assertEqual([], self.errors(document), kind)

    def test_a_stated_element_needs_no_rationale(self) -> None:
        for kind, body in ELEMENTS.items():
            with self.subTest(element=kind):
                self.assertEqual([], self.errors(model(**{kind: [dict(body, origin="stated")]})), kind)

    def test_origin_is_required(self) -> None:
        for kind, body in ELEMENTS.items():
            with self.subTest(element=kind):
                self.assertRejected(
                    model(**{kind: [dict(body)]}),
                    f"{kind}: an element with no origin says nothing about whether it was decided",
                )

    def test_a_third_origin_is_rejected(self) -> None:
        self.assertRejected(
            model(subdomains=[dict(ELEMENTS["subdomains"], origin="inferred")]),
            "the set is closed at stated and modeled",
        )


class StateIsExclusive(Case):
    def test_blocked_requires_its_reason(self) -> None:
        self.assertRejected(
            {
                "contract_version": "domain-model/1",
                "model_id": "dm_1a2b3c4d",
                "producer": "domain-modeler",
                "request": {"id": "cr_7a2e4d10", "description": "x", "artifacts": ["a.md"]},
                "state": "blocked",
            },
            "a blocked analysis that does not say why leaves the caller to re-run it",
        )

    def test_a_blocking_reason_on_a_modeled_analysis_is_rejected(self) -> None:
        self.assertRejected(model(blocking_reason="the request was thin"), "it says two things at once")

    def test_a_blocked_analysis_carries_no_elements(self) -> None:
        self.assertEqual(
            [],
            self.errors(
                {
                    "contract_version": "domain-model/1",
                    "model_id": "dm_1a2b3c4d",
                    "producer": "domain-modeler",
                    "request": {"id": "cr_7a2e4d10", "description": "x", "artifacts": ["a.md"]},
                    "state": "blocked",
                    "blocking_reason": "the request names no domain this ontology can model",
                }
            ),
        )

    def test_a_modeled_analysis_must_reach_a_subdomain_and_a_context(self) -> None:
        """Strategic before tactical: a model that drew no context did not reach a design."""
        for missing in ("subdomains", "contexts"):
            with self.subTest(missing=missing):
                document = model()
                del document[missing]
                self.assertRejected(document, f"{missing} is what the rest of the model hangs from")

    def test_a_third_state_is_rejected(self) -> None:
        self.assertRejected(model(state="partial"), "the consumer branches on state")


class OneAuthorityPerVocabulary(Case):
    """What this contract deliberately does not re-encode, asserted so the omission stays a decision.

    Adding either vocabulary here would be a second copy of something `knowledge-object.json` already
    holds — and the per-node-type `ddd` sets have changed once already. These tests fail if someone
    closes the enum, which is the point: the repair for a wrong value is at authoring, not here.
    """

    def test_a_ddd_value_wrong_for_its_element_kind_is_accepted(self) -> None:
        document = model(definitions=[dict(ELEMENTS["definitions"], ddd="aggregate", origin="stated")])
        self.assertEqual([], self.errors(document), "`aggregate` is a boundary, and this contract does not know that")

    def test_a_free_text_attribute_type_is_accepted(self) -> None:
        attribute = {"name": "issued_at", "type": "Date", "required": True}
        document = model(definitions=[dict(ELEMENTS["definitions"], attributes=[attribute], origin="stated")])
        self.assertEqual([], self.errors(document), "the closed primitive vocabulary lives in the ontology contract")

    def test_a_ddd_value_that_is_not_an_identifier_is_still_rejected(self) -> None:
        """Not closed is not unconstrained: the shape still has to be a value the ontology could carry."""
        self.assertRejected(
            model(definitions=[dict(ELEMENTS["definitions"], ddd="Aggregate Root", origin="stated")]),
            "kebab-case is the form every ddd value takes",
        )


class RefusingIsPartOfModelling(Case):
    def test_an_open_question_must_say_what_the_answer_would_change(self) -> None:
        self.assertRejected(
            model(open_questions=[{"question": "May an order be partly cancelled?"}]),
            "a question with no stated consequence cannot be prioritized",
        )

    def test_an_open_question_with_its_consequence_is_accepted(self) -> None:
        document = model(
            open_questions=[
                {
                    "question": "May an order be partly cancelled?",
                    "why_it_matters": "it decides whether cancellation is a state or a per-item flag",
                    "blocks": ["Order"],
                }
            ]
        )
        self.assertEqual([], self.errors(document))

    def test_an_exclusion_must_carry_its_reason(self) -> None:
        self.assertRejected(model(excluded=[{"subject": "ProposalRepository"}]), "absence needs a reason")

    def test_an_exclusion_with_its_reason_is_accepted(self) -> None:
        document = model(excluded=[{"subject": "ProposalRepository", "reason": "stack knowledge"}])
        self.assertEqual([], self.errors(document))


class DocumentedExample(unittest.TestCase):
    """The worked result in the agent's prose is the shape a model reproduces.

    An example that does not conform teaches a shape the boundary then rejects. The last two assertions
    are about what the example *refrains* from: it must show a decision with its reasoning and a gap left
    open, because an example where everything is `stated` and nothing is unresolved would teach that a
    complete-looking model is the normal outcome.
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

    def test_the_example_shows_a_decision_with_its_reasoning(self) -> None:
        example = json.loads(self.blocks[0])
        modeled = [
            element
            for kind in ELEMENTS
            for element in example.get(kind, [])
            if element.get("origin") == "modeled"
        ]
        self.assertTrue(modeled, "an example with nothing modeled teaches that nothing is ever decided")
        self.assertTrue(all(e.get("rationale") for e in modeled))

    def test_the_example_leaves_something_open(self) -> None:
        self.assertTrue(
            json.loads(self.blocks[0]).get("open_questions"),
            "a model that resolves everything is the failure the agent is warned about",
        )
