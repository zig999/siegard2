"""The four repairs building the evidence forced on foundation/0003, each proven both ways.

A repair with no test is a claim. Each class below covers one of the four contradictions the
fixture exposed, and each asserts the accepted shape as well as the rejected one — a contract
that rejected both would look identical to one that rejects correctly.

The repairs, and what each replaced:

- R9 required `identity` of every `definition`, including `ddd: value-object`, which is defined
  by holding none. It is now required of the three constructs that have an identity and
  forbidden of the two that do not.
- R10 required a `quality-attribute` rule to declare "the system boundary, the one boundary
  that is not a bounded context", which `boundary.ddd` made unrepresentable. Such a rule now
  declares the bounded context it constrains, like every other rule.
- The closed edge vocabulary of R17 omitted `attributes[].of` and `rejections[].error` while
  R29 and R11 required both to resolve. Both are now edges. Covered in
  tests/test_edge_table_agreement.py, which reads the specification's table directly.
- `references` and `supersedes` were removed under R52 and `superseded_by` became a resolvable
  reference rather than an edge.
"""

from __future__ import annotations

from tests.support import KnowledgeCase

PROPOSAL = "definition/sales/proposal.md"
PROPOSAL_ITEM = "definition/sales/proposal-item.md"
EXPIRED = "definition/sales/proposal-expired.md"
RESPONSE_TIME = "rule/sales/proposal-response-time.md"
RETIRED_RULE = "rule/sales/proposal-validity.md"
READ_MODEL = "definition/sales/customer-proposals.md"


def attribute(data: dict, name: str) -> dict:
    return next(a for a in data["attributes"] if a["name"] == name)


class IdentityFollowsTheConstruct(KnowledgeCase):
    """R9 — required of an entity, aggregate root, or read model; forbidden of the other two."""

    def test_value_object_without_identity_is_accepted(self):
        data, _ = self.read(PROPOSAL_ITEM)
        self.assertEqual(data["ddd"], "value-object")
        self.assertNotIn("identity", data)
        self.assertAccepted()

    def test_value_object_with_identity_is_rejected(self):
        self.edit(PROPOSAL_ITEM, lambda d: d.update(identity={"attributes": ["description"]}))
        self.assertRejected("identity")

    def test_domain_error_with_identity_is_rejected(self):
        self.edit(EXPIRED, lambda d: d.update(identity={"attributes": ["proposal_number"]}))
        self.assertRejected("identity")

    def test_aggregate_root_without_identity_is_rejected(self):
        self.edit(PROPOSAL, lambda d: d.pop("identity"))
        self.assertRejected("'identity' is a required property")

    def test_aggregate_root_with_identity_is_accepted(self):
        data, _ = self.read(PROPOSAL)
        self.assertEqual(data["ddd"], "aggregate-root")
        self.assertIn("identity", data)
        self.assertAccepted()


class QualityAttributeDeclaresItsContext(KnowledgeCase):
    """R10 — a quality attribute is recorded against a bounded context, not an unrepresentable one."""

    def test_quality_attribute_rule_in_a_bounded_context_is_accepted(self):
        data, _ = self.read(RESPONSE_TIME)
        self.assertEqual(data["ddd"], "quality-attribute")
        self.assertEqual(data["boundary"], "ko.boundary.sales")
        self.assertAccepted()

    def test_quality_attribute_rule_needs_a_boundary_like_every_other_rule(self):
        self.edit(RESPONSE_TIME, lambda d: d.pop("boundary"))
        self.assertRejected("'boundary' is a required property")

    def test_no_boundary_kind_exists_for_a_system(self):
        """The rejected alternative, asserted so it cannot creep back in unnoticed.

        Admitting `ddd: system` was rejected for the reason the DDD mapping table already gives
        for not modelling the domain as a node: it would hold one instance.
        """
        self.edit("boundary/sales.md", lambda d: d.update(ddd="system"))
        self.assertRejected("'system' is not one of")


class BindingBindsBothPrimitives(KnowledgeCase):
    """R28 — a `ref` and a `list` carry `binding` identically.

    The asymmetry this closes was demonstrated, not theorised: the identical crossing was
    rejected as a `ref` and accepted as a `list`, so R28 claimed a mechanical check it
    delivered for half the cases. The last test here is the one that would have caught it.
    """

    def test_cross_aggregate_list_by_identity_is_accepted(self):
        data, _ = self.read(READ_MODEL)
        proposals = attribute(data, "proposals")
        self.assertEqual(proposals["type"], "list")
        self.assertEqual(proposals["binding"], "by-identity")
        self.assertEqual(data["boundary"], "ko.boundary.sales")
        self.assertAccepted()

    def test_cross_aggregate_list_embedded_is_rejected(self):
        self.edit(READ_MODEL, lambda d: attribute(d, "proposals").update(binding="embedded"))
        self.assertRejected("attributes.proposals", "by-identity")

    def test_same_aggregate_list_embedded_is_accepted(self):
        data, _ = self.read(PROPOSAL)
        items = attribute(data, "items")
        self.assertEqual(items["binding"], "embedded")
        self.assertAccepted()

    def test_list_without_binding_is_rejected(self):
        self.edit(PROPOSAL, lambda d: attribute(d, "items").pop("binding"))
        self.assertRejected("'binding' is a required property")

    def test_a_list_and_a_ref_across_one_boundary_are_judged_alike(self):
        """The regression that motivated the repair, expressed as one assertion.

        Both attributes cross out of `ko.boundary.sales.proposal` to another aggregate. Before
        the repair the `ref` was rejected and the `list` was not, so this test compares the two
        verdicts rather than asserting each separately.
        """
        as_ref = self.problems_after(
            PROPOSAL, lambda d: attribute(d, "customer").update(binding="embedded")
        )
        as_list = self.problems_after(
            READ_MODEL, lambda d: attribute(d, "proposals").update(binding="embedded")
        )
        self.assertTrue(any("by-identity" in p for p in as_ref), as_ref)
        self.assertTrue(any("by-identity" in p for p in as_list), as_list)


class SupersessionResolvesWithoutBeingTraversed(KnowledgeCase):
    """R22 and R40 — the target must resolve, and expansion must never follow it."""

    def test_superseded_object_with_a_resolving_replacement_is_accepted(self):
        data, _ = self.read(RETIRED_RULE)
        self.assertEqual(data["status"], "superseded")
        self.assertEqual(data["superseded_by"], "ko.rule.sales.proposal-expiration")
        self.assertAccepted()

    def test_superseded_by_naming_an_absent_node_is_rejected(self):
        self.edit(RETIRED_RULE, lambda d: d.update(superseded_by="ko.rule.sales.nowhere"))
        self.assertRejected("superseded_by", "which the graph does not hold")

    def test_superseded_by_naming_another_type_is_rejected(self):
        self.edit(RETIRED_RULE, lambda d: d.update(superseded_by="ko.lifecycle.sales.proposal"))
        self.assertRejected("superseded_by", "is replaced by")

    def test_superseded_status_without_a_replacement_is_rejected(self):
        self.edit(RETIRED_RULE, lambda d: d.pop("superseded_by"))
        self.assertRejected("'superseded_by' is a required property")
