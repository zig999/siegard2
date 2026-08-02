"""The profile the analysis writes in: eight kinds, 1:1 with the vocabulary it records.

The conversion that mapped eight DDD kinds onto six node types is gone. Three of those collapses were reversible through `ddd`; two were
not — a subdomain became a field of a boundary and a context relationship became an entry in a list —
so neither survived as something an identifier could reach.

What is asserted here is what the profile decides and what it refuses to decide. The envelope is not
its business: `tests/test_notation_agreement.py` holds that, and this file would be asserting the same
fact twice if it repeated one field of it.

Two properties carry most of the weight.

**A kind is not a shape chosen to make the base checkable.** So `subdomain`, `context`, `aggregate`
and `lifecycle` carry no `ddd` — the kind is the construct — while `definition`, `rule`, `interface`
and `process` do, because each covers several.

**Nothing records which pass has run.** An object with an open `kind: authoring` gap is one the
enrichment has not reached, and that is the whole of it: the three fields no analysis carries are
required of an object that declares no such gap, and excused of one that does. A field saying the
same thing would be a second home for it, and `foundation/0001` R11 forbids the state it would name.
"""

from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from . import SHIPPED_SCHEMAS

SCHEMA = SHIPPED_SCHEMAS / "domain-object.json"

KINDS = ("subdomain", "context", "aggregate", "definition", "rule",
         "lifecycle", "interface", "process")
CARRY_DDD = ("definition", "rule", "interface", "process")
ARE_THE_CONSTRUCT = ("subdomain", "context", "aggregate", "lifecycle")

ENVELOPE = {
    "contract_version": "domain-object/1",
    "generated": {"by": "domain-modeler", "at": "2026-08-02T10:00:00Z"},
    "origin": "stated",
    "description": "One sentence.",
    "question": "What is it?",
    "out_of_scope": ["How it is stored."],
}

COMPLETE = {
    "subdomain": {"id": "dm.subdomain.sales", "type": "subdomain", "title": "Sales",
                  "subdomain_type": "core"},
    "context": {"id": "dm.context.sales", "type": "context", "title": "Sales",
                "subdomain": "dm.subdomain.sales"},
    "aggregate": {"id": "dm.aggregate.sales.proposal", "type": "aggregate", "title": "Proposal",
                  "boundary": "dm.context.sales", "root": "dm.definition.sales.proposal"},
    "definition": {"id": "dm.definition.sales.proposal", "type": "definition", "title": "Proposal",
                   "boundary": "dm.aggregate.sales.proposal", "ddd": "aggregate-root",
                   "attributes": [{"name": "number", "type": "string", "max_length": 30,
                                   "required": True}],
                   "identity": {"attributes": ["number"]}},
    "rule": {"id": "dm.rule.sales.proposal-expiration", "type": "rule", "title": "Proposal expiration",
             "boundary": "dm.context.sales", "ddd": "invariant",
             "statement": "A proposal MUST NOT be accepted after its validity period has passed.",
             "expression": "proposal.accepted_at <= proposal.valid_until"},
    "lifecycle": {"id": "dm.lifecycle.sales.proposal", "type": "lifecycle", "title": "Proposal lifecycle",
                  "boundary": "dm.context.sales", "subject": "dm.definition.sales.proposal",
                  "states": ["draft", "issued"], "initial": "draft",
                  "transitions": [{"from": "draft", "trigger": "issue", "to": "issued"}],
                  "rejections": [{"from": "issued", "trigger": "issue",
                                  "error": "dm.definition.sales.already-issued"}]},
    "interface": {"id": "dm.interface.sales.proposal-accepted", "type": "interface",
                  "title": "Proposal accepted", "boundary": "dm.context.sales", "ddd": "domain-event",
                  "version": "1", "schema": "events/proposal-accepted.json", "ownership": "published"},
    "process": {"id": "dm.process.sales.issue-proposal", "type": "process", "title": "Issue proposal",
                "boundary": "dm.context.sales", "ddd": "use-case",
                "steps": [{"ko": "dm.definition.sales.proposal"}]},
}


def obj(kind: str, **over) -> dict:
    return {**ENVELOPE, **COMPLETE[kind], **over}


class Case(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def errors(self, document: dict) -> list:
        return list(self.validator.iter_errors(document))

    def assertAccepted(self, document: dict, why: str = "") -> None:
        found = self.errors(document)
        self.assertEqual([], found, why or (found[0].message if found else ""))

    def assertRefused(self, document: dict, why: str) -> None:
        self.assertNotEqual([], self.errors(document), why)


class TheVocabulary(Case):
    def test_the_schema_is_itself_valid(self) -> None:
        Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))

    def test_it_is_closed_at_the_eight_kinds_the_analysis_records(self) -> None:
        declared = json.loads(SCHEMA.read_text())["properties"]["type"]["enum"]
        self.assertEqual(sorted(KINDS), sorted(declared))

    def test_every_kind_has_a_complete_form_the_contract_accepts(self) -> None:
        for kind in KINDS:
            with self.subTest(kind=kind):
                self.assertAccepted(obj(kind))

    def test_a_ninth_kind_is_refused(self) -> None:
        self.assertRefused(obj("rule", type="policy"),
                           "a construct with no kind is not recorded until the vocabulary names one")


