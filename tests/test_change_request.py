"""The contract the method required for as long as it deferred it.

`foundation/0001` R1 makes a change request originate every change and states that a change with no request
is work outside the framework. The same document deferred its schema, and the deferral held until
`foundation/0007` R24 required a prerequisite to be declared with its contract version: three capabilities
declared `change-request` as an input artifact with no contract, and could not satisfy R24 because there was
nothing to name. That is what this contract closes, and the tests below hold the two properties that
motivated its shape.

**The body stays prose.** `foundation/0005` R16a says an artifact that only explains something to a reader
takes prose, and a schema around it is ceremony. So `statement` is a string and nothing parses it — what the
contract adds is identity, provenance, and the one field a predicate reads.

**`type` is two values, not a taxonomy.** Exactly one escalation predicate reads it. A third value would be
a distinction nothing consumes, which is the speculative generalization this repository refuses. The test
that pins the vocabulary at two is therefore asserting a decision, not an implementation detail — it fails
if someone widens it without a predicate to justify the widening.
"""

from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from . import SHIPPED_ROOT, SHIPPED_SCHEMAS

SCHEMA = SHIPPED_SCHEMAS / "change-request.json"
DECLARATION = SHIPPED_ROOT / "capabilities.declaration.json"


def request(**over) -> dict:
    document = {
        "contract_version": "change-request/1",
        "request_id": "cr_7a2e4d10",
        "type": "ordinary",
        "requested_by": "the sales team lead",
        "requested_at": "2026-08-01T09:00:00Z",
        "statement": "Sales must issue priced proposals that stop being acceptable after a bounded period.",
        "artifacts": ["intake/sales-request.md"],
    }
    document.update(over)
    return document


class Case(unittest.TestCase):
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

    def test_the_smallest_request_is_accepted(self) -> None:
        self.assertEqual([], self.errors(request()))

    def test_an_invented_field_is_rejected(self) -> None:
        self.assertRejected(request(priority="high"), "additionalProperties is false")

    def test_every_required_field_is_required(self) -> None:
        for field in ("request_id", "type", "requested_by", "requested_at", "statement", "artifacts"):
            with self.subTest(field=field):
                document = request()
                del document[field]
                self.assertRejected(document, f"{field} is required")

    def test_an_identifier_of_the_wrong_shape_is_rejected(self) -> None:
        """Six other contracts carry a field of this shape referring to it."""
        self.assertRejected(request(request_id="request-1"), "cr_ plus eight hex digits")


class TypeIsTwoValues(Case):
    """The vocabulary is a decision, and this is where widening it becomes visible."""

    def test_both_values_are_accepted(self) -> None:
        for value in ("ordinary", "regulatory"):
            with self.subTest(type=value):
                self.assertEqual([], self.errors(request(type=value)))

    def test_a_third_value_is_rejected(self) -> None:
        self.assertRejected(request(type="feature"), "a value nothing reads is a distinction nothing consumes")

    def test_regulatory_is_present_because_a_predicate_reads_it(self) -> None:
        """`foundation/0001`'s escalation table triggers on this exact value."""
        schema = json.loads(SCHEMA.read_text())
        self.assertIn("regulatory", schema["properties"]["type"]["enum"])

    def test_the_vocabulary_is_exactly_two(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(2, len(schema["properties"]["type"]["enum"]), "widening needs a predicate first")


class WhatItSeparates(Case):
    """A constraint binds the solution; a statement describes the problem."""

    def test_a_constraint_is_optional_and_non_empty_when_present(self) -> None:
        self.assertEqual([], self.errors(request(constraints=["must keep the v1 API working"])))
        self.assertRejected(request(constraints=[]), "an empty array asserts a search rather than a finding")

    def test_out_of_scope_is_optional_here_and_required_of_a_knowledge_object(self) -> None:
        """The asymmetry is deliberate: a request's silence is answered by an open question."""
        self.assertEqual([], self.errors(request(out_of_scope=["renewal after expiry"])))
        knowledge_object = json.loads((SHIPPED_SCHEMAS / "knowledge-object.json").read_text())
        self.assertIn("out_of_scope", knowledge_object["required"])
        self.assertNotIn("out_of_scope", json.loads(SCHEMA.read_text())["required"])

    def test_the_statement_is_prose_that_nothing_parses(self) -> None:
        statement = json.loads(SCHEMA.read_text())["properties"]["statement"]
        self.assertEqual("string", statement["type"])
        self.assertNotIn("pattern", statement)

    def test_an_artifact_must_be_named(self) -> None:
        self.assertRejected(request(artifacts=[]), "a request nobody can re-read cannot be checked against")


class ItClosesTheDeclarationGap(unittest.TestCase):
    """R24: every artifact that must exist before a capability runs is declared with its contract version.

    Five capabilities take a change request. Three declared the artifact with no contract and two did not
    name the artifact at all, because there was nothing to name. This is the assertion that the gap stays
    closed — a new capability taking a request and skipping the contract fails here.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.declarations = json.loads(DECLARATION.read_text())["declarations"]

    def takers(self) -> list[tuple[str, dict]]:
        return [
            (d["identifier"], i)
            for d in self.declarations
            for i in d.get("inputs", [])
            if i.get("artifact") == "change-request"
        ]

    def test_five_capabilities_declare_it(self) -> None:
        self.assertEqual(
            {"impact-analyst", "root-selector", "spec-delta-author", "domain-modeler", "model-domain"},
            {name for name, _ in self.takers()},
        )

    def test_every_taker_names_the_contract_version(self) -> None:
        for name, declared in self.takers():
            with self.subTest(capability=name):
                self.assertEqual("change-request/1", declared.get("contract"))

    def test_no_capability_takes_a_request_without_naming_the_artifact(self) -> None:
        """The other half of the gap: an input called `request` that declares no artifact."""
        loose = [
            (d["identifier"], i["name"])
            for d in self.declarations
            for i in d.get("inputs", [])
            if i["name"] in ("request", "change_request") and "artifact" not in i
        ]
        self.assertEqual([], loose)
