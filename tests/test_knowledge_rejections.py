"""The eleven rejections specs/0003 requires before it may be accepted.

Validation item 2 of that specification enumerates what tests must prove the contract
rejects. Each case below names the item it discharges, and each mutates the fixture in
exactly one place so a passing test cannot be passing on an unrelated failure. The
unmutated tree is asserted clean in tests/test_knowledge_fixture.py.

Item 2 lists eleven cases; the ninth carries two variants — an undecided state-trigger
pair and an unreachable state — so twelve tests appear here.
"""

from __future__ import annotations

from pathlib import Path

from knowledge_graph_lib import Graph, Node
from tests.support import KnowledgeCase
from validate_knowledge import check_cardinality

PROPOSAL = "definition/sales/proposal.md"
PROPOSAL_ITEM = "definition/sales/proposal-item.md"
RULE = "rule/sales/proposal-expiration.md"
LIFECYCLE = "lifecycle/sales/proposal.md"
BILLING_LIFECYCLE = "lifecycle/billing/invoice.md"


class SchemaRejections(KnowledgeCase):
    """Cases the frontmatter contract decides on its own."""

    def test_unknown_type(self):
        self.edit(PROPOSAL, lambda d: d.update(type="widget"))
        self.assertRejected("'widget' is not one of")

    def test_missing_question(self):
        self.edit(PROPOSAL, lambda d: d.pop("question"))
        self.assertRejected("'question' is a required property")

    def test_empty_out_of_scope(self):
        self.edit(PROPOSAL, lambda d: d.update(out_of_scope=[]))
        self.assertRejected("out_of_scope")

    def test_rule_with_neither_expression_nor_examples(self):
        def strip(data):
            data.pop("expression")
            data.pop("examples")

        self.edit(RULE, strip)
        self.assertRejected("is not valid under any of the given schemas")

    def test_decimal_without_scale(self):
        def drop_scale(data):
            for attribute in data["attributes"]:
                if attribute["type"] == "decimal":
                    attribute.pop("scale")

        self.edit(PROPOSAL_ITEM, drop_scale)
        self.assertRejected("'scale' is a required property")

    def test_enum_repeating_lifecycle_states(self):
        """R27: a lifecycle-bound enum names the lifecycle and never restates the states."""

        def restate(data):
            for attribute in data["attributes"]:
                if attribute["type"] == "enum":
                    attribute["values"] = ["draft", "issued", "accepted", "expired", "cancelled"]

        self.edit(PROPOSAL, restate)
        self.assertRejected("attributes.", "is not valid under any of the given schemas")


class GraphRejections(KnowledgeCase):
    """Cases only the materialized graph can decide."""

    def test_ref_across_an_aggregate_without_by_identity(self):
        def embed(data):
            for attribute in data["attributes"]:
                if attribute["type"] == "ref":
                    attribute["binding"] = "embedded"

        self.edit(PROPOSAL, embed)
        self.assertRejected("by-identity", "attributes.customer")

    def test_two_lifecycles_over_one_subject(self):
        self.duplicate(
            BILLING_LIFECYCLE,
            "lifecycle/billing/invoice-audit.md",
            "ko.lifecycle.billing.invoice-audit",
        )
        self.assertRejected("inverse cardinality", "lifecycle.subject")

    def test_undecided_state_trigger_pair(self):
        def drop_a_rejection(data):
            data["rejections"] = [
                r for r in data["rejections"] if r["error"] != "ko.definition.sales.proposal-already-issued"
            ]

        self.edit(LIFECYCLE, drop_a_rejection)
        self.assertRejected("(issued, issue)", "not total")

    def test_unreachable_state(self):
        """A state no transition arrives at, isolated from every other lifecycle failure.

        The replacement table stays total and gives every non-terminal state an outgoing
        transition, so `unreachable` is the only thing left for the check to find.
        """

        def isolate(data):
            data["states"] = ["draft", "unreachable", "paid"]
            data["initial"] = "draft"
            data["terminal"] = ["paid"]
            data["transitions"] = [
                {"from": "draft", "trigger": "issue", "to": "paid"},
                {"from": "unreachable", "trigger": "issue", "to": "paid"},
            ]
            data["rejections"] = [
                {
                    "from": "terminal",
                    "trigger": ["issue"],
                    "error": "ko.definition.billing.invoice-terminal",
                }
            ]

        self.edit(BILLING_LIFECYCLE, isolate)
        self.assertRejected("'unreachable' is not reachable")

    def test_id_that_disagrees_with_its_path(self):
        self.rename(PROPOSAL, "definition/sales/offer.md")
        self.assertRejected("computes path")


class ForwardCardinality(KnowledgeCase):
    """Item 2's "a violated edge cardinality", on the one axis the schema cannot reach.

    Every forward cardinality in the edge table is 0..n or exactly-1 over a scalar field,
    so the frontmatter contract already rejects a violation before a graph exists: there is
    no schema-valid tree in which a definition declares zero or two `boundary` edges. The
    mechanism is therefore exercised against a graph built by hand. That the case is
    unreachable through valid input is itself a finding about R18, recorded in the
    fixture's README rather than hidden behind a passing test.
    """

    def test_missing_required_edge_is_reported(self):
        graph = Graph(root=Path("synthetic"))
        graph.nodes["ko.definition.sales.thing"] = Node(
            id="ko.definition.sales.thing",
            kind="definition",
            path=Path("synthetic/definition/sales/thing.md"),
            data={"type": "definition"},  # no `boundary`, so no boundary edge exists
        )
        check_cardinality(graph)
        self.assertTrue(
            any("'boundary' edge(s), and cardinality requires 1" in p for p in graph.problems),
            f"the forward cardinality check reported nothing: {graph.problems}",
        )

    def test_satisfied_required_edge_is_not_reported(self):
        graph = Graph(root=Path("synthetic"))
        graph.nodes["ko.boundary.sales"] = Node(
            id="ko.boundary.sales",
            kind="boundary",
            path=Path("synthetic/boundary/sales.md"),
            data={"type": "boundary", "ddd": "bounded-context"},
        )
        graph.nodes["ko.definition.sales.thing"] = Node(
            id="ko.definition.sales.thing",
            kind="definition",
            path=Path("synthetic/definition/sales/thing.md"),
            data={"type": "definition", "boundary": "ko.boundary.sales"},
        )
        from knowledge_graph_lib import _materialize_edges

        _materialize_edges(graph)
        check_cardinality(graph)
        self.assertEqual(graph.problems, [])