class TheKindIsTheConstruct(Case):
    """Where a kind covers one construct, naming it twice is naming it twice."""

    def test_the_four_that_are_their_own_construct_refuse_a_ddd(self) -> None:
        for kind in ARE_THE_CONSTRUCT:
            with self.subTest(kind=kind):
                self.assertRefused(obj(kind, ddd=kind), "the kind already says which construct it is")

    def test_the_four_that_cover_several_require_one(self) -> None:
        for kind in CARRY_DDD:
            document = obj(kind)
            del document["ddd"]
            with self.subTest(kind=kind):
                self.assertRefused(document, "an entity and a value object are not the same fact")

    def test_a_scope_belongs_to_no_scope(self) -> None:
        for kind in ("subdomain", "context"):
            with self.subTest(kind=kind):
                self.assertRefused(obj(kind, boundary="dm.context.other"),
                                   "the absence of a boundary is what identifies a partition root")

    def test_everything_else_declares_the_one_scope_it_belongs_to(self) -> None:
        for kind in ("aggregate", "definition", "rule", "lifecycle", "interface", "process"):
            document = obj(kind)
            del document["boundary"]
            with self.subTest(kind=kind):
                self.assertRefused(document, "membership is derived from this field")


class Identity(Case):
    def test_a_scope_takes_two_segments_and_everything_else_takes_three(self) -> None:
        self.assertRefused(obj("subdomain", id="dm.subdomain.sales.extra"), "a subdomain is a scope")
        self.assertRefused(obj("rule", id="dm.rule.proposal-expiration"), "a rule sits in a scope")

    def test_an_identifier_from_the_retired_profile_is_refused(self) -> None:
        """`ko.` named the vocabulary that collapsed eight kinds into six."""
        self.assertRefused(obj("definition", id="ko.definition.sales.proposal"),
                           "the prefix names which vocabulary spells the kinds")

    def test_a_boundary_names_a_context_or_an_aggregate_and_nothing_else(self) -> None:
        self.assertAccepted(obj("rule", boundary="dm.context.sales"))
        self.assertAccepted(obj("definition", boundary="dm.aggregate.sales.proposal"))
        self.assertRefused(obj("rule", boundary="dm.subdomain.sales"),
                           "a subdomain partitions the problem, and holds no object")


class RationaleTravelsWithTheDecision(Case):
    """`foundation/0003` R4 forbade it while the analysis lived elsewhere. It no longer does."""

    def test_a_decided_fact_carries_the_reason_it_was_decided(self) -> None:
        self.assertRefused(obj("subdomain", origin="modeled"),
                           "a reviewer disagrees with a decision, and needs the reason to do it")

    def test_a_decided_fact_with_its_reason_is_accepted(self) -> None:
        self.assertAccepted(obj("subdomain", origin="modeled",
                                rationale="the request is entirely about how this business wins work"))

    def test_a_stated_fact_owes_none(self) -> None:
        """The material is the reason; repeating it would be prose written to satisfy a validator."""
        self.assertAccepted(obj("subdomain"))
        self.assertNotIn("rationale", obj("subdomain"))


class StagedIsDerivedAndNeverStored(Case):
    """The whole of item 5, expressed as a conditional rather than as a field.

    An open `kind: authoring` gap says the enrichment has not reached this object. That is the same
    fact a `staged` flag would carry, and two homes for one fact can disagree — which is why
    an object's own gaps are its incompleteness: there is no flag to set and none to forget.
    """

    def unenriched(self, kind: str = "subdomain") -> dict:
        document = obj(kind, gaps=[{"kind": "authoring", "field": "question"}])
        for field in ("question", "description", "out_of_scope"):
            document.pop(field)
        return document

    def test_an_object_declaring_no_authoring_gap_owes_all_three(self) -> None:
        document = obj("subdomain")
        del document["question"]
        self.assertRefused(document, "an object that claims to be finished answers a question")

    def test_an_object_carrying_one_is_excused(self) -> None:
        self.assertAccepted(self.unenriched())

    def test_a_domain_gap_does_not_excuse_them(self) -> None:
        """A fact the domain owes says nothing about whether a pass of this framework has run."""
        document = self.unenriched()
        document["gaps"] = [{"kind": "domain", "field": "subdomain_type", "why": "unclassified"}]
        self.assertRefused(document, "the two kinds of gap are answered by different people")

    def test_the_contract_carries_no_field_naming_the_state(self) -> None:
        properties = json.loads(SCHEMA.read_text())["properties"]
        for named in ("staged", "status", "maturity", "approved"):
            with self.subTest(field=named):
                self.assertNotEqual({"type": "string"}, properties.get(named))
        self.assertEqual({"not": {}}, {k: v for k, v in properties["status"].items() if k == "not"})


class GapsStandInForWhatIsMissing(Case):
    def test_a_kind_short_of_a_required_fact_may_declare_it_instead(self) -> None:
        document = obj("subdomain", gaps=[{"kind": "domain", "field": "subdomain_type",
                                           "why": "the request classifies no subdomain"}])
        del document["subdomain_type"]
        self.assertAccepted(document)

    def test_a_gap_does_not_make_a_forbidden_field_allowed(self) -> None:
        self.assertRefused(
            obj("context", boundary="dm.context.other",
                gaps=[{"kind": "domain", "field": "subdomain", "why": "unstated"}]),
            "a gap says a fact is absent; it cannot say a prohibition does not apply",
        )

    def test_an_identified_definition_declares_how_it_is_identified(self) -> None:
        document = obj("definition")
        del document["identity"]
        self.assertRefused(document, "an aggregate root has an identity that persists through change")

    def test_a_value_object_declares_none(self) -> None:
        document = obj("definition", ddd="value-object")
        del document["identity"]
        self.assertAccepted(document, "a value object is defined entirely by its attributes")

    def test_a_rule_declares_an_expression_or_examples(self) -> None:
        document = obj("rule")
        del document["expression"]
        self.assertRefused(document, "a rule with neither cannot become a test")
        document["examples"] = [{
            "given": {"valid_until": "2026-01-31"},
            "when": {"accepted_at": "2026-02-01"},
            "then": {"refused": True},
        }]
        self.assertAccepted(document)
